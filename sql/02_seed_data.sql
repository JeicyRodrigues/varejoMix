-- Carga idempotente das fixtures geradas por python/synthetic_data.py.
BEGIN;

INSERT INTO categories (category_id, category_name)
VALUES
  (1, 'Eletrônicos'),
  (2, 'Casa e cozinha'),
  (3, 'Livros e acessórios')
ON CONFLICT DO NOTHING;

INSERT INTO customers (customer_id, full_name, email, city, created_at)
VALUES
  (1, 'Ana Lima', 'ana.lima@example.test', 'São Paulo', '2024-11-10'),
  (2, 'Bruno Costa', 'bruno.costa@example.test', 'Campinas', '2024-11-12'),
  (3, 'Carla Souza', 'carla.souza@example.test', 'São Paulo', '2024-11-15'),
  (4, 'Diego Alves', 'diego.alves@example.test', 'Santos', '2024-11-20'),
  (5, 'Elisa Rocha', 'elisa.rocha@example.test', 'Campinas', '2024-12-01'),
  (6, 'Fabio Reis', 'fabio.reis@example.test', 'São Paulo', '2024-12-06'),
  (7, 'Gabi Melo', 'gabi.melo@example.test', 'Santos', '2024-12-15'),
  (8, 'Heitor Nunes', 'heitor.nunes@example.test', 'Campinas', '2024-12-20'),
  (9, 'Iris Prado', 'iris.prado@example.test', 'São Paulo', '2025-01-02'),
  (10, 'João Pires', 'joao.pires@example.test', 'Santos', '2025-01-05')
ON CONFLICT DO NOTHING;

INSERT INTO products (product_id, sku, product_name, category_id, unit_price, unit_cost)
VALUES
  (1, 'VM-1001', 'Notebook Essencial', 1, 899.99, 660.0),
  (2, 'VM-1002', 'Fone Bluetooth', 1, 79.9, 38.0),
  (3, 'VM-2001', 'Cafeteira Compacta', 2, 129.0, 70.0),
  (4, 'VM-2002', 'Café Especial 500g', 2, 22.5, 12.0),
  (5, 'VM-3001', 'Livro Dados no Varejo', 3, 45.0, 20.0),
  (6, 'VM-3002', 'Mochila Urbana', 3, 159.0, 75.0)
ON CONFLICT DO NOTHING;

INSERT INTO stores (store_id, store_name, city, store_type)
VALUES
  (1, 'Centro', 'São Paulo', 'physical'),
  (2, 'Shopping Norte', 'São Paulo', 'physical'),
  (3, 'Loja virtual', 'Online', 'ecommerce')
ON CONFLICT DO NOTHING;

