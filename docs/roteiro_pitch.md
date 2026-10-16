# Pitch — VarejoMix

**Status do vídeo:** pendente. Não foi criado nem publicado vídeo nesta entrega; portanto, não há URL a divulgar.

## Roteiro sugerido (90 segundos)

1. **Problema (0–15 s):** pedidos, estoque e navegação omnichannel chegam em formatos e ritmos diferentes; relatórios inconsistentes dificultam decisões.
2. **Arquitetura (15–35 s):** PostgreSQL mantém transações e integridade; MongoDB registra eventos flexíveis; Python consolida dados em Bronze, Silver e Gold.
3. **Demonstração (35–60 s):** mostrar uma sessão percorrendo page_view, search, carrinho e checkout; em seguida, uma fato com granularidade item de pedido, receita líquida e uma consulta por canal.
4. **Reprodutibilidade (60–78 s):** reprocessar as entradas, comprovar chaves únicas e consultar uma versão anterior do Delta Lake; apresentar resultados reais dos testes e `EXPLAIN ANALYZE`.
5. **Limites e conclusão (78–90 s):** dados sintéticos, sem modelo preditivo treinado; o dataset de features está preparado para trabalho futuro. Concluir que a proposta privilegia simplicidade, auditabilidade e baixo custo local.

Antes de gravar, atualizar o status e inserir o link somente depois da publicação autorizada.
