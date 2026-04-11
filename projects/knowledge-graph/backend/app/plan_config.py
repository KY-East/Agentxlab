"""Subscription plan definitions. Adjust prices and limits here."""

from __future__ import annotations

PLAN_CONFIG: dict[str, dict] = {
    "free": {
        "monthly_tokens": 50_000,
        "allowed_models": ["deepseek/deepseek-chat"],
        "price_monthly_cents": 0,
        "price_once_cents": 0,
        "label_en": "Free",
        "label_zh": "免费版",
    },
    "pro": {
        "monthly_tokens": 500_000,
        "allowed_models": [
            "deepseek/deepseek-chat",
            "openai/gpt-4o",
            "anthropic/claude-sonnet-4-20250514",
        ],
        "price_monthly_cents": 999,
        "price_once_cents": 0,
        "label_en": "Pro",
        "label_zh": "专业版",
    },
    "lifetime": {
        "monthly_tokens": 300_000,
        "allowed_models": [
            "deepseek/deepseek-chat",
            "openai/gpt-4o",
            "anthropic/claude-sonnet-4-20250514",
        ],
        "price_monthly_cents": 0,
        "price_once_cents": 9900,
        "label_en": "Lifetime",
        "label_zh": "终身版",
    },
}


def get_plan(name: str) -> dict:
    return PLAN_CONFIG.get(name, PLAN_CONFIG["free"])
