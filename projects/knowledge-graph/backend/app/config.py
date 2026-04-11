from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/knowledge_graph"
    cors_origins: list[str] = ["http://localhost:5173"]

    # AI — DeepSeek via LiteLLM
    deepseek_api_key: str = ""
    default_ai_model: str = "deepseek/deepseek-chat"

    # Zep Cloud — Agent Memory & Graph RAG
    zep_api_key: str = ""

    # OpenAlex — Academic Data
    openalex_email: str = ""

    # Auth — Google OAuth + JWT
    google_client_id: str = ""
    jwt_secret: str = "change-me-in-production"

    # SMTP for email verification / password reset
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    app_base_url: str = "http://localhost:5173"

    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""
    stripe_lifetime_price_id: str = ""

    # Crypto payment
    crypto_wallet_address: str = ""
    crypto_wallet_network: str = "TRC-20"

    # Legacy keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
