# VarejoMix — Arquitetura de Dados Híbrida para Varejo Omnichannel

Projeto acadêmico reproduzível que integra transações, eventos comportamentais e análises do varejista fictício VarejoMix. As fixtures são sintéticas e determinísticas; os números não representam uma operação comercial.

## Arquitetura

PostgreSQL modela o OLTP normalizado e o esquema estrela. MongoDB armazena eventos JSON. Python extrai e valida as fontes e implementa Bronze, Silver e Gold. Parquet organiza os datasets; uma tabela Gold é escrita como Delta Lake via `deltalake` (delta-rs), com histórico/time travel realmente exercitado. DuckDB consulta o Gold Parquet sem servidor analítico.

A [arquitetura detalhada](docs/arquitetura.md) e o [diagrama dimensional](docs/modelo_dimensional.mmd) descrevem granularidades e escolhas. A [imagem da arquitetura](docs/arquitetura.png) e o [diagrama estrela PNG](docs/modelo_dimensional.png) são derivados dos arquivos-fonte Mermaid.

**Estado honesto dos componentes:** o pipeline local, Parquet, Delta, DuckDB, notebook em modo PostgreSQL, scripts SQL e consultas foram executados neste ambiente. PostgreSQL 16 foi inicializado localmente e está comprovado nos artefatos de evidência. A sandbox não dispõe de Docker/Compose; assim, o serviço MongoDB do Compose não foi iniciado nem há evidência de conexão live a MongoDB nesta execução. A integração Mongo existe em `seed_mongo.py` e no modo `--source services`, mas precisa de um Mongo ativo para execução. Modo `fixtures` é o caminho offline, e é explicitamente identificado como sintético.

## Tecnologias e pré-requisitos

Python 3.12 ou compatível com as dependências, Git, Docker Engine com plugin Docker Compose (para os serviços opcionais) e PostgreSQL/MongoDB locais ou pelo Compose. O pipeline offline não exige servidor. O diretório `.venv/` é local e não precisa ser versionado.

```bash
git clone <caminho-ou-url-do-repositorio>
cd VarejoMix
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

O `.env.example` contém apenas valores para demonstração local. Ajuste `POSTGRES_PASSWORD` se desejar, mantendo coerentes `DATABASE_URL` e `POSTGRES_*`. Nunca use os valores de demonstração numa instalação exposta. A senha do arquivo de exemplo não é uma credencial de serviço real.

## Iniciar e carregar os serviços locais

Com Docker Compose instalado:

```bash
docker compose up -d --wait
set -a && source .env && set +a
```

Carregue o OLTP, as dimensões/fato, o espelho analítico de eventos e os índices nesta ordem. As cargas de seed são idempotentes e podem ser reexecutadas. O Compose publica as portas somente em `127.0.0.1`.

```bash
for f in sql/01_schema.sql sql/02_seed_data.sql sql/06_dimensional_model.sql \
         sql/07_behavioral_event_mirror.sql sql/04_indexes.sql sql/03_analytical_queries.sql; do
  docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$f"
