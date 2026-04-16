"""Emergence decomposition experiment runner — Checkpoint 0 (dry run, baseline only).

Scope (Simplicity First):
- Only supports baseline group. No A/B/C/D/E yet.
- Runs N debates, captures raw transcripts + token usage + cost + latency.
- Generates dry_run_report.md with extrapolation to 900 full runs.
- Nothing else: no judge, no diversity calc, no dashboard.

Usage:
    python runner.py --n 10 --depth quick

Notes:
- Copies knowledge_graph.db to an isolated experiment DB before running,
  so production AXL data is never touched.
- Monkey-patches litellm.acompletion globally to capture every LLM call
  regardless of which AXL service triggered it (debate_engine / session_memory
  / spark_extractor all count toward total cost).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------- 1. Path + env bootstrap (must run before any app.* import) ----------

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "projects" / "knowledge-graph" / "backend"
EXP_DIR = Path(__file__).resolve().parent
RESULTS_ROOT = EXP_DIR / "results"
SRC_DB = BACKEND_DIR / "knowledge_graph.db"

if not SRC_DB.exists():
    sys.exit(f"FATAL: source DB missing at {SRC_DB}")

# The AXL backend code does `from app.config import settings` which reads .env
# from the current working directory. We chdir into backend so pydantic-settings
# finds it. Production uvicorn loads .env into os.environ via python-dotenv; we
# replicate that manually so litellm (which reads os.environ directly) sees the
# OpenAI / Anthropic / DeepSeek keys.
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

def _load_env_file(path: Path) -> None:
    """Load .env into os.environ. Force-overrides existing vars for the API
    keys we care about, because the parent shell (e.g. Claude Code) may have
    its own ANTHROPIC_API_KEY/OPENAI_API_KEY that is incompatible with litellm.
    """
    if not path.exists():
        return
    FORCE_OVERRIDE = {"DEEPSEEK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if not key:
            continue
        if key in FORCE_OVERRIDE or key not in os.environ:
            os.environ[key] = val

_load_env_file(BACKEND_DIR / ".env")

# ---------- 2. Discipline constants (Checkpoint 0 frozen) ----------

BASELINE_DISCIPLINE_IDS = [94, 1, 4183, 3244, 3396, 1955, 4515]
# Physics, Mathematics, Economics, Psychology, Social Sciences, CS, Arts & Humanities

EXPERIMENT_USER_ID = 1  # ken@klesa.com — existing user, lets quota code path no-op safely

# ---------- 3. Token usage tracker (monkey-patch litellm) ----------

# Fallback pricing (USD per 1M tokens) if litellm's cost calculator doesn't
# know a model. Keeps cmp_04 from reporting $0 when it actually spent money.
_FALLBACK_PRICING = {
    "deepseek": (0.14, 0.28),
    "gpt-5":    (2.50, 10.00),   # gpt-4o tier approximation
    "gpt-4":    (2.50, 10.00),
    "claude-opus": (15.00, 75.00),
    "claude":   (3.00, 15.00),
}
_DEFAULT_FALLBACK = (1.00, 3.00)

def _fallback_cost(model: str | None, pt: int, ct: int) -> float:
    if not model:
        pi, po = _DEFAULT_FALLBACK
    else:
        mlower = model.lower()
        match = next((v for k, v in _FALLBACK_PRICING.items() if k in mlower), _DEFAULT_FALLBACK)
        pi, po = match
    return (pt * pi + ct * po) / 1_000_000

def _compute_cost(model: str | None, response, pt: int, ct: int) -> float:
    """Use litellm.completion_cost when possible, fall back to heuristic table."""
    try:
        import litellm
        cost = litellm.completion_cost(completion_response=response)
        if cost and cost > 0:
            return float(cost)
    except Exception:
        pass
    return _fallback_cost(model, pt, ct)

_usage_log: list[dict] = []

def _install_litellm_tracker() -> None:
    import litellm
    original = litellm.acompletion

    async def tracked(*args, **kwargs):
        start = time.perf_counter()
        response = await original(*args, **kwargs)
        dur = time.perf_counter() - start
        usage = getattr(response, "usage", None)
        pt = getattr(usage, "prompt_tokens", 0) if usage else 0
        ct = getattr(usage, "completion_tokens", 0) if usage else 0
        tt = getattr(usage, "total_tokens", pt + ct) if usage else (pt + ct)
        model = kwargs.get("model")
        _usage_log.append({
            "model": model,
            "prompt_tokens": pt,
            "completion_tokens": ct,
            "total_tokens": tt,
            "cost_usd": _compute_cost(model, response, pt, ct),
            "duration_s": dur,
        })
        return response

    litellm.acompletion = tracked

# ---------- 4. DB setup ----------

def _prepare_experiment_db(run_dir: Path) -> Path:
    exp_db = run_dir / "experiment.db"
    shutil.copy2(SRC_DB, exp_db)
    # Override DATABASE_URL before app.config gets imported downstream.
    os.environ["DATABASE_URL"] = f"sqlite:///{exp_db.as_posix()}"
    return exp_db

# ---------- 5. One debate ----------

async def run_one_debate(question: dict, depth: str, rounds: int, run_dir: Path) -> dict:
    """Run a single baseline debate. Returns metrics dict."""
    # Delayed imports — DATABASE_URL must already be set.
    from app.db import SessionLocal
    from app.models.debate import Debate, DebateAgent
    from app.models.discipline import Discipline
    from app.services.debate_engine import (
        generate_agents, run_round, generate_summary, assign_models_to_agents,
    )

    qid = question["id"]
    qtext = question["text"]

    t_start = time.perf_counter()
    usage_start_idx = len(_usage_log)
    fail_reason: str | None = None
    debate_id: int | None = None
    transcript: dict = {}

    db = SessionLocal()
    try:
        disciplines = (
            db.query(Discipline)
            .filter(Discipline.id.in_(BASELINE_DISCIPLINE_IDS))
            .all()
        )
        if len(disciplines) != len(BASELINE_DISCIPLINE_IDS):
            raise RuntimeError(f"expected {len(BASELINE_DISCIPLINE_IDS)} disciplines, got {len(disciplines)}")

        title_parts = [(d.name_zh or d.name_en) for d in disciplines]
        title = f"[EXP] {qid}: " + " × ".join(title_parts)

        debate = Debate(
            title=title,
            mode="free",
            language="zh",
            depth=depth,
            proposition=qtext,
            status="active",
            created_by=EXPERIMENT_USER_ID,
        )
        debate.disciplines = list(disciplines)
        db.add(debate)
        db.flush()

        agent_specs = await generate_agents(
            disciplines, mode="free", proposition=qtext,
            language="zh", user_id=None, db=db,
        )
        for spec in agent_specs:
            db.add(DebateAgent(debate_id=debate.id, **spec))
        db.flush()

        db.refresh(debate)
        assign_models_to_agents(list(debate.agents), db)
        db.commit()

        debate_id = debate.id

        # Run N rounds.
        for r in range(rounds):
            db.refresh(debate)
            await run_round(debate, db, user_id=None)
            db.commit()

        # Final synthesis.
        db.refresh(debate)
        await generate_summary(debate, db, user_id=None)
        db.commit()

        # Dump full transcript.
        db.refresh(debate)
        transcript = {
            "debate_id": debate.id,
            "title": debate.title,
            "question_id": qid,
            "question_text": qtext,
            "mode": debate.mode,
            "depth": debate.depth,
            "disciplines": [
                {"id": d.id, "name_en": d.name_en, "name_zh": d.name_zh}
                for d in debate.disciplines
            ],
            "agents": [
                {
                    "id": a.id, "name": a.agent_name, "persona": a.persona,
                    "rank": a.rank, "discipline_id": a.discipline_id,
                    "model": a.assigned_model, "system_prompt": a.system_prompt,
                }
                for a in debate.agents
            ],
            "messages": [
                {
                    "id": m.id, "round": m.round_number, "agent_id": m.agent_id,
                    "role": m.role, "content": m.content,
                }
                for m in sorted(debate.messages, key=lambda x: (x.round_number, x.id))
            ],
            "summary": {
                "consensus": debate.summary_consensus,
                "disagreements": debate.summary_disagreements,
                "open_questions": debate.summary_open_questions,
                "directions": debate.summary_directions,
            },
        }

    except Exception as exc:
        fail_reason = f"{type(exc).__name__}: {exc}"
        db.rollback()
    finally:
        db.close()

    duration_s = time.perf_counter() - t_start
    debate_calls = _usage_log[usage_start_idx:]
    tokens_total = sum(u["total_tokens"] for u in debate_calls)
    cost_total = sum(u["cost_usd"] for u in debate_calls)

    metrics = {
        "question_id": qid,
        "debate_id": debate_id,
        "success": fail_reason is None,
        "fail_reason": fail_reason,
        "duration_s": round(duration_s, 2),
        "llm_calls": len(debate_calls),
        "prompt_tokens": sum(u["prompt_tokens"] for u in debate_calls),
        "completion_tokens": sum(u["completion_tokens"] for u in debate_calls),
        "total_tokens": tokens_total,
        "cost_usd": round(cost_total, 4),
        "model_breakdown": _breakdown_by_model(debate_calls),
    }

    # Save raw transcript + per-debate metrics.
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"baseline_{qid}.json").write_text(
        json.dumps({"metrics": metrics, "transcript": transcript}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return metrics

def _breakdown_by_model(calls: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for c in calls:
        m = c["model"] or "unknown"
        bucket = out.setdefault(m, {"calls": 0, "total_tokens": 0, "cost_usd": 0.0})
        bucket["calls"] += 1
        bucket["total_tokens"] += c["total_tokens"]
        bucket["cost_usd"] = round(bucket["cost_usd"] + c["cost_usd"], 4)
    return out

# ---------- 6. Dry-run report generator ----------

def _percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)

def write_dry_run_report(run_dir: Path, all_metrics: list[dict], n_full_runs: int = 900) -> None:
    successes = [m for m in all_metrics if m["success"]]
    failures = [m for m in all_metrics if not m["success"]]
    n, n_ok, n_fail = len(all_metrics), len(successes), len(failures)

    def stats(key: str) -> dict:
        vals = sorted([m[key] for m in successes])
        if not vals:
            return {"mean": 0, "median": 0, "p25": 0, "p75": 0, "min": 0, "max": 0}
        mean = sum(vals) / len(vals)
        return {
            "mean": round(mean, 4),
            "median": round(_percentile(vals, 0.5), 4),
            "p25": round(_percentile(vals, 0.25), 4),
            "p75": round(_percentile(vals, 0.75), 4),
            "min": round(vals[0], 4),
            "max": round(vals[-1], 4),
        }

    cost_stats = stats("cost_usd")
    tok_stats = stats("total_tokens")
    dur_stats = stats("duration_s")
    call_stats = stats("llm_calls")

    # Extrapolation: use mean cost from successes, scale to n_full_runs.
    est_total_cost = cost_stats["mean"] * n_full_runs if n_ok else 0
    est_low = cost_stats["p25"] * n_full_runs if n_ok else 0
    est_high = cost_stats["p75"] * n_full_runs if n_ok else 0

    threshold = 500
    verdict = "PROCEED" if est_total_cost <= threshold else "STOP — consult Ken"
    if n_fail > 0:
        verdict += f" (⚠ {n_fail}/{n} failed)"

    lines = [
        "# Dry Run Report — Checkpoint 0",
        "",
        f"**Generated**: {datetime.now(timezone.utc).isoformat()}",
        f"**Run dir**: `{run_dir.name}`",
        f"**Group**: baseline only",
        f"**Depth**: quick",
        f"**Rounds**: 3",
        f"**Disciplines (fixed for all groups)**: Physics / Mathematics / Economics / Psychology / Social Sciences / CS / Arts & Humanities",
        "",
        "## Sample",
        "",
        f"- N = {n} ({n_ok} ok / {n_fail} failed)",
        "",
        "## Per-debate cost (USD)",
        "",
        f"| stat | value |",
        f"|---|---|",
        f"| mean   | ${cost_stats['mean']:.4f} |",
        f"| median | ${cost_stats['median']:.4f} |",
        f"| p25    | ${cost_stats['p25']:.4f} |",
        f"| p75    | ${cost_stats['p75']:.4f} |",
        f"| min    | ${cost_stats['min']:.4f} |",
        f"| max    | ${cost_stats['max']:.4f} |",
        "",
        "## Per-debate tokens",
        "",
        f"| stat | value |",
        f"|---|---|",
        f"| mean   | {tok_stats['mean']:,.0f} |",
        f"| median | {tok_stats['median']:,.0f} |",
        f"| min    | {tok_stats['min']:,.0f} |",
        f"| max    | {tok_stats['max']:,.0f} |",
        "",
        "## Per-debate latency (seconds)",
        "",
        f"| stat | value |",
        f"|---|---|",
        f"| mean   | {dur_stats['mean']:.1f}s |",
        f"| median | {dur_stats['median']:.1f}s |",
        f"| min    | {dur_stats['min']:.1f}s |",
        f"| max    | {dur_stats['max']:.1f}s |",
        "",
        "## LLM calls per debate",
        "",
        f"- mean: {call_stats['mean']:.1f} / median: {call_stats['median']:.0f} / range: {call_stats['min']:.0f}–{call_stats['max']:.0f}",
        "",
        "## Extrapolation to full experiment",
        "",
        f"Full run = {n_full_runs} debates (6 groups × 50 questions × 3 runs).",
        "",
        f"- **Point estimate (mean × {n_full_runs})**: **${est_total_cost:.2f}**",
        f"- **IQR band (p25–p75)**: ${est_low:.2f} – ${est_high:.2f}",
        "",
        f"## Threshold check",
        "",
        f"- Budget threshold: **${threshold}**",
        f"- Estimated: **${est_total_cost:.2f}**",
        f"- Verdict: **{verdict}**",
        "",
    ]

    if failures:
        lines += [
            "## Failures",
            "",
        ]
        for f in failures:
            lines.append(f"- `{f['question_id']}`: {f['fail_reason']}")
        lines.append("")

    lines += [
        "## Per-debate table",
        "",
        "| qid | success | duration_s | llm_calls | total_tokens | cost_usd |",
        "|---|---|---|---|---|---|",
    ]
    for m in all_metrics:
        lines.append(
            f"| {m['question_id']} | {'ok' if m['success'] else 'FAIL'} | "
            f"{m['duration_s']} | {m['llm_calls']} | {m['total_tokens']} | ${m['cost_usd']:.4f} |"
        )
    lines.append("")

    lines += [
        "## Next step",
        "",
        "If verdict = PROCEED and 0 failures:",
        "- Ken approves → Checkpoint 1 (pilot, 80 debates baseline+A with judge self-consistency)",
        "",
        "If verdict = STOP:",
        "- Discuss with Ken: cut runs, cut groups, switch to cheaper model, or adjust depth",
        "",
    ]

    (run_dir / "dry_run_report.md").write_text("\n".join(lines), encoding="utf-8")

# ---------- 7. Main ----------

async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=10, help="number of debates to run")
    parser.add_argument("--depth", default="quick", choices=["quick", "standard", "deep", "max"])
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--qids", default="", help="comma-separated specific question ids to run (overrides --n and --seed)")
    parser.add_argument("--run-dir-name", default="", help="optional fixed run dir name to append into an existing results dir")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_ROOT / (args.run_dir_name or f"dry_run_{ts}")
    run_dir.mkdir(parents=True, exist_ok=True)

    _prepare_experiment_db(run_dir)
    _install_litellm_tracker()

    # Load questions.
    bench = json.loads((EXP_DIR / "benchmark_questions.json").read_text(encoding="utf-8"))
    questions = bench["questions"]
    if args.qids:
        wanted = [q.strip() for q in args.qids.split(",") if q.strip()]
        by_id = {q["id"]: q for q in questions}
        missing = [qid for qid in wanted if qid not in by_id]
        if missing:
            sys.exit(f"FATAL: qids not in benchmark: {missing}")
        sampled = [by_id[qid] for qid in wanted]
    else:
        random.Random(args.seed).shuffle(questions)
        sampled = questions[: args.n]

    print(f"[dry_run] run_dir: {run_dir}")
    print(f"[dry_run] sampled {len(sampled)} questions (qids={args.qids or 'random seed='+str(args.seed)})")
    for q in sampled:
        print(f"  - {q['id']}: {q['text'][:50]}")

    progress_path = run_dir / "progress.jsonl"
    def _heartbeat(entry: dict) -> None:
        with progress_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    PER_DEBATE_TIMEOUT_S = 2000  # 33 min hard cap per debate
    INTER_DEBATE_SLEEP_S = 65    # cool down for Anthropic minute-level quota

    _heartbeat({"ts": datetime.now(timezone.utc).isoformat(), "event": "run_start", "n": len(sampled)})

    all_metrics: list[dict] = []
    for i, q in enumerate(sampled, start=1):
        print(f"\n[dry_run] ({i}/{len(sampled)}) starting {q['id']}...", flush=True)
        _heartbeat({"ts": datetime.now(timezone.utc).isoformat(), "event": "debate_start", "i": i, "qid": q["id"]})
        t0 = time.perf_counter()
        try:
            m = await asyncio.wait_for(
                run_one_debate(q, depth=args.depth, rounds=args.rounds, run_dir=run_dir),
                timeout=PER_DEBATE_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            m = {
                "question_id": q["id"], "debate_id": None,
                "success": False, "fail_reason": f"TimeoutError: exceeded {PER_DEBATE_TIMEOUT_S}s hard cap",
                "duration_s": round(time.perf_counter() - t0, 2),
                "llm_calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "total_tokens": 0, "cost_usd": 0.0, "model_breakdown": {},
            }
        except Exception as exc:
            m = {
                "question_id": q["id"], "debate_id": None,
                "success": False, "fail_reason": f"{type(exc).__name__}: {exc}",
                "duration_s": round(time.perf_counter() - t0, 2),
                "llm_calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "total_tokens": 0, "cost_usd": 0.0, "model_breakdown": {},
            }
        status = "ok" if m["success"] else f"FAIL ({m['fail_reason']})"
        print(f"[dry_run] ({i}/{len(sampled)}) {q['id']}: {status} "
              f"— {m['duration_s']}s, {m['llm_calls']} calls, "
              f"{m['total_tokens']} tokens, ${m['cost_usd']:.4f}", flush=True)
        _heartbeat({
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": "debate_done", "i": i, "qid": q["id"],
            "success": m["success"], "duration_s": m["duration_s"],
            "total_tokens": m["total_tokens"], "cost_usd": m["cost_usd"],
            "fail_reason": m.get("fail_reason"),
        })
        all_metrics.append(m)
        if i < len(sampled):
            print(f"[dry_run] sleep {INTER_DEBATE_SLEEP_S}s (Anthropic quota cooldown)...", flush=True)
            await asyncio.sleep(INTER_DEBATE_SLEEP_S)

    (run_dir / "cost.json").write_text(
        json.dumps(all_metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    write_dry_run_report(run_dir, all_metrics)

    total_cost = sum(m["cost_usd"] for m in all_metrics if m["success"])
    n_ok = sum(1 for m in all_metrics if m["success"])
    n_fail = len(all_metrics) - n_ok
    print(f"\n[dry_run] done. {n_ok} ok / {n_fail} failed. "
          f"Total cost: ${total_cost:.4f}")
    print(f"[dry_run] report: {run_dir / 'dry_run_report.md'}")

if __name__ == "__main__":
    asyncio.run(main())
