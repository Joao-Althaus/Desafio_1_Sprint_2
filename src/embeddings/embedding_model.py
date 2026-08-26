from sentence_transformers import SentenceTransformer


DEFAULT_MODEL_NAME = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def load_embedding_model(
    model_name: str = DEFAULT_MODEL_NAME,
) -> SentenceTransformer:
    """
    Carrega e retorna o modelo de embeddings informado.
    """

    print(f"Carregando modelo {model_name}...")

    model = SentenceTransformer(model_name)

    print("Modelo carregado com sucesso!")

    return model