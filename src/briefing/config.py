from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class FeishuTarget:
    kind: str
    id: str


@dataclass(frozen=True)
class AppConfig:
    timezone: str = "Asia/Shanghai"
    feishu_targets: tuple[FeishuTarget, ...] = field(default_factory=tuple)
    github_token: str | None = None
    github_query: str = "topic:artificial-intelligence stars:>50"
    state_path: str = "state/briefing_state.json"
    sources: dict[str, Any] = field(default_factory=dict)


def _parse_target(raw: dict[str, Any]) -> FeishuTarget:
    kind = str(raw.get("kind", "")).strip()
    target_id = str(raw.get("id", "")).strip()
    if kind not in {"user", "chat"}:
        raise ValueError("feishu_targets entries must include kind=user or kind=chat")
    if not target_id:
        raise ValueError("feishu_targets entries must include id")
    return FeishuTarget(kind=kind, id=target_id)


def load_config(path: Path) -> AppConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_targets = data.get("feishu_targets")
    if not raw_targets:
        raise ValueError("missing required field: feishu_targets")
    targets = tuple(_parse_target(item) for item in raw_targets)
    return AppConfig(
        timezone=str(data.get("timezone", "Asia/Shanghai")),
        feishu_targets=targets,
        github_token=data.get("github_token"),
        github_query=str(data.get("github_query", "topic:artificial-intelligence stars:>50")),
        state_path=str(data.get("state_path", "state/briefing_state.json")),
        sources=dict(data.get("sources", {})),
    )


def default_config() -> dict[str, Any]:
    return {
        "timezone": "Asia/Shanghai",
        "feishu_targets": [
            {"kind": "user", "id": "ou_your_open_id"},
            {"kind": "chat", "id": "oc_your_chat_id"},
        ],
        "github_query": "topic:artificial-intelligence stars:>50",
        "state_path": "state/briefing_state.json",
        "sources": {
            "github": {"enabled": True},
            "ai": {"enabled": True},
            "video": {"enabled": True},
        },
    }
