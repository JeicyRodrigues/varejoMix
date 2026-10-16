"""Fixtures sintéticas determinísticas do projeto VarejoMix."""
from __future__ import annotations
import argparse
import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CATEGORIES = [
    {"category_id": 1, "category_name": "Eletrônicos"},
    {"category_id": 2, "category_name": "Casa e cozinha"},
    {"category_id": 3, "category_name": "Livros e acessórios"},
]
PRODUCTS = [
    {"product_id": 1, "sku": "VM-1001", "product_name": "Notebook Essencial", "category_id": 1, "unit_price": 899.99, "unit_cost": 660.00},
    {"product_id": 2, "sku": "VM-1002", "product_name": "Fone Bluetooth", "category_id": 1, "unit_price": 79.90, "unit_cost": 38.00},
    {"product_id": 3, "sku": "VM-2001", "product_name": "Cafeteira Compacta", "category_id": 2, "unit_price": 129.00, "unit_cost": 70.00},
    {"product_id": 4, "sku": "VM-2002", "product_name": "Café Especial 500g", "category_id": 2, "unit_price": 22.50, "unit_cost": 12.00},
    {"product_id": 5, "sku": "VM-3001", "product_name": "Livro Dados no Varejo", "category_id": 3, "unit_price": 45.00, "unit_cost": 20.00},
    {"product_id": 6, "sku": "VM-3002", "product_name": "Mochila Urbana", "category_id": 3, "unit_price": 159.00, "unit_cost": 75.00},
]
STORES = [
    {"store_id": 1, "store_name": "Centro", "city": "São Paulo", "store_type": "physical"},
    {"store_id": 2, "store_name": "Shopping Norte", "city": "São Paulo", "store_type": "physical"},
    {"store_id": 3, "store_name": "Loja virtual", "city": "Online", "store_type": "ecommerce"},
]
CUSTOMERS = [
    {"customer_id": 1, "full_name": "Ana Lima", "email": "ana.lima@example.test", "city": "São Paulo", "created_at": "2024-11-10"},
    {"customer_id": 2, "full_name": "Bruno Costa", "email": "bruno.costa@example.test", "city": "Campinas", "created_at": "2024-11-12"},
    {"customer_id": 3, "full_name": "Carla Souza", "email": "carla.souza@example.test", "city": "São Paulo", "created_at": "2024-11-15"},
    {"customer_id": 4, "full_name": "Diego Alves", "email": "diego.alves@example.test", "city": "Santos", "created_at": "2024-11-20"},
    {"customer_id": 5, "full_name": "Elisa Rocha", "email": "elisa.rocha@example.test", "city": "Campinas", "created_at": "2024-12-01"},
    {"customer_id": 6, "full_name": "Fabio Reis", "email": "fabio.reis@example.test", "city": "São Paulo", "created_at": "2024-12-06"},
    {"customer_id": 7, "full_name": "Gabi Melo", "email": "gabi.melo@example.test", "city": "Santos", "created_at": "2024-12-15"},
    {"customer_id": 8, "full_name": "Heitor Nunes", "email": "heitor.nunes@example.test", "city": "Campinas", "created_at": "2024-12-20"},
    {"customer_id": 9, "full_name": "Iris Prado", "email": "iris.prado@example.test", "city": "São Paulo", "created_at": "2025-01-02"},
    {"customer_id": 10, "full_name": "João Pires", "email": "joao.pires@example.test", "city": "Santos", "created_at": "2025-01-05"},
]
# order_id, customer, store, date, channel, status
ORDERS = [
    {"order_id": 1001, "customer_id": 1, "store_id": 1, "ordered_at": "2025-01-03T14:20:00Z", "channel": "loja", "status": "completed"},
    {"order_id": 1002, "customer_id": 2, "store_id": 3, "ordered_at": "2025-01-04T18:10:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1003, "customer_id": 3, "store_id": 2, "ordered_at": "2025-01-10T13:15:00Z", "channel": "loja", "status": "completed"},
    {"order_id": 1004, "customer_id": 1, "store_id": 3, "ordered_at": "2025-01-25T20:05:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1005, "customer_id": 4, "store_id": 3, "ordered_at": "2025-02-02T16:30:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1006, "customer_id": 5, "store_id": 1, "ordered_at": "2025-02-05T11:45:00Z", "channel": "loja", "status": "completed"},
    {"order_id": 1007, "customer_id": 6, "store_id": 3, "ordered_at": "2025-02-11T19:00:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1008, "customer_id": 2, "store_id": 2, "ordered_at": "2025-02-15T15:00:00Z", "channel": "loja", "status": "completed"},
    {"order_id": 1009, "customer_id": 7, "store_id": 3, "ordered_at": "2025-02-28T21:10:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1010, "customer_id": 1, "store_id": 1, "ordered_at": "2025-03-01T10:20:00Z", "channel": "loja", "status": "completed"},
    {"order_id": 1011, "customer_id": 3, "store_id": 3, "ordered_at": "2025-03-05T17:40:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1012, "customer_id": 8, "store_id": 3, "ordered_at": "2025-03-08T12:00:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1013, "customer_id": 4, "store_id": 2, "ordered_at": "2025-03-10T09:30:00Z", "channel": "loja", "status": "completed"},
    {"order_id": 1014, "customer_id": 5, "store_id": 3, "ordered_at": "2025-03-12T13:20:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1015, "customer_id": 6, "store_id": 1, "ordered_at": "2025-03-18T18:15:00Z", "channel": "loja", "status": "completed"},
    {"order_id": 1016, "customer_id": 9, "store_id": 3, "ordered_at": "2025-03-20T20:00:00Z", "channel": "ecommerce", "status": "cancelled"},
    {"order_id": 1017, "customer_id": 10, "store_id": 3, "ordered_at": "2025-03-24T16:10:00Z", "channel": "ecommerce", "status": "completed"},
    {"order_id": 1018, "customer_id": 1, "store_id": 3, "ordered_at": "2025-03-30T22:30:00Z", "channel": "ecommerce", "status": "completed"},
]
# Uma linha por order_id, product_id, quantity, discount e returned_quantity.
ITEMS = [
    {"order_item_id": 5001, "order_id": 1001, "product_id": 1, "quantity": 1, "unit_price": 899.99, "discount_amount": 50.00, "returned_quantity": 0},
    {"order_item_id": 5002, "order_id": 1001, "product_id": 2, "quantity": 1, "unit_price": 79.90, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5003, "order_id": 1002, "product_id": 4, "quantity": 2, "unit_price": 22.50, "discount_amount": 2.00, "returned_quantity": 0},
    {"order_item_id": 5004, "order_id": 1003, "product_id": 6, "quantity": 1, "unit_price": 159.00, "discount_amount": 10.00, "returned_quantity": 0},
    {"order_item_id": 5005, "order_id": 1004, "product_id": 4, "quantity": 1, "unit_price": 22.50, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5006, "order_id": 1005, "product_id": 3, "quantity": 1, "unit_price": 129.00, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5007, "order_id": 1005, "product_id": 4, "quantity": 3, "unit_price": 22.50, "discount_amount": 3.00, "returned_quantity": 0},
    {"order_item_id": 5008, "order_id": 1006, "product_id": 6, "quantity": 1, "unit_price": 159.00, "discount_amount": 10.00, "returned_quantity": 0},
    {"order_item_id": 5009, "order_id": 1007, "product_id": 2, "quantity": 2, "unit_price": 79.90, "discount_amount": 10.00, "returned_quantity": 0},
    {"order_item_id": 5010, "order_id": 1008, "product_id": 6, "quantity": 1, "unit_price": 159.00, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5011, "order_id": 1008, "product_id": 5, "quantity": 1, "unit_price": 45.00, "discount_amount": 5.00, "returned_quantity": 0},
    {"order_item_id": 5012, "order_id": 1009, "product_id": 1, "quantity": 1, "unit_price": 899.99, "discount_amount": 80.00, "returned_quantity": 0},
    {"order_item_id": 5013, "order_id": 1010, "product_id": 2, "quantity": 1, "unit_price": 79.90, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5014, "order_id": 1011, "product_id": 5, "quantity": 2, "unit_price": 45.00, "discount_amount": 0.00, "returned_quantity": 1},
    {"order_item_id": 5015, "order_id": 1012, "product_id": 3, "quantity": 1, "unit_price": 129.00, "discount_amount": 9.00, "returned_quantity": 0},
    {"order_item_id": 5016, "order_id": 1013, "product_id": 6, "quantity": 1, "unit_price": 159.00, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5017, "order_id": 1014, "product_id": 4, "quantity": 4, "unit_price": 22.50, "discount_amount": 5.00, "returned_quantity": 0},
    {"order_item_id": 5018, "order_id": 1015, "product_id": 6, "quantity": 1, "unit_price": 159.00, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5019, "order_id": 1016, "product_id": 3, "quantity": 1, "unit_price": 129.00, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5020, "order_id": 1017, "product_id": 1, "quantity": 1, "unit_price": 899.99, "discount_amount": 40.00, "returned_quantity": 0},
    {"order_item_id": 5021, "order_id": 1017, "product_id": 2, "quantity": 1, "unit_price": 79.90, "discount_amount": 0.00, "returned_quantity": 0},
    {"order_item_id": 5022, "order_id": 1018, "product_id": 6, "quantity": 1, "unit_price": 159.00, "discount_amount": 0.00, "returned_quantity": 0},
]

EVENT_SEQUENCES = [
    ("sess-ana-01", 1, ["page_view", "search", "add_to_cart", "checkout_start", "purchase"], 1018),
    ("sess-bruno-01", 2, ["page_view", "search", "add_to_cart", "purchase"], 1002),
    ("sess-carla-01", 3, ["page_view", "search", "add_to_cart", "checkout_start"], None),
    ("sess-diego-01", 4, ["page_view", "search"], None),
    ("sess-elisa-01", 5, ["page_view", "add_to_cart", "checkout_start", "purchase"], 1014),
    ("sess-fabio-01", 6, ["page_view", "search", "add_to_cart"], None),
    ("sess-gabi-01", 7, ["page_view", "search", "add_to_cart", "checkout_start", "purchase"], 1009),
    ("sess-anon-01", None, ["page_view", "search"], None),
]

def build_events() -> list[dict]:
    events = []
    base = datetime(2025, 3, 25, 14, 0, tzinfo=timezone.utc)
    for si, (session, customer, sequence, order_id) in enumerate(EVENT_SEQUENCES):
        for ei, kind in enumerate(sequence):
            props: dict = {}
            if kind == "page_view": props = {"page": "/produtos"}
            elif kind == "search": props = {"search_term": "cafe" if si % 2 else "fone"}
            elif kind == "add_to_cart": props = {"product_id": [1, 2, 3, 4, 5, 6][si % 6], "cart_item_count": 1}
            elif kind == "checkout_start": props = {"cart_item_count": 1}
            elif kind == "purchase": props = {"order_id": order_id, "value": 100.0 + si}
            events.append({
                "event_id": f"evt-{si+1:02d}-{ei+1:02d}",
                "customer_id": customer,
                "session_id": session,
                "occurred_at": (base + timedelta(days=si, minutes=ei * 3)).isoformat().replace("+00:00", "Z"),
                "channel": "ecommerce", "event_type": kind, "properties": props,
                "source": "synthetic_fixture"
            })
    return events

def write_sources(root: Path = ROOT) -> None:
    base = root / "data" / "source"
    base.mkdir(parents=True, exist_ok=True)
    order_totals: dict[int, float] = {}
    for item in ITEMS:
        order_totals[item["order_id"]] = order_totals.get(item["order_id"], 0.0) + item["quantity"] * item["unit_price"] - item["discount_amount"]
    orders_with_totals = [{**order, "order_total": round(order_totals[order["order_id"]], 2)} for order in ORDERS]
    tables = {"categories": CATEGORIES, "products": PRODUCTS, "stores": STORES,
              "customers": CUSTOMERS, "orders": orders_with_totals, "order_items": ITEMS}
    for name, rows in tables.items():
        with (base / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    payments = []
    item_totals = {}
    for item in ITEMS:
        item_totals[item["order_id"]] = item_totals.get(item["order_id"], 0.0) + item["quantity"] * item["unit_price"] - item["discount_amount"]
    for order in ORDERS:
        paid = order["status"] == "completed"
        payments.append({"payment_id": order["order_id"] + 8000, "order_id": order["order_id"],
                         "payment_method": "card" if order["order_id"] % 2 else "pix",
                         "amount": round(item_totals[order["order_id"]], 2),
                         "payment_status": "captured" if paid else "void",
                         "paid_at": order["ordered_at"] if paid else ""})
    with (base / "payments.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(payments[0])); w.writeheader(); w.writerows(payments)
    inventory = []
    mid = 9001
    for store in STORES[:2]:
        for product in PRODUCTS:
            inventory.append({"movement_id": mid, "store_id": store["store_id"], "product_id": product["product_id"],
                              "moved_at": "2025-01-01T08:00:00Z", "movement_type": "opening", "quantity_delta": 4 if product["product_id"] != 6 else 2})
            mid += 1
    # Movimentos demonstrativos: uma loja fica sem o produto 4, outra tem estoque residual.
    inventory.extend([
        {"movement_id": mid, "store_id": 1, "product_id": 4, "moved_at": "2025-03-12T10:00:00Z", "movement_type": "sale", "quantity_delta": -4},
        {"movement_id": mid + 1, "store_id": 2, "product_id": 6, "moved_at": "2025-03-18T12:00:00Z", "movement_type": "adjustment", "quantity_delta": -1},
    ])
    with (base / "inventory_movements.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(inventory[0])); w.writeheader(); w.writerows(inventory)
    with (base / "events.json").open("w", encoding="utf-8") as f:
        json.dump(build_events(), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--root", type=Path, default=ROOT)
    write_sources(p.parse_args().root)
    print(f"Fixtures determinísticas gravadas em {p.parse_args().root / 'data/source'}")
