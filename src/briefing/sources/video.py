from __future__ import annotations

import re
from urllib.parse import urlparse

import requests

from ..models import SourceItem


def fetch_short_video_trends(source_urls: list[str] | None = None) -> list[SourceItem]:
    urls = source_urls or [
        "https://www.douyin.com/",
        "https://www.xiaohongshu.com/",
    ]
    items: list[SourceItem] = []
    for url in urls:
        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            text = response.text
            host = urlparse(url).netloc
            title = "短视频热门内容"
            if "douyin" in host:
                title = "抖音热门内容"
            elif "xiaohongshu" in host:
                title = "小红书热门内容"
            match = re.search(r"href=\"([^\"]+)\"", text)
            resolved_url = url
            if match:
                resolved_url = match.group(1)
            items.append(
                SourceItem(
                    title=title,
                    url=resolved_url,
                    score=70,
                    summary="从公开页面提取的可见链接与页面信号",
                    source="video",
                    metadata={"page_length": len(text)},
                )
            )
        except Exception:
            continue
    return items
