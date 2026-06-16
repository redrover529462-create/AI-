from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceItem:
    title: str
    url: str
    score: float = 0.0
    published_at: str | None = None
    summary: str | None = None
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BriefingBundle:
    ai_items: tuple[SourceItem, ...]
    video_items: tuple[SourceItem, ...]
    github_items: tuple[SourceItem, ...]
