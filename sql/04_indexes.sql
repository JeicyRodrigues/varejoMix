-- Índices orientados às consultas declaradas em 03_analytical_queries.sql.
CREATE INDEX IF NOT EXISTS idx_orders_ordered_at ON orders (ordered_at);
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders (customer_id, ordered_at);
CREATE INDEX IF NOT EXISTS idx_orders_channel_date ON orders (channel, ordered_at);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_store_product_time ON inventory_movements (store_id, product_id, moved_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments (payment_status);
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_channel ON dw.fact_sales (date_key, channel_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_date ON dw.fact_sales (customer_key, date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product_date ON dw.fact_sales (product_key, date_key);
-- UNIQUE constraints already create B-tree indexes for order_id, order_item_id, SKU and event identifiers.
ANALYZE orders;
ANALYZE order_items;
ANALYZE inventory_movements;
ANALYZE dw.fact_sales;
ANALYZE dw.fact_session_events;
