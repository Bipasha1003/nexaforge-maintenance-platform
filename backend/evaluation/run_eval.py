"""
Full end-to-end evaluation: runs the WHOLE agent (router -> tool ->
answer generation) for every question in the eval set, and checks
whether it picked the exact correct tool out of all 7 categories
(search_manual, check_schedule, machine_info, company_info,
log_issue, escalate, out_of_scope).

Saves results to evaluation/eval_results.csv and prints an overall
"routing accuracy" and "answer accuracy" score.

Run from backend/:
    python evaluation/run_eval.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # evaluation/

import pandas as pd

from agent.run import run_agent
from eval_questions import EVAL_QUESTIONS, EXPECTED_TOOL, EXPECTED_KEYWORDS


def check_answer_correct(question, answer):
    """For questions with ground-truth keywords, returns True only if
    ALL required keywords appear in the answer (case-insensitive).
    Questions with no keywords defined return None (not checked) —
    they still count toward routing accuracy, just not answer
    accuracy, since we haven't hand-verified an expected value for
    them yet."""
    keywords = EXPECTED_KEYWORDS.get(question)
    if keywords is None:
        return None
    answer_lower = answer.lower()
    return all(kw.lower() in answer_lower for kw in keywords)


def run_full_eval():
    rows = []
    for i, q in enumerate(EVAL_QUESTIONS):
        expected_tool = EXPECTED_TOOL.get(q, "search_manual")

        try:
            result = run_agent(q, session_id=f"eval_{i}")
        except Exception as e:
            print(f"[EVAL ERROR] \"{q[:60]}\" raised {type(e).__name__}: {e}")
            rows.append({
                "question": q,
                "answer": f"[ERROR] {type(e).__name__}: {e}",
                "sources_used": "",
                "actual_tool": "ERROR",
                "expected_tool": expected_tool,
                "tool_correct": False,
                "answer_correct": None,
            })
            continue

        actual_tool = result["tool_used"]
        tool_correct = (actual_tool == expected_tool)
        answer_correct = check_answer_correct(q, result["answer"])

        rows.append({
            "question": q,
            "answer": result["answer"],
            "sources_used": " | ".join(
                f"{s['source']} p.{s['page']}" for s in result.get("sources", [])
            ),
            "actual_tool": actual_tool,
            "expected_tool": expected_tool,
            "tool_correct": tool_correct,
            "answer_correct": answer_correct,
        })
        print(f"Done: {q[:60]}  tool={actual_tool} (expected {expected_tool})  tool_ok={tool_correct}  answer_ok={answer_correct}")

    df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_results.csv")
    df.to_csv(out_path, index=False)

    routing_accuracy = df["tool_correct"].mean()

    checked = df[df["answer_correct"].notna()]
    answer_accuracy = checked["answer_correct"].mean() if len(checked) > 0 else None

    print(f"\nSaved {len(df)} results to {out_path}")
    print(f"Routing accuracy: {routing_accuracy:.1%}  ({df['tool_correct'].sum()}/{len(df)})")
    if answer_accuracy is not None:
        print(f"Answer accuracy:  {answer_accuracy:.1%}  ({checked['answer_correct'].sum()}/{len(checked)} keyword-checked questions)")
    else:
        print("Answer accuracy:  no questions had EXPECTED_KEYWORDS defined")

    wrong_tool = df[~df["tool_correct"]]
    if len(wrong_tool) > 0:
        print(f"\n{len(wrong_tool)} question(s) got the wrong tool:")
        for _, row in wrong_tool.iterrows():
            print(f"  - \"{row['question']}\"  (expected {row['expected_tool']}, got {row['actual_tool']})")

    wrong_answers = checked[checked["answer_correct"] == False]
    if len(wrong_answers) > 0:
        print(f"\n{len(wrong_answers)} question(s) had the right tool but a WRONG or incomplete answer:")
        for _, row in wrong_answers.iterrows():
            print(f"  - \"{row['question']}\"")
            print(f"    got: {row['answer'][:150]}")

    return df


if __name__ == "__main__":
    run_full_eval()