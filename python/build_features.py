"""Features RFM de clientes até uma data de corte fixa; nenhum alvo preditivo é treinado."""
from __future__ import annotations
import argparse, json
from datetime import date
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def build_features(customers: pd.DataFrame, fact: pd.DataFrame, events: list[dict], as_of: str | date = "2025-04-01") -> pd.DataFrame:
    cutoff = pd.Timestamp(as_of).normalize()
    orders=fact.copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"],errors="coerce").dt.normalize()
    orders=orders.loc[(orders["order_date"].notna()) & (orders["order_date"] < cutoff)].copy()
    event_rows=[]
    for e in events:
        ts=pd.to_datetime(e.get("occurred_at"),utc=True,errors="coerce")
        if pd.isna(ts) or ts.tz_convert(None).normalize() >= cutoff: continue
        cid=e.get("customer_id")
        if cid is not None: event_rows.append((int(cid),str(e.get("session_id")),str(e.get("event_id"))))
    event_df=pd.DataFrame(event_rows,columns=["customer_id","session_id","event_id"])
    # Agrega por pedido antes de calcular ticket; evita ponderar pedidos com mais linhas.
    order_level=(orders.groupby(["customer_id","order_id","order_date","channel"],as_index=False)
                 .agg(order_net=("net_amount","sum"),items=("quantity","sum"),returned=("returned_quantity","sum")))
    rows=[]
    for customer in customers[["customer_id"]].drop_duplicates().to_dict("records"):
        cid=int(customer["customer_id"])
        own=order_level.loc[order_level.customer_id.astype(int)==cid]
        if len(own):
            by_channel=own.groupby("channel").size().sort_values(ascending=False)
            predominant=sorted(by_channel[by_channel==by_channel.max()].index.astype(str))[0]
            last=own.order_date.max(); first=own.order_date.min()
            total=float(own.order_net.sum()); freq=int(own.order_id.nunique())
            recency=int((cutoff-last).days); days_first=int((cutoff-first).days)
            ticket=total/freq; total_items=int((own["items"]-own["returned"]).sum())
        else:
            predominant=None; last=pd.NaT; recency=None; days_first=None; total=0.0; freq=0; ticket=None; total_items=0
        eown=event_df.loc[event_df.customer_id==cid] if len(event_df) else event_df
        rows.append({"customer_id":cid,"reference_date":cutoff.date().isoformat(),"last_purchase_date":None if pd.isna(last) else last.date().isoformat(),
                     "recency_days":recency,"purchase_frequency":freq,"monetary_total":round(total,2),
                     "average_ticket":None if ticket is None else round(ticket,2),"total_items":total_items,
                     "predominant_channel":predominant,"days_since_first_purchase":days_first,
                     "event_count":int(len(eown)),"session_count":int(eown.session_id.nunique()) if len(eown) else 0})
    result=pd.DataFrame(rows)
    return result.sort_values("customer_id").reset_index(drop=True)

def write_features(root: Path=ROOT, as_of: str="2025-04-01") -> dict:
    customers=pd.read_csv(root/"data/source/customers.csv")
    fact=pd.read_parquet(root/"data/gold/fact_sales.parquet")
    events=json.loads((root/"data/source/events.json").read_text(encoding="utf-8"))
    features=build_features(customers,fact,events,as_of)
    dest=root/"data/gold/customer_features.parquet"; dest.parent.mkdir(parents=True,exist_ok=True)
    features.to_parquet(dest,index=False,engine="pyarrow")
    manifest={"path":str(dest.relative_to(root)),"rows":len(features),"columns":len(features.columns),"nulls":features.isna().sum().astype(int).to_dict(),"reference_date":as_of,"trained_model":False}
    (root/"data/gold/customer_features_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=ROOT);p.add_argument("--as-of",default="2025-04-01");a=p.parse_args()
    print(json.dumps(write_features(a.root,a.as_of),ensure_ascii=False,indent=2))