done
python python/seed_mongo.py
```

O SQL 07 é uma carga estática derivada das mesmas fixtures para permitir consultas SQL do funil no espelho analítico. Em produção, substitua-a pela extração incremental Mongo → camada analítica. O projeto não afirma transação distribuída entre PostgreSQL e MongoDB. As consultas SQL analíticas incluem receita/margem, ranking de produtos, ruptura, funil por sessão, coortes, recorrência, canal/loja/período e a view mensal. `sql/05_explain_analyze.sql` executa o plano avaliado.

## Fontes sintéticas e pipeline

As fixtures vêm de `python/synthetic_data.py`; `python/generate_seed_sql.py` materializa os CSV/JSON e os dois scripts de seed SQL a partir do catálogo sintético comum:

```bash
python python/synthetic_data.py
python python/generate_seed_sql.py
cp data/source/events.json nosql/sample_events.json
python -m lakehouse.pipeline --source fixtures
python python/build_features.py --as-of 2025-04-01
```

`--source fixtures` é offline e reprodutível. Para extrair de PostgreSQL e MongoDB já carregados, configure `DATABASE_URL`, `MONGO_URI`, `MONGO_DATABASE` e `MONGO_COLLECTION` no ambiente e rode `python -m lakehouse.pipeline --source services`. O modo de serviços grava origem e `run_id` nos registros Silver/Gold. Uma segunda execução de conteúdo idêntico sobrescreve o snapshot Gold pela chave completa (uma linha por `order_item_id`) e não acrescenta duplicatas; o commit Delta mais recente ainda avança para preservar histórico.

Estrutura: Bronze mantém snapshot bruto por hash de entrada; Silver deduplica por chave natural, normaliza datas UTC, verifica referências/totais e separa rejeições em `data/silver/rejects.json`; Gold publica a fato dimensional, dimensões, agregado DuckDB e tabela Delta `data/gold/fact_sales_delta/`. A fato Gold tem uma linha por item de pedido concluído. Delta Lake não é sinônimo de Parquet: o log `_delta_log/` e seus dados permitem ler a versão 0 após a reexecução da versão 1. Não remova logs/arquivos se precisar do time travel.

## SQL analítico

Para executar/reexecutar consultas em PostgreSQL já carregado:

```bash
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/04_indexes.sql
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/03_analytical_queries.sql
docker compose exec -T postgres sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < sql/05_explain_analyze.sql
```

A métrica de receita bruta é quantidade original × preço histórico. Receita líquida = bruta − desconto − parcela líquida devolvida. Cancelados são excluídos. Margem é estimada como líquida − custo do produto para unidades não devolvidas; não inclui impostos, frete, taxas ou custos operacionais. Ruptura é saldo acumulado de movimentos menor ou igual a zero. Funil usa sessões distintas: base de sessões com `page_view`, janela 25/03 a 01/04/2025 em UTC, limite superior exclusivo em 02/04.

## Notebook e dataset de Ciência de Dados

```bash
jupyter lab python/analise_varejomix.ipynb
```

Com `DATABASE_URL` apontando para o banco, o notebook usa SQLAlchemy e `pandas.read_sql` no esquema `dw`. Sem URL, consulta o fato Parquet por `pandas.read_sql` numa base SQLite em memória, para demonstração sem servidor. O notebook lê os eventos sintéticos JSON. O dataset `data/gold/customer_features.parquet` tem 10 clientes e 12 features: última compra, recência, frequência, monetário total, ticket médio, itens, canal predominante, dias desde primeira compra, eventos, sessões e data de referência. Cinco campos de compra são nulos para o cliente sintético sem compra. O corte temporal é `2025-04-01`; observações na data de corte ou depois são excluídas. Não há rótulo, modelo treinado ou validação preditiva.

A regra e os tipos por coluna estão em [docs/dicionario_dados.md](docs/dicionario_dados.md). O arquivo gerado pode ser reproduzido com `python python/build_features.py --as-of 2025-04-01`.

## Testes e evidências reais

```bash
pytest -q
```

A suíte executada neste repositório concluiu **17 testes aprovados**. Os testes de constraint usam SQLite em memória para comportamento relacional rápido; os scripts DDL/carga/consultas foram adicionalmente executados contra PostgreSQL 16 real. O pipeline, Delta Lake/delta-rs e DuckDB foram executados em arquivos locais. Resultados e limites estão em `evidencias/STATUS_EXECUCAO.md`, `evidencias/resultados_testes.txt`, `evidencias/consultas_exemplo.txt`, `evidencias/explain_analyze.txt`, `evidencias/execucao_pipeline_2.json` e `evidencias/execucao_features.json`.

Resultado do conjunto sintético observado: 10 clientes, 18 pedidos, 22 itens brutos, 21 linhas de venda elegíveis e 29 eventos; receita bruta R$ 4.671,47; receita líquida R$ 4.402,47; margem estimada R$ 1.482,47; 0 rejeições no snapshot válido. Reprocessar a tabela Delta produziu a versão 1 e permitiu ler a versão anterior 0 com os mesmos 21 registros. `EXPLAIN ANALYZE` foi registrado sobre 21 linhas; o plano escolheu sequential scan e reportou 0,268 ms no ambiente observado. Esse tempo, nessa amostra pequena, não demonstra performance de produção; os índices são justificáveis pelo padrão de consulta em volumes maiores, não por um benchmark alegado.

## Documentos e limitações

O [caso de mercado](docs/caso_mercado.md) usa a publicação técnica da própria Uber e distingue fatos divulgados, decisões propostas e resultados locais. [Fontes primárias](docs/caso_mercado.md#referências-primárias) incluem documentação oficial do PostgreSQL, MongoDB, Delta Lake, Apache Parquet, pandas, SQLAlchemy e Kimball Group. O relatório técnico (PDF, 7 páginas) está em `relatorio/relatorio_tecnico.pdf`, com fonte Typst em `relatorio/main.typ`. Os limites principais são o volume sintético reduzido, o serviço Mongo não executado nesta sandbox, o modelo de custo simplificado e a ausência de treinamento/avaliação de ML.

**Link do vídeo pitch:** pendente; o vídeo ainda não foi publicado. O roteiro de 90 segundos está em [docs/roteiro_pitch.md](docs/roteiro_pitch.md).
