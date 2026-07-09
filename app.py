import json
import re
import subprocess
import sys
from pathlib import Path

import streamlit as st

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.vectordb.client import get_client, get_or_create_collection
from src.vectordb.query import search, list_document_ids

st.set_page_config(
    page_title="Assistente Clínico RAG",
    page_icon="🏥",
    layout="wide",
)

# ── Constantes ──────────────────────────────────────────────────────────────

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

PATHS = {
    "raw": Path("data/raw"),
    "processed": Path("data/processed/documents.json"),
    "chunked": Path("data/chunked/chunks.json"),
    "embeddings": Path("data/embeddings/embeddings.json"),
    "vectordb": Path("data/vectordb/chroma"),
}


# ── Helpers ──────────────────────────────────────────────────────────────────


def check_status() -> dict[str, bool]:
    pdfs = list(PATHS["raw"].glob("*.pdf"))
    return {
        "pdfs_brutos": len(pdfs) > 0,
        "num_pdfs": len(pdfs),
        "documentos_processados": PATHS["processed"].exists(),
        "chunks_gerados": PATHS["chunked"].exists(),
        "embeddings_gerados": PATHS["embeddings"].exists(),
        "vectordb_populado": PATHS["vectordb"].exists(),
    }


def run_pipeline_step(step_name: str, module_path: str) -> None:
    status_placeholder = st.empty()
    status_placeholder.info(f"Executando {step_name}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", module_path],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            st.error(f"**{step_name}** falhou:\n```\n{result.stderr}\n```")
        else:
            st.success(f"**{step_name}** concluído com sucesso!")
    except subprocess.TimeoutExpired:
        st.error(f"**{step_name}** excedeu o tempo limite.")
    except Exception as e:
        st.error(f"**{step_name}** erro inesperado: {e}")
    finally:
        status_placeholder.empty()
        st.cache_data.clear()


def extract_study_acronyms(question: str) -> set[str]:
    return {
        m.group(0)
        for m in re.finditer(r"\b[A-Z]{4,}\b", question)
    } - SIGLAS_IGNORADAS


def load_chunks_preview() -> list[dict]:
    if PATHS["chunked"].exists():
        with open(PATHS["chunked"]) as f:
            return json.load(f)
    return []


def load_documents_preview() -> list[dict]:
    if PATHS["processed"].exists():
        with open(PATHS["processed"]) as f:
            data = json.load(f)
        seen = set()
        docs = []
        for d in data:
            doc_id = d.get("document_id", "")
            if doc_id not in seen:
                docs.append(
                    {
                        "document_id": doc_id,
                        "document_name": d.get("document_name", ""),
                        "category": d.get("category", ""),
                        "pages": d.get("page", ""),
                    }
                )
                seen.add(doc_id)
        return docs
    return []


