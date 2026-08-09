import os
import sys
sys.path.append(os.path.dirname(__file__))
from splitter import chunk_document
from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_chunks(chunks):
    model = get_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False)
    for c, emb in zip(chunks, embeddings):
        c["embedding"] = emb.tolist()
    return chunks

if __name__ == "__main__":
    chunks = chunk_document("sample_pdfs/manual1.pdf")
    chunks = embed_chunks(chunks)
    print(f"Total chunks embedded: {len(chunks)}")
    print(f"Embedding dimension: {len(chunks[0]['embedding'])}")
    print("Sample embedding (first 5 values):", chunks[0]["embedding"][:5])