import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.vectorizer import get_model
from storage.client import get_connection

def semantic_search(query, top_k=5):
    model = get_model()
    query_embedding = model.encode(query).tolist()
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT chunk_id, page_number, source, text,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding_str, embedding_str, top_k)
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    results = []
    for row in rows:
        results.append({
            "chunk_id": row[0],
            "page_number": row[1],
            "source": row[2],
            "text": row[3],
            "similarity": row[4]
        })
    return results

if __name__ == "__main__":
    query = "What should I do if the spindle will not start?"
    results = semantic_search(query, top_k=3)
    print(f"Query: {query}")
    print(f"Top {len(results)} results:")
    for r in results:
        print(f"\n[Page {r['page_number']}] similarity={r['similarity']:.4f}")
        print(r['text'][:200])