"""Azure OpenAI chat model factory."""

from __future__ import annotations

from langchain_openai import AzureChatOpenAI

from app.config.settings import get_settings


def create_azure_chat_model() -> AzureChatOpenAI:
    settings = get_settings()
    return AzureChatOpenAI(
        api_key=settings.azure_openai_chat_api_key,
        base_url=settings.azure_openai_base_url,
        model=settings.azure_openai_chat_model,
        temperature=0.9,
    )
