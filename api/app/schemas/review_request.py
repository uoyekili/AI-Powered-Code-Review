"""Request and acceptance response schemas for starting a review."""

from __future__ import annotations

from pydantic import Field, field_validator

from app.schemas.common import CamelModel


class SubmitReviewRequest(CamelModel):
    """Payload for creating a new review task."""

    repository_url: str = Field(..., min_length=1)
    branch: str = Field(..., min_length=1, max_length=255)

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, value: str) -> str:
        """Validate a conservative Git branch/ref name accepted by the MVP."""

        branch = value.strip()
        forbidden_characters = set("~^:?*[\\")
        if (
            not branch
            or branch.startswith(("-", ".", "/"))
            or branch.endswith((".", "/"))
            or ".." in branch
            or "//" in branch
            or "@{" in branch
            or any(character.isspace() or character in forbidden_characters for character in branch)
        ):
            raise ValueError("must be a valid Git branch name")
        return branch


class SubmitReviewResponse(CamelModel):
    """Response returned after a review task is accepted."""

    review_id: str