INSERT INTO orders (order_id, customer_id, store_id, ordered_at, channel, status, order_total)
VALUES
  (1001, 1, 1, '2025-01-03T14:20:00Z', 'loja', 'completed', '929.89'),
  (1002, 2, 3, '2025-01-04T18:10:00Z', 'ecommerce', 'completed', '43.00'),
  (1003, 3, 2, '2025-01-10T13:15:00Z', 'loja', 'completed', '149.00'),
  (1004, 1, 3, '2025-01-25T20:05:00Z', 'ecommerce', 'completed', '22.50'),
  (1005, 4, 3, '2025-02-02T16:30:00Z', 'ecommerce', 'completed', '193.50'),
  (1006, 5, 1, '2025-02-05T11:45:00Z', 'loja', 'completed', '149.00'),
  (1007, 6, 3, '2025-02-11T19:00:00Z', 'ecommerce', 'completed', '149.80'),
  (1008, 2, 2, '2025-02-15T15:00:00Z', 'loja', 'completed', '199.00'),
  (1009, 7, 3, '2025-02-28T21:10:00Z', 'ecommerce', 'completed', '819.99'),
  (1010, 1, 1, '2025-03-01T10:20:00Z', 'loja', 'completed', '79.90'),
  (1011, 3, 3, '2025-03-05T17:40:00Z', 'ecommerce', 'completed', '90.00'),
  (1012, 8, 3, '2025-03-08T12:00:00Z', 'ecommerce', 'completed', '120.00'),
  (1013, 4, 2, '2025-03-10T09:30:00Z', 'loja', 'completed', '159.00'),
  (1014, 5, 3, '2025-03-12T13:20:00Z', 'ecommerce', 'completed', '85.00'),
  (1015, 6, 1, '2025-03-18T18:15:00Z', 'loja', 'completed', '159.00'),
  (1016, 9, 3, '2025-03-20T20:00:00Z', 'ecommerce', 'cancelled', '129.00'),
  (1017, 10, 3, '2025-03-24T16:10:00Z', 'ecommerce', 'completed', '939.89'),
  (1018, 1, 3, '2025-03-30T22:30:00Z', 'ecommerce', 'completed', '159.00')
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price, discount_amount, returned_quantity)
VALUES
  (5001, 1001, 1, 1, 899.99, 50.0, 0),
  (5002, 1001, 2, 1, 79.9, 0.0, 0),
  (5003, 1002, 4, 2, 22.5, 2.0, 0),
  (5004, 1003, 6, 1, 159.0, 10.0, 0),
  (5005, 1004, 4, 1, 22.5, 0.0, 0),
  (5006, 1005, 3, 1, 129.0, 0.0, 0),
  (5007, 1005, 4, 3, 22.5, 3.0, 0),
  (5008, 1006, 6, 1, 159.0, 10.0, 0),
  (5009, 1007, 2, 2, 79.9, 10.0, 0),
  (5010, 1008, 6, 1, 159.0, 0.0, 0),
  (5011, 1008, 5, 1, 45.0, 5.0, 0),
  (5012, 1009, 1, 1, 899.99, 80.0, 0),
  (5013, 1010, 2, 1, 79.9, 0.0, 0),
  (5014, 1011, 5, 2, 45.0, 0.0, 1),
  (5015, 1012, 3, 1, 129.0, 9.0, 0),
  (5016, 1013, 6, 1, 159.0, 0.0, 0),
  (5017, 1014, 4, 4, 22.5, 5.0, 0),
  (5018, 1015, 6, 1, 159.0, 0.0, 0),
  (5019, 1016, 3, 1, 129.0, 0.0, 0),
  (5020, 1017, 1, 1, 899.99, 40.0, 0),
  (5021, 1017, 2, 1, 79.9, 0.0, 0),
  (5022, 1018, 6, 1, 159.0, 0.0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO payments (payment_id, order_id, payment_method, amount, payment_status, paid_at)
VALUES
  (9001, 1001, 'card', '929.89', 'captured', '2025-01-03T14:20:00Z'),
  (9002, 1002, 'pix', '43.00', 'captured', '2025-01-04T18:10:00Z'),
  (9003, 1003, 'card', '149.00', 'captured', '2025-01-10T13:15:00Z'),
  (9004, 1004, 'pix', '22.50', 'captured', '2025-01-25T20:05:00Z'),
  (9005, 1005, 'card', '193.50', 'captured', '2025-02-02T16:30:00Z'),
  (9006, 1006, 'pix', '149.00', 'captured', '2025-02-05T11:45:00Z'),
  (9007, 1007, 'card', '149.80', 'captured', '2025-02-11T19:00:00Z'),
  (9008, 1008, 'pix', '199.00', 'captured', '2025-02-15T15:00:00Z'),
  (9009, 1009, 'card', '819.99', 'captured', '2025-02-28T21:10:00Z'),
  (9010, 1010, 'pix', '79.90', 'captured', '2025-03-01T10:20:00Z'),
  (9011, 1011, 'card', '90.00', 'captured', '2025-03-05T17:40:00Z'),
  (9012, 1012, 'pix', '120.00', 'captured', '2025-03-08T12:00:00Z'),
  (9013, 1013, 'card', '159.00', 'captured', '2025-03-10T09:30:00Z'),
  (9014, 1014, 'pix', '85.00', 'captured', '2025-03-12T13:20:00Z'),
  (9015, 1015, 'card', '159.00', 'captured', '2025-03-18T18:15:00Z'),
  (9016, 1016, 'pix', '129.00', 'void', NULL),
  (9017, 1017, 'card', '939.89', 'captured', '2025-03-24T16:10:00Z'),
  (9018, 1018, 'pix', '159.00', 'captured', '2025-03-30T22:30:00Z')
ON CONFLICT DO NOTHING;

INSERT INTO inventory_movements (movement_id, store_id, product_id, moved_at, movement_type, quantity_delta)
VALUES
  (9001, 1, 1, '2025-01-01T08:00:00Z', 'opening', 4),
  (9002, 1, 2, '2025-01-01T08:00:00Z', 'opening', 4),
  (9003, 1, 3, '2025-01-01T08:00:00Z', 'opening', 4),
  (9004, 1, 4, '2025-01-01T08:00:00Z', 'opening', 4),
  (9005, 1, 5, '2025-01-01T08:00:00Z', 'opening', 4),
  (9006, 1, 6, '2025-01-01T08:00:00Z', 'opening', 2),
  (9007, 2, 1, '2025-01-01T08:00:00Z', 'opening', 4),
  (9008, 2, 2, '2025-01-01T08:00:00Z', 'opening', 4),
  (9009, 2, 3, '2025-01-01T08:00:00Z', 'opening', 4),
  (9010, 2, 4, '2025-01-01T08:00:00Z', 'opening', 4),
  (9011, 2, 5, '2025-01-01T08:00:00Z', 'opening', 4),
  (9012, 2, 6, '2025-01-01T08:00:00Z', 'opening', 2),
  (9013, 1, 4, '2025-03-12T10:00:00Z', 'sale', -4),
  (9014, 2, 6, '2025-03-18T12:00:00Z', 'adjustment', -1)
ON CONFLICT DO NOTHING;

SELECT setval(pg_get_serial_sequence('categories','category_id'), GREATEST(COALESCE((SELECT MAX(category_id) FROM categories),1),1), true);

SELECT setval(pg_get_serial_sequence('customers','customer_id'), GREATEST(COALESCE((SELECT MAX(customer_id) FROM customers),1),1), true);

SELECT setval(pg_get_serial_sequence('products','product_id'), GREATEST(COALESCE((SELECT MAX(product_id) FROM products),1),1), true);

SELECT setval(pg_get_serial_sequence('stores','store_id'), GREATEST(COALESCE((SELECT MAX(store_id) FROM stores),1),1), true);

SELECT setval(pg_get_serial_sequence('orders','order_id'), GREATEST(COALESCE((SELECT MAX(order_id) FROM orders),1),1), true);

SELECT setval(pg_get_serial_sequence('order_items','order_item_id'), GREATEST(COALESCE((SELECT MAX(order_item_id) FROM order_items),1),1), true);

SELECT setval(pg_get_serial_sequence('payments','payment_id'), GREATEST(COALESCE((SELECT MAX(payment_id) FROM payments),1),1), true);

SELECT setval(pg_get_serial_sequence('inventory_movements','movement_id'), GREATEST(COALESCE((SELECT MAX(movement_id) FROM inventory_movements),1),1), true);

COMMIT;
