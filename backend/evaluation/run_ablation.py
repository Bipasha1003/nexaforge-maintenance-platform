"""
Ablation study: for every eval question, runs three retrieval stages
side by side and records which chunk each one ranked #1:

    1. keyword_search  — BM25 only
    2. hybrid_search    — BM25 + vector, merged (no rerank)
    3. search_with_rerank — full pipeline: hybrid + LLM rerank

Saves results to evaluation/ablation_results.csv so you can see, per
question, whether reranking actually changed (and hopefully improved)
the top result versus hybrid search alone.

Run from backend/:
    python evaluation/run_ablation.py
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_DIR = os.path.join(BACKEND_DIR, "search")

sys.path.append(BACKEND_DIR)                                  # backend/  (for storage.client etc.)
sys.path.append(SEARCH_DIR)                                    # backend/search/  (merge.py needs this
                                                                 # on the path for its own flat
                                                                 # "from semantic import ..." import)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))    # evaluation/

import pandas as pd

# Flat imports (not "search.X") on purpose — matches how these modules
# import each other internally (e.g. rerank.py does "from merge import
# hybrid_search"), so we stay consistent with the rest of the codebase.
from keyword_search import keyword_search
from merge import hybrid_search
from rerank import search_with_rerank
from eval_questions import EVAL_QUESTIONS


def get_top_source(chunks):
    """Returns 'source p.N' for the top-ranked chunk, or None if empty."""
    if not chunks:
        return None
    top = chunks[0]
    return f"{top['source']} p.{top['page_number']}"


def run_ablation():
    rows = []
    for q in EVAL_QUESTIONS:
        keyword_only = keyword_search(q, top_k=5)
        hybrid_only = hybrid_search(q, top_k=5)
        hybrid_reranked = search_with_rerank(q, final_k=5, candidate_pool=10)

        rows.append({
            "question": q,
            "keyword_top_source": get_top_source(keyword_only),
            "hybrid_top_source": get_top_source(hybrid_only),
            "hybrid_rerank_top_source": get_top_source(hybrid_reranked),
            "rerank_changed_top_result": get_top_source(hybrid_only) != get_top_source(hybrid_reranked),
        })
        print(f"Done: {q[:60]}")

    df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ablation_results.csv")
    df.to_csv(out_path, index=False)

    changed_count = df["rerank_changed_top_result"].sum()
    print(f"\nSaved {len(df)} rows to {out_path}")
    print(f"Rerank changed the top result on {changed_count}/{len(df)} questions.")
    return df


if __name__ == "__main__":
    run_ablation()