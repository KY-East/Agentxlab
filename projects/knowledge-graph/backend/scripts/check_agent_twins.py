"""P0 验证工具：同学科双 agent 雷同 + 变笨监控指标（一体化）。

用法：
    python scripts/check_agent_twins.py [debate_id]
    python scripts/check_agent_twins.py 10 --compare 11   # 改前 10 vs 改后 11

输出：
1. D1 相似度指标 —— 同学科 Prof vs Assoc 每轮配对
   - 字数差百分比（目标 ≥ 15%）
   - 开头 200 字 ROUGE-L（目标 < 0.40）
   - Jaccard (字符 3-gram)
   - 开头 100 字是否一字不差（硬告警）
2. D2 变笨监控三轴（全辩论聚合）
   - 变短：平均每条发言字数（警戒线 < 1500 = 下降 >40%）
   - 变浅：平均每条的 heading 数 + 引用条数（警戒线降 >50%）
   - 变平：sparks 总数 + moderator 互攻点数（暂估）

决策门判据详见 notes/research/agent-twin-fix-decision-gate.md D1/D2。
"""
import argparse
import re
import sqlite3
import sys
import io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def char_ngrams(text: str, n: int = 3) -> set[str]:
    text = re.sub(r"\s+", "", text)
    return {text[i:i + n] for i in range(len(text) - n + 1)} if len(text) >= n else set()


def jaccard(a: str, b: str, n: int = 3) -> float:
    ga, gb = char_ngrams(a, n), char_ngrams(b, n)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def rouge_l(a: str, b: str) -> float:
    """Char-level LCS-based ROUGE-L (F1) over first 200 chars."""
    a, b = a[:200], b[:200]
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0.0
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs = dp[m][n]
    if lcs == 0:
        return 0.0
    p, r = lcs / n, lcs / m
    return 2 * p * r / (p + r)


def prefix_identical(a: str, b: str, n: int = 100) -> bool:
    """Check if the first n chars are character-for-character identical."""
    return len(a) >= n and len(b) >= n and a[:n] == b[:n]


def count_headings(text: str) -> int:
    """Count markdown headings + bold-line starts."""
    return sum(
        1 for line in text.split("\n")
        if line.strip().startswith("#") or re.match(r"^\s*\*\*[^*]", line)
    )


def count_citations(text: str) -> int:
    """Count author-year-ish citation patterns."""
    return len(re.findall(r"[A-Z][a-z]+\s*(?:et al\.?\s*)?\(?\d{4}\)?", text))


def analyze_debate(did: int, db_path: str = "knowledge_graph.db") -> dict:
    c = sqlite3.connect(db_path)

    agents = c.execute("""
        SELECT id, agent_name, discipline_id, persona, rank, assigned_model
        FROM debate_agents WHERE debate_id=? AND persona != 'moderator'
        ORDER BY discipline_id, sort_order
    """, (did,)).fetchall()
    if not agents:
        return {"error": f"Debate {did} has no non-moderator agents"}

    by_disc: dict[int, list] = {}
    for a in agents:
        by_disc.setdefault(a[2], []).append(a)

    # D1: twin similarity per discipline per round
    d1_rows = []
    for disc_id, pair in by_disc.items():
        prof = next((a for a in pair if a[4] == "professor"), None)
        assoc = next((a for a in pair if a[4] in ("associate", "assistant")), None)
        if not (prof and assoc):
            continue
        for rnd in (1, 2, 3):
            pm = c.execute(
                "SELECT content FROM debate_messages WHERE debate_id=? AND agent_id=? AND round_number=?",
                (did, prof[0], rnd),
            ).fetchone()
            am = c.execute(
                "SELECT content FROM debate_messages WHERE debate_id=? AND agent_id=? AND round_number=?",
                (did, assoc[0], rnd),
            ).fetchone()
            if not (pm and am):
                continue
            p_text, a_text = pm[0], am[0]
            p_len, a_len = len(p_text), len(a_text)
            len_diff = abs(p_len - a_len) / max(p_len, a_len)
            rouge = rouge_l(p_text, a_text)
            jac = jaccard(p_text, a_text)
            prefix_twin = prefix_identical(p_text, a_text, 100)
            d1_rows.append({
                "disc_id": disc_id, "round": rnd,
                "prof_model": prof[5], "assoc_model": assoc[5],
                "p_len": p_len, "a_len": a_len,
                "len_diff_pct": len_diff * 100,
                "rouge_l_200": rouge,
                "jaccard_3gram": jac,
                "prefix_100_identical": prefix_twin,
            })

    # D2: dumb monitoring per debate
    msgs = c.execute("""
        SELECT content FROM debate_messages
        WHERE debate_id=? AND role='agent'
        AND agent_id IN (SELECT id FROM debate_agents WHERE debate_id=? AND persona!='moderator')
    """, (did, did)).fetchall()
    agent_contents = [m[0] for m in msgs]
    n_msgs = len(agent_contents)
    avg_len = sum(len(x) for x in agent_contents) / n_msgs if n_msgs else 0
    avg_headings = sum(count_headings(x) for x in agent_contents) / n_msgs if n_msgs else 0
    avg_citations = sum(count_citations(x) for x in agent_contents) / n_msgs if n_msgs else 0
    n_sparks = c.execute(
        "SELECT COUNT(*) FROM sparks WHERE debate_id=?", (did,)
    ).fetchone()[0] if _has_sparks(c) else None

    return {
        "debate_id": did,
        "d1_rows": d1_rows,
        "d2": {
            "n_agent_msgs": n_msgs,
            "avg_len_chars": round(avg_len),
            "avg_headings": round(avg_headings, 1),
            "avg_citations": round(avg_citations, 1),
            "n_sparks": n_sparks,
        },
    }


