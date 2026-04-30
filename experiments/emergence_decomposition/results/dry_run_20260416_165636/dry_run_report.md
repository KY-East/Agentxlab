# Dry Run Report — Checkpoint 0

**Generated**: 2026-04-17T00:29:59.295408+00:00
**Run dir**: `dry_run_20260416_165636`
**Group**: baseline only
**Depth**: quick
**Rounds**: 3
**Disciplines (fixed for all groups)**: Physics / Mathematics / Economics / Psychology / Social Sciences / CS / Arts & Humanities

## Sample

- N = 1 (0 ok / 1 failed)

## Per-debate cost (USD)

| stat | value |
|---|---|
| mean   | $0.0000 |
| median | $0.0000 |
| p25    | $0.0000 |
| p75    | $0.0000 |
| min    | $0.0000 |
| max    | $0.0000 |

## Per-debate tokens

| stat | value |
|---|---|
| mean   | 0 |
| median | 0 |
| min    | 0 |
| max    | 0 |

## Per-debate latency (seconds)

| stat | value |
|---|---|
| mean   | 0.0s |
| median | 0.0s |
| min    | 0.0s |
| max    | 0.0s |

## LLM calls per debate

- mean: 0.0 / median: 0 / range: 0–0

## Extrapolation to full experiment

Full run = 900 debates (6 groups × 50 questions × 3 runs).

- **Point estimate (mean × 900)**: **$0.00**
- **IQR band (p25–p75)**: $0.00 – $0.00

## Threshold check

- Budget threshold: **$500**
- Estimated: **$0.00**
- Verdict: **PROCEED (⚠ 1/1 failed)**

## Failures

- `meta_01`: TimeoutError: exceeded 2000s hard cap

## Per-debate table

| qid | success | duration_s | llm_calls | total_tokens | cost_usd |
|---|---|---|---|---|---|
| meta_01 | FAIL | 2000.0 | 0 | 0 | $0.0000 |

## Next step

If verdict = PROCEED and 0 failures:
- Ken approves → Checkpoint 1 (pilot, 80 debates baseline+A with judge self-consistency)

If verdict = STOP:
- Discuss with Ken: cut runs, cut groups, switch to cheaper model, or adjust depth
