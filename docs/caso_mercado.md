# Caso público: plataforma de dados da Uber

A Uber documenta publicamente o Apache Hudi como componente central de seu data lake. O texto técnico da própria equipe descreve problemas de dados mutáveis, eventos tardios, backfills e necessidade de processamento incremental; relata que Hudi foi criado para acrescentar transações ACID, indexação/upserts e processamento incremental sobre armazenamento de data lake. A publicação descreve integração com ingestão Spark em lote, pipelines derivados e ingestão em tempo real com Flink [1].

**Fato publicado pela empresa:** o artigo de 2026 informa aproximadamente 19.500 datasets Hudi e cita Parquet em operações bulk-insert, Spark Batch e Flink, entre outros detalhes de sua plataforma. Esses números são afirmações da publicação da Uber sobre sua própria infraestrutura e não foram reproduzidos nem verificados independentemente neste projeto. São contexto do caso, não benchmark comparável.

**Decisão proposta para a VarejoMix:** não replicar a escala ou o stack distribuído da Uber. O projeto usa o princípio transferível de separar ingestão, dados brutos, dados curados e consumo, com chaves idempotentes e histórico de versões; para o volume acadêmico, Python local, Parquet, Delta Lake via delta-rs e DuckDB reduzem a infraestrutura.

**Resultado experimental local:** a evidência de testes, versão Delta e `EXPLAIN ANALYZE` é produzida neste repositório e deve ser lida separadamente do caso público. O caso não prova que PostgreSQL, MongoDB ou Delta sejam usados pela Uber neste fluxo específico.

## Referências primárias

[1] Uber Engineering, “Apache Hudi™ at Uber: Engineering for Trillion-Record-Scale Data Lake Operations”, publicação técnica da equipe Uber, 2026. https://www.uber.com/us/en/blog/apache-hudi-at-uber/

[2] PostgreSQL Global Development Group, “Constraints”, documentação oficial. https://www.postgresql.org/docs/current/ddl-constraints.html

[3] MongoDB, “Data Modeling in MongoDB”, documentação oficial. https://www.mongodb.com/docs/manual/data-modeling/

[4] Delta Lake, “Table batch reads and writes” (time travel, gravação e retenção), documentação oficial. https://docs.delta.io/delta-batch/

[5] Apache Software Foundation, “File Format”, documentação oficial do Apache Parquet. https://parquet.apache.org/docs/file-format/

[6] pandas, “pandas.read_sql”, documentação oficial. https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html

[7] SQLAlchemy, “Engine Configuration”, documentação oficial. https://docs.sqlalchemy.org/en/20/core/engines.html

[8] Ralph Kimball, “Declaring the Grain”, Kimball Group, 1 mar. 2003. https://www.kimballgroup.com/2003/03/declaring-the-grain/

## Precisão e limites das fontes

A referência [1] é a publicação técnica da empresa sobre sua própria implantação (fonte primária para o que ela afirma sobre seus sistemas). As referências [2]–[8] documentam mecanismos, não resultados da VarejoMix. A documentação de constraints alerta que `CHECK` não substitui `NOT NULL`; a documentação de Delta explica que o time travel depende da retenção de logs e arquivos de dados; Kimball define o grão como a descrição de negócio do que uma linha da fato representa. As fontes foram abertas e consultadas em 15 out. 2026. Todas as métricas locais devem vir de arquivos em `evidencias/`.
