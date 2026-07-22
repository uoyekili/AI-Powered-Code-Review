"""LangChain runnable: chunk text → LLMChunkReviewResponse."""

from __future__ import annotations

from langchain_core.runnables import Runnable

from app.llm.prompts.chunk_review import CHUNK_REVIEW_PROMPT
from app.llm.providers.azure_openai import create_azure_chat_model
from app.schemas.chunk_review_schema import LLMChunkReviewResponse


def create_chunk_review_runnable() -> Runnable:
    model = create_azure_chat_model().with_structured_output(LLMChunkReviewResponse)
    return CHUNK_REVIEW_PROMPT | model
