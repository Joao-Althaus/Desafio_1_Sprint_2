import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

COMPARISON_MODEL = (
    "sentence-transformers/distiluse-base-multilingual-cased-v2"
)

CHUNKS_FILE = Path("data/chunked/chunks.json")
EVAL_FILE = Path("eval/embedding_eval.json")


def cosine_similarity(query_embedding, chunk_embeddings):
    """
    Calcula a similaridade de cosseno entre a query e os chunks.
    """

    query_embedding = np.asarray(query_embedding)

    chunk_embeddings = np.asarray(chunk_embeddings)

    return np.dot(chunk_embeddings, query_embedding)


def rank_chunks(model, chunks, query):
    """
    Gera o embedding da query e ordena os chunks
    pela similaridade semântica.
    """

    texts = [chunk["text"] for chunk in chunks]

    chunk_embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    scores = cosine_similarity(
        query_embedding,
        chunk_embeddings,
    )

    ranked_indices = np.argsort(scores)[::-1]

    return [
        (
            chunks[index]["id"],
            float(scores[index]),
        )
        for index in ranked_indices
    ]


def hit_at_k(ranked_ids, relevant_ids, k):
    """
    Verifica se pelo menos um chunk relevante
    aparece entre os K primeiros resultados.
    """

    top_k = ranked_ids[:k]

    return int(
        any(chunk_id in relevant_ids for chunk_id in top_k)
    )


def reciprocal_rank(ranked_ids, relevant_ids):
    """
    Calcula o Reciprocal Rank da primeira ocorrência relevante.
    """

    for position, chunk_id in enumerate(ranked_ids, start=1):

        if chunk_id in relevant_ids:
            return 1 / position

    return 0.0


def evaluate_model(
    model_name,
    chunks,
    evaluation_cases,
):
    """
    Avalia um modelo de embeddings usando
    Hit@1, Hit@3, Hit@5 e MRR.
    """

    print()
    print("=" * 60)
    print(f"Avaliando modelo: {model_name}")
    print("=" * 60)

    model = SentenceTransformer(model_name)

    results = []

    for case in evaluation_cases:

        query = case["question"]

        relevant_ids = {case["source_chunk_id"]}

        ranked_results = rank_chunks(
            model,
            chunks,
            query,
        )

        ranked_ids = [
            chunk_id
            for chunk_id, _ in ranked_results
        ]

        results.append(
            {
                "query": query,
                "hit@1": hit_at_k(
                    ranked_ids,
                    relevant_ids,
                    1,
                ),
                "hit@3": hit_at_k(
                    ranked_ids,
                    relevant_ids,
                    3,
                ),
                "hit@5": hit_at_k(
                    ranked_ids,
                    relevant_ids,
                    5,
                ),
                "reciprocal_rank": reciprocal_rank(
                    ranked_ids,
                    relevant_ids,
                ),
                "top_results": ranked_results[:5],
            }
        )

    total = len(results)

    metrics = {
        "model": model_name,
        "num_queries": total,
        "hit@1": sum(
            result["hit@1"]
            for result in results
        ) / total,
        "hit@3": sum(
            result["hit@3"]
            for result in results
        ) / total,
        "hit@5": sum(
            result["hit@5"]
            for result in results
        ) / total,
        "mrr": sum(
            result["reciprocal_rank"]
            for result in results
        ) / total,
    }

    return metrics, results


def main():

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        chunks = json.load(file)

    with open(
        EVAL_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        evaluation_cases = json.load(file)

    models = [
        DEFAULT_MODEL,
        COMPARISON_MODEL,
    ]

    all_results = []

    for model_name in models:

        metrics, query_results = evaluate_model(
            model_name,
            chunks,
            evaluation_cases,
        )

        all_results.append(
            {
                "metrics": metrics,
                "queries": query_results,
            }
        )

        print()
        print("Métricas:")
        print(
            f"Hit@1: {metrics['hit@1']:.3f}"
        )
        print(
            f"Hit@3: {metrics['hit@3']:.3f}"
        )
        print(
            f"Hit@5: {metrics['hit@5']:.3f}"
        )
        print(
            f"MRR:    {metrics['mrr']:.3f}"
        )

    output_file = Path(
        "eval/embedding_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            all_results,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(
        f"Resultados salvos em: {output_file}"
    )


if __name__ == "__main__":
    main()