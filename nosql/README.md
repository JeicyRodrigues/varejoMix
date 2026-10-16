# Eventos sintéticos

`sample_events.json` é uma amostra válida dos eventos gerados por `python/synthetic_data.py`. Cada item corresponde a um único evento append-only. O schema está em `event_schema.json`; o carregador idempotente e os índices MongoDB estão em `python/seed_mongo.py`. Os identificadores de pedido e cliente são referências escalares às fontes relacionais, não cópias dos documentos dessas entidades.
