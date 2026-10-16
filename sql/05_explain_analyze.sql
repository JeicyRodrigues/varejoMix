-- Execute depois de 04_indexes.sql e ANALYZE para obter plano e tempos reais locais.
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT)
SELECT f.order_id, f.order_item_id, f.net_amount
FROM dw.fact_sales f
JOIN dw.dim_date d USING (date_key)
JOIN dw.dim_channel c USING (channel_key)
WHERE d.calendar_date >= DATE '2025-03-01'
  AND d.calendar_date < DATE '2025-04-01'
  AND c.channel_name = 'ecommerce'
ORDER BY f.net_amount DESC;
