import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic import semantic_search
from keyword_search import keyword_search

def normalize_scores(results, score_key):
    if not results:
        return results
    scores = [r[score_key] for r in results]
    min_s, max_s = min(scores), max(scores)
    range_s = max_s - min_s
    for r in results:
        if range_s == 0:
            r["normalized_score"] = 1.0 if max_s > 0 else 0.0
        else:
            r["normalized_score"] = (r[score_key] - min_s) / range_s
    return results

def hybrid_search(query, top_k=5, vector_weight=0.5, keyword_weight=0.5, pool_size=15):
    vector_results = semantic_search(query, top_k=pool_size)
    keyword_results = keyword_search(query, top_k=pool_size)

    vector_results = normalize_scores(vector_results, "similarity")
    keyword_results = normalize_scores(keyword_results, "bm25_score")

    combined = {}
    for r in vector_results:
        combined[r["chunk_id"]] = {
            "chunk_id": r["chunk_id"],
            "page_number": r["page_number"],
            "source": r["source"],
            "text": r["text"],
            "vector_score": r["normalized_score"],
            "keyword_score": 0.0
        }
    for r in keyword_results:
        if r["chunk_id"] in combined:
            combined[r["chunk_id"]]["keyword_score"] = r["normalized_score"]
        else:
            combined[r["chunk_id"]] = {
                "chunk_id": r["chunk_id"],
                "page_number": r["page_number"],
                "source": r["source"],
                "text": r["text"],
                "vector_score": 0.0,
                "keyword_score": r["normalized_score"]
            }

    for c in combined.values():
        c["hybrid_score"] = (vector_weight * c["vector_score"]) + (keyword_weight * c["keyword_score"])

    ranked = sorted(combined.values(), key=lambda x: x["hybrid_score"], reverse=True)
    return ranked[:top_k]

if __name__ == "__main__":
    query = "What causes E-322 and how do I fix it?"

    print("--- Raw vector_results (before merge) ---")
    v_results = semantic_search(query, top_k=5)
    for r in v_results:
        print(f"[Page {r['page_number']}] similarity={r['similarity']:.4f} | {r['text'][:80]}")

    print("\n--- Raw keyword_results (before merge) ---")
    k_results = keyword_search(query, top_k=5)
    for r in k_results:
        print(f"[Page {r['page_number']}] bm25_score={r['bm25_score']:.4f} | {r['text'][:80]}")

    print("\n--- Hybrid merged ---")
    results = hybrid_search(query, top_k=3)
    for r in results:
        print(f"\n[Page {r['page_number']}] hybrid={r['hybrid_score']:.4f} (vector={r['vector_score']:.4f}, keyword={r['keyword_score']:.4f})")
        print(r['text'][:200])