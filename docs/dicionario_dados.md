# Dicionário de dados

## OLTP PostgreSQL

| Tabela | Granularidade e colunas essenciais | Integridade / regra |
|---|---|---|
| `customers` | Uma linha por cliente: `customer_id`, nome, e-mail, cidade, criação | PK; e-mail UNIQUE/NOT NULL |
| `categories` | Uma linha por categoria | PK e nome UNIQUE |
| `products` | Uma linha por SKU: categoria, preço atual e custo unitário | FK para categoria; SKU UNIQUE; preço > 0; custo entre 0 e preço |
| `stores` | Uma unidade ou canal virtual | PK; tipo física/e-commerce |
| `orders` | Um cabeçalho por pedido: cliente, loja, canal, status, data e total declarado | FK cliente/loja; valores/status/canal restritos |
| `order_items` | Uma linha por produto em pedido: quantidade, preço histórico, desconto, devolução | FKs para pedido/produto; quantidade positiva; devolvida ≤ comprada; desconto ≤ valor bruto |
| `payments` | Um pagamento por pedido no conjunto demonstrativo | FK/UNIQUE pedido; valor ≥ 0; estado captured/void |
| `inventory_movements` | Um movimento assinado por produto/loja | FKs e quantidade não zero; saldo operacional = soma de movimentos |

`order_total` é armazenado no cabeçalho para refletir o valor declarado e a carga; a reconciliação entre cabeçalho e itens é uma regra interlinhas validada no pipeline/testes, porque `CHECK` por linha não impõe agregação entre tabelas. `unit_price` do item é um snapshot histórico; o preço de catálogo pode mudar.

## MongoDB `behavior_events`

Um documento por evento. Os campos obrigatórios são `event_id`, `session_id`, `occurred_at`, `channel`, `event_type` e `properties`; `customer_id` é opcional para sessão anônima. `properties` varia por tipo e mantém apenas atributos pequenos, com `product_id`/`order_id` como referências lógicas. A coleção usa unicidade por `event_id` e índices de sessão-tempo, tipo-tempo e cliente-tempo. `nosql/event_schema.json` é o contrato JSON; `python/seed_mongo.py` valida e cria índices/validador quando conectado.

## Lakehouse Silver/Gold

| Campo da fato Gold | Tipo Parquet (lógico) | Origem e regra |
|---|---|---|
| `order_id`, `order_item_id` | int64 | Chaves operacionais; item é chave natural única da fato |
| `customer_id`, `product_id`, `store_id` | int64 | FKs/naturais das dimensões |
| `product_name`, `category_name`, `store_name`, `channel` | string | Atributos descritivos da fonte no processamento |
| `order_date`, `order_month` | string ISO (`YYYY-MM-DD`, `YYYY-MM`) | Data UTC do pedido; partição mensal na cópia Hive-style |
| `quantity`, `returned_quantity` | int64 | Quantidade pedida e devolvida |
| `gross_amount` | float64 | `quantity × unit_price` histórico |
| `discount_amount` | float64 | Desconto do item na fonte |
| `return_amount` | float64 | `returned_quantity × (unit_price − discount/quantity)`, arredondado a centavos |
| `net_amount` | float64 | Bruta − desconto − devolução |
| `estimated_cost` | float64 | `(quantity − returned_quantity) × unit_cost` atual da fixture |
| `margin_amount` | float64 | Receita líquida − custo estimado, sem despesas operacionais/impostos |
| `_source`, `_run_id`, `_processed_at_utc` | string | Proveniência, hash de conteúdo e instante UTC de processamento |

Em PostgreSQL os valores monetários usam `NUMERIC`; na saída Parquet o cálculo é arredondado a centavos em `float64` para interoperabilidade do dataset pequeno. Em produção financeira seria melhor preservar decimal/inteiro em centavos e declarar a política de arredondamento.

## Dataset `customer_features.parquet`

| Coluna | Tipo | Regra no corte 2025-04-01 |
|---|---|---|
| `customer_id` | int64 | ID natural de `customers`, único por linha |
| `reference_date` | string ISO | Data de corte, exclusiva para observações após seu início |
| `last_purchase_date` | string ISO / nulo | Maior data de pedido concluído antes do corte |
| `recency_days` | int64 / nulo | Dias entre corte e última compra |
| `purchase_frequency` | int64 | Número de pedidos concluídos observados |
| `monetary_total` | float64 | Soma de receita líquida; zero para cliente sem compra |
| `average_ticket` | float64 / nulo | Total monetário ÷ pedidos, agregando primeiro por pedido |
| `total_items` | int64 | Itens retidos após devoluções |
| `predominant_channel` | string / nulo | Canal de maior contagem de pedidos; empate resolvido alfabeticamente |
| `days_since_first_purchase` | int64 / nulo | Dias entre corte e primeira compra |
| `event_count` | int64 | Eventos associados ao cliente antes do corte |
| `session_count` | int64 | Sessões distintas do cliente antes do corte |

**Execução observada:** 10 linhas e 12 colunas, ID de cliente sem duplicatas. Foram 0 nulos nas colunas ID, data de referência, frequência, total monetário, itens, eventos e sessões. Cinco medidas/atributos de clientes sem compra podem ser nulos: data da última compra, recência, ticket médio, canal predominante e dias desde primeira compra. Na fixture atual o cliente 9 nunca concluiu uma compra; cada uma dessas cinco colunas tem 1 nulo. Não há alvo de recompra, divisão temporal de treino/teste nem modelo treinado.
