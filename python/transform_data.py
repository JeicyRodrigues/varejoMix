"""Transformações determinísticas de Bronze para Silver."""
from __future__ import annotations
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
import pandas as pd
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "nosql" / "event_schema.json"

def validate_events(events: list[dict], customer_ids: set[int] | None = None) -> tuple[pd.DataFrame, list[dict]]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    accepted: list[dict] = []
    rejected: list[dict] = []
    seen: set[str] = set()
    for pos, event in enumerate(events):
        errors = sorted(validator.iter_errors(event), key=lambda e: list(e.path))
        reason = "; ".join(f"{'.'.join(map(str, e.path)) or '$'}: {e.message}" for e in errors)
        if not reason:
            try:
                stamp = pd.to_datetime(event["occurred_at"], utc=True, errors="raise")
                if pd.isna(stamp):
                    raise ValueError("timestamp ausente")
                event = {**event, "occurred_at": stamp.isoformat().replace("+00:00", "Z")}
            except (ValueError, TypeError, KeyError) as exc:
                reason = f"occurred_at inválido: {exc}"
        if not reason and event["event_id"] in seen:
            # Duplicata idempotente: não conta duas vezes, mas não é erro fatal.
            continue
        if not reason and customer_ids is not None and event.get("customer_id") is not None and event["customer_id"] not in customer_ids:
            reason = "customer_id sem correspondência no snapshot de clientes"
        if reason:
            rejected.append({"position": pos, "record": event, "reason": reason})
        else:
            seen.add(event["event_id"])
            accepted.append(event)
    return pd.DataFrame(accepted), rejected

def clean_tables(data: dict[str, Any]) -> tuple[dict[str, pd.DataFrame], list[dict]]:
    frames = {name: value.copy() for name, value in data.items() if name != "events" and isinstance(value, pd.DataFrame)}
    rejects: list[dict] = []
    # Conversões tipadas e normalização de timestamps em UTC.
    if "orders" in frames:
        frames["orders"]["ordered_at"] = pd.to_datetime(frames["orders"]["ordered_at"], utc=True, errors="coerce")
    if "inventory_movements" in frames:
        frames["inventory_movements"]["moved_at"] = pd.to_datetime(frames["inventory_movements"]["moved_at"], utc=True, errors="coerce")
    for table, key in [("customers", "customer_id"), ("products", "product_id"), ("stores", "store_id"),
                       ("orders", "order_id"), ("order_items", "order_item_id"),
                       ("payments", "payment_id"), ("inventory_movements", "movement_id")]:
        if table in frames:
            dup = frames[table].duplicated(key, keep="first")
            for _, row in frames[table].loc[dup].iterrows():
                rejects.append({"table": table, "record": row.where(pd.notna(row), None).to_dict(), "reason": f"duplicata {key}"})
            frames[table] = frames[table].drop_duplicates(key, keep="first").reset_index(drop=True)
    if "orders" in frames:
        bad = frames["orders"]["ordered_at"].isna() | frames["orders"]["customer_id"].isna()
        for _, row in frames["orders"].loc[bad].iterrows():
            rejects.append({"table": "orders", "record": row.where(pd.notna(row), None).to_dict(), "reason": "timestamp ou cliente inválido/ausente"})
        frames["orders"] = frames["orders"].loc[~bad].copy()
    if "order_items" in frames and "orders" in frames and "products" in frames:
        valid_orders = set(frames["orders"]["order_id"].astype(int))
        valid_products = set(frames["products"]["product_id"].astype(int))
        invalid = ~frames["order_items"]["order_id"].astype(int).isin(valid_orders) | ~frames["order_items"]["product_id"].astype(int).isin(valid_products)
        for _, row in frames["order_items"].loc[invalid].iterrows():
            rejects.append({"table": "order_items", "record": row.where(pd.notna(row), None).to_dict(), "reason": "pedido ou produto referenciado inexistente"})
        frames["order_items"] = frames["order_items"].loc[~invalid].copy()
        value_bad = (frames["order_items"]["quantity"].astype(int) <= 0) | (frames["order_items"]["returned_quantity"].astype(int) < 0) | (frames["order_items"]["returned_quantity"].astype(int) > frames["order_items"]["quantity"].astype(int))
        for _, row in frames["order_items"].loc[value_bad].iterrows():
            rejects.append({"table": "order_items", "record": row.where(pd.notna(row), None).to_dict(), "reason": "quantidade inválida"})
        frames["order_items"] = frames["order_items"].loc[~value_bad].copy()
    event_frame, event_rejects = validate_events(data.get("events", []), set(frames.get("customers", pd.DataFrame(columns=["customer_id"]))["customer_id"].dropna().astype(int)))
    rejects.extend({"table": "events", **r} for r in event_rejects)
    frames["events"] = event_frame
    return frames, rejects

def processing_metadata(df: pd.DataFrame, source: str, run_id: str) -> pd.DataFrame:
    out = df.copy()
    out["_source"] = source
    out["_processed_at_utc"] = datetime.now(timezone.utc).isoformat()
    out["_run_id"] = run_id
    return out
