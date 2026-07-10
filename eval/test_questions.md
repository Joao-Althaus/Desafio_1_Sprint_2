# Conjunto de Teste — Avaliação do Assistente RAG Clínico

Perguntas escolhidas para cobrir cenários variados: pergunta direta sobre bula, pergunta sobre diretriz (PCDT Hipertensão), pergunta que exige distinguir estudos clínicos diferentes (LIFE, RENAAL, ELITE, OPTIMAAL), pergunta fora do escopo (deve responder "não encontrado"), e pergunta ambígua/genérica.

> Perguntas ajustadas para o acervo real: `losartana_bula_profissional.pdf` e `Hipertensão Arterial Sistêmica_Protocolo.pdf` (PCDT).

| # | Pergunta | Tipo | O que está testando |
|---|---|---|---|
| 1 | Qual a dose recomendada de Losartana para pacientes adultos com hipertensão? | Direta / bula | Recuperação simples de fato objetivo |
| 2 | Quais são as contraindicações da Losartana? | Direta / bula | Recuperação de lista/seção específica |
| 3 | Segundo o PCDT de Hipertensão Arterial, qual a primeira linha de tratamento farmacológico? | Direta / diretriz | Recuperação em documento de diretriz (não bula) |
| 4 | O que o Estudo LIFE concluiu sobre desfechos cardiovasculares com o uso de Losartana? | Filtro de estudo | Testa o filtro de estudo clínico (`estudo_alvo`) — checar se não mistura com RENAAL/ELITE |
| 5 | Compare os resultados do Estudo RENAAL com o Estudo ELITE mencionados na bula da Losartana. | Filtro de estudo (múltiplo) | Pergunta menciona 2 estudos — hoje o código só filtra pelo primeiro encontrado na lista; ver como o sistema se comporta |
| 6 | Qual a dosagem pediátrica recomendada de Sacubitril/Valsartana? | Fora do escopo | Fármaco que não existe no acervo — deve responder que não encontrou informação, sem alucinar |
| 7 | Quais os efeitos colaterais mais comuns relatados nos estudos clínicos da Losartana? | Genérica/ambígua | Sem menção a estudo específico — ver quão bem o retrieval geral se sai |
| 8 | Existe interação medicamentosa entre Losartana e diuréticos poupadores de potássio (ex: espironolactona)? | Direta / seção específica | Testa recuperação de uma subseção mais específica (interações medicamentosas) dentro da própria bula |

## Critérios de avaliação (para preencher no results.md)

- **Fidelidade** (a resposta é fiel ao contexto recuperado, sem inventar dado que não está lá?)
  - `2` = totalmente fiel, todo dado citado está no contexto
  - `1` = parcialmente fiel (mistura contexto real com alguma inferência não sustentada)
  - `0` = alucinação clara (afirma algo que não está no contexto recuperado)

- **Relevância** (o contexto recuperado é de fato relevante para a pergunta?)
  - `2` = os chunks recuperados respondem diretamente à pergunta
  - `1` = parcialmente relevante (contexto relacionado mas não específico o suficiente)
  - `0` = irrelevante (retrieval trouxe chunks que não têm nada a ver)
