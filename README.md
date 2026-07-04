# Clinical RAG Assistant

This project is a simple example of a clinical RAG assistant. It takes PDF files, prepares the text, and stores the result in JSON for later use.

## English

### What this project does

This project reads PDF files from a folder, cleans the text, and creates a JSON file with the extracted content.

### How to install

1. Create a virtual environment.
2. Activate it.
3. Install the dependencies:

   pip install -r requirements.txt

### How to run

Run the ingestion step with:

   python3 -m src.ingestion.ingest

You can also choose a different folder:

   python3 -m src.ingestion.ingest --raw-dir data/raw --processed-dir data/processed

### Tests

Run the tests with:

   python3 -m unittest discover -s tests -p 'test_*.py'

## Português (Brasil)

Este projeto é um exemplo simples de um assistente clínico RAG. Ele lê arquivos PDF, prepara o texto e salva o resultado em JSON para uso futuro.

### O que este projeto faz

Este projeto lê arquivos PDF de uma pasta, limpa o texto e cria um arquivo JSON com o conteúdo extraído.

### Como instalar

1. Crie um ambiente virtual.
2. Ative o ambiente.
3. Instale as dependências:

   pip install -r requirements.txt

### Como executar

Execute a etapa de ingestão com:

   python3 -m src.ingestion.ingest

Você também pode escolher uma pasta diferente:

   python3 -m src.ingestion.ingest --raw-dir data/raw --processed-dir data/processed

### Testes

Execute os testes com:

   python3 -m unittest discover -s tests -p 'test_*.py'