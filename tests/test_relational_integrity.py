import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def conn():
    engine=create_engine("sqlite:///:memory:")
    @event.listens_for(engine,"connect")
    def fk_on(dbapi_connection, _): dbapi_connection.execute("PRAGMA foreign_keys=ON")
    with engine.begin() as c:
        c.exec_driver_sql("CREATE TABLE customers(customer_id INTEGER PRIMARY KEY)")
        c.exec_driver_sql("CREATE TABLE categories(category_id INTEGER PRIMARY KEY)")
        c.exec_driver_sql("CREATE TABLE products(product_id INTEGER PRIMARY KEY, category_id INTEGER NOT NULL REFERENCES categories(category_id), price NUMERIC NOT NULL CHECK(price>0))")
        c.exec_driver_sql("CREATE TABLE stores(store_id INTEGER PRIMARY KEY)")
        c.exec_driver_sql("CREATE TABLE orders(order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(customer_id), store_id INTEGER NOT NULL REFERENCES stores(store_id), total NUMERIC NOT NULL CHECK(total>=0))")
        c.exec_driver_sql("CREATE TABLE order_items(item_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(order_id), product_id INTEGER NOT NULL REFERENCES products(product_id), quantity INTEGER NOT NULL CHECK(quantity>0), unit_price NUMERIC NOT NULL CHECK(unit_price>0), discount NUMERIC NOT NULL CHECK(discount>=0 AND discount<=quantity*unit_price), returned INTEGER NOT NULL CHECK(returned BETWEEN 0 AND quantity))")
        c.exec_driver_sql("CREATE TABLE payments(payment_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL UNIQUE REFERENCES orders(order_id), amount NUMERIC NOT NULL CHECK(amount>=0))")
        c.exec_driver_sql("INSERT INTO customers VALUES(1)"); c.exec_driver_sql("INSERT INTO categories VALUES(1)")
        c.exec_driver_sql("INSERT INTO products VALUES(1,1,10)"); c.exec_driver_sql("INSERT INTO stores VALUES(1)")
        c.exec_driver_sql("INSERT INTO orders VALUES(1,1,1,20)")
    try:
        with engine.connect() as c: yield c
    finally: engine.dispose()

def test_impede_pedido_com_cliente_inexistente(conn):
    with pytest.raises(IntegrityError):
        with conn.begin(): conn.execute(text("INSERT INTO orders VALUES(2,999,1,1)"))

def test_impede_item_com_pedido_ou_produto_inexistente(conn):
    with pytest.raises(IntegrityError):
        with conn.begin(): conn.execute(text("INSERT INTO order_items VALUES(1,999,1,1,10,0,0)"))
    with pytest.raises(IntegrityError):
        with conn.begin(): conn.execute(text("INSERT INTO order_items VALUES(1,1,999,1,10,0,0)"))

def test_restringe_quantidade_desconto_e_devolucao(conn):
    invalid=["INSERT INTO order_items VALUES(1,1,1,0,10,0,0)",
             "INSERT INTO order_items VALUES(1,1,1,1,10,11,0)",
             "INSERT INTO order_items VALUES(1,1,1,1,10,0,2)"]
    for statement in invalid:
        with pytest.raises(IntegrityError):
            with conn.begin(): conn.execute(text(statement))

def test_total_do_pedido_reconcilia_com_itens(conn):
    with conn.begin():
        conn.execute(text("INSERT INTO order_items VALUES(1,1,1,2,10,0,0)"))
    total=conn.execute(text("SELECT total FROM orders WHERE order_id=1")).scalar_one()
    line_total=conn.execute(text("SELECT SUM(quantity*unit_price-discount) FROM order_items WHERE order_id=1")).scalar_one()
    assert round(float(total),2)==round(float(line_total),2)==20.00
