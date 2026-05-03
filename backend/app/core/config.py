from pathlib import Path

from pydantic_settings import BaseSettings


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    google_api_key: str = ""

    notion_integration_token: str = ""
    notion_notes_database_id: str = ""

    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_api_key: str = ""
    deepseek_model_name: str = "deepseek-chat"

    jwt_secret: str = "dev-secret-change-in-production"

    class Config:
        env_file = (str(ROOT_DIR / ".env"), str(ROOT_DIR / "backend" / ".env"))


settings = Settings()
