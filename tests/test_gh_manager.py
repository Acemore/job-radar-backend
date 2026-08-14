import json

import asyncpg

from src import gh_manager
from src.sanitizer import sanitize_text


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


async def test_save_candidate_background_to_db(monkeypatch, github_mock_data, test_db):
    async def mock_fetch(*args, **kwargs):
        return github_mock_data

    monkeypatch.setattr("src.gh_manager.get_github_background", mock_fetch)

    raw_github_background = await gh_manager.get_github_background(
        owner="test",
        repo="test",
    )

    first_discussion = (
        raw_github_background.get("data", {})
        .get("repository", {})
        .get("discussions", {})
        .get("nodes", [])[0]
    )

    cleaned_title = sanitize_text(first_discussion["title"])
    cleaned_body = sanitize_text(first_discussion["body"])

    comments_data = first_discussion.get("comments", {"nodes": []})
    if comments_data.get("nodes"):
        first_comment_body = comments_data["nodes"][0]["body"]
        comments_data["nodes"][0]["body"] = sanitize_text(first_comment_body)
    serialized_comments = json.dumps(comments_data, ensure_ascii=False)

    conn = await asyncpg.connect(test_db)
    await conn.execute(
        "INSERT INTO candidate_background (title, body, comments) VALUES ($1, $2, $3);",
        cleaned_title,
        cleaned_body,
        serialized_comments,
    )
    discussion = await conn.fetchrow(
        "SELECT * FROM candidate_background WHERE title = $1;",
        cleaned_title,
    )
    await conn.close()

    assert discussion is not None

    assert discussion["id"] is not None
    assert isinstance(discussion["id"], int)

    assert discussion["title"] == cleaned_title
    assert discussion["body"] == cleaned_body

    parsed_comments = json.loads(discussion["comments"])
    assert isinstance(parsed_comments, dict)
    assert isinstance(parsed_comments["nodes"], list)
    assert len(parsed_comments["nodes"]) > 0
    assert parsed_comments == comments_data

    assert "[MASKED_EMAIL]" in discussion["body"]
    assert discussion["body"].count("[MASKED_IP]") == 2
    assert "[MASKED_PHONE]" in parsed_comments["nodes"][0]["body"]
    assert parsed_comments["nodes"][0]["body"].count("[MASKED_PATH]") == 2
