"""Repository cloning and scanning interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import logging
import os
import shutil
from uuid import uuid4

from git import Repo
from github import Github
from github.Repository import Repository

from app.config.settings import get_settings
from app.utils.github_url import parse_github_url

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RepositorySummary:
    """High-level repository scan result."""

    primary_language: str
    file_count: int = 0
    dir_count: int = 0
    total_lines: int = 0


class RepositoryService:
    """Clone and inspect GitHub repositories."""

    def __init__(self, repository_url: str, branch: str) -> None:
        self.repo_info = parse_github_url(repository_url)
        self.repo = self._load_repository()
        self.local_path = None
        self.branch = branch

    def _load_repository(self) -> Repository:
        github = Github()
        repo = github.get_repo(f"{self.repo_info.owner}/{self.repo_info.name}")
        return repo

    def clone_repository(self):
        """
        Clone a GitHub repository.
        """

        settings = get_settings()
        clone_dir = settings.clone_dir

        # Resolve local repository path
        self.local_path = Path(clone_dir) / str(uuid4())
        self.local_path.mkdir(parents=True, exist_ok=True)

        try:
            Repo.clone_from(self.repo.clone_url, self.local_path, branch=self.branch)
            logger.info(f"Repository cloned successfully to {self.local_path}")

        except Exception:
            logger.exception(
                "Failed to clone repository (remote_url=%s, branch=%s)",
                self.repo.clone_url,
                self.branch,
            )
            raise

    def scan_repository(self) -> RepositorySummary:
        """Analyze repository metadata and local structure."""

        if self.local_path is None:
            raise RuntimeError("Repository must be cloned before scanning")

        settings = get_settings()
        allowed_exts = settings.allowed_exts
        ignored_dirs = settings.ignored_dirs
        primary_language = self.repo.language or "Unknown"

        file_count = 0
        dir_count = 0
        total_lines = 0

        for root, directories, filenames in os.walk(self.local_path):
            directories[:] = [
                directory
                for directory in directories
                if directory not in ignored_dirs
            ]
            dir_count += len(directories)

            for filename in filenames:
                path = Path(root) / filename
                if path.suffix.lower() not in allowed_exts:
                    continue

                file_count += 1
                try:
                    with path.open("r", encoding="utf-8", errors="ignore") as f:
                        total_lines += sum(1 for _ in f)
                except OSError:
                    pass

        return RepositorySummary(primary_language, file_count, dir_count, total_lines)

    def cleanup(self) -> None:
        """Remove a cloned repository from disk."""

        if not self.local_path:
            return

        shutil.rmtree(self.local_path, ignore_errors=True)
        self.local_path = None
