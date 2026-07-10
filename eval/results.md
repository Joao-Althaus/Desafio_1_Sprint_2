# Relatório de Avaliação — Assistente RAG Clínico

## 1. Como gerar os dados deste relatório (passo a passo — hoje)

### Passo 1 — Rodar a configuração atual (chunk_size=400, overlap=60)
Seu índice atual já deve estar pronto (`data/vectordb/chroma`). Rode:
```bash
python -m eval.run_eval --persist-dir data/vectordb/chroma --collection-name clinical_docs --label config_atual
```
Isso gera `eval/raw_results_config_atual.json` com pergunta, resposta e tempo de execução para cada uma das 8 perguntas de `eval/test_questions.md`.

### Passo 2 — Gerar uma configuração alternativa de chunk (para comparação)
No arquivo de chunking (`generate_chunks`), troque temporariamente:
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,      # trocar para 800
    chunk_overlap=60,    # trocar para 100
    ...
)
```
Depois rode o pipeline apontando para pastas alternativas (para não sobrescrever os dados atuais):
```bash
python -m src.chunking.chunking --processed-dir data/processed --chunked-dir data/chunked_alt
python -m src.embeddings.embedding --input-file data/chunked_alt/chunks.json --output-dir data/embeddings_alt --output-file data/embeddings_alt/embeddings.json
python -m src.vectordb.store --embeddings-file data/embeddings_alt/embeddings.json --persist-dir data/vectordb/chroma_alt --collection-name clinical_docs_alt
```
Rode a avaliação na configuração alternativa:
```bash
python -m eval.run_eval --persist-dir data/vectordb/chroma_alt --collection-name clinical_docs_alt --label config_alt
```
**Não esqueça de reverter o `chunk_size`/`chunk_overlap` para 400/60 depois** (a configuração de produção continua sendo a atual).

### Passo 3 — Preencher as tabelas abaixo
Abra `eval/raw_results_config_atual.json` e `eval/raw_results_config_alt.json`, leia cada resposta, e preencha manualmente a fidelidade e relevância usando a rubrica de `eval/test_questions.md`.

---

## 2. Configurações comparadas

| Configuração | chunk_size | chunk_overlap | Coleção |
|---|---|---|---|
| Atual (produção) | 400 tokens | 60 tokens | `clinical_docs` |
| Alternativa | 800 tokens | 100 tokens | `clinical_docs_alt` |

---

## 3. Tabela de Fidelidade e Relevância — Configuração Atual (400/60)

| # | Pergunta | Fidelidade (0-2) | Relevância (0-2) | Observação |
|---|---|---|---|---|
| 1 | Dose de Losartana | 1 | 2 | Cita fonte inexistente no acervo ("Manual de gestação de alto risco", pág. 38) junto com dado plausível da bula real |
| 2 | Contraindicações | 2 | 2 | Consistente com bula (gravidez, insuficiência renal/hepática, angioedema) |
| 3 | Primeira linha PCDT | 2 | 2 | Cita página 36 corretamente; checar se "benazepril" é exemplo real do PCDT ou inventado |
| 4 | Estudo LIFE | 2 | 2 | Dados específicos (13% redução risco, 25% AVC) com citação de página |
| 5 | RENAAL vs ELITE | 2 | 2 | Descreve corretamente os dois estudos e por que não são comparáveis diretamente |
| 6 | Sacubitril/Valsartana (fora do escopo) | 0 | 0 | Alucinação grave: inventou dosagem pediátrica específica para fármaco fora do acervo, violando instrução explícita do prompt |
| 7 | Efeitos colaterais | 2 | 2 | Cita fontes internas reais (Losartana pág. 4, PCDT pág. 55) |
| 8 | Interação com espironolactona | 0 | 1 | Fabricou referências acadêmicas inexistentes (ex: "Journal of Cardiac Failure, vol. 12") |
| **Média** | | **1.375/2** | **1.625/2** | Tempo médio de resposta: 83.5s |

## 4. Tabela de Fidelidade e Relevância — Configuração Alternativa (800/100)

| # | Pergunta | Fidelidade (0-2) | Relevância (0-2) | Observação |
|---|---|---|---|---|
| 1 | Dose de Losartana | 1 | 2 | Cita a fonte genérica (PCDT) sem página; dose similar à config atual, mas menos específica |
| 2 | Contraindicações | 0 | 1 | **Contaminação cruzada:** respondeu sobre "Besilato de anlodipino" e "Nifedipino" em vez de Losartana — chunk maior parece ter misturado seções de fármacos diferentes do PCDT |
| 3 | Primeira linha PCDT | 2 | 2 | Resposta idêntica à config atual — pergunta não é sensível ao tamanho do chunk neste caso |
| 4 | Estudo LIFE | 2 | 2 | Dados consistentes e até mais completos que a config atual |
| 5 | RENAAL vs ELITE | 2 | 2 | Consistente com a config atual |
| 6 | Sacubitril/Valsartana (fora do escopo) | 0 | 0 | Ainda alucina uma dosagem específica de memória, apesar de reconhecer que não está no contexto |
| 7 | Efeitos colaterais | 0 | 0 | **Alucinação grave:** inventou 3 citações acadêmicas completas (revistas, anos, percentuais) sem nenhuma relação com o contexto recuperado |
| 8 | Interação com espironolactona | 1 | 2 | Resposta clinicamente plausível, sem citações fabricadas (melhor que a config atual nesse quesito) |
| **Média** | | **1.0/2** | **1.375/2** | Tempo médio de resposta: 73.0s |

---

## 5. Casos Insatisfatórios

- **Pergunta #6 (Sacubitril/Valsartana — fora do escopo), ambas as configurações:**
  - **O que aconteceu:** o prompt instrui explicitamente que, se o contexto não tiver relação com a pergunta, o modelo deve dizer que a informação não foi localizada. Em vez disso, nas duas configurações o LLM forneceu dosagens específicas (pediátrica na config atual, adulta na config alt) que não vêm de nenhum documento do acervo — são inventadas a partir do conhecimento paramétrico do modelo.
  - **Causa provável:** o modelo (Llama 3) tem conhecimento de treinamento sobre esse fármaco e "preenche a lacuna" em vez de se restringir ao contexto, mesmo com instrução explícita em contrário.
  - **Melhoria sugerida:** reforçar no prompt uma instrução mais rígida tipo "responda EXCLUSIVAMENTE com base no contexto, mesmo que você tenha conhecimento prévio sobre o assunto" e/ou adicionar um passo de verificação pós-geração (ex: checar se termos-chave da resposta aparecem no contexto recuperado).

- **Pergunta #8 (interação medicamentosa), configuração atual:**
  - **O que aconteceu:** o LLM fabricou referências acadêmicas completas (nome de revista, volume, ano) que não existem no contexto recuperado nem, aparentemente, na realidade.
  - **Causa provável:** a pergunta pede uma resposta "analítica e fundamentada", o que pode incentivar o modelo a complementar com citações de aparência acadêmica quando o contexto recuperado é insuficiente.
  - **Melhoria sugerida:** proibir explicitamente no prompt a citação de fontes externas/acadêmicas que não estejam no contexto fornecido.

- **Pergunta #2 (contraindicações), configuração alternativa (800/100):**
  - **O que aconteceu:** a resposta trocou a Losartana por "Besilato de anlodipino" e "Nifedipino" — fármacos que não foram perguntados.
  - **Causa provável:** com chunks maiores (800 tokens), é mais provável que um único chunk contenha trechos sobre múltiplas classes de anti-hipertensivos do PCDT, e o retrieval semântico pode ter trazido esse chunk "misto" com maior relevância aparente do que um chunk específico da bula da Losartana.
  - **Melhoria sugerida:** ao aumentar o chunk_size, considerar também reduzir o `top_k` ou adicionar um filtro por `document_id` quando a pergunta menciona um fármaco específico (semelhante ao filtro já existente para estudos clínicos).

- **Pergunta #7 (efeitos colaterais), configuração alternativa (800/100):**
  - **O que aconteceu:** alucinação mais grave do teste — três citações acadêmicas completas e fabricadas (revistas, anos, percentuais de efeitos colaterais), sem nenhuma relação com os dois documentos reais do acervo.
  - **Causa provável:** possivelmente o contexto recuperado com chunks maiores ficou mais diluído/genérico, e diante de um contexto menos específico o modelo recorreu a "preencher" com conhecimento próprio de forma mais assertiva do que na config atual (que, para a mesma pergunta, citou corretamente páginas reais do acervo).
  - **Melhoria sugerida:** mesma do caso anterior — reforço de prompt proibindo citação de fontes externas, e considerar reduzir a temperatura do LLM (atualmente 0.1, já baixa, mas pode precisar de ajuste no prompt em vez da temperatura).

---

## 6. Comparação entre Configurações e Racional da Otimização

**Resumo quantitativo (8 perguntas de teste):**

| Métrica | Config Atual (400/60) | Config Alternativa (800/100) |
|---|---|---|
| Fidelidade média | 1.375 / 2 | 1.0 / 2 |
| Relevância média | 1.625 / 2 | 1.375 / 2 |
| Tempo médio de resposta | 83.5s | 73.0s |
| Total de chunks gerados | — (config de produção) | 195 chunks |

**Qualidade da resposta:** a configuração atual (400 tokens, overlap 60) teve desempenho melhor tanto em fidelidade quanto em relevância neste conjunto de teste. O ganho mais evidente foi na pergunta sobre contraindicações (#2), onde a config alternativa confundiu a Losartana com outros fármacos citados no mesmo documento (PCDT), e na pergunta sobre efeitos colaterais (#7), onde a config alternativa produziu a alucinação mais grave do teste (citações acadêmicas fabricadas).

**Trade-off observado (diferente do esperado teoricamente):** a expectativa inicial era que chunks maiores preservariam mais contexto ao redor de nomes de estudos/fármacos, reduzindo problemas de corte no meio da informação (identificado no debug do pipeline de chunking). Na prática, com apenas 2 documentos no acervo, chunks maiores parecem ter tido o efeito oposto: por abrangerem mais conteúdo por chunk, aumentaram a chance de um único chunk misturar informações de fármacos ou seções diferentes do mesmo documento (PCDT trata de várias classes terapêuticas), o que confundiu o LLM em pelo menos uma pergunta. Isso sugere que, para um acervo pequeno e denso como este, chunks menores e mais específicos (400/60) favorecem uma recuperação mais precisa.

**Tempo de resposta:** a configuração alternativa foi, em média, ~10s mais rápida — mas essa diferença é pequena frente à variância observada entre perguntas (27s a 118s) e não deve ser o fator decisivo na escolha, dado o tamanho pequeno da amostra (8 perguntas).

**Padrão recorrente entre as duas configurações:** independentemente do chunk size, o sistema alucinou de forma consistente quando (a) a pergunta era sobre um fármaco fora do acervo (#6), e (b) a pergunta pedia uma resposta "analítica e fundamentada" sem contexto específico suficiente (#8 na config atual, #7 na config alt). Isso indica que o problema de alucinação neste projeto está mais ligado ao prompt/comportamento do LLM do que à configuração de chunking em si — vale priorizar o ajuste do prompt (instrução mais rígida contra uso de conhecimento externo) antes de investir mais tempo ajustando chunk_size/overlap.

**Configuração escolhida para produção:** manter **400/60** (configuração atual), com base nos dados observados — teve fidelidade e relevância médias mais altas neste teste, e o ganho de velocidade da alternativa não compensa a perda de qualidade, especialmente em um domínio clínico onde exatidão é mais crítica que latência.

---

*Gerado a partir de `eval/run_eval.py` e `eval/test_questions.md`. Preencher as seções 3, 4, 5 e 6 com os dados reais antes da entrega.*
