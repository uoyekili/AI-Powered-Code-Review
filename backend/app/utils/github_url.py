"""GitHub URL parsing helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

GITHUB_URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)/?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GitHubRepoInfo:
    """Parsed GitHub repository coordinates."""

    owner: str
    name: str


def parse_github_url(url: str) -> GitHubRepoInfo | None:
    """
    Parse a GitHub repository URL.

    Args:
        url: Candidate repository URL.

    Returns:
        Parsed repository info, or None when the URL is invalid.
    """

    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    match = GITHUB_URL_PATTERN.match(url)
    if match:
        owner = match.group("owner")
        repo = match.group("repo")
        if repo.endswith(".git"):
            repo = repo[:-4]
        return GitHubRepoInfo(
            owner=owner,
            name=repo,
        )

    parsed = urlparse(url)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    return GitHubRepoInfo(
        owner=owner,
        name=repo,
    )
