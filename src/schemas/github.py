from pydantic import BaseModel, model_validator


class GithubReplySchema(BaseModel):
    body: str


class GithubCommentSchema(BaseModel):
    body: str
    replies: list[GithubReplySchema]

    @model_validator(mode="before")
    @classmethod
    def unwrap_nodes(cls, data: dict) -> dict:
        if isinstance(data, dict) and "replies" in data:
            if isinstance(data["replies"], dict) and "nodes" in data["replies"]:
                data["replies"] = data["replies"]["nodes"]
        return data


class GithubDiscussionSchema(BaseModel):
    title: str
    body: str
    comments: list[GithubCommentSchema]

    @model_validator(mode="before")
    @classmethod
    def unwrap_nodes(cls, data: dict) -> dict:
        if isinstance(data, dict) and "comments" in data:
            if isinstance(data["comments"], dict) and "nodes" in data["comments"]:
                data["comments"] = data["comments"]["nodes"]
        return data


class GithubGraphQLResponseSchema(BaseModel):
    discussions: list[GithubDiscussionSchema]

    @model_validator(mode="before")
    @classmethod
    def unwrap_graphql_response(cls, data: dict) -> dict:
        if isinstance(data, dict):
            data["discussions"] = (
                data.get("data", {})
                .get("repository", {})
                .get("discussions", [])
                .get("nodes", [])
            )
        return data


if __name__ == "__main__":
    import json
    import os

    file_path = "output.txt"

    if not os.path.exists(file_path):
        print(f"🔴 Validation file not found at: {file_path}")
    else:
        try:
            print(f"🚀 Loading raw GraphQL response from '{file_path}'...")
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.loads(f.read())

            print("⚙️ Initializing Pydantic validation container...")
            validated_response = GithubGraphQLResponseSchema.model_validate(raw_data)

            print(
                f"🟢 Success! Validated discussions count: "
                f"{len(validated_response.discussions)}"
            )

            if validated_response.discussions:
                first_discussion = validated_response.discussions[0]
                print(f"📌 First Discussion Title: {first_discussion.title}")
                print(
                    f"💬 Comments count in first discussion: "
                    f"{len(first_discussion.comments)}"
                )

                if first_discussion.comments:
                    first_comment = first_discussion.comments[0]
                    print(f"  └─ 📝 First Comment Text: {first_comment.body}")
                    print(
                        f"  └─ 🔄 Replies count in this comment: "
                        f"{len(first_comment.replies)}"
                    )

                    if first_comment.replies:
                        first_reply = first_comment.replies[0]
                        print(f"      └─ 🎯 First Reply Text: {first_reply.body}")

        except Exception as e:
            print(f"🔴 Pydantic validation failed: {e}")
