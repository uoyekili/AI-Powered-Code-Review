import re
from dataclasses import dataclass
from urllib.parse import urlparse


GITHUB_URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)/?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GitHubRepoInfo:
    owner: str
    name: str
    url: str


def parse_github_url(url: str) -> GitHubRepoInfo | None:
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    match = GITHUB_URL_PATTERN.match(url)
    if not match:
        parsed = urlparse(url)
        if parsed.netloc.lower() in {"github.com", "www.github.com"}:
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                if repo.endswith(".git"):
                    repo = repo[:-4]
                return GitHubRepoInfo(owner=owner, name=repo, url=f"https://github.com/{owner}/{repo}")
        return None

    owner = match.group("owner")
    repo = match.group("repo")
    if repo.endswith(".git"):
        repo = repo[:-4]

    return GitHubRepoInfo(owner=owner, name=repo, url=f"https://github.com/{owner}/{repo}")
