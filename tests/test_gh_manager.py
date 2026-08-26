from sqlalchemy import select

from src import gh_manager
from src.models.candidate_background import CandidateBackgroundModel
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


async def test_save_candidate_background_to_db(
    monkeypatch, github_mock_data, test_db, db_session
):
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

    new_background = CandidateBackgroundModel(
        title=cleaned_title,
        body=cleaned_body,
        comments=comments_data,
    )
    db_session.add(new_background)
    await db_session.flush()

    query = select(CandidateBackgroundModel).where(
        CandidateBackgroundModel.title == cleaned_title
    )
    result = await db_session.execute(query)
    discussion = result.scalar_one_or_none()

    assert discussion is not None

    assert discussion.id is not None
    assert isinstance(discussion.id, int)

    assert discussion.title == cleaned_title
    assert discussion.body == cleaned_body

    assert isinstance(discussion.comments, dict)
    assert isinstance(discussion.comments["nodes"], list)
    assert len(discussion.comments["nodes"]) > 0
    assert discussion.comments == comments_data

    assert "[MASKED_EMAIL]" in discussion.body
    assert discussion.body.count("[MASKED_IP]") == 2
    assert "[MASKED_PHONE]" in discussion.comments["nodes"][0]["body"]
    assert discussion.comments["nodes"][0]["body"].count("[MASKED_PATH]") == 2
