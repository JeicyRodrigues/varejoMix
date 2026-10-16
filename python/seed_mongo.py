"""Valida e faz upsert das fixtures de eventos na collection MongoDB."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from pymongo import MongoClient, ReplaceOne
from jsonschema import Draft202012Validator, FormatChecker
ROOT = Path(__file__).resolve().parents[1]

def seed(uri: str, database: str, source: Path) -> int:
    schema = json.loads((ROOT / "nosql/event_schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    events = json.loads(source.read_text(encoding="utf-8"))
    for i, event in enumerate(events):
        errors = list(validator.iter_errors(event))
        if errors:
            raise ValueError(f"Evento posição {i} inválido: {errors[0].message}")
    with MongoClient(uri, serverSelectionTimeoutMS=4000) as client:
        client.admin.command("ping")
        db = client[database]
        name = os.getenv("MONGO_COLLECTION", "behavior_events")
        if name not in db.list_collection_names():
            db.create_collection(name, validator={"$jsonSchema": {
                "bsonType": "object", "required": ["event_id", "session_id", "occurred_at", "channel", "event_type", "properties"],
                "properties": {"event_id": {"bsonType": "string"}, "session_id": {"bsonType": "string"},
                               "occurred_at": {"bsonType": "string"}, "channel": {"enum": ["loja", "ecommerce"]},
                               "event_type": {"enum": ["page_view", "search", "add_to_cart", "checkout_start", "purchase"]},
                               "properties": {"bsonType": "object"}}
            }})
        collection = db[name]
        collection.create_index("event_id", unique=True, name="uq_event_id")
        collection.create_index([("session_id", 1), ("occurred_at", 1)], name="ix_session_time")
        collection.create_index([("event_type", 1), ("occurred_at", 1)], name="ix_type_time")
        collection.create_index([("customer_id", 1), ("occurred_at", 1)], name="ix_customer_time")
        if events:
            collection.bulk_write([ReplaceOne({"event_id": e["event_id"]}, e, upsert=True) for e in events], ordered=False)
        return collection.count_documents({})

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--uri", default=os.getenv("MONGO_URI", "mongodb://localhost:27017")); p.add_argument("--database", default=os.getenv("MONGO_DATABASE", "varejomix")); p.add_argument("--source", type=Path, default=ROOT / "data/source/events.json")
    a = p.parse_args(); print(f"MongoDB respondeu; documentos na collection: {seed(a.uri,a.database,a.source)}")
