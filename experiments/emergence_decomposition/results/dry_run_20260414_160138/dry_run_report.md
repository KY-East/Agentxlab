# Dry Run Report — Checkpoint 0

**Generated**: 2026-04-14T23:11:38.828188+00:00
**Run dir**: `dry_run_20260414_160138`
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

- `cmp_06`: AuthenticationError: litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
- `cmp_04`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4W7stDu2A7n63zZG34j"}
- `dec_10`: AuthenticationError: litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
- `dec_02`: AuthenticationError: litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
- `prob_05`: AuthenticationError: litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
- `eval_06`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4WLsifdbLxbPR9WxYRa"}
- `cmp_07`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4WPSBM96S8yQwn99US6"}
- `prob_10`: AuthenticationError: litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
- `cmp_10`: AuthenticationError: litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
- `dec_07`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4WVVyxa7t5AFmMXkvhB"}

## Per-debate table

| qid | success | duration_s | llm_calls | total_tokens | cost_usd |
|---|---|---|---|---|---|
| cmp_06 | FAIL | 9.06 | 1 | 195 | $0.0000 |
| cmp_04 | FAIL | 295.5 | 11 | 23548 | $0.0045 |
| dec_10 | FAIL | 35.36 | 3 | 2139 | $0.0004 |
| dec_02 | FAIL | 91.77 | 5 | 6085 | $0.0012 |
| prob_05 | FAIL | 9.02 | 1 | 181 | $0.0000 |
| eval_06 | FAIL | 40.09 | 3 | 2287 | $0.0005 |
| cmp_07 | FAIL | 34.72 | 3 | 2098 | $0.0004 |
| prob_10 | FAIL | 8.78 | 1 | 205 | $0.0000 |
| cmp_10 | FAIL | 37.02 | 3 | 2272 | $0.0005 |
| dec_07 | FAIL | 36.53 | 3 | 2346 | $0.0005 |

## Next step

If verdict = PROCEED and 0 failures:
- Ken approves → Checkpoint 1 (pilot, 80 debates baseline+A with judge self-consistency)

If verdict = STOP:
- Discuss with Ken: cut runs, cut groups, switch to cheaper model, or adjust depth
