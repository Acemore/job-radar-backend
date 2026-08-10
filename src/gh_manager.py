import asyncio
import json


async def get_github_background(owner: str, repo: str) -> dict:
    query = """
    query($owner: String!, $repo: String!, $cursor: String) {
        repository(owner: $owner, name: $repo) {
            discussions(first: 10, after: $cursor) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    title
                    body
                    comments(first: 100) {
                        nodes {
                            body
                            replies(first: 50) {
                                nodes {
                                    body
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    flat_query = query.replace("\n", " ").strip()

    all_discussions = []
    has_next_page = True
    discussion_cursor = None

    while has_next_page:
        args = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={flat_query}",
            "-F",
            f"owner={owner}",
            "-F",
            f"repo={repo}",
        ]

        if discussion_cursor:
            args.extend(["-F", f"cursor={discussion_cursor}"])
        else:
            args.extend(["-F", "cursor=null"])

        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(stderr.decode())

        raw_response = stdout.decode()
        response = json.loads(raw_response)

        repository_data = response.get("data", {}).get("repository")
        if not repository_data:
            break

        discussion_data = repository_data.get("discussions", {})
        nodes = discussion_data.get("nodes", [])
        page_info = discussion_data.get("pageInfo", {})

        all_discussions.extend(nodes)
        has_next_page = page_info.get("hasNextPage")
        discussion_cursor = page_info.get("endCursor")

    return {
        "data": {
            "repository": {
                "discussions": {
                    "nodes": all_discussions,
                }
            }
        }
    }


if __name__ == "__main__":

    async def main():
        try:
            print("🚀 Sending asynchronous GraphQL query to GitHub API...")
            data = await get_github_background(
                owner="Acemore",
                repo="job-radar-backend",
            )
            print("🟢 Success! Parsed JSON response from Python memory:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"🔴 Execution failed: {e}")

    asyncio.run(main())
