# Dry Run Report — Checkpoint 0

**Generated**: 2026-04-16T23:05:55.987314+00:00
**Run dir**: `dry_run_20260416_142920`
**Group**: baseline only
**Depth**: quick
**Rounds**: 3
**Disciplines (fixed for all groups)**: Physics / Mathematics / Economics / Psychology / Social Sciences / CS / Arts & Humanities

## Sample

- N = 5 (5 ok / 0 failed)

## Per-debate cost (USD)

| stat | value |
|---|---|
| mean   | $1.0264 |
| median | $0.9879 |
| p25    | $0.9446 |
| p75    | $1.1222 |
| min    | $0.7913 |
| max    | $1.2859 |

## Per-debate tokens

| stat | value |
|---|---|
| mean   | 334,774 |
| median | 332,405 |
| min    | 328,145 |
| max    | 341,544 |

## Per-debate latency (seconds)

| stat | value |
|---|---|
| mean   | 1106.1s |
| median | 1123.9s |
| min    | 1028.9s |
| max    | 1158.3s |

## LLM calls per debate

- mean: 54.0 / median: 54 / range: 54–54

## Extrapolation to full experiment

Full run = 900 debates (6 groups × 50 questions × 3 runs).

- **Point estimate (mean × 900)**: **$923.76**
- **IQR band (p25–p75)**: $850.14 – $1009.98

## Threshold check

- Budget threshold: **$500**
- Estimated: **$923.76**
- Verdict: **STOP — consult Ken**

## Per-debate table

| qid | success | duration_s | llm_calls | total_tokens | cost_usd |
|---|---|---|---|---|---|
| str_03 | ok | 1153.2 | 54 | 341544 | $1.2859 |
| str_04 | ok | 1158.28 | 54 | 340620 | $1.1222 |
| str_07 | ok | 1066.47 | 54 | 328145 | $0.7913 |
| eval_04 | ok | 1028.86 | 54 | 331158 | $0.9879 |
| eval_09 | ok | 1123.86 | 54 | 332405 | $0.9446 |

## Next step

If verdict = PROCEED and 0 failures:
- Ken approves → Checkpoint 1 (pilot, 80 debates baseline+A with judge self-consistency)

If verdict = STOP:
- Discuss with Ken: cut runs, cut groups, switch to cheaper model, or adjust depth
