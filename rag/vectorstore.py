from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # Güncellenmiş import
import os

def create_vectorstore(docs, save_path="faiss_index"):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embedding_model)
    vectorstore.save_local(save_path)
    print(f"FAISS veritabanı '{save_path}' olarak kaydedildi.")
    return vectorstore


def load_vectorstore(load_path="rag/faiss_index"):
    # FAISS dosyasının tam yolunu belirle
    absolute_path = os.path.abspath(load_path)

    print(f"✅ FAISS dizini: {absolute_path}")  # Hata ayıklamak için ekledik

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = FAISS.load_local(
        absolute_path,
        embedding_model,
        allow_dangerous_deserialization=True  # Güvenlik ayarı
    )

    print(f"✅ FAISS veritabanı '{absolute_path}' yüklendi.")
    return vectorstore.as_retriever()

