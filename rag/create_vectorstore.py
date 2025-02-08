from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

# PDF dosyalarını yükle
folder_path = "./Training Module Files"  # PDF'lerin olduğu klasör
pdf_loaders = [PyPDFLoader(os.path.join(folder_path, file)) for file in os.listdir(folder_path) if file.endswith(".pdf")]

# Tüm PDF'leri oku
documents = []
for loader in pdf_loaders:
    documents.extend(loader.load())

print(f"{len(documents)} doküman yüklendi.")

# Dokümanları parçalara ayır
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

print(f"{len(docs)} parça doküman oluşturuldu.")

# FAISS vektör veritabanını oluştur
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embedding_model)

# FAISS Veritabanını Kaydet
vectorstore.save_local("faiss_index")
print("✅ FAISS veritabanı başarıyla oluşturuldu ve kaydedildi!")
