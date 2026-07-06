# Clinical RAG Assistant

This project is a simple example of a clinical RAG assistant. It takes PDF files, prepares the text, and stores the result in JSON for later use.

## English

### What this project does

This project reads PDF files from a folder, cleans the text, and creates a JSON file with the extracted content.

### How to install

1. Create a virtual environment.
``` bash
python3 -m venv .venv # manually
# or
uv sync # using UV if you have it installed
```
2. Activate it.
``` bash
source .venv/bin/activate # linux and macOS
# or
\.venv\Scripts\activate # windows

```
3. Install the dependencies:
``` bash
pip install -r requirements.txt # reading requirements.txt
# uv sync already installs dependencies if you used it
```

### How to run

You can run it step by step or just run the **main.py** file in the root of the project.

Run the ingestion step with:

``` bash
python3 -m src.ingestion.ingest
# You can also choose a different folder:
python3 -m src.ingestion.ingest --raw-dir data/raw --processed-dir data/processed
```

Now run the chunking step with:


``` bash
python -m src.chunking.chunking
# or use the parameters:
python3 -m src.chunking.chunking --processed-dir data/processed --chunked-dir data/chunked
```

Now run the embbedings generation step with:

``` bash
python -m src.embeddings.embedding
```

### Tests

Run the tests with:

``` bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Português (Brasil)

Este projeto é um exemplo simples de um assistente clínico RAG. Ele lê arquivos PDF, prepara o texto e salva o resultado em JSON para uso futuro.

### O que este projeto faz

Este projeto lê arquivos PDF de uma pasta, limpa o texto e cria um arquivo JSON com o conteúdo extraído.

### Como instalar

1. Crie um ambiente virtual
``` bash
python3 -m venv .venv # manualmente
# ou
uv sync # usando o UV caso tenha instalado
```
2. Ative o ambiente.
``` bash
source .venv/bin/activate # linux e macOS
# ou
\.venv\Scripts\activate # windowns
```
3. Instale as dependências:
``` bash
pip install -r requirements.txt # lendo o requirements.txt
# o uv sync já instala as dependências caso usou ele
```

### Como executar

Você pode executar passo a passo ou so executar o arquivo **main.py** na raiz do projeto

Execute a etapa de ingestão com:

``` bash
python3 -m src.ingestion.ingest
# Você também pode escolher uma pasta diferente:
python3 -m src.ingestion.ingest --raw-dir data/raw --processed-dir data/processed
```

Agora execute a etapa de chunking com

``` bash
python -m src.chunking.chunking
# ou use os parâmetros
python3 -m src.chunking.chunking --processed-dir data/processed --chunked-dir data/chunked
```

Agora execute a etapa de geração de embbedings com

``` bash
python -m src.embeddings.embedding
```


### Testes

Execute os testes com:

``` bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
