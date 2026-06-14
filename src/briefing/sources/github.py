from __future__ import annotations

from datetime import datetime, timezone

import requests

from ..models import SourceItem


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    from os import getenv
    token = getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_github_projects(query: str, per_page: int = 10) -> list[SourceItem]:
    response = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": query, "sort": "stars", "order": "desc", "per_page": per_page},
        headers=_headers(),
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    now = datetime.now(timezone.utc)
    items: list[SourceItem] = []
    for repo in payload.get("items", []):
        updated_at = repo.get("updated_at")
        fresh = False
        freshness_bonus = 0.0
        if updated_at:
            try:
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                age_days = max(0, (now - updated).days)
                freshness_bonus = max(0.0, 30.0 - age_days)
                fresh = age_days <= 7
            except ValueError:
                fresh = False
        title = repo.get("full_name", "unknown repo")
        description = repo.get("description") or ""
        momentum = float(repo.get("stargazers_count", 0)) + freshness_bonus + float(repo.get("forks_count", 0)) * 0.2
        items.append(
            SourceItem(
                title=title,
                url=repo.get("html_url", ""),
                score=momentum,
                published_at=updated_at,
                summary=description,
                source="github",
                metadata={
                    "language": repo.get("language"),
                    "forks": repo.get("forks_count", 0),
                    "fresh": fresh,
                    "momentum": momentum,
                },
            )
        )
    return items
