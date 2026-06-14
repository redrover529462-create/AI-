from __future__ import annotations

from typing import Any

import requests

from ..models import SourceItem


def fetch_ai_news(source_urls: list[str] | None = None) -> list[SourceItem]:
    urls = source_urls or ["https://openai.com/news/"]
    items: list[SourceItem] = []
    for url in urls:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            text = response.text
            title = "OpenAI News"
            if "OpenAI" in text:
                title = "OpenAI 官方动态"
            items.append(
                SourceItem(
                    title=title,
                    url=url,
                    score=80,
                    summary="从公开页面抓取到的最新官方动态",
                    source="ai",
                    metadata={"content_length": len(text)},
                )
            )
        except Exception:
            continue
    return items
