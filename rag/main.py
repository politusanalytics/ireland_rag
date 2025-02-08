from flask import Flask, request, jsonify
from loader import load_and_split_pdfs
from vectorstore import create_vectorstore, load_vectorstore
from query import answer_query

app = Flask(__name__)

# FAISS Veritabanını yükle
retriever = load_vectorstore()

@app.route('/query', methods=['POST'])
def query_endpoint():
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Sorgu boş olamaz"}), 400

    # Sorguya yanıt üret
    answer = answer_query(query, retriever)
    return jsonify({"query": query, "answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
