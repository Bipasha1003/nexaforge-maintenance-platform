"""
Full end-to-end evaluation: runs the WHOLE agent (router -> tool ->
answer generation) for every question in the eval set, and checks
whether it made the correct answer-vs-escalate decision.

Saves results to evaluation/eval_results.csv and prints an overall
"escalation accuracy" score.

Run from backend/:
    python evaluation/run_eval.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # evaluation/

import pandas as pd

from agent.run import run_agent
from eval_questions import EVAL_QUESTIONS, EXPECTED_ESCALATE, EXPECTED_KEYWORDS


def check_answer_correct(question, answer):
    """For questions with ground-truth keywords, returns True only if
    ALL required keywords appear in the answer (case-insensitive).
    Questions with no keywords defined return None (not checked) —
    they still count toward escalation accuracy, just not answer
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
        # Unique session_id per question so agent/state.py's in-memory
        # history doesn't bleed between unrelated eval questions.
        result = run_agent(q, session_id=f"eval_{i}")

        actual_escalate = (result["tool_used"] == "escalate")
        expected_escalate = EXPECTED_ESCALATE.get(q, False)
        escalate_correct = (actual_escalate == expected_escalate)
        answer_correct = check_answer_correct(q, result["answer"])

        rows.append({
            "question": q,
            "answer": result["answer"],
            "sources_used": " | ".join(
                f"{s['source']} p.{s['page']}" for s in result.get("sources", [])
            ),
            "tool_used": result["tool_used"],
            "actual_escalate": actual_escalate,
            "expected_escalate": expected_escalate,
            "escalate_correct": escalate_correct,
            "answer_correct": answer_correct,
        })
        print(f"Done: {q[:60]}  tool={result['tool_used']}  escalate_ok={escalate_correct}  answer_ok={answer_correct}")

    df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_results.csv")
    df.to_csv(out_path, index=False)

    escalate_accuracy = df["escalate_correct"].mean()

    # Answer accuracy only counts questions where we actually defined
    # ground-truth keywords (answer_correct is not None).
    checked = df[df["answer_correct"].notna()]
    answer_accuracy = checked["answer_correct"].mean() if len(checked) > 0 else None

    print(f"\nSaved {len(df)} results to {out_path}")
    print(f"Escalation accuracy: {escalate_accuracy:.1%}  ({df['escalate_correct'].sum()}/{len(df)})")
    if answer_accuracy is not None:
        print(f"Answer accuracy:     {answer_accuracy:.1%}  ({checked['answer_correct'].sum()}/{len(checked)} keyword-checked questions)")
    else:
        print("Answer accuracy:     no questions had EXPECTED_KEYWORDS defined")

    wrong_escalate = df[~df["escalate_correct"]]
    if len(wrong_escalate) > 0:
        print(f"\n{len(wrong_escalate)} question(s) got the wrong escalate decision:")
        for _, row in wrong_escalate.iterrows():
            print(f"  - \"{row['question']}\"  (expected escalate={row['expected_escalate']}, got tool={row['tool_used']})")

    wrong_answers = checked[checked["answer_correct"] == False]
    if len(wrong_answers) > 0:
        print(f"\n{len(wrong_answers)} question(s) had the right tool but a WRONG or incomplete answer:")
        for _, row in wrong_answers.iterrows():
            print(f"  - \"{row['question']}\"")
            print(f"    got: {row['answer'][:150]}")

    return df


if __name__ == "__main__":
    run_full_eval()