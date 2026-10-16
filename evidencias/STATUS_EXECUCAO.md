# Status da execução — verificado em 15 out. 2026

## Validado nesta sandbox

- Python 3.12.3; suíte `pytest -q`: **17 passed** (`resultados_testes.txt`).
- PostgreSQL **16** local inicializado; DDL OLTP, seeds idempotentes, dimensões/fato, espelho de 29 eventos, índices, view e consultas analíticas executados em banco real (`consultas_exemplo.txt`). Reexecutar as cargas preservou 18 pedidos, 22 itens, 21 linhas fato e 29 eventos.
- `EXPLAIN ANALYZE` real após `ANALYZE`, com tempo observado de 0,268 ms em tabela de 21 linhas (`explain_analyze.txt`). O plano usou scans sequenciais, coerentes com a escala pequena; não é benchmark de produção.
- Pipeline local em modo `fixtures`, Bronze/Silver/Gold, Parquet, DuckDB e Delta Lake via `deltalake`/delta-rs. Execução repetida gerou Delta versão 1, leu versão anterior 0 e confirmou as mesmas 21 linhas (`execucao_pipeline_2.json`).
- Dataset Parquet com 10 clientes e 12 features (`execucao_features.json`).
- Notebook executado com conexão SQLAlchemy/pandas `read_sql` contra PostgreSQL local; resultados incorporados no `.ipynb` e copiados para `notebook_execution.txt`.
- Relatório Typst estrito compilado sem warnings; PDF A4 de 7 páginas validado (título, autor, texto, fontes e intervalo 6–10 páginas; `relatorio/pdf_verification.json`).

## Não executado nesta sandbox

- Docker Engine/Compose não está instalado. Os serviços definidos no `docker-compose.yml` não foram inicializados.
- MongoDB **não foi iniciado** e não houve conexão live. `nosql/` e `python/seed_mongo.py` definem schema, índices e upsert; execução Mongo real depende de MongoDB ativo. As fontes sintéticas JSON abasteceram o pipeline e o espelho SQL.

Não afirmar as condições acima como resultados de execução. Para validar a integração Mongo, iniciar os serviços com `docker compose up -d --wait` e executar `python python/seed_mongo.py` conforme o README.
