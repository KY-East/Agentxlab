# Dry Run Report — Checkpoint 0

**Generated**: 2026-04-16T00:57:34.395248+00:00
**Run dir**: `dry_run_20260415_171016`
**Group**: baseline only
**Depth**: quick
**Rounds**: 3
**Disciplines (fixed for all groups)**: Physics / Mathematics / Economics / Psychology / Social Sciences / CS / Arts & Humanities

## Sample

- N = 3 (3 ok / 0 failed)

## Per-debate cost (USD)

| stat | value |
|---|---|
| mean   | $0.9052 |
| median | $0.8770 |
| p25    | $0.8519 |
| p75    | $0.9444 |
| min    | $0.8269 |
| max    | $1.0118 |

## Per-debate tokens

| stat | value |
|---|---|
| mean   | 323,885 |
| median | 327,752 |
| min    | 312,027 |
| max    | 331,877 |

## Per-debate latency (seconds)

| stat | value |
|---|---|
| mean   | 901.4s |
| median | 892.0s |
| min    | 885.4s |
| max    | 926.7s |

## LLM calls per debate

- mean: 54.0 / median: 54 / range: 54–54

## Extrapolation to full experiment

Full run = 900 debates (6 groups × 50 questions × 3 runs).

- **Point estimate (mean × 900)**: **$814.68**
- **IQR band (p25–p75)**: $766.71 – $849.96

## Threshold check

- Budget threshold: **$500**
- Estimated: **$814.68**
- Verdict: **STOP — consult Ken**

## Per-debate table

| qid | success | duration_s | llm_calls | total_tokens | cost_usd |
|---|---|---|---|---|---|
| cmp_06 | ok | 885.39 | 54 | 312027 | $0.8269 |
| cmp_04 | ok | 892.03 | 54 | 331877 | $0.8770 |
| dec_10 | ok | 926.69 | 54 | 327752 | $1.0118 |

## Next step

If verdict = PROCEED and 0 failures:
- Ken approves → Checkpoint 1 (pilot, 80 debates baseline+A with judge self-consistency)

If verdict = STOP:
- Discuss with Ken: cut runs, cut groups, switch to cheaper model, or adjust depth
