from pathlib import Path
import shutil
import pandas as pd
from lakehouse.pipeline import run_pipeline
ROOT=Path(__file__).resolve().parents[1]

def _run(tmp_path):
    shutil.copytree(ROOT/"data/source",tmp_path/"data/source")
    return run_pipeline(tmp_path,"fixtures")

def test_receita_e_margem_batem_totais_sinteticos(tmp_path):
    result=_run(tmp_path)
    assert result["gross_revenue"]==4671.47
    assert result["net_revenue"]==4402.47
    assert result["estimated_margin"]==1482.47

def test_fato_tem_uma_linha_por_item_e_join_nao_duplica_valores(tmp_path):
    _run(tmp_path)
    fact=pd.read_parquet(tmp_path/"data/gold/fact_sales.parquet")
    products=pd.read_csv(tmp_path/"data/source/products.csv")
    assert len(fact)==21
    assert fact.order_item_id.is_unique
    joined=fact.merge(products[["product_id","sku"]],on="product_id",validate="many_to_one")
    assert joined.order_item_id.nunique()==len(fact)
    assert round(joined.net_amount.sum(),2)==4402.47

def test_receita_por_canal_confere_com_soma_item_a_item(tmp_path):
    _run(tmp_path)
    fact=pd.read_parquet(tmp_path/"data/gold/fact_sales.parquet")
    source_orders=pd.read_csv(tmp_path/"data/source/orders.csv")
    source_items=pd.read_csv(tmp_path/"data/source/order_items.csv")
    expected=(source_items.merge(source_orders,on="order_id",validate="many_to_one")
              .query("status == 'completed'")
              .assign(net=lambda d:d.quantity*d.unit_price-d.discount_amount-d.returned_quantity*(d.unit_price-d.discount_amount/d.quantity))
              .groupby("channel").net.sum().round(2).to_dict())
    actual=fact.groupby("channel").net_amount.sum().round(2).to_dict()
    assert actual==expected
