from pathlib import Path
import shutil
import pandas as pd
from deltalake import DeltaTable
from lakehouse.pipeline import run_pipeline
from extract_data import read_fixtures
from transform_data import clean_tables
ROOT=Path(__file__).resolve().parents[1]

def test_reprocessamento_sem_duplicar_e_leitura_de_versao_anterior(tmp_path):
    shutil.copytree(ROOT/"data/source",tmp_path/"data/source")
    first=run_pipeline(tmp_path,"fixtures")
    second=run_pipeline(tmp_path,"fixtures")
    fact=pd.read_parquet(tmp_path/"data/gold/fact_sales.parquet")
    assert first["counts"]["fact_sales"]==second["counts"]["fact_sales"]==21
    assert fact.order_item_id.is_unique
    assert second["delta"]["version_after_run"]==1
    assert second["delta"]["previous_version_before_run"]==0
    assert second["delta"]["previous_rows_read"]==21
    assert second["delta"]["previous_version_read_ok"] is True
    historical=DeltaTable(str(tmp_path/"data/gold/fact_sales_delta"),version=0).to_pyarrow_table()
    assert historical.num_rows==21

def test_bronze_silver_gold_parquet_duckdb_e_contagens(tmp_path):
    shutil.copytree(ROOT/"data/source",tmp_path/"data/source")
    result=run_pipeline(tmp_path,"fixtures")
    rid=result["run_id"]
    assert (tmp_path/f"data/bronze/run_id={rid}/orders.csv").exists()
    assert (tmp_path/"data/silver/orders.parquet").exists()
    assert (tmp_path/"data/silver/events_by_date").is_dir()
    assert (tmp_path/"data/gold/fact_sales.parquet").exists()
    assert (tmp_path/"data/gold/monthly_sales_duckdb.csv").exists()
    assert result["counts"]["rejected_records"]==0

def test_registros_invalidos_sao_documentados_em_quarentena():
    data=read_fixtures(ROOT/"data/source")
    data["events"] += [{**data["events"][0],"event_id":"evt-invalid","occurred_at":"invalid"}]
    frames,rejects=clean_tables(data)
    assert len(frames["events"])==29
    assert any(r.get("table")=="events" and "occurred_at" in r["reason"] for r in rejects)
