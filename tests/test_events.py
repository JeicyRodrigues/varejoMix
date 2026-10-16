import json
from pathlib import Path
import pandas as pd
from transform_data import validate_events, clean_tables
from extract_data import read_fixtures
ROOT=Path(__file__).resolve().parents[1]

def test_eventos_sinteticos_validam_contrato():
    rows=json.loads((ROOT/"data/source/events.json").read_text(encoding="utf-8"))
    valid,rejected=validate_events(rows,set(range(1,11)))
    assert rejected==[]
    assert len(valid)==len(rows)==29
    assert valid.event_id.is_unique

def test_deduplica_identificador_e_rejeita_timestamps_ausentes_invalidos():
    rows=json.loads((ROOT/"data/source/events.json").read_text(encoding="utf-8"))[:1]
    rows += [dict(rows[0]), {**rows[0],"event_id":"bad-time","occurred_at":"not-a-timestamp"},
             {**rows[0],"event_id":"missing-time","occurred_at":None}]
    valid,rejected=validate_events(rows,set(range(1,11)))
    assert len(valid)==1
    assert len(rejected)==2
    assert all("occurred_at" in item["reason"] for item in rejected)

def test_sessao_obrigatoria_cliente_conhecido_ou_anonimo_e_integridade_de_eventos():
    rows=json.loads((ROOT/"data/source/events.json").read_text(encoding="utf-8"))[:1]
    bad=[{**rows[0],"event_id":"unknown-customer","customer_id":999}, {**rows[0],"event_id":"no-session","session_id":""}]
    valid,rejected=validate_events(rows+bad,{1,2,3})
    assert len(valid)==1
    assert any("customer_id" in r["reason"] for r in rejected)
    assert any("session_id" in r["reason"] for r in rejected)

def test_limpeza_separa_item_com_referencia_invalida():
    data=read_fixtures(ROOT/"data/source")
    data["order_items"]=pd.concat([data["order_items"],pd.DataFrame([{"order_item_id":99999,"order_id":99999,"product_id":1,"quantity":1,"unit_price":10,"discount_amount":0,"returned_quantity":0}])],ignore_index=True)
    frames,rejects=clean_tables(data)
    assert len(frames["order_items"])==22
    assert any("inexistente" in r["reason"] for r in rejects)
