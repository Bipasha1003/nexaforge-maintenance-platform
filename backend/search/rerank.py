import os
import sys
from huggingface_hub import InferenceClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# search/  <- ADD THIS LINE

from merge import hybrid_search

HF_TOKEN = os.getenv("HF_TOKEN")
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = InferenceClient(token=HF_TOKEN)
    return _client


def rerank(query, candidates, top_k=5):
    client = _get_client()
    texts = [c["text"] for c in candidates]

    # sentence_similarity compares one query against many candidates and
    # returns one score per candidate, in order — exactly the shape a
    # cross-encoder reranker needs. This is my best mapping of your real
    # rerank.py onto HF's hosted API; if this specific call errors on
    # this model, send me the exact error and I'll adjust it.
    scores = client.sentence_similarity(query, texts, model=RERANK_MODEL)

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
        print(r['text'])  # full text, not [:200] — need to see the whole chunk
        print("=" * 60)