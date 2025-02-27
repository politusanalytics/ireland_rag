import os
import openai
from dotenv import load_dotenv
from pymongo import MongoClient
import re
import markdown

# .env dosyasını yükle
load_dotenv()

# OpenAI API Anahtarını Al
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ HATA: OPENAI_API_KEY bulunamadı! .env dosyanızı kontrol edin.")

client = openai.OpenAI(api_key=api_key)  # OpenAI istemcisini oluşturduk.

# MongoDB Bağlantısını Kur
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

if not MONGO_URI:
    raise ValueError("❌ HATA: MONGO_URI bulunamadı! .env dosyanızı kontrol edin.")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]  # MongoDB'deki veritabanı adı
collection = db[COLLECTION_NAME]  # MongoDB koleksiyonu


def clean_filename(filename):
    """Normalize filename by removing the path and extension to match MongoDB records."""
    filename = os.path.basename(filename)  # Remove path
    filename = re.sub(r'\.pdf$', '', filename, flags=re.IGNORECASE)  # Remove '.pdf' extension
    return filename

def get_document_links(relevant_docs):
    """Retrieve document links from MongoDB based on FAISS search results, ensuring uniqueness."""
    document_links = []
    unique_sources = set()  # To track unique document names

    print("\n=== 🔍 [DEBUG] FAISS Retrieved Documents ===")
    
    for index, doc in enumerate(relevant_docs):
        raw_file_name = doc.metadata.get("source", "")
        cleaned_file_name = clean_filename(raw_file_name)  # Normalize filename

        # **Skip duplicates**
        if cleaned_file_name in unique_sources:
            continue  # Skip duplicate entries
        
        unique_sources.add(cleaned_file_name)  # Mark this file as seen

        print(f"📄 FAISS Filename: {raw_file_name} → 🌟 Cleaned: {cleaned_file_name}")  # Debugging

        # **Fetch all stored files from MongoDB**
        stored_files = list(collection.find({}, {"file_name": 1, "link": 1}))  
        stored_file_names = [doc["file_name"] for doc in stored_files if "file_name" in doc]

        print(f"📂 [DEBUG] MongoDB'de Kayıtlı Dosyalar: {stored_file_names}")

        # **Check if there's a match in MongoDB**
        db_doc = collection.find_one({
            "file_name": {"$regex": f"^{cleaned_file_name}$", "$options": "i"}  
        })

        if db_doc:
            link = db_doc.get("link", "#")  # Default '#' if no valid link
            file_name = db_doc.get("file_name", "Unknown File")
            print(f"✅ [MATCH] {file_name} → {link}")  # Debugging
            document_links.append(f'<a href="{link}" target="_blank">{link[:60]}...</a>')
        else:
            print(f"❌ [NO MATCH] {cleaned_file_name} not found in MongoDB!")  

    print("=============================================\n")

    return "<br>".join(document_links) if document_links else "📌 <strong>There is no link for this document.</strong>"




from sklearn.metrics.pairwise import cosine_similarity

def compute_text_similarity(query, document_text, embedding_model):
    """Compute cosine similarity between query and document text embeddings."""
    query_embedding = embedding_model.embed_documents([query])[0]
    doc_embedding = embedding_model.embed_documents([document_text])[0]
    return cosine_similarity([query_embedding], [doc_embedding])[0][0]

def answer_query(query, retriever, embedding_model):
    """RAG-based query processing function with similarity filtering."""
    
    # Fetch relevant documents from FAISS
    relevant_docs = retriever.invoke(query)

    # 🚀 DEBUGGING: Print retrieved documents
    print("\n=== 🔍 [DEBUG] RAG Retrieved Documents ===")
    if not relevant_docs:
        print("❌ No documents retrieved by FAISS!\n")
    for i, doc in enumerate(relevant_docs[:5]):  # Show up to 5 sources
        print(f"📄 {i+1}. Document: {doc.page_content[:300]}...")  # First 300 characters
        print(f"   🔗 FAISS Metadata: {doc.metadata}")  # Debugging
    print("=========================\n")

    # ✅ **Check If FAISS Returned No Documents**
    if not relevant_docs:
        return """
        <strong>📌 No relevant documents found.</strong><br>
        Sorry, our knowledge base does not contain an answer to this question.<br>
        However, you can try rephrasing your query or reaching out for additional assistance.
        """

    # ✅ **Filter Out Documents Below Similarity Threshold**
    filtered_docs = []
    filtered_docs_low_sim = []
    for doc in relevant_docs:
        similarity_score = compute_text_similarity(query, doc.page_content, embedding_model)
        print(f"🔍 [DEBUG] Similarity Score: {similarity_score}")  # Debugging
        if similarity_score >= 0.65:  # Highly relevant
            filtered_docs.append(doc)
        elif 0.55 <= similarity_score < 0.65:  # Low relevance
            filtered_docs_low_sim.append(doc)

    # ✅ **Handle No High Similarity Results**
    disclaimer = ""  # Default (no disclaimer)
    
    if not filtered_docs:
        if not filtered_docs_low_sim:
            return """
            <strong>📌 No relevant documents found.</strong><br>
            Sorry, our knowledge base does not contain an answer to this question.<br>
            However, you can try rephrasing your query or reaching out for additional assistance.
            """
        else:
            # If only low-similarity documents exist, use them **with a disclaimer**
            disclaimer = """
            <strong>⚠️ Note:</strong> The following response is based on documents with **low similarity** (0.5 - 0.6).<br>
            The answer might not be fully accurate./n
            """
            filtered_docs = filtered_docs_low_sim  # Use low-similarity docs

    # ✅ **Prepare context from first 3 relevant documents**
    context = "\n".join([doc.page_content for doc in filtered_docs[:3]])

    # ✅ **Fetch document links from MongoDB**
    document_links = get_document_links(filtered_docs)

    # ✅ **Call OpenAI API**
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"}
        ]
    )

    # ✅ **Convert response to HTML**
    answer_text = response.choices[0].message.content
    answer_html = markdown.markdown(answer_text)

    # ✅ **Format final output**
    formatted_response = f"""
    {disclaimer}  <!-- Adds disclaimer if applicable -->

    {answer_html}

    <strong>📄 Source Documents:</strong><br>
    {document_links}
    """

    return formatted_response  # Return as HTML