from loader import load_and_split_pdfs
from vectorstore import create_vectorstore

docs = load_and_split_pdfs("./Training Module Files")
create_vectorstore(docs)