def _has_sparks(c: sqlite3.Connection) -> bool:
    return bool(c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='sparks'"
    ).fetchone())


def print_report(result: dict, label: str = "") -> None:
    if "error" in result:
        print(f"ERROR: {result['error']}")
        return
    did = result["debate_id"]
    head = f"Debate #{did}" + (f" ({label})" if label else "")
    print(f"\n{'=' * 80}\n{head}\n{'=' * 80}")

    print("\n--- D1 同学科 Prof vs Assoc 相似度（越低越好）---")
    print(f"{'disc':>4}  {'rnd':>3}  {'prof_model':<25} {'assoc_model':<25} "
          f"{'len_diff%':>9} {'ROUGE-L':>8} {'Jaccard':>8} {'identical':>10}")
    for r in result["d1_rows"]:
        warn = "⚠️" if r["prefix_100_identical"] else (
            "⚠" if r["len_diff_pct"] < 15 or r["rouge_l_200"] > 0.40 else "✓"
        )
        print(
            f"{r['disc_id']:>4}  r{r['round']}  {str(r['prof_model'])[:24]:<25} "
            f"{str(r['assoc_model'])[:24]:<25} {r['len_diff_pct']:>8.1f}% "
            f"{r['rouge_l_200']:>7.3f} {r['jaccard_3gram']:>7.3f} "
            f"{'YES'if r['prefix_100_identical'] else 'no':>10}  {warn}"
        )

    print("\nD1 门槛判定（目标：len_diff≥15%, ROUGE<0.40, 开头非一字不差）:")
    d1 = result["d1_rows"]
    pass_count = sum(
        1 for r in d1
        if r["len_diff_pct"] >= 15 and r["rouge_l_200"] < 0.40 and not r["prefix_100_identical"]
    )
    print(f"  通过: {pass_count}/{len(d1)} pair-rounds")

    d2 = result["d2"]
    print(f"\n--- D2 变笨监控三轴 ---")
    print(f"  n_agent_msgs: {d2['n_agent_msgs']}")
    print(f"  avg_len_chars:  {d2['avg_len_chars']}  (基线约 2500，警戒 < 1500)")
    print(f"  avg_headings:   {d2['avg_headings']}  (基线约 4-6，警戒 < 2)")
    print(f"  avg_citations:  {d2['avg_citations']}")
    print(f"  n_sparks:       {d2['n_sparks']}  (基线约 25，警戒 < 12)")


def print_compare(before: dict, after: dict) -> None:
    print(f"\n{'=' * 80}\n对比：Debate #{before['debate_id']} (改前) vs #{after['debate_id']} (改后)\n{'=' * 80}")
    for metric in ("avg_len_chars", "avg_headings", "avg_citations", "n_sparks"):
        b, a = before["d2"][metric], after["d2"][metric]
        if b is None or a is None:
            continue
        delta = (a - b) / b * 100 if b else 0
        arrow = "↓" if delta < 0 else "↑"
        warn = "⚠变笨" if delta < -40 else ("✓" if -10 <= delta <= 10 else "")
        print(f"  {metric:20s}  {b:>6} → {a:>6}  {arrow}{abs(delta):>5.1f}%  {warn}")

    # D1 aggregate: 平均 ROUGE-L and 平均 len_diff
    b_rouge = sum(r["rouge_l_200"] for r in before["d1_rows"]) / len(before["d1_rows"]) if before["d1_rows"] else 0
    a_rouge = sum(r["rouge_l_200"] for r in after["d1_rows"]) / len(after["d1_rows"]) if after["d1_rows"] else 0
    b_ldiff = sum(r["len_diff_pct"] for r in before["d1_rows"]) / len(before["d1_rows"]) if before["d1_rows"] else 0
    a_ldiff = sum(r["len_diff_pct"] for r in after["d1_rows"]) / len(after["d1_rows"]) if after["d1_rows"] else 0
    print(f"\n  D1 平均 ROUGE-L:     {b_rouge:.3f} → {a_rouge:.3f}")
    print(f"  D1 平均 len_diff%:   {b_ldiff:.1f}% → {a_ldiff:.1f}%")
    b_identical = sum(1 for r in before["d1_rows"] if r["prefix_100_identical"])
    a_identical = sum(1 for r in after["d1_rows"] if r["prefix_100_identical"])
    print(f"  D1 开头一字不差 pairs: {b_identical} → {a_identical}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("debate_id", type=int, nargs="?", default=10)
    ap.add_argument("--compare", type=int, help="compare to another debate")
    ap.add_argument("--db", default="knowledge_graph.db")
    args = ap.parse_args()

    result = analyze_debate(args.debate_id, args.db)
    print_report(result, "baseline" if args.compare else "")

    if args.compare is not None:
        after = analyze_debate(args.compare, args.db)
        print_report(after, "after G+F")
        print_compare(result, after)


if __name__ == "__main__":
    main()
