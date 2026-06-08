# Python Skill — Canonical Example

One complete, real-world example demonstrating all standards.

---

## Async HTTP Client with Retry

**Scenario:** Fetch data from a REST API with retry logic and type-safe response parsing.

```python
import asyncio
import logging
from dataclasses import dataclass

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class Post:
    id: int
    title: str
    body: str
    user_id: int


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
async def fetch_post(client: httpx.AsyncClient, post_id: int) -> Post:
    """Fetch a single post by ID with automatic retry.

    Args:
        client: Shared async HTTP client.
        post_id: The post's numeric identifier.

    Returns:
        A parsed Post dataclass.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses (after retries).
    """
    response = await client.get(f"/posts/{post_id}")
    response.raise_for_status()
    data = response.json()
    return Post(
        id=data["id"],
        title=data["title"],
        body=data["body"],
        user_id=data["userId"],
    )


async def fetch_posts(post_ids: list[int]) -> list[Post | str]:
    """Fetch multiple posts concurrently.

    Args:
        post_ids: IDs to fetch in parallel.

    Returns:
        List of Post objects or error strings for failed fetches.
    """
    base_url = "https://jsonplaceholder.typicode.com"
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        results = await asyncio.gather(
            *(fetch_post(client, pid) for pid in post_ids),
            return_exceptions=True,
        )
    posts: list[Post | str] = []
    for pid, result in zip(post_ids, results):
        if isinstance(result, Exception):
            logger.error("Failed to fetch post %d: %s", pid, result)
            posts.append(f"ERROR:{pid}")
        else:
            posts.append(result)
    return posts


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetched = asyncio.run(fetch_posts([1, 2, 3]))
    for post in fetched:
        print(post)
```

**Dependencies:** `pip install httpx tenacity`

**How it works:**
- `@dataclass` gives a typed, immutable-friendly container without boilerplate.
- Shared `httpx.AsyncClient` reuses the TCP connection pool across concurrent requests.
- `asyncio.gather(..., return_exceptions=True)` collects successes and failures without aborting.
- `@retry` from `tenacity` handles transient failures transparently.
- Logging replaces print() so the caller controls verbosity.
