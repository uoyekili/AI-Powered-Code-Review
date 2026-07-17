import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config.settings import get_settings
from app.prompts.code_review import (
    AGGREGATE_REVIEW_PROMPT,
    CODE_REVIEW_SYSTEM_PROMPT,
    FILE_REVIEW_PROMPT,
)

logger = logging.getLogger(__name__)


class LangChainService:
    """Dedicated LangChain service for all LLM interactions."""

    def __init__(self) -> None:
        settings = get_settings()
        self._llm = ChatOpenAI(
            model=settings.azure_openai_chat_model,
            api_key=settings.azure_openai_chat_api_key,
            base_url=settings.azure_openai_base_url,
            temperature=1,
            model_kwargs={"response_format": {"type": "json_object"}},
        )

    async def _chat_json(self, user_prompt: str) -> dict[str, Any]:
        messages = [
            SystemMessage(content=CODE_REVIEW_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        response = await self._llm.ainvoke(messages)
        content = response.content
        if not isinstance(content, str):
            content = str(content or "{}")
        return json.loads(content)

    async def review_file(
        self,
        *,
        owner: str,
        repo: str,
        file_path: str,
        extension: str,
        content: str,
        line_count: int,
    ) -> dict[str, Any]:
        prompt = FILE_REVIEW_PROMPT.format(
            owner=owner,
            repo=repo,
            file_path=file_path,
            extension=extension or "text",
            content=content,
            line_count=line_count,
        )
        try:
            return await self._chat_json(prompt)
        except Exception as exc:
            logger.exception("LangChain file review failed for %s: %s", file_path, exc)
            return {
                "summary": f"Automated review could not be completed for {file_path}.",
                "score": 70,
                "issues": [],
            }

    async def aggregate_review(
        self,
        *,
        owner: str,
        repo: str,
        primary_language: str,
        metadata_summary: str,
        file_summaries: str,
    ) -> dict[str, Any]:
        prompt = AGGREGATE_REVIEW_PROMPT.format(
            owner=owner,
            repo=repo,
            primary_language=primary_language,
            metadata_summary=metadata_summary,
            file_summaries=file_summaries,
        )
        try:
            return await self._chat_json(prompt)
        except Exception as exc:
            logger.exception("LangChain aggregate review failed: %s", exc)
            return {
                "metrics": {
                    "overall_score": 70,
                    "security_score": 70,
                    "performance_score": 70,
                    "maintainability_score": 70,
                    "code_quality_score": 70,
                    "architecture_score": 70,
                },
                "issue_severity": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0,
                },
                "issues_by_category": {
                    "security": 0,
                    "performance": 0,
                    "maintainability": 0,
                    "code_quality": 0,
                    "architecture": 0,
                },
            }
