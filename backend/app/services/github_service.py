import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import httpx
from git import Repo

from app.config.settings import get_settings
from app.core.exceptions import CloneRepositoryError
from app.utils.github_url import GitHubRepoInfo

logger = logging.getLogger(__name__)


@dataclass
class GitHubMetadata:
    description: str
    stars: int
    forks: int
    primary_language: str
    last_updated: datetime | None


class GitHubService:
    async def fetch_metadata(self, repo_info: GitHubRepoInfo) -> GitHubMetadata:
        url = f"https://api.github.com/repos/{repo_info.owner}/{repo_info.name}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers={"Accept": "application/vnd.github+json"},
                )
                if response.status_code == 200:
                    data = response.json()
                    updated = data.get("updated_at")
                    return GitHubMetadata(
                        description=data.get("description") or "",
                        stars=data.get("stargazers_count", 0),
                        forks=data.get("forks_count", 0),
                        primary_language=data.get("language") or "Unknown",
                        last_updated=datetime.fromisoformat(updated.replace("Z", "+00:00"))
                        if updated
                        else None,
                    )
        except Exception as exc:
            logger.warning("GitHub API metadata fetch failed: %s", exc)

        return GitHubMetadata(
            description="",
            stars=0,
            forks=0,
            primary_language="Unknown",
            last_updated=None,
        )

    def clone_repository(self, repo_info: GitHubRepoInfo, task_id: str) -> Path:
        settings = get_settings()
        clone_root = Path(settings.clone_dir)
        clone_root.mkdir(parents=True, exist_ok=True)

        target_dir = clone_root / f"{repo_info.owner}_{repo_info.name}_{task_id}"
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)

        clone_url = f"https://github.com/{repo_info.owner}/{repo_info.name}.git"
        try:
            Repo.clone_from(clone_url, target_dir, depth=1)
            return target_dir
        except Exception as exc:
            logger.exception("Failed to clone repository: %s", exc)
            raise CloneRepositoryError(f"Failed to clone repository: {exc}") from exc

    @staticmethod
    def cleanup_clone(path: Path) -> None:
        try:
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        except Exception as exc:
            logger.warning("Failed to cleanup clone at %s: %s", path, exc)
