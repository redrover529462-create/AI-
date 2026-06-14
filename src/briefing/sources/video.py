from __future__ import annotations

import os
from datetime import datetime, timezone

import requests

from ..models import SourceItem


def _score_video(text: str, title: str) -> dict[str, float]:
    lower_text = text.lower()
    hook_words = ["揭秘", "教程", "如何", "3分钟", "实测", "对比", "前后", "模板"]
    utility_words = ["教程", "方法", "技巧", "攻略", "步骤", "模板"]
    emotion_words = ["震惊", "离谱", "爆了", "泪目", "太强", "真香"]
    repeatable_words = ["模板", "框架", "公式", "清单", "案例"]
    title_score = sum(1.0 for word in hook_words if word in title or word in text)
    body_score = sum(1.0 for word in utility_words if word in lower_text)
    emotion = sum(1.0 for word in emotion_words if word in title or word in text)
    repeatability = sum(1.0 for word in repeatable_words if word in title or word in text)
    return {
        "hook_strength": min(3.0, title_score),
        "utility": min(3.0, body_score),
        "emotion": min(3.0, emotion),
        "repeatability": min(3.0, repeatability),
        "score": min(100.0, title_score * 20 + body_score * 12 + emotion * 10 + repeatability * 8),
    }


def _normalize_items(payload: object, kind: str) -> list[SourceItem]:
    if isinstance(payload, dict):
        if isinstance(payload.get("data"), list):
            raw_items = payload["data"]
        elif isinstance(payload.get("result"), list):
            raw_items = payload["result"]
        else:
            raw_items = []
    elif isinstance(payload, list):
        raw_items = payload
    else:
        raw_items = []

    items: list[SourceItem] = []
    for index, raw_item in enumerate(raw_items[:10], start=1):
        if not isinstance(raw_item, dict):
            continue
        title = str(
            raw_item.get("word")
            or raw_item.get("title")
            or raw_item.get("name")
            or raw_item.get("keyword")
            or raw_item.get("sentence")
            or "热门内容"
        )
        url = str(
            raw_item.get("url")
            or raw_item.get("share_url")
            or raw_item.get("shareLink")
            or raw_item.get("link")
            or raw_item.get("share_link")
            or raw_item.get("share_url")
            or ""
        )
        if not url:
            url = f"https://www.xiaohongshu.com/search_result?keyword={title}" if kind == "xhs" else f"https://www.douyin.com/search/{title}"
        hot_value = float(raw_item.get("hot_value") or raw_item.get("hotnum") or raw_item.get("score") or 0)
        score_data = _score_video(title, title)
        score = max(score_data["score"], min(100.0, hot_value / 100000))
        items.append(
            SourceItem(
                title=title,
                url=url,
                score=score,
                summary=str(raw_item.get("desc") or raw_item.get("desc_short") or raw_item.get("note_desc") or "热门榜单样本"),
                source=kind,
                metadata={
                    "rank": raw_item.get("position") or index,
                    "hot_value": hot_value,
                    "hook_strength": score_data["hook_strength"],
                    "utility": score_data["utility"],
                    "emotion": score_data["emotion"],
                    "repeatability": score_data["repeatability"],
                    "tag": raw_item.get("tag") or raw_item.get("label") or "",
                },
            )
        )
    return items


def _fetch_json(url: str, headers: dict[str, str] | None = None) -> object:
    response = requests.get(url, timeout=30, headers=headers or {"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.json()


def fetch_short_video_trends(source_feeds: list[dict[str, str]] | None = None, xhs_hot_token: str | None = None) -> list[SourceItem]:
    feeds = source_feeds or [
        {"provider": "douyin_hotlist", "name": "抖音热榜", "url": "https://api.iyuns.com/api/douyinhot"},
        {"provider": "xhs_hot_search", "name": "小红书热搜", "url": "https://api.justoneapi.com/api/xiaohongshu/hot-search/v1", "requires_token": True},
    ]
    items: list[SourceItem] = []
    for feed in feeds:
        provider = feed.get("provider", "")
        feed_url = feed.get("url", "")
        if not feed_url:
            continue
        try:
            if provider == "douyin_hotlist":
                payload = _fetch_json(feed_url)
                items.extend(_normalize_items(payload, "douyin"))
            elif provider == "xhs_hot_search" and xhs_hot_token:
                payload = _fetch_json(
                    f"{feed_url}?token={xhs_hot_token}&pageNum=1&orderBy=premium_engage_num&nd=DAY_7",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                items.extend(_normalize_items(payload, "xhs"))
        except Exception:
            continue
    unique: list[SourceItem] = []
    seen: set[str] = set()
    for item in sorted(items, key=lambda item: item.score, reverse=True):
        key = item.title.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique[:10]
