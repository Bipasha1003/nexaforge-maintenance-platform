import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rank_bm25 import BM25Okapi
from storage.client import get_connection

def load_all_chunks():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT chunk_id, page_number, source, text FROM chunks ORDER BY chunk_id")
            rows = cur.fetchall()
    finally:
        conn.close()

    chunks = []
    for row in rows:
        chunks.append({
            "chunk_id": row[0],
            "page_number": row[1],
            "source": row[2],
            "text": row[3]
        })
    return chunks

def build_bm25_index(chunks):
    tokenized = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)
    return bm25

def keyword_search(query, top_k=5):
    chunks = load_all_chunks()
    bm25 = build_bm25_index(chunks)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    results = []
    for chunk, score in scored_chunks[:top_k]:
        results.append({
            "chunk_id": chunk["chunk_id"],
            "page_number": chunk["page_number"],
            "source": chunk["source"],
            "text": chunk["text"],
            "bm25_score": score
        })
    return results

if __name__ == "__main__":
    query = "E-322 coolant pump thermal overload"
    results = keyword_search(query, top_k=3)
    print(f"Query: {query}")
    print(f"Top {len(results)} results:")
    for r in results:
        print(f"\n[Page {r['page_number']}] bm25_score={r['bm25_score']:.4f}")
        print(r['text'][:200])