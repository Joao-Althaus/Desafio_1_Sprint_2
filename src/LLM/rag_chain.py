import os
from pathlib import Path
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


import chromadb
from src.vectordb.client import get_client, get_or_create_collection
from src.vectordb.query import search

def inicializar_rag(vectorstore_path="data/vectordb/chroma"):
    """
    Inicializa o pipeline RAG usando o cliente nativo do Chroma da Squad
    para garantir compatibilidade total de leitura dos dados.
    """
    path_obj = Path(vectorstore_path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Diretório da base vetorial não encontrado em: {vectorstore_path}")

    
    client = chromadb.PersistentClient(path=str(path_obj))
    collection = client.get_collection(name="clinical_docs")
    
   
    llm = Ollama(model="llama3", temperature=0.1)

    
    template = """
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
    
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    chain_final = prompt | llm | StrOutputParser()

    
    
    def ragnar_chain_execution(input_data):
        original_question = input_data if isinstance(input_data, str) else input_data.get("question")
        
        
        results = search(collection, original_question, top_k=6)
        
        
        estudos_mapeados = ["LIFE", "RENAAL", "ELITE", "OPTIMAAL"]
        estudo_alvo = None
        for estudo in estudos_mapeados:
            if estudo.lower() in original_question.lower():
                estudo_alvo = estudo
                break

        formatted_chunks = []
        for res in results:
            texto_bloco = res['text']
            
            
            if estudo_alvo and estudo_alvo.lower() not in texto_bloco.lower():
                continue 
                
            doc_id = res["metadata"].get("document_id", "Documento")
            page_num = res["metadata"].get("page_start", "?")
            display_name = doc_id.replace("_", " ").title()
            
            formatted_chunks.append(f"[Fonte: {display_name} - Pág. {page_num}]\nConteúdo: {texto_bloco}")
            
        contexto_formatado = "\n\n---\n\n".join(formatted_chunks)
        
       
        if not formatted_chunks:
            contexto_formatado = "Nenhum bloco específico sobre o estudo solicitado foi localizado no contexto."

        
        return chain_final.invoke({"context": contexto_formatado, "question": original_question})

    rag_chain_pronta = RunnableLambda(ragnar_chain_execution)
    
    
    return rag_chain_pronta, collection

if __name__ == "__main__":
    print("Módulo RAG Chain integrado com o banco nativo da Squad!")