from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

import requests

from ..models import SourceItem


def _score_video(text: str, title: str, url: str) -> dict[str, float]:
    lower_text = text.lower()
    hook_words = ["揭秘", "教程", "如何", "3分钟", "实测", "对比", "前后", "模板"]
    utility_words = ["教程", "方法", "技巧", "攻略", "步骤", "模板"]
    emotion_words = ["震惊", "离谱", "爆了", "泪目", "太强", "真香"]
    repeatable_words = ["模板", "框架", "公式", "清单", "案例"]
    title_score = 0.0
    body_score = 0.0
    for word in hook_words:
        if word in title or word in text:
            title_score += 1.0
    for word in utility_words:
        if word in lower_text:
            body_score += 1.0
    emotion = sum(1.0 for word in emotion_words if word in title or word in text)
    repeatability = sum(1.0 for word in repeatable_words if word in title or word in text)
    return {
        "hook_strength": min(3.0, title_score),
        "utility": min(3.0, body_score),
        "emotion": min(3.0, emotion),
        "repeatability": min(3.0, repeatability),
        "score": min(100.0, title_score * 20 + body_score * 12 + emotion * 10 + repeatability * 8),
    }


def _fetch_feed(url: str) -> tuple[str, str]:
    response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.text, response.url


def fetch_short_video_trends(source_feeds: list[dict[str, str]] | None = None) -> list[SourceItem]:
    feeds = source_feeds or [
        {"name": "douyin", "url": "https://www.iesdouyin.com/share/video/"},
        {"name": "xiaohongshu", "url": "https://www.xiaohongshu.com/explore"},
    ]
    items: list[SourceItem] = []
    for feed in feeds:
        feed_name = feed.get("name", "video")
        feed_url = feed.get("url", "")
        if not feed_url:
            continue
        try:
            text, final_url = _fetch_feed(feed_url)
            host = urlparse(final_url).netloc
            title = f"{feed_name} 热门内容"
            if "douyin" in host:
                title = "抖音热门内容"
            elif "xiaohongshu" in host:
                title = "小红书热门内容"
            score_data = _score_video(text, title, final_url)
            items.append(
                SourceItem(
                    title=title,
                    url=final_url,
                    score=score_data["score"],
                    summary="从公开榜单/搜索页抓取到的热门样本",
                    source="video",
                    metadata={
                        "page_length": len(text),
                        "hook_strength": score_data["hook_strength"],
                        "utility": score_data["utility"],
                        "emotion": score_data["emotion"],
                        "repeatability": score_data["repeatability"],
                        "feed_name": feed_name,
                    },
                )
            )
        except Exception:
            continue
    return items
