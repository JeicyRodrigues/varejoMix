"""Pipeline local Bronze -> Silver -> Gold com Parquet e Delta Lake (delta-rs)."""
from __future__ import annotations
import argparse, hashlib, json, logging, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
import duckdb
import pandas as pd
import pyarrow as pa
from deltalake import DeltaTable, write_deltalake
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from extract_data import read_fixtures, extract_services
from transform_data import clean_tables, processing_metadata

LOG = logging.getLogger("varejomix.pipeline")

def _stable_value(data):
    if isinstance(data, pd.DataFrame):
        return json.loads(data.to_json(orient="records", date_format="iso", date_unit="us"))
    return data

def _run_id(data, source: str) -> str:
    payload = json.dumps({k: _stable_value(v) for k, v in sorted(data.items())}, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256((source + payload).encode("utf-8")).hexdigest()[:16]

def _write_parquet(df: pd.DataFrame, path: Path, partitions: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.is_dir(): shutil.rmtree(path)
        else: path.unlink()
    if partitions and len(df):
        df.to_parquet(path, index=False, engine="pyarrow", partition_cols=partitions)
    else:
        if path.suffix == "": path.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False, engine="pyarrow")

def build_fact(frames: dict[str, pd.DataFrame], source: str, run_id: str) -> pd.DataFrame:
    orders = frames["orders"].copy()
    items = frames["order_items"].copy()
    products = frames["products"].copy()
    stores = frames["stores"].copy()
    customers = frames["customers"].copy()
    cats = frames["categories"].copy()
    orders["customer_id"] = orders["customer_id"].astype(int)
    orders["store_id"] = orders["store_id"].astype(int)
    items["order_id"] = items["order_id"].astype(int)
    items["product_id"] = items["product_id"].astype(int)
    products["product_id"] = products["product_id"].astype(int)
    products["category_id"] = products["category_id"].astype(int)
    # O preço de catálogo não substitui o preço histórico congelado no item vendido.
    products = products.rename(columns={"unit_price": "catalog_unit_price"})
    sales = orders.loc[orders["status"] == "completed"].merge(items, on="order_id", validate="one_to_many")
    sales = sales.merge(products, on="product_id", validate="many_to_one")
    sales = sales.merge(cats, on="category_id", validate="many_to_one")
    sales = sales.merge(stores, on="store_id", validate="many_to_one")
    sales = sales.merge(customers[["customer_id"]], on="customer_id", validate="many_to_one")
    sales["order_date"] = sales["ordered_at"].dt.strftime("%Y-%m-%d")
    sales["order_month"] = sales["ordered_at"].dt.strftime("%Y-%m")
    sales["gross_amount"] = (sales["quantity"].astype(float) * sales["unit_price"].astype(float)).round(2)
    sales["return_amount"] = (sales["returned_quantity"].astype(float) * (sales["unit_price"].astype(float) - sales["discount_amount"].astype(float) / sales["quantity"].astype(float))).round(2)
    sales["net_amount"] = (sales["gross_amount"] - sales["discount_amount"].astype(float) - sales["return_amount"]).round(2)
    sales["estimated_cost"] = ((sales["quantity"].astype(float) - sales["returned_quantity"].astype(float)) * sales["unit_cost"].astype(float)).round(2)
    sales["margin_amount"] = (sales["net_amount"] - sales["estimated_cost"]).round(2)
    out = sales[["order_id","order_item_id","customer_id","product_id","product_name","category_name","order_date","order_month","store_id","store_name","channel","quantity","returned_quantity","gross_amount","discount_amount","return_amount","net_amount","estimated_cost","margin_amount"]].copy()
    out["_source"] = source; out["_run_id"] = run_id
    out["_processed_at_utc"] = datetime.now(timezone.utc).isoformat()
    if out["order_item_id"].duplicated().any():
        raise ValueError("A fato Gold não respeitou a granularidade de uma linha por item")
    return out

def run_pipeline(root: Path = ROOT, source: str = "fixtures") -> dict:
    source_dir = root / "data/source"
    if source == "fixtures":
        if not (source_dir / "orders.csv").exists():
            sys.path.insert(0, str(root/"python")); import synthetic_data; synthetic_data.write_sources(root)
        data = read_fixtures(source_dir)
        source_label = "synthetic_fixture"
    elif source == "services":
        data = extract_services(); source_label = "postgresql+mongodb"
    else:
        raise ValueError("source deve ser fixtures ou services")
    run_id = _run_id(data, source_label)
    processed_at = datetime.now(timezone.utc).isoformat()
    bronze_path = root / "data/bronze" / f"run_id={run_id}"
    bronze_path.mkdir(parents=True, exist_ok=True)
    # Raw snapshot idempotente: mesmo conteúdo produz a mesma pasta, sem novos snapshots duplicados.
    for name, value in data.items():
        target = bronze_path / (f"{name}.json" if name == "events" else f"{name}.csv")
        if isinstance(value, pd.DataFrame): value.to_csv(target, index=False)
        else: target.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    frames, rejects = clean_tables(data)
    # Cross-row total validation is not a CHECK constraint; it is enforced as a pipeline assertion.
    expected = frames["order_items"].assign(line_total=lambda x: x.quantity.astype(float)*x.unit_price.astype(float)-x.discount_amount.astype(float)).groupby("order_id").line_total.sum()
    declared = frames["orders"].set_index("order_id")["order_total"].astype(float)
    mismatches = [(int(k),float(v),float(expected.get(k,0))) for k,v in declared.items() if abs(v-float(expected.get(k,0))) > .01]
    if mismatches:
        raise ValueError(f"Totais de pedido divergem dos itens: {mismatches}")
    if rejects:
        (root/"data/silver/rejects.json").write_text(json.dumps(rejects,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    silver_dir = root / "data/silver"
    silver_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in frames.items():
        out = processing_metadata(frame, source_label, run_id)
        if name == "orders" and len(out): out["order_month"] = out["ordered_at"].dt.strftime("%Y-%m")
        if name == "events" and len(out):
            out["properties_json"] = out["properties"].map(lambda x: json.dumps(x,ensure_ascii=False,sort_keys=True))
            out = out.drop(columns=["properties"])
            out["event_date"] = pd.to_datetime(out["occurred_at"],utc=True).dt.strftime("%Y-%m-%d")
            _write_parquet(out, silver_dir / "events_by_date", ["event_date"])
        else:
            _write_parquet(out, silver_dir / f"{name}.parquet")
    fact = build_fact(frames, source_label, run_id)
    gold = root / "data/gold"; gold.mkdir(parents=True, exist_ok=True)
    _write_parquet(fact, gold/"fact_sales.parquet")
    _write_parquet(fact, gold/"fact_sales_by_month", ["order_month"])
    dim_frames = {
        "dim_customer": frames["customers"], "dim_product": frames["products"],
        "dim_store": frames["stores"], "dim_category": frames["categories"]
    }
    for name, df in dim_frames.items():
        _write_parquet(processing_metadata(df,source_label,run_id), gold/f"{name}.parquet")
    delta_path = gold/"fact_sales_delta"
    old_version = DeltaTable(str(delta_path)).version() if (delta_path/"_delta_log").exists() else None
    arrow = pa.Table.from_pandas(fact, preserve_index=False)
    write_deltalake(str(delta_path), arrow, mode="overwrite" if old_version is not None else "error", partition_by=["order_month"], schema_mode="overwrite" if old_version is not None else None)
    delta = DeltaTable(str(delta_path))
    latest_version = delta.version()
    previous_rows = None
    previous_read_ok = None
    if old_version is not None:
        previous_rows = DeltaTable(str(delta_path), version=old_version).to_pyarrow_table().num_rows
        previous_read_ok = previous_rows == len(fact)
    con = duckdb.connect()
    try:
        monthly = con.execute("SELECT order_month, channel, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(net_amount),2) AS net_revenue FROM read_parquet(?) GROUP BY 1,2 ORDER BY 1,2", [str(gold/"fact_sales.parquet")]).df()
    finally: con.close()
    monthly.to_csv(gold/"monthly_sales_duckdb.csv",index=False)
    manifest={"run_id":run_id,"source":source_label,"processed_at_utc":processed_at,
              "counts":{"customers":len(frames["customers"]),"orders":len(frames["orders"]),"order_items":len(frames["order_items"]),"events":len(frames["events"]),"fact_sales":len(fact),"rejected_records":len(rejects)},
              "delta":{"path":str(delta_path.relative_to(root)),"previous_version_before_run":old_version,"version_after_run":latest_version,"previous_rows_read":previous_rows,"previous_version_read_ok":previous_read_ok},
              "gross_revenue":round(float(fact.gross_amount.sum()),2),"net_revenue":round(float(fact.net_amount.sum()),2),"estimated_margin":round(float(fact.margin_amount.sum()),2),
              "idempotency":"Gold fact is fully overwritten from deduplicated stable natural keys; repeated snapshot contains one row per order_item_id."}
    (gold/"pipeline_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    LOG.info("run_id=%s rows=%s events=%s delta_version=%s",run_id,len(fact),len(frames["events"]),latest_version)
    return manifest

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--root",type=Path,default=ROOT); parser.add_argument("--source",choices=["fixtures","services"],default="fixtures"); parser.add_argument("--log-level",default="INFO")
    args=parser.parse_args(); logging.basicConfig(level=getattr(logging,args.log_level.upper(),logging.INFO),format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try: print(json.dumps(run_pipeline(args.root,args.source),ensure_ascii=False,indent=2))
    except Exception:
        LOG.exception("Pipeline falhou; saída deve ser inspecionada antes de consumo")
        raise
