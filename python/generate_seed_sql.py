"""Gera scripts SQL estáticos a partir do catálogo determinístico de fixtures."""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import synthetic_data as sd

def q(v):
    if v is None or v == "": return "NULL"
    if isinstance(v, bool): return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)): return str(v)
    return "'" + str(v).replace("'", "''") + "'"

def insert(table, rows, columns):
    return f"INSERT INTO {table} ({', '.join(columns)})\nVALUES\n" + ",\n".join("  (" + ", ".join(q(r.get(c)) for c in columns) + ")" for r in rows) + "\nON CONFLICT DO NOTHING;\n"

def main():
    sd.write_sources(ROOT)
    base = ROOT / "data/source"
    def csvrows(name):
        with (base / f"{name}.csv").open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))
    rows=["-- Carga idempotente das fixtures geradas por python/synthetic_data.py.\nBEGIN;\n"]
    for table, data, cols in [
        ("categories", sd.CATEGORIES, ["category_id","category_name"]),
        ("customers", sd.CUSTOMERS, ["customer_id","full_name","email","city","created_at"]),
        ("products", sd.PRODUCTS, ["product_id","sku","product_name","category_id","unit_price","unit_cost"]),
        ("stores", sd.STORES, ["store_id","store_name","city","store_type"]),
    ]: rows.append(insert(table,data,cols))
    totals={}
    for item in sd.ITEMS:
        totals[item["order_id"]]=totals.get(item["order_id"],0)+item["quantity"]*item["unit_price"]-item["discount_amount"]
    orders=[dict(o,order_total=f"{totals[o['order_id']]:.2f}") for o in sd.ORDERS]
    rows.append(insert("orders",orders,["order_id","customer_id","store_id","ordered_at","channel","status","order_total"]))
    rows.append(insert("order_items",sd.ITEMS,["order_item_id","order_id","product_id","quantity","unit_price","discount_amount","returned_quantity"]))
    pays=csvrows("payments")
    for p in pays:
        for c in ("payment_id","order_id"): p[c]=int(p[c])
        p["amount"]=f"{float(p['amount']):.2f}"
        if not p["paid_at"]: p["paid_at"]=None
    rows.append(insert("payments",pays,["payment_id","order_id","payment_method","amount","payment_status","paid_at"]))
    inv=csvrows("inventory_movements")
    for m in inv:
        for c in ("movement_id","store_id","product_id","quantity_delta"): m[c]=int(m[c])
    rows.append(insert("inventory_movements",inv,["movement_id","store_id","product_id","moved_at","movement_type","quantity_delta"]))
    for table, col in [("categories","category_id"),("customers","customer_id"),("products","product_id"),("stores","store_id"),("orders","order_id"),("order_items","order_item_id"),("payments","payment_id"),("inventory_movements","movement_id")]:
        rows.append(f"SELECT setval(pg_get_serial_sequence('{table}','{col}'), GREATEST(COALESCE((SELECT MAX({col}) FROM {table}),1),1), true);\n")
    rows.append("COMMIT;\n")
    (ROOT/"sql/02_seed_data.sql").write_text("\n".join(rows),encoding="utf-8")

    events=json.loads((base/"events.json").read_text(encoding="utf-8"))
    vals=[]
    for e in events:
        props=json.dumps(e["properties"],ensure_ascii=False,separators=(",",":"))
        vals.append("  ("+", ".join([q(e["event_id"]),q(e.get("customer_id")),q(e["session_id"]),q(e["occurred_at"]),q(e["channel"]),q(e["event_type"]),q(props)])+")")
    event_sql="""-- Espelho analítico derivado das fixtures Mongo. Em produção, extração Python/Mongo substitui este seed.\n-- event_id é chave natural; cada reexecução faz upsert sem duplicar eventos.\nBEGIN;\nCREATE TEMP TABLE event_input(event_id TEXT,customer_id INTEGER,session_id TEXT,occurred_at TEXT,channel TEXT,event_type TEXT,properties TEXT) ON COMMIT DROP;\nINSERT INTO event_input VALUES\n"""+",\n".join(vals)+";\nINSERT INTO dw.dim_date(date_key,calendar_date,calendar_year,calendar_month,year_month)\nSELECT DISTINCT TO_CHAR(occurred_at::timestamptz::date,'YYYYMMDD')::INTEGER, occurred_at::timestamptz::date,\n       EXTRACT(YEAR FROM occurred_at::timestamptz)::INTEGER, EXTRACT(MONTH FROM occurred_at::timestamptz)::INTEGER,\n       TO_CHAR(occurred_at::timestamptz,'YYYY-MM') FROM event_input\nON CONFLICT(date_key) DO NOTHING;\nINSERT INTO dw.fact_session_events(event_id,customer_key,session_id,occurred_at,date_key,channel_key,event_type,properties)\nSELECT e.event_id,dc.customer_key,e.session_id,e.occurred_at::timestamptz,\n       TO_CHAR(e.occurred_at::timestamptz::date,'YYYYMMDD')::INTEGER,dch.channel_key,e.event_type,e.properties::jsonb\nFROM event_input e LEFT JOIN dw.dim_customer dc ON dc.customer_id=e.customer_id\nJOIN dw.dim_channel dch ON dch.channel_name=e.channel\nON CONFLICT(event_id) DO UPDATE SET customer_key=EXCLUDED.customer_key,session_id=EXCLUDED.session_id,\n  occurred_at=EXCLUDED.occurred_at,date_key=EXCLUDED.date_key,channel_key=EXCLUDED.channel_key,\n  event_type=EXCLUDED.event_type,properties=EXCLUDED.properties;\nCOMMIT;\n"
    (ROOT/"sql/07_behavioral_event_mirror.sql").write_text(event_sql,encoding="utf-8")
    print(f"Seeds SQL regenerados: {ROOT/'sql/02_seed_data.sql'} e {ROOT/'sql/07_behavioral_event_mirror.sql'}")
if __name__ == "__main__": main()
