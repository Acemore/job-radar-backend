from src import gh_manager


async def test_get_github_background_mock(monkeypatch, github_mock_data):
    async def mock_fetch(*arg, **kwarg):
        return github_mock_data

    monkeypatch.setattr("src.gh_manager.get_github_background", mock_fetch)

    result = await gh_manager.get_github_background(owner="test", repo="test")

    assert isinstance(result, dict)
    assert "data" in result
    assert (
        len(
            result.get("data", {})
            .get("repository", {})
            .get("discussions", {})
            .get("nodes", [])
        )
        == 2
    )
