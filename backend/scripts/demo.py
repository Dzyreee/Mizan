"""CLI demo of the Phase 2 pipeline — prints the agent trace + final answer.

Usage:
    .venv/bin/python scripts/demo.py "توفيت امرأة وتركت زوجاً وأماً وأباً وتركتها 90000 ريال"
    .venv/bin/python scripts/demo.py --llm-only "<tricky 'awl case>"   # ablation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.orchestrator import solve  # noqa: E402

DEFAULT_Q = "توفي رجل وترك زوجة وابنين وبنتاً، والتركة 120000 ريال"


def main() -> None:
    args = sys.argv[1:]
    verify = "--llm-only" not in args
    args = [a for a in args if a != "--llm-only"]
    question = args[0] if args else DEFAULT_Q

    print(f"\nQ: {question}")
    print(f"mode: {'FULL (verified)' if verify else 'LLM-ONLY (ablation)'}")
    answer, trace = solve(question, verify_pipeline=verify)
    print(trace.render())

    print("\n┌─ ANSWER " + "─" * 55)
    if answer["mode"] == "llm_only":
        print(f"│ ⚠️  {answer['warning']}")
        ls = answer["llm_shares"]
        if ls.get("blocked"):
            print("│ LLM call blocked:", ls["detail"])
        elif ls.get("parsed"):
            print("│ LLM-stated shares:", ls["parsed"].get("shares"))
        else:
            print("│ LLM prose answer:", (ls.get("raw") or "")[:240].replace("\n", " "))
    else:
        flag = "✅ VERIFIED" if answer["verified"] else "⚠️  NOT VERIFIED"
        print(f"│ {flag} — {answer['verdict']}  (kind: {answer['distribution_kind']})")
        for s in answer["shares"]:
            who = s["heir"] if s["count"] == 1 else f"{s['count']}x {s['heir']}"
            print(f"│   {who:<14} {s['ratio']:>7}  =  {s['amount_total']:>12,.2f} {s['currency']}")
        if not answer["verification"]["agree"]:
            print("│ issues:", answer["verification"]["issues"])
        print("│ ruling:", (answer["ruling"][:160] + "…") if answer["ruling"] else "—")
    print("└" + "─" * 64)


if __name__ == "__main__":
    main()
