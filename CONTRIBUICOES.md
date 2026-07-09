## **Contribuições Squad 4**


### **Bruno Jordao das Neves Moura**


#### Contribuição


#### Reflexão


### **Cleidyanne Castro Pereira**

#### Contribuição

Fiquei responsável pela etapa inicial de ingestão e pré-processamento dos dados do acervo clínico. Implementei a leitura dos PDFs utilizando LangChain, organizei a extração do conteúdo por página, apliquei limpeza e normalização textual com regex e estruturei os dados em formato JSON para uso nas próximas etapas do pipeline RAG.

Também adicionei metadados aos documentos processados, como nome do arquivo, categoria, página e identificador do documento, permitindo maior rastreabilidade das fontes durante a recuperação de informações. Além disso, incluí suporte via CLI para definir os diretórios de entrada e saída, atualizei a documentação do projeto e adicionei testes para validar a limpeza de texto e a ingestão dos documentos.

Principais entregas:
- Pipeline de ingestão de PDFs clínicos
- Limpeza e normalização de texto
- Exportação dos documentos processados para JSON
- Inclusão de metadados para rastreabilidade
- Testes unitários para ingestão e pré-processamento
- Atualização da documentação de uso

#### Reflexão
Minha principal contribuição foi transformar os documentos clínicos brutos em uma base de dados textual estruturada, limpa e pronta para alimentar as etapas seguintes de chunking, embeddings e recuperação semântica. Durante o desenvolvimento, entendi melhor a importância da etapa de ingestão em sistemas RAG, especialmente em contextos sensíveis como saúde, onde a rastreabilidade da fonte e a qualidade do texto extraído impactam diretamente a confiabilidade das respostas. Essa etapa me ajudou a enxergar o projeto não apenas como um script isolado, mas como parte de uma arquitetura maior de dados e IA.

### **João Vitor Althaus Godoi**

#### Contribuição


#### Reflexão


### **José Ivanildo de Oliveira Marques**

#### Contribuição


#### Reflexão


### **Kaique Silva Sousa**

#### Contribuição

Fiquei responsável pela etapa de segmentação (chunking) dos documentos previamente processados. Implementei o agrupamento das páginas extraídas para reconstruir os documentos e utilizei o RecursiveCharacterTextSplitter do LangChain, combinado com o tiktoken, para realizar a quebra do texto baseada em tokens. Isso garante que os fragmentos fiquem otimizados para os modelos de embedding e LLMs nas próximas etapas do pipeline RAG.

Para garantir a rastreabilidade da origem de cada trecho, usei a lógica que injeta tags de marcação de página ([PAGE X]), que foi demonstrada por Gisele no ultimo workshop, antes da quebra do texto. Após o chunking, extraio o intervalo exato de páginas (início e fim) de cada fragmento via regex, limpando as marcações em seguida. Além disso, implementei a geração de um hash (SHA-256) para o conteúdo de cada chunk, visando o controle de integridade, incluí suporte via CLI para a definição de diretórios, criei testes para validar a geração dos chunks e atualizei a documentação do projeto.

Principais entregas:
- Pipeline de chunking baseado em limite de tokens (cl100k_base)
- Agrupamento de páginas e reconstrução de documentos
- Lógica de tagueamento para extração precisa de intervalo de páginas (page_start e page_end)
- Geração de hash (SHA-256) por chunk para rastreabilidade de conteúdo
- Estruturação e exportação dos fragmentos e metadados em JSON
- Suporte a CLI para configuração de caminhos de entrada e saída
- Testes unitários para validação da geração de chunks
- Atualização da documentação do projeto

#### Reflexão

Minha contribuição nesta etapa foi resolver o desafio de quebrar textos longos sem perder o contexto semântico e a referência exata de onde a informação veio. Gostei muito da técnica de injetar e depois remover as marcações de página, ela me permitiu manter a granularidade da rastreabilidade mesmo após o texto ser fatiado. Durante o desenvolvimento, compreendi na prática como o chunk size e o overlap são críticos para sistemas RAG. Um chunking mal feito pode cortar informações vitais pela metade, mas a solução implementada garante que os dados estejam íntegros, bem delimitados e altamente rastreáveis, o que é fundamental para a precisão das buscas e respostas no sistema de saúde por ser uma área muito sensivel a erros.

### **Natan Alencar Maia**

#### Contribuição


#### Reflexão
