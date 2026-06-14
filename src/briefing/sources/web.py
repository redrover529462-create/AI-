from __future__ import annotations

from datetime import datetime, timezone

import requests

from ..models import SourceItem


def _classify_ai_item(title: str, summary: str | None) -> dict[str, float | str]:
    text = f"{title} {summary or ''}".lower()
    if any(keyword in text for keyword in ["model", "模型", "release", "发布", "launch"]):
        category = "模型发布"
    elif any(keyword in text for keyword in ["agent", "tool", "workflow", "app", "assistant", "工具"]):
        category = "Agent/工具"
    elif any(keyword in text for keyword in ["paper", "研究", "论文", "benchmark", "eval"]):
        category = "研究/论文"
    else:
        category = "行业动态"
    strength = 1.0
    if any(keyword in text for keyword in ["openai", "anthropic", "google", "meta", "microsoft"]):
        strength += 1.0
    if any(keyword in text for keyword in ["agent", "model", "模型", "release", "发布"]):
        strength += 1.0
    return {"category": category, "strength": min(3.0, strength)}


def fetch_ai_news(source_urls: list[str] | None = None) -> list[SourceItem]:
    urls = source_urls or ["https://openai.com/news/"]
    items: list[SourceItem] = []
    for url in urls:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            text = response.text
            title = "OpenAI 官方动态" if "OpenAI" in text else "AI 行业动态"
            classification = _classify_ai_item(title, "从公开页面抓取到的最新官方动态")
            items.append(
                SourceItem(
                    title=title,
                    url=url,
                    score=80 + classification["strength"],
                    summary="从公开页面抓取到的最新官方动态",
                    source="ai",
                    metadata={
                        "content_length": len(text),
                        "category": classification["category"],
                        "trend_strength": classification["strength"],
                    },
                )
            )
        except Exception:
            continue
    return items
