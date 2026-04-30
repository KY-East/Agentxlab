"""KPAX independent LLM client.

Thin litellm wrapper that lets KPAX call LLMs without importing AXL's
`app.services.ai_provider`. This satisfies Ken 2026-04-15 hard rule #6
(`PROJECT.md` §5.1): KPAX must not import AXL Python modules.

Design notes:
- Signature matches `app.services.ai_provider.chat_completion` for the
  subset KPAX actually uses (messages / temperature / max_tokens / model
  / retries). KPAX does NOT use the `user_id` / `db` token-quota path —
  KPAX has its own ledger in `token_ledger.py` that counts wallet tokens,
  not LLM tokens.
- Model default comes from env `KPAX_LLM_MODEL`, fallback
  `deepseek/deepseek-chat` (matches AXL default so KPAX behaves the same
  in dev unless the operator overrides).
- Logging follows `PROJECT.md` §9 AXL log spec: structured via `extra=`.
"""

from __future__ import annotations

import asyncio
import logging
import os

import litellm

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "deepseek/deepseek-chat"


def _resolve_model(model: str | None) -> str:
    if model:
        return model
    return os.getenv("KPAX_LLM_MODEL", _DEFAULT_MODEL)


async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    retries: int = 2,
) -> str:
    """Generic LLM chat call with retry.

    Raises the last exception if all retries are exhausted. Callers should
    decide their own fallback behavior (the three KPAX services have
    `_fallback()` helpers for this).
    """
    chosen = _resolve_model(model)

    last_exc: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            response = await litellm.acompletion(
                model=chosen,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content

            usage = getattr(response, "usage", None)
            logger.info(
                "llm call ok",
                extra={
                    "step": "llm_call_ok",
                    "model": chosen,
                    "attempt": attempt,
                    "tokens_total": getattr(usage, "total_tokens", None),
                    "tokens_in": getattr(usage, "prompt_tokens", None),
                    "tokens_out": getattr(usage, "completion_tokens", None),
                },
            )
            return content
        except Exception as exc:
            last_exc = exc
            if attempt > retries:
                logger.exception(
                    "llm call failed after retries",
                    extra={
                        "step": "llm_call_fail",
                        "model": chosen,
                        "attempts": attempt,
                    },
                )
                raise
            logger.warning(
                "llm call attempt failed, retrying",
                extra={
                    "step": "llm_call_retry",
                    "model": chosen,
                    "attempt": attempt,
                    "error": str(exc),
                },
            )
            await asyncio.sleep(2 * attempt)

    # unreachable — loop either returns or raises
    raise RuntimeError("llm_client retry loop exited unexpectedly") from last_exc
