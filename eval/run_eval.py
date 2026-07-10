"""
Script de avaliação do RAG.

Roda o conjunto de perguntas de teste (eval/test_questions.md) contra a chain RAG
e salva pergunta, resposta, chunks recuperados (fonte + página) e tempo de resposta
em eval/raw_results_<label>.json.

Uso:
    python -m eval.run_eval --persist-dir data/vectordb/chroma --collection-name clinical_docs --label config_atual
    python -m eval.run_eval --persist-dir data/vectordb/chroma_alt --collection-name clinical_docs_alt --label config_alt

Ajuste a linha marcada com "AJUSTAR" abaixo para o caminho real do módulo
onde está a função `inicializar_rag` (o arquivo que você mandou para debug).
"""

import argparse
import json
import time
from pathlib import Path

from src.LLM.rag_chain import inicializar_rag  # noqa: E402

OUTPUT_DIR = Path("eval")

TEST_QUESTIONS = [
    "Qual a dose recomendada de Losartana para pacientes adultos com hipertensão?",
    "Quais são as contraindicações da Losartana?",
    "Segundo o PCDT de Hipertensão Arterial, qual a primeira linha de tratamento farmacológico?",
    "O que o Estudo LIFE concluiu sobre desfechos cardiovasculares com o uso de Losartana?",
    "Compare os resultados do Estudo RENAAL com o Estudo ELITE mencionados na bula da Losartana.",
    "Qual a dosagem pediátrica recomendada de Sacubitril/Valsartana?",
    "Quais os efeitos colaterais mais comuns relatados nos estudos clínicos da Losartana?",
    "Existe interação medicamentosa entre Losartana e diuréticos poupadores de potássio (ex: espironolactona)?",
]


def main(persist_dir: str, collection_name: str, label: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Inicializando RAG (persist_dir={persist_dir}, collection={collection_name})...")
    rag_chain, collection = inicializar_rag(vectorstore_path=persist_dir)

    results = []

    for i, question in enumerate(TEST_QUESTIONS, start=1):
        print(f"[{i}/{len(TEST_QUESTIONS)}] {question}")
        start = time.perf_counter()
        try:
            answer = rag_chain.invoke(question)
            error = None
        except Exception as exc:  # noqa: BLE001
            answer = None
            error = str(exc)
        elapsed = time.perf_counter() - start

        results.append(
            {
                "question": question,
                "answer": answer,
                "error": error,
                "elapsed_seconds": round(elapsed, 2),
            }
        )

    output_file = OUTPUT_DIR / f"raw_results_{label}.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    print(f"\nResultados salvos em: {output_file}")
    print("Agora abra o arquivo, leia cada resposta e preencha a tabela em eval/results.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roda o conjunto de teste contra a chain RAG")
    parser.add_argument("--persist-dir", type=str, default="data/vectordb/chroma")
    parser.add_argument("--collection-name", type=str, default="clinical_docs")
    parser.add_argument("--label", type=str, required=True, help="Identificador da rodada (ex: config_atual, config_alt)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.persist_dir, args.collection_name, args.label)
