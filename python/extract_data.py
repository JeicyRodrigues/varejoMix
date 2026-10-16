"""Extração de fontes reais, quando configuradas, e fixtures sintéticas locais."""
from __future__ import annotations
import json
import os
from pathlib import Path
import pandas as pd

TABLES = ["categories", "customers", "products", "stores", "orders", "order_items", "payments", "inventory_movements"]

def read_fixtures(source_dir: Path) -> dict[str, pd.DataFrame | list[dict]]:
    data: dict[str, pd.DataFrame | list[dict]] = {}
    for table in TABLES:
        data[table] = pd.read_csv(source_dir / f"{table}.csv")
    with (source_dir / "events.json").open(encoding="utf-8") as f:
        data["events"] = json.load(f)
    return data

def extract_postgres(database_url: str) -> dict[str, pd.DataFrame]:
    """Read OLTP tables using SQLAlchemy and pandas.read_sql."""
    from sqlalchemy import create_engine, text
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            return {table: pd.read_sql(text(f'SELECT * FROM "{table}"'), connection) for table in TABLES}
    finally:
        engine.dispose()

def extract_mongo(uri: str, database: str, collection: str) -> list[dict]:
    from pymongo import MongoClient
    with MongoClient(uri, serverSelectionTimeoutMS=4000) as client:
        client.admin.command("ping")
        return list(client[database][collection].find({}, {"_id": 0}).sort("event_id", 1))

def extract_services() -> dict[str, pd.DataFrame | list[dict]]:
    url = os.getenv("DATABASE_URL")
    mongo_uri = os.getenv("MONGO_URI")
    if not url or not mongo_uri:
        raise RuntimeError("source=services requer DATABASE_URL e MONGO_URI; use source=fixtures para modo offline")
    data = extract_postgres(url)
    data["events"] = extract_mongo(mongo_uri, os.getenv("MONGO_DATABASE", "varejomix"), os.getenv("MONGO_COLLECTION", "behavior_events"))
    return data
