# import asyncio

# from app.services.github_service import GitHubMetadata, GitHubService
# from app.utils.github_url import parse_github_url

# REPO_URL = "https://github.com/octocat/Hello-World"


# def test_parse_github_url():
#     info = parse_github_url(REPO_URL)
#     assert info is not None
#     assert info.owner == "octocat"
#     assert info.name == "Hello-World"


# def test_parse_invalid_url():
#     assert parse_github_url("not-a-valid-url") is None


# def test_fetch_metadata_returns_object():
#     info = parse_github_url(REPO_URL)
#     metadata = asyncio.run(GitHubService().fetch_metadata(info))
#     assert isinstance(metadata, GitHubMetadata)


# def test_clone_repository():
#     info = parse_github_url(REPO_URL)
#     clone_path = GitHubService().clone_repository(info, "pytest")
#     assert clone_path.exists()
#     assert any(clone_path.rglob("*"))
