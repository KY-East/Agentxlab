# Dry Run Report — Checkpoint 0

**Generated**: 2026-04-14T23:33:53.942414+00:00
**Run dir**: `dry_run_20260414_161227`
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

- `cmp_06`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4WcCD5Tf9vwCqnkzXG7"}
- `cmp_04`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4WtGMZBxHga5sUhX5rU"}
- `dec_10`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4WziPtayn6DgbTNDoYd"}
- `dec_02`: BadGatewayError: litellm.BadGatewayError: AnthropicException BadGatewayError - <html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>cloudflare</center>
</body>
</html>

- `prob_05`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4XBYKDi8h6LY2uBE34T"}
- `eval_06`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4XCGWyrGm9Nt7XtFxF8"}
- `cmp_07`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4XX2Emjvm82X3ahw5V5"}
- `prob_10`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4XkBNp5JvwA2ePq3uXN"}
- `cmp_10`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4XpBEVGyt7w1CF6zT4h"}
- `dec_07`: AuthenticationError: litellm.AuthenticationError: AnthropicException - {"type":"error","error":{"type":"authentication_error","message":"x-api-key header is required"},"request_id":"req_011Ca4YBsUWa61QDPn4dDupg"}

## Per-debate table

| qid | success | duration_s | llm_calls | total_tokens | cost_usd |
|---|---|---|---|---|---|
| cmp_06 | FAIL | 38.97 | 3 | 2207 | $0.0004 |
| cmp_04 | FAIL | 218.04 | 9 | 22050 | $0.0042 |
| dec_10 | FAIL | 87.51 | 5 | 6554 | $0.0013 |
| dec_02 | FAIL | 133.59 | 5 | 9409 | $0.0019 |
| prob_05 | FAIL | 13.26 | 1 | 181 | $0.0000 |
| eval_06 | FAIL | 9.87 | 1 | 198 | $0.0000 |
| cmp_07 | FAIL | 254.52 | 9 | 26245 | $0.0049 |
| prob_10 | FAIL | 178.41 | 7 | 17746 | $0.0034 |
| cmp_10 | FAIL | 54.22 | 3 | 4401 | $0.0009 |
| dec_07 | FAIL | 294.92 | 13 | 31181 | $0.0057 |

## Next step

If verdict = PROCEED and 0 failures:
- Ken approves → Checkpoint 1 (pilot, 80 debates baseline+A with judge self-consistency)

If verdict = STOP:
- Discuss with Ken: cut runs, cut groups, switch to cheaper model, or adjust depth
