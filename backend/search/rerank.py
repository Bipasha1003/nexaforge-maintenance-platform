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
    
    try:
        # Try to use Hugging Face to rerank the best answers
        scores = client.sentence_similarity(query, texts, model=RERANK_MODEL)
        for c, score in zip(candidates, scores):
            c["rerank_score"] = float(score)
            
        ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
        return ranked[:top_k]
        
    except Exception as e:
        # SAFETY NET: If Hugging Face free API fails or refuses the model, 
        # do NOT crash. Just use the original hybrid search scores!
        print(f"[RERANK WARNING] Hugging Face API failed: {e}. Falling back to hybrid scores.")
        for c in candidates:
            # Copy the hybrid score so the rest of the app doesn't break
            c["rerank_score"] = c.get("hybrid_score", 0.0) 
            
        return candidates[:top_k]



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