-- 1. Receita bruta, líquida e margem estimada. A fato já exclui pedidos cancelados.
-- Bruta = quantidade original * preço; líquida = bruta - desconto - devolução líquida.
-- Margem estimada = líquida - custo * unidades não devolvidas (sem frete/impostos).
SELECT SUM(gross_amount) AS gross_revenue,
       SUM(net_amount) AS net_revenue,
       SUM(margin_amount) AS estimated_margin
FROM dw.fact_sales;

-- 2. Produtos por volume efetivamente retido (devoluções não contam como unidades vendidas).
SELECT p.product_id, p.product_name,
       SUM(f.quantity - f.returned_quantity) AS units_sold,
       SUM(f.net_amount) AS net_revenue
FROM dw.fact_sales f JOIN dw.dim_product p USING (product_key)
GROUP BY p.product_id, p.product_name
ORDER BY units_sold DESC, p.product_id;

-- 3. Ruptura operacional: saldo acumulado <= 0 no último movimento por produto/loja.
WITH inventory_balance AS (
  SELECT store_id, product_id, SUM(quantity_delta) AS available_quantity
  FROM inventory_movements GROUP BY store_id, product_id
)
SELECT s.store_name, p.product_name, ls.available_quantity
FROM inventory_balance ls
JOIN stores s USING (store_id) JOIN products p USING (product_id)
WHERE ls.available_quantity <= 0
ORDER BY s.store_name, p.product_name;

-- 4. Funil por sessões distintas na janela inclusiva 2025-03-25..2025-04-01.
-- Base: sessões com page_view; estágio: sessões com >=1 evento daquele tipo.
WITH session_stage AS (
  SELECT session_id,
         BOOL_OR(event_type = 'page_view') AS viewed,
         BOOL_OR(event_type = 'search') AS searched,
         BOOL_OR(event_type = 'add_to_cart') AS added_to_cart,
         BOOL_OR(event_type = 'checkout_start') AS checkout_started,
         BOOL_OR(event_type = 'purchase') AS purchased
  FROM dw.fact_session_events
  WHERE occurred_at >= TIMESTAMPTZ '2025-03-25 00:00:00+00'
    AND occurred_at < TIMESTAMPTZ '2025-04-02 00:00:00+00'
  GROUP BY session_id
)
SELECT COUNT(*) FILTER (WHERE viewed) AS page_view_sessions,
       COUNT(*) FILTER (WHERE searched) AS search_sessions,
       COUNT(*) FILTER (WHERE added_to_cart) AS add_to_cart_sessions,
       COUNT(*) FILTER (WHERE checkout_started) AS checkout_sessions,
       COUNT(*) FILTER (WHERE purchased) AS purchase_sessions,
       ROUND(COUNT(*) FILTER (WHERE purchased)::NUMERIC / NULLIF(COUNT(*) FILTER (WHERE viewed),0), 4) AS session_conversion
FROM session_stage;

-- 5. Coorte pelo mês da primeira compra e meses decorridos até cada compra.
WITH first_order AS (
  SELECT customer_key, MIN(date_key) AS cohort_date_key
  FROM dw.fact_sales GROUP BY customer_key
), cohort_activity AS (
  SELECT f.customer_key, d.year_month,
         c.year_month AS cohort_month,
         (d.calendar_year - c.calendar_year) * 12 + (d.calendar_month - c.calendar_month) AS month_number
  FROM dw.fact_sales f
  JOIN dw.dim_date d USING (date_key)
  JOIN first_order fo USING (customer_key)
  JOIN dw.dim_date c ON c.date_key = fo.cohort_date_key
)
SELECT cohort_month, month_number, COUNT(DISTINCT customer_key) AS active_customers
FROM cohort_activity GROUP BY cohort_month, month_number ORDER BY cohort_month, month_number;

-- 6. Recorrência e intervalo em dias entre compras concluídas.
WITH order_dates AS (
  SELECT DISTINCT customer_key, order_id, date_key FROM dw.fact_sales
), ordered AS (
  SELECT customer_key, order_id, date_key,
         LAG(date_key) OVER (PARTITION BY customer_key ORDER BY date_key, order_id) AS previous_date_key,
         ROW_NUMBER() OVER (PARTITION BY customer_key ORDER BY date_key, order_id) AS purchase_number
  FROM order_dates
)
SELECT customer_key, COUNT(*) AS completed_orders,
       AVG((d.calendar_date - prev.calendar_date)) FILTER (WHERE previous_date_key IS NOT NULL) AS avg_days_between
FROM ordered o JOIN dw.dim_date d ON d.date_key = o.date_key
LEFT JOIN dw.dim_date prev ON prev.date_key = o.previous_date_key
GROUP BY customer_key ORDER BY completed_orders DESC, customer_key;

-- 7. Comparação por mês, canal e loja.
SELECT d.year_month, c.channel_name, s.store_name,
       COUNT(DISTINCT f.order_id) AS orders,
       SUM(f.net_amount) AS net_revenue
FROM dw.fact_sales f JOIN dw.dim_date d USING (date_key)
JOIN dw.dim_channel c USING (channel_key) JOIN dw.dim_store s USING (store_key)
GROUP BY d.year_month, c.channel_name, s.store_name
ORDER BY d.year_month, c.channel_name, s.store_name;

-- View para consumo recorrente por mês/canal.
CREATE OR REPLACE VIEW dw.vw_monthly_channel_sales AS
SELECT d.year_month, c.channel_name, COUNT(DISTINCT f.order_id) AS order_count,
       SUM(f.gross_amount) AS gross_revenue, SUM(f.net_amount) AS net_revenue,
       SUM(f.margin_amount) AS estimated_margin
FROM dw.fact_sales f JOIN dw.dim_date d USING (date_key)
JOIN dw.dim_channel c USING (channel_key)
GROUP BY d.year_month, c.channel_name;
