from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_embedding_model() -> SentenceTransformer:
    """
    Carrega e retorna o modelo de embeddings.
    """

    print(f"Carregando modelo {MODEL_NAME}...")

    model = SentenceTransformer(MODEL_NAME)

    print("Modelo carregado com sucesso!")

    return model