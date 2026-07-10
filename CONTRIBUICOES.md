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
Fiquei responsável por construir o 'cérebro' do nosso sistema, integrando a LLM(Ollama) ao banco vetorial através do LangChain para consolidar o pipeline RAG. Essa estrutura agora permite a busca inteligente de informações nos PDFs para responder às perguntas do usuário. Para garantir a segurança e a coerência dos resultados, implementei Templates de Prompt com regras estritas e criei um filtro de contexto. Isso impede que a IA misture dados de documentos ou estudos diferentes, eliminando possíveis alucinações e desvios de foco por parte da LLM.

Principais Entregas:
- O pipeline RAG e o filtro em Python que barra a mistura de dados e estudos vizinhos.
- Ajustes no salvamento e leitura para garantir que a numeração das páginas seja guardada de forma mais eficiente.
- Criação dos testes integrados que simulam perguntas e validam se o motor RAG está respondendo com precisão e sem alucinar.
- Criação e calibração dos templates de prompt com regras estritas de comportamento para evitar desvios da IA.

#### Reflexão
O maior aprendizado nessa entrega foi perceber que quando lidamos com dados muito específicos (bulas e estudos clínicos), a engenharia de prompt sozinha não faz milagre. No início, parecia que o desafio seria apenas conectar as ferramentas, mas quando os blocos de estudos diferentes começaram a se misturar, ficou claro que precisava de um controle mais rígido por parte do código.

Desenvolver o filtro de contexto me mostrou que a confiabilidade de um sistema RAG depende muito mais de como a gente trata e blinda o dado do que do modelo de IA em si. Entregar um pipeline que roda local, não alucina e respeita rigorosamente as fontes foi um desafio que me trouxe muitos aprendizados.

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

Realizei uma revisão técnica completa do pipeline RAG, percorrendo todas as etapas -- ingestão de PDFs, chunking, geração de embeddings, indexação no ChromaDB e a chain de geração de respostas com LangChain//Ollama -- identificando bugs, incosistencias e pontos de risco em cada módulo. Também fui resposável por implementar a interface gráfica em streamlit, integrando a chain que já existente para permitir que o usuário faça perguntas e visualize as respostas junto com as fontes/páginas recuperadas dos documentos clínicos.

Principais entregas:
- Revisão e debug de ponta a ponta do pipeline RAG (ingestão, chunking, embeddings, indexação, geração)
- Identificação de bugs de execução (ex: erro de parsing de argumentos no script de indexação no ChromaDB)
- Documento consolidado de debug com sugestões de correção priorizadas
- Interface gráfica em Streamlit para interação com o sistema RAG


#### Reflexão

Debugar o projeto inteiro antes de construir a interface me ajudou a entender de verdade como as peças se conectam — desde como o texto de um PDF vira chunk até como o LLM usa esse contexto pra responder. Percebi como pequenos detalhes (como o nome exato de um modelo no Ollama ou um nome de collection hardcoded) podem quebrar silenciosamente o pipeline, e como decisões na etapa de ingestão e chunking impactam diretamente a qualidade e a confiabilidade das respostas geradas mais à frente. Essa etapa de revisão foi essencial pra eu conseguir desenhar uma interface que realmente refletisse o funcionamento real do sistema, e não só uma camada visual por cima.
