class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidGitHubUrlError(AppError):
    def __init__(self, message: str = "Invalid GitHub repository URL") -> None:
        super().__init__(message, status_code=400)


class ReviewNotFoundError(AppError):
    def __init__(self, task_id: str) -> None:
        super().__init__(f"Review task '{task_id}' not found", status_code=404)


class CloneRepositoryError(AppError):
    def __init__(self, message: str = "Failed to clone repository") -> None:
        super().__init__(message, status_code=422)
