from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any

import requests

from ..models import SourceItem


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
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
    items: list[SourceItem] = []
    for repo in payload.get("items", []):
        items.append(
            SourceItem(
                title=repo.get("full_name", "unknown repo"),
                url=repo.get("html_url", ""),
                score=float(repo.get("stargazers_count", 0)),
                published_at=repo.get("updated_at"),
                summary=repo.get("description"),
                source="github",
                metadata={"language": repo.get("language"), "forks": repo.get("forks_count", 0)},
            )
        )
    return items
