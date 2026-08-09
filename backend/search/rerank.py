import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))                   # search/  <- ADD THIS LINE
from sentence_transformers import CrossEncoder
from merge import hybrid_search

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

def rerank(query, candidates, top_k=5):
    reranker = get_reranker()
    pairs = [[query, c["text"]] for c in candidates]
    scores = reranker.predict(pairs)

    for c, score in zip(candidates, scores):
        c["rerank_score"] = float(score)

    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]

def search_with_rerank(query, final_k=5, candidate_pool=10):
    candidates = hybrid_search(query, top_k=candidate_pool)
    final_results = rerank(query, candidates, top_k=final_k)
    return final_results

if __name__ == "__main__":
    query = "What causes E-322 and how do I fix it?"
    results = search_with_rerank(query, final_k=3)
    print(f"Query: {query}")
    print(f"Top {len(results)} reranked results:")
    for r in results:
        print(f"\n[Page {r['page_number']}] rerank_score={r['rerank_score']:.4f} (hybrid={r['hybrid_score']:.4f})")
        print(r['text'])   # full text, not [:200] — need to see the whole chunk
        print("=" * 60)