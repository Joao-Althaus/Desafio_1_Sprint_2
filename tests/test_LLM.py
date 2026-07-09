
import sys
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.LLM.rag_chain import inicializar_rag

try:
    print("-> Carregando o pipeline RAG oficial do time...")
    
   
    banco_path = BASE_DIR / "data" / "vectordb" / "chroma"
    
    if not banco_path.exists():
        print(f"\n[ALERTA]: O caminho {banco_path} não foi detectado automaticamente.")
    
    chain, retriever = inicializar_rag(vectorstore_path=str(banco_path))
    print("-> Pipeline carregado com sucesso!\n")
    
    # Pergunta de Teste
    pergunta = "No estudo RENAAL, quais foram os principais desfechos avaliados em pacientes com diabetes tipo 2 e nefropatia que usaram losartana?"

    print(f"Sua Pergunta: {pergunta}")
    print("Aguardando resposta do Ollama (Llama 3)...\n")
    
    print("=== RESPOSTA DO ASSISTENTE CLÍNICO ===")
    
    
    for chunk in chain.stream(pergunta):
        print(chunk, end="", flush=True)
        
    print("\n=======================================")

except FileNotFoundError as e:
    print(f"\n[ERRO DE CONFIGURAÇÃO]: {e}")
except Exception as e:
    print(f"\n[ERRO INESPERADO]: {e}")