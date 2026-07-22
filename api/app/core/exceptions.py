"""Application-level exceptions."""


class AppError(Exception):
    """Base application error with an HTTP status code."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidGitHubUrlError(AppError):
    """Raised when a repository URL is not a valid GitHub URL."""

    def __init__(self, message: str = "Invalid GitHub repository URL") -> None:
        super().__init__(message, status_code=400)


class ReviewNotFoundError(AppError):
    """Raised when a review task cannot be found."""

    def __init__(self, task_id: str) -> None:
        super().__init__(f"Review task '{task_id}' not found", status_code=404)
