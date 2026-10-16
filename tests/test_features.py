from pathlib import Path
import json, shutil
import pandas as pd
from build_features import build_features, write_features
from lakehouse.pipeline import run_pipeline
ROOT=Path(__file__).resolve().parents[1]

def _inputs(tmp_path):
    shutil.copytree(ROOT/"data/source",tmp_path/"data/source")
    run_pipeline(tmp_path,"fixtures")
    customers=pd.read_csv(tmp_path/"data/source/customers.csv")
    fact=pd.read_parquet(tmp_path/"data/gold/fact_sales.parquet")
    events=json.loads((tmp_path/"data/source/events.json").read_text(encoding="utf-8"))
    return customers,fact,events

def test_dataset_tem_unicidade_tipos_e_cliente_sem_compra(tmp_path):
    customers,fact,events=_inputs(tmp_path)
    features=build_features(customers,fact,events,"2025-04-01")
    assert len(features)==10 and features.customer_id.is_unique
    assert features.purchase_frequency.dtype.kind in "iu"
    assert features.loc[features.customer_id==1,"purchase_frequency"].item()==4
    never=features.loc[features.customer_id==9].iloc[0]
    assert never.purchase_frequency==0 and never.last_purchase_date is None
    assert pd.isna(never.recency_days)

def test_features_nao_usam_eventos_ou_compras_depois_da_data_de_referencia(tmp_path):
    customers,fact,events=_inputs(tmp_path)
    baseline=build_features(customers,fact,events,"2025-04-01")
    future_event={"event_id":"future","customer_id":1,"session_id":"future-session","occurred_at":"2025-04-01T12:00:00Z"}
    future_order=fact.iloc[[0]].copy();future_order["order_date"]="2025-04-01"
    updated=build_features(customers,pd.concat([fact,future_order],ignore_index=True),events+[future_event],"2025-04-01")
    a=baseline.loc[baseline.customer_id==1].iloc[0];b=updated.loc[updated.customer_id==1].iloc[0]
    assert a.purchase_frequency==b.purchase_frequency
    assert a.event_count==b.event_count

def test_exporta_parquet_e_manifest_de_features(tmp_path):
    shutil.copytree(ROOT/"data/source",tmp_path/"data/source")
    run_pipeline(tmp_path,"fixtures")
    summary=write_features(tmp_path,"2025-04-01")
    out=pd.read_parquet(tmp_path/"data/gold/customer_features.parquet")
    assert summary["rows"]==10 and summary["columns"]==12
    assert len(out)==10 and out.customer_id.is_unique
    assert summary["trained_model"] is False
