# Modelagem de eventos no MongoDB

## Decisão

Cada evento comportamental é um documento independente na coleção `behavior_events`. O documento registra `event_id`, cliente opcional, sessão, timestamp UTC, canal, tipo e um objeto pequeno `properties`. A estrutura variável é adequada porque um `search` tem `search_term`, enquanto um `purchase` pode ter `order_id` e `value`.

Embuto somente propriedades pequenas e lidas com o evento. Não embuto cliente, catálogo, pedido ou histórico de sessão: são entidades compartilhadas ou com crescimento independente e já pertencem às fontes relacionais/event stream. `customer_id` e `order_id` são referências lógicas escalares. O serviço consumidor pode enriquecer esses identificadores por consulta, aceitando consistência eventual entre os eventos e o OLTP.

## Acesso, cardinalidade e consistência

A cardinalidade é muitos eventos para uma sessão e muitos eventos para um cliente; clientes podem ser anônimos e eventos existem mesmo quando não há `customer_id`. O padrão de leitura esperado é funil por intervalo temporal, sessão e tipo de evento, além de timeline por cliente. Atualizações são raras; os eventos são tratados como append-only. `event_id` é idempotente e único. O timestamp é ISO-8601 com fuso, normalizado para UTC no pipeline.

O tamanho esperado é pequeno: identificadores curtos e propriedades escalares; não se guardam arrays de carrinho crescente nem conteúdo de produto. Isso reduz duplicação e evita documentos grandes. A associação a pedido/cliente é lógica e pode ser tardia; a validação rejeita formatos inválidos, mas não finge consistência transacional distribuída entre PostgreSQL e MongoDB.

## Índices propostos e implementados pelo script Mongo

- `event_id` único: evita duplicação em reprocessamento.
- `(session_id, occurred_at)`: sequência de eventos por sessão.
- `(event_type, occurred_at)`: contagem de estágios do funil por janela.
- `(customer_id, occurred_at)`: jornada identificada por cliente.

O arquivo `event_schema.json` descreve o contrato JSON Schema; `python/seed_mongo.py` cria a collection com validação e índices, e importa os mesmos eventos determinísticos usados em modo offline.
