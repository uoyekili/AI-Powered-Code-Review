"""Tests for GitHub URL parsing."""

from app.utils.github_url import parse_github_url


def test_parse_valid_github_url() -> None:
    info = parse_github_url("https://github.com/owner/repo")
    assert info is not None
    assert info.owner == "owner"
    assert info.name == "repo"
    assert info.url == "https://github.com/owner/repo"


def test_parse_github_url_with_git_suffix() -> None:
    info = parse_github_url("https://github.com/owner/repo.git")
    assert info is not None
    assert info.name == "repo"


def test_parse_invalid_url() -> None:
    assert parse_github_url("https://gitlab.com/owner/repo") is None
    assert parse_github_url("not-a-url") is None