def init_rag_resources(vectorstore_path: str):
    path_obj = Path(vectorstore_path)
    client = get_client(path_obj)
    collection = get_or_create_collection(client)
    llm = OllamaLLM(model="llama3", temperature=0.1)
    prompt = PromptTemplate(
        template=CLINICAL_PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    chain = prompt | llm | StrOutputParser()
    return collection, chain


def ask_rag(
    question: str,
    collection,
    chain,
    top_k: int = SEARCH_TOP_K,
    max_chunks: int = MAX_CONTEXT_CHUNKS,
):
    estudos_alvo = extract_study_acronyms(question)

    try:
        results = search(collection, question, top_k=top_k)
    except Exception as e:
        return f"Erro ao buscar na base vetorial: {e}", []

    formatted_chunks = []
    for res in results:
        texto = res["text"]

        if estudos_alvo:
            if not any(
                re.search(rf"\b{re.escape(e)}\b", texto, re.IGNORECASE)
                for e in estudos_alvo
            ):
                continue

        doc_id = res["metadata"].get("document_id", "Documento")
        page = res["metadata"].get("page_start", "?")
        name = doc_id.replace("_", " ").title()
        dist = res.get("distance", 0)

        formatted_chunks.append(
            {
                "display": f"[Fonte: {name} - Pág. {page}] (distância: {dist:.4f})",
                "text": texto,
                "document_id": doc_id,
                "page": page,
                "distance": dist,
            }
        )

    shown = formatted_chunks[:max_chunks]
    contexto = "\n\n---\n\n".join(
        f"{c['display']}\nConteúdo: {c['text']}" for c in shown
    )

    if not shown:
        contexto = "Nenhum bloco específico sobre o estudo solicitado foi localizado no contexto."

    try:
        resposta = chain.invoke({"context": contexto, "question": question})
    except Exception as e:
        return f"Erro ao gerar resposta: {e}", shown

    return resposta, shown


# ── Sessão ───────────────────────────────────────────────────────────────────

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

if "collection" not in st.session_state:
    st.session_state.collection = None

if "chain" not in st.session_state:
    st.session_state.chain = None


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/hospital.png",
        width=60,
    )
    st.title("🏥 Assistente")
    st.markdown("Pipeline RAG para documentos clínicos")

    st.divider()

    # ── Status ───────────────────────────────────────────────────────────────
    st.subheader("📊 Status da Base")
    status = check_status()

    status_items = [
        ("📄 PDFs crus", status["pdfs_brutos"],
         f"{status['num_pdfs']} PDF(s) encontrado(s)"),
        ("📑 Docs processados", status["documentos_processados"]),
        ("✂️ Chunks gerados", status["chunks_gerados"]),
        ("🧠 Embeddings gerados", status["embeddings_gerados"]),
        ("🗄️ Vector DB populado", status["vectordb_populado"]),
    ]

    for label, ok, *extra in status_items:
        icon = "✅" if ok else "❌"
        detail = f" — {extra[0]}" if extra else ""
        st.markdown(f"{icon} **{label}**{detail}")

    st.divider()

    # ── Pipeline ─────────────────────────────────────────────────────────────
    st.subheader("⚙️ Pipeline")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Executar Tudo", use_container_width=True, type="primary"):
            for nome, modulo in [
                ("1/4 Ingestão", "src.ingestion.ingest"),
                ("2/4 Chunking", "src.chunking.chunking"),
                ("3/4 Embeddings", "src.embeddings.embedding"),
                ("4/4 Vector Store", "src.vectordb.store"),
            ]:
                run_pipeline_step(nome, modulo)
            st.rerun()

    with col2:
        if st.button("🔄 Recarregar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if st.button("📥 Ingestão", use_container_width=True):
        run_pipeline_step("1/4 Ingestão", "src.ingestion.ingest")
        st.rerun()
    if st.button("✂️ Chunking", use_container_width=True):
        run_pipeline_step("2/4 Chunking", "src.chunking.chunking")
        st.rerun()
    if st.button("🧠 Embeddings", use_container_width=True):
        run_pipeline_step("3/4 Embeddings", "src.embeddings.embedding")
        st.rerun()
    if st.button("🗄️ Vector Store", use_container_width=True):
        run_pipeline_step("4/4 Vector Store", "src.vectordb.store")
        st.rerun()

    st.divider()

    # ── Config ───────────────────────────────────────────────────────────────
    st.subheader("🔧 Configuração")
    user_top_k = st.slider(
        "Chunks recuperados (top_k)",
        min_value=5,
        max_value=50,
        value=SEARCH_TOP_K,
        step=5,
    )

    st.divider()

    # ── Documentos ───────────────────────────────────────────────────────────
    st.subheader("📚 Documentos na Base")
    docs = load_documents_preview()
    if docs:
        for d in docs:
            with st.expander(f"{d['document_name']}"):
                st.markdown(f"**ID:** `{d['document_id']}`")
                st.markdown(f"**Categoria:** {d['category']}")
                st.markdown(f"**Páginas:** {d['pages']}")
    else:
        st.info("Nenhum documento processado ainda.")

    chunks_all = load_chunks_preview()
    if chunks_all:
        st.markdown(f"**Total de chunks:** {len(chunks_all)}")

    st.divider()
    st.caption(f"Python {sys.version.split()[0]} · Streamlit {st.__version__}")


# ── Main ─────────────────────────────────────────────────────────────────────

st.title("🏥 Assistente Clínico — RAG")
st.markdown(
    "Faça perguntas sobre **Hipertensão Arterial Sistêmica** e **Bula da Losartana** "
    "com base nos documentos oficiais. O assistente recupera trechos relevantes e "
    "responde com análise fundamentada."
)

st.divider()

# Verificar se o vector DB está pronto
if not status["vectordb_populado"]:
    st.warning(
        "⚠️ A base vetorial ainda não foi populada. "
        "Execute o pipeline completo no menu lateral para poder fazer perguntas."
    )
    st.info(
        "💡 Se os dados já foram processados, clique em **Vector Store** no sidebar "
        "para povoar o banco vetorial."
    )

# Inicializar RAG se possível
if status["vectordb_populado"] and st.session_state.collection is None:
    with st.spinner("Carregando base vetorial e modelo de linguagem..."):
        try:
            col, ch = init_rag_resources("data/vectordb/chroma")
            st.session_state.collection = col
            st.session_state.chain = ch
            st.success("✅ Recursos carregados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao carregar recursos: {e}")

# ── Chat ─────────────────────────────────────────────────────────────────────

chat_container = st.container()

with chat_container:
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "chunks" in msg and msg["chunks"]:
                with st.expander(f"📄 Fontes utilizadas ({len(msg['chunks'])})"):
                    for c in msg["chunks"]:
                        st.markdown(f"**{c['display']}**")
                        st.markdown(f"> {c['text']}")
                        st.markdown("---")

# Input
if prompt := st.chat_input("Digite sua pergunta sobre os documentos clínicos..."):
    st.session_state.mensagens.append({"role": "user", "content": prompt})

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

        if st.session_state.collection is None:
            with st.chat_message("assistant"):
                st.error(
                    "A base vetorial não está disponível. Execute o pipeline "
                    "no menu lateral primeiro."
                )
            st.session_state.mensagens.append(
                {
                    "role": "assistant",
                    "content": "Erro: base vetorial não disponível.",
                    "chunks": [],
                }
            )
        else:
            with st.chat_message("assistant"):
                with st.spinner("Buscando e analisando..."):
                    resposta, chunks = ask_rag(
                        prompt,
                        st.session_state.collection,
                        st.session_state.chain,
                        top_k=user_top_k,
                    )
                st.markdown(resposta)

                if chunks:
                    with st.expander(f"📄 Ver fontes consultadas ({len(chunks)})"):
                        for c in chunks:
                            st.markdown(f"**{c['display']}**")
                            st.markdown(f"> {c['text']}")
                            st.markdown("---")

            st.session_state.mensagens.append(
                {"role": "assistant", "content": resposta, "chunks": chunks}
            )
