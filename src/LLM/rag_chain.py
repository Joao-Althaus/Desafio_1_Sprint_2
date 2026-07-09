import re
from pathlib import Path
from typing import TYPE_CHECKING

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from src.vectordb.client import get_client, get_or_create_collection
from src.vectordb.query import search

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection

CLINICAL_PROMPT_TEMPLATE = """
Você é um Assistente Clínico especialista em análise de documentos médicos e bulas. 
Sua tarefa é responder à pergunta do profissional de saúde baseando-se estritamente no contexto fornecido.

Diretrizes:
1. Responda à pergunta de forma direta, analítica e resumida, utilizando APENAS os dados explícitos do contexto abaixo.
2. Se o contexto contiver a resposta, extraia os dados e cite a fonte baseando-se no documento/página fornecido.
3. Se o contexto estiver completamente vazio ou não contiver absolutamente nenhuma relação com a pergunta, diga apenas que a informação não foi localizada no acervo atual.
4. ATENÇÃO CRÍTICA: Não misture dados de estudos clínicos diferentes (ex: Estudo LIFE, Estudo RENAAL, Estudo ELITE). Se a pergunta for sobre o Estudo LIFE, use APENAS os dados do parágrafo que cita explicitamente o termo "LIFE". Nunca atribua dados de um estudo a outro.

Contexto Recuperado:
{context}

Pergunta Médica: {question}

Resposta Analítica e Fundamentada:
"""

SEARCH_TOP_K = 30
MAX_CONTEXT_CHUNKS = 10
SIGLAS_IGNORADAS = {"IECA"}


def inicializar_rag(
    vectorstore_path: str = "data/vectordb/chroma",
    top_k: int = 6,
) -> "tuple[RunnableLambda, Collection]":
    path_obj = Path(vectorstore_path)
    client = get_client(path_obj)
    collection = get_or_create_collection(client)

    llm = OllamaLLM(model="llama3", temperature=0.1)

    prompt = PromptTemplate(
        template=CLINICAL_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    chain_final = prompt | llm | StrOutputParser()

    def rag_chain_execution(input_data):
        original_question = (
            input_data if isinstance(input_data, str) else input_data.get("question")
        )

        if not original_question or not original_question.strip():
            return "Erro: a pergunta fornecida está vazia ou inválida."

        estudos_alvo = {
            m.group(0)
            for m in re.finditer(r"\b[A-Z]{4,}\b", original_question)
        } - SIGLAS_IGNORADAS

        try:
            results = search(collection, original_question, top_k=SEARCH_TOP_K)
        except Exception as e:
            return f"Erro ao buscar na base vetorial: {e}"

        formatted_chunks = []
        for res in results:
            texto_bloco = res["text"]

            if estudos_alvo:
                if not any(
                    re.search(rf"\b{re.escape(estudo)}\b", texto_bloco, re.IGNORECASE)
                    for estudo in estudos_alvo
                ):
                    continue

            doc_id = res["metadata"].get("document_id", "Documento")
            page_num = res["metadata"].get("page_start", "?")
            display_name = doc_id.replace("_", " ").title()

            formatted_chunks.append(
                f"[Fonte: {display_name} - Pág. {page_num}]\nConteúdo: {texto_bloco}"
            )

        formatted_chunks = formatted_chunks[:MAX_CONTEXT_CHUNKS]
        contexto_formatado = "\n\n---\n\n".join(formatted_chunks)

        if not formatted_chunks:
            contexto_formatado = "Nenhum bloco específico sobre o estudo solicitado foi localizado no contexto."

        try:
            return chain_final.invoke(
                {"context": contexto_formatado, "question": original_question}
            )
        except Exception as e:
            return f"Erro ao gerar resposta com o modelo de linguagem: {e}"

    rag_chain_pronta = RunnableLambda(rag_chain_execution)

    return rag_chain_pronta, collection


if __name__ == "__main__":
    chain, col = inicializar_rag()
    resposta = chain.invoke("Qual foi o desfecho primário do Estudo LIFE?")
    print(resposta)
