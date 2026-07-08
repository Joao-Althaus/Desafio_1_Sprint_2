from src.ingestion import ingest
from src.chunking import chunking
from src.embeddings import embedding
from src.vectordb import query, store


def build_pipeline():
    print("=== 1/4 Ingestão ===")
    ingest.main()

    print("\n=== 2/4 Chunking ===")
    chunking.main()

    print("\n=== 3/4 Embeddings ===")
    embedding.main()

    print("\n=== 4/4 Vectordb (Chroma) ===")
    return store.main()


def interactive_search(collection):
    print("\nDigite uma pergunta sobre hipertensão/losartana (ENTER vazio pra sair).")

    while True:
        question = input("\n> ").strip()

        if not question:
            print("Encerrando.")
            break

        results = query.search(collection, question, top_k=5)

        if not results:
            print("Nenhum resultado encontrado.")
            continue

        for i, result in enumerate(results, start=1):
            print(
                f"\n[{i}] distância={result['distance']:.4f} "
                f"| documento={result['metadata']['document_id']}"
            )
            print(result["text"])


if __name__ == "__main__":
    collection = build_pipeline()

    # if collection is not None:
      #   interactive_search(collection)
