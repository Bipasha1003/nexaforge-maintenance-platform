import os
import re
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# search/

from merge import hybrid_search
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_thinking(text: str) -> str:
    """openai/gpt-oss-120b is a reasoning model and can prepend
    <think>...</think> scratch reasoning before its real answer, same
    issue documented in pipeline/image_extraction.py for qwen3.6. Strip
    it before trying to parse JSON."""
    return _THINK_BLOCK.sub("", text).strip()

# NOTE: Reranking previously called the Hugging Face free Serverless
# Inference API (cross-encoder/ms-marco-MiniLM-L-6-v2). As of 2026, HF
# routes many community models through third-party "Inference Providers"
# that don't actually host that model, so the call failed 100% of the time
# with an empty-body HTTP error and silently fell back to hybrid scores.
#
# This version reranks using the same Groq LLM already used elsewhere in
# the app (agent/router.py, agent/run.py) — no new dependency, no local
# model to load, safe on Render's free-tier RAM. It asks the LLM to read
# the candidate chunks and return the most relevant ones in order.

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    return _llm


RERANK_PROMPT = """You are ranking search results for a manufacturing maintenance assistant.

Question: {query}

Below are {n} candidate passages, each with an ID. Read them and decide which
are most directly relevant to answering the question.

{passages}

Return ONLY a JSON array of the passage IDs, ordered from MOST relevant to
LEAST relevant. Include at most {top_k} IDs. Example: [3, 1, 5]
Nothing else — no explanation, no markdown."""


def _format_passages(candidates):
    lines = []
    for i, c in enumerate(candidates):
        snippet = c["text"][:500]  # keep prompt size/cost bounded
        lines.append(f"[ID {i}] (page {c['page_number']}, source: {c['source']})\n{snippet}")
    return "\n\n".join(lines)


def _fallback_to_hybrid(candidates, top_k):
    for c in candidates:
        c["rerank_score"] = c.get("hybrid_score", 0.0)
    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]


def rerank(query, candidates, top_k=5):
    if not candidates:
        return []

    try:
        llm = get_llm()
        prompt = RERANK_PROMPT.format(
            query=query,
            n=len(candidates),
            passages=_format_passages(candidates),
            top_k=top_k,
        )
        response = llm.invoke(prompt)
        raw = _strip_thinking(response.content.strip())

        try:
            order = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("[")
            end = raw.rfind("]") + 1
            order = json.loads(raw[start:end]) if start != -1 and end != 0 else None

        if order is None:
            # Couldn't find any JSON array at all — log what the model
            # actually said so this is debuggable instead of a guess.
            print(f"[RERANK DEBUG] Could not find a JSON array in LLM output: {raw!r}")
            raise ValueError("LLM did not return a parseable ranking")

        if order == []:
            # Valid JSON, model just found nothing worth ranking — not an
            # error, just fall back to hybrid order quietly.
            print("[RERANK INFO] LLM returned an empty ranking; using hybrid order.")
            return _fallback_to_hybrid(candidates, top_k)

        ranked = []
        seen = set()
        for idx in order:
            if isinstance(idx, int) and 0 <= idx < len(candidates) and idx not in seen:
                c = candidates[idx]
                # Score by position: first = highest, so downstream code that
                # sorts by rerank_score still behaves correctly.
                c["rerank_score"] = len(order) - len(ranked)
                ranked.append(c)
                seen.add(idx)
            if len(ranked) >= top_k:
                break

        if not ranked:
            raise ValueError("LLM ranking didn't match any valid candidate IDs")

        return ranked

    except Exception as e:
        print(f"[RERANK WARNING] LLM rerank failed: {type(e).__name__}: {e}. Falling back to hybrid scores.")
        return _fallback_to_hybrid(candidates, top_k)


def search_with_rerank(query, final_k=5, candidate_pool=10):
    candidates = hybrid_search(query, top_k=candidate_pool)
    final_results = rerank(query, candidates, top_k=final_k)
    return final_results


if __name__ == "__main__":
    query = "What causes E-322 and how do I fix it?"
    results = search_with_rerank(query, final_k=3)
    print(f"Query: {query}")
    print(f"Top {len(results)} results:")
    for r in results:
        print(f"\n[Page {r['page_number']}] rerank_score={r['rerank_score']} (hybrid={r['hybrid_score']:.4f})")
        print(r['text'])
        print("=" * 60)