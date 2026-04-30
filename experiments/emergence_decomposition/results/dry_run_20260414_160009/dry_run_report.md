# Dry Run Report — Checkpoint 0

**Generated**: 2026-04-14T23:00:42.975531+00:00
**Run dir**: `dry_run_20260414_160009`
**Group**: baseline only
**Depth**: quick
**Rounds**: 3
**Disciplines (fixed for all groups)**: Physics / Mathematics / Economics / Psychology / Social Sciences / CS / Arts & Humanities

## Sample

- N = 10 (0 ok / 10 failed)

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
- Verdict: **PROCEED (⚠ 10/10 failed)**

## Failures

- `cmp_06`: NameError: name 'names' is not defined
- `cmp_04`: NameError: name 'names' is not defined
- `dec_10`: NameError: name 'names' is not defined
- `dec_02`: NameError: name 'names' is not defined
- `prob_05`: NameError: name 'names' is not defined
- `eval_06`: NameError: name 'names' is not defined
- `cmp_07`: NameError: name 'names' is not defined
- `prob_10`: NameError: name 'names' is not defined
- `cmp_10`: NameError: name 'names' is not defined
- `dec_07`: NameError: name 'names' is not defined

## Per-debate table

| qid | success | duration_s | llm_calls | total_tokens | cost_usd |
|---|---|---|---|---|---|
| cmp_06 | FAIL | 3.05 | 1 | 186 | $0.0000 |
| cmp_04 | FAIL | 2.92 | 1 | 207 | $0.0000 |
| dec_10 | FAIL | 3.26 | 1 | 188 | $0.0000 |
| dec_02 | FAIL | 3.01 | 1 | 198 | $0.0000 |
| prob_05 | FAIL | 2.84 | 1 | 181 | $0.0000 |
| eval_06 | FAIL | 2.45 | 1 | 198 | $0.0000 |
| cmp_07 | FAIL | 2.78 | 1 | 205 | $0.0000 |
| prob_10 | FAIL | 2.67 | 1 | 205 | $0.0000 |
| cmp_10 | FAIL | 2.21 | 1 | 183 | $0.0000 |
| dec_07 | FAIL | 2.59 | 1 | 209 | $0.0000 |

## Next step

If verdict = PROCEED and 0 failures:
- Ken approves → Checkpoint 1 (pilot, 80 debates baseline+A with judge self-consistency)

If verdict = STOP:
- Discuss with Ken: cut runs, cut groups, switch to cheaper model, or adjust depth
