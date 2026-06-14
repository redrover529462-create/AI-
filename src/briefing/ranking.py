from __future__ import annotations

from datetime import datetime, timezone


def rank_items(items: list[dict]) -> list[dict]:
    def key(item: dict) -> tuple:
        published = item.get("published_at")
        if published:
            try:
                published_score = datetime.fromisoformat(published).timestamp()
            except ValueError:
                published_score = 0.0
        else:
            published_score = 0.0
        return (float(item.get("score", 0)), published_score)

    return sorted(items, key=key, reverse=True)
