from __future__ import annotations

from xml.etree import ElementTree as ET

import requests
from xml.etree.ElementTree import ParseError

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
    if any(keyword in text for keyword in ["openai", "anthropic", "google", "meta", "microsoft", "hugging face"]):
        strength += 1.0
    if any(keyword in text for keyword in ["agent", "model", "模型", "release", "发布", "gemma", "olmo"]):
        strength += 1.0
    return {"category": category, "strength": min(3.0, strength)}


def _parse_rss_items(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, str]] = []
    for item in root.findall(".//item")[:10]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or item.findtext("summary") or "").strip()
        pub_date = (item.findtext("pubDate") or item.findtext("date") or "").strip()
        if title or link:
            items.append({"title": title, "link": link, "description": description, "pubDate": pub_date})
    if items:
        return items
    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:10]:
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link = ""
        link_node = entry.find("{http://www.w3.org/2005/Atom}link")
        if link_node is not None:
            link = (link_node.attrib.get("href") or "").strip()
        summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
        updated = (entry.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
        if title or link:
            items.append({"title": title, "link": link, "description": summary, "pubDate": updated})
    return items


def fetch_ai_news(source_urls: list[str] | None = None) -> list[SourceItem]:
    urls = source_urls or [
        "https://aihot.virxact.com/feed.xml",
        "https://aihot.virxact.com/feed/daily.xml",
        "https://aihot.virxact.com/feed/all.xml",
    ]
    items: list[SourceItem] = []
    for url in urls:
        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            try:
                raw_items = _parse_rss_items(response.text)
            except ParseError:
                raw_items = []
            if not raw_items and response.text.strip():
                text = response.text.strip()
                raw_items = [{"title": text[:60], "link": url, "description": text[:240], "pubDate": ""}]
            for raw_item in raw_items[:4]:
                title = raw_item.get("title") or "AI 行业动态"
                summary = raw_item.get("description") or "来自公开 RSS 的最新 AI 动态"
                classification = _classify_ai_item(title, summary)
                items.append(
                    SourceItem(
                        title=title,
                        url=raw_item.get("link") or url,
                        published_at=raw_item.get("pubDate") or None,
                        score=80 + classification["strength"],
                        summary=summary,
                        source="ai",
                        metadata={
                            "content_length": len(response.text),
                            "category": classification["category"],
                            "trend_strength": classification["strength"],
                            "feed": url,
                        },
                    )
                )
        except Exception:
            continue
    return items
