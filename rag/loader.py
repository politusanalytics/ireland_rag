import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_split_pdfs(folder_path):
    # PDF dosyalarını yükleme
    pdf_loaders = [PyPDFLoader(os.path.join(folder_path, file)) for file in os.listdir(folder_path) if file.endswith(".pdf")]

    # Tüm PDF'leri okuma
    documents = []
    for loader in pdf_loaders:
        documents.extend(loader.load())

    print(f"{len(documents)} doküman yüklendi.")

    # Dokümanları parçalama
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    print(f"{len(docs)} parça doküman oluşturuldu.")
    return docs
