-- Espelho analítico derivado das fixtures Mongo. Em produção, extração Python/Mongo substitui este seed.
-- event_id é chave natural; cada reexecução faz upsert sem duplicar eventos.
BEGIN;
CREATE TEMP TABLE event_input(event_id TEXT,customer_id INTEGER,session_id TEXT,occurred_at TEXT,channel TEXT,event_type TEXT,properties TEXT) ON COMMIT DROP;
INSERT INTO event_input VALUES
  ('evt-01-01', 1, 'sess-ana-01', '2025-03-25T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-01-02', 1, 'sess-ana-01', '2025-03-25T14:03:00Z', 'ecommerce', 'search', '{"search_term":"fone"}'),
  ('evt-01-03', 1, 'sess-ana-01', '2025-03-25T14:06:00Z', 'ecommerce', 'add_to_cart', '{"product_id":1,"cart_item_count":1}'),
  ('evt-01-04', 1, 'sess-ana-01', '2025-03-25T14:09:00Z', 'ecommerce', 'checkout_start', '{"cart_item_count":1}'),
  ('evt-01-05', 1, 'sess-ana-01', '2025-03-25T14:12:00Z', 'ecommerce', 'purchase', '{"order_id":1018,"value":100.0}'),
  ('evt-02-01', 2, 'sess-bruno-01', '2025-03-26T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-02-02', 2, 'sess-bruno-01', '2025-03-26T14:03:00Z', 'ecommerce', 'search', '{"search_term":"cafe"}'),
  ('evt-02-03', 2, 'sess-bruno-01', '2025-03-26T14:06:00Z', 'ecommerce', 'add_to_cart', '{"product_id":2,"cart_item_count":1}'),
  ('evt-02-04', 2, 'sess-bruno-01', '2025-03-26T14:09:00Z', 'ecommerce', 'purchase', '{"order_id":1002,"value":101.0}'),
  ('evt-03-01', 3, 'sess-carla-01', '2025-03-27T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-03-02', 3, 'sess-carla-01', '2025-03-27T14:03:00Z', 'ecommerce', 'search', '{"search_term":"fone"}'),
  ('evt-03-03', 3, 'sess-carla-01', '2025-03-27T14:06:00Z', 'ecommerce', 'add_to_cart', '{"product_id":3,"cart_item_count":1}'),
  ('evt-03-04', 3, 'sess-carla-01', '2025-03-27T14:09:00Z', 'ecommerce', 'checkout_start', '{"cart_item_count":1}'),
  ('evt-04-01', 4, 'sess-diego-01', '2025-03-28T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-04-02', 4, 'sess-diego-01', '2025-03-28T14:03:00Z', 'ecommerce', 'search', '{"search_term":"cafe"}'),
  ('evt-05-01', 5, 'sess-elisa-01', '2025-03-29T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-05-02', 5, 'sess-elisa-01', '2025-03-29T14:03:00Z', 'ecommerce', 'add_to_cart', '{"product_id":5,"cart_item_count":1}'),
  ('evt-05-03', 5, 'sess-elisa-01', '2025-03-29T14:06:00Z', 'ecommerce', 'checkout_start', '{"cart_item_count":1}'),
  ('evt-05-04', 5, 'sess-elisa-01', '2025-03-29T14:09:00Z', 'ecommerce', 'purchase', '{"order_id":1014,"value":104.0}'),
  ('evt-06-01', 6, 'sess-fabio-01', '2025-03-30T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-06-02', 6, 'sess-fabio-01', '2025-03-30T14:03:00Z', 'ecommerce', 'search', '{"search_term":"cafe"}'),
  ('evt-06-03', 6, 'sess-fabio-01', '2025-03-30T14:06:00Z', 'ecommerce', 'add_to_cart', '{"product_id":6,"cart_item_count":1}'),
  ('evt-07-01', 7, 'sess-gabi-01', '2025-03-31T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-07-02', 7, 'sess-gabi-01', '2025-03-31T14:03:00Z', 'ecommerce', 'search', '{"search_term":"fone"}'),
  ('evt-07-03', 7, 'sess-gabi-01', '2025-03-31T14:06:00Z', 'ecommerce', 'add_to_cart', '{"product_id":1,"cart_item_count":1}'),
  ('evt-07-04', 7, 'sess-gabi-01', '2025-03-31T14:09:00Z', 'ecommerce', 'checkout_start', '{"cart_item_count":1}'),
  ('evt-07-05', 7, 'sess-gabi-01', '2025-03-31T14:12:00Z', 'ecommerce', 'purchase', '{"order_id":1009,"value":106.0}'),
  ('evt-08-01', NULL, 'sess-anon-01', '2025-04-01T14:00:00Z', 'ecommerce', 'page_view', '{"page":"/produtos"}'),
  ('evt-08-02', NULL, 'sess-anon-01', '2025-04-01T14:03:00Z', 'ecommerce', 'search', '{"search_term":"cafe"}');
INSERT INTO dw.dim_date(date_key,calendar_date,calendar_year,calendar_month,year_month)
SELECT DISTINCT TO_CHAR(occurred_at::timestamptz::date,'YYYYMMDD')::INTEGER, occurred_at::timestamptz::date,
       EXTRACT(YEAR FROM occurred_at::timestamptz)::INTEGER, EXTRACT(MONTH FROM occurred_at::timestamptz)::INTEGER,
       TO_CHAR(occurred_at::timestamptz,'YYYY-MM') FROM event_input
ON CONFLICT(date_key) DO NOTHING;
INSERT INTO dw.fact_session_events(event_id,customer_key,session_id,occurred_at,date_key,channel_key,event_type,properties)
SELECT e.event_id,dc.customer_key,e.session_id,e.occurred_at::timestamptz,
       TO_CHAR(e.occurred_at::timestamptz::date,'YYYYMMDD')::INTEGER,dch.channel_key,e.event_type,e.properties::jsonb
FROM event_input e LEFT JOIN dw.dim_customer dc ON dc.customer_id=e.customer_id
JOIN dw.dim_channel dch ON dch.channel_name=e.channel
ON CONFLICT(event_id) DO UPDATE SET customer_key=EXCLUDED.customer_key,session_id=EXCLUDED.session_id,
  occurred_at=EXCLUDED.occurred_at,date_key=EXCLUDED.date_key,channel_key=EXCLUDED.channel_key,
  event_type=EXCLUDED.event_type,properties=EXCLUDED.properties;
COMMIT;
