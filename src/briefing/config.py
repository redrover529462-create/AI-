from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import os


@dataclass(frozen=True)
class FeishuTarget:
    kind: str
    id: str
    label: str = ""


@dataclass(frozen=True)
class AppConfig:
    timezone: str = "Asia/Shanghai"
    feishu_targets: tuple[FeishuTarget, ...] = field(default_factory=tuple)
    github_token: str | None = None
    github_query: str = "stars:>100 topic:artificial-intelligence"
    xhs_hot_token: str | None = None
    video_sources: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    state_path: str = "state/briefing_state.json"
    sources: dict[str, Any] = field(default_factory=dict)


def _parse_target(raw: dict[str, Any]) -> FeishuTarget:
    kind = str(raw.get("kind", "")).strip()
    target_id = str(raw.get("id", "")).strip()
    label = str(raw.get("label", "")).strip()
    if kind not in {"user", "chat"}:
        raise ValueError("feishu_targets entries must include kind=user or kind=chat")
    if not target_id:
        raise ValueError("feishu_targets entries must include id")
    return FeishuTarget(kind=kind, id=target_id, label=label)


def _merge_targets(file_targets: list[dict[str, Any]], env_user_id: str | None, env_chat_id: str | None) -> tuple[FeishuTarget, ...]:
    targets = [_parse_target(item) for item in file_targets]
    if env_user_id and not any(target.kind == "user" for target in targets):
        targets.append(FeishuTarget(kind="user", id=env_user_id, label="env-user"))
    if env_chat_id and not any(target.kind == "chat" for target in targets):
        targets.append(FeishuTarget(kind="chat", id=env_chat_id, label="env-chat"))
    return tuple(targets)


def load_config(path: Path) -> AppConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_targets = data.get("feishu_targets") or []
    env_user_id = os.getenv("FEISHU_USER_ID")
    env_chat_id = os.getenv("FEISHU_CHAT_ID")
    targets = _merge_targets(raw_targets, env_user_id, env_chat_id)
    if not targets:
        raise ValueError("missing required field: feishu_targets")
    raw_video_sources = (data.get("sources") or {}).get("video", {}).get("sources", [])
    return AppConfig(
        timezone=str(data.get("timezone", "Asia/Shanghai")),
        feishu_targets=targets,
        github_token=data.get("github_token") or os.getenv("GITHUB_TOKEN"),
        github_query=str(data.get("github_query", "stars:>100 topic:artificial-intelligence")),
        xhs_hot_token=data.get("xhs_hot_token") or os.getenv("XHS_HOT_TOKEN"),
        video_sources=tuple(dict(item) for item in raw_video_sources if isinstance(item, dict)),
        state_path=str(data.get("state_path", "state/briefing_state.json")),
        sources=dict(data.get("sources", {})),
    )


def default_config() -> dict[str, Any]:
    return {
        "timezone": "Asia/Shanghai",
        "feishu_targets": [
            {"kind": "user", "id": "oc_769b1ff9f89b9d1a1ba8aa75fc0cfba3", "label": "me"},
            {"kind": "chat", "id": "oc_your_chat_id", "label": "team"},
        ],
        "github_query": "stars:>100 topic:artificial-intelligence",
        "state_path": "state/briefing_state.json",
        "sources": {
            "github": {"enabled": True},
            "ai": {"enabled": True, "urls": ["https://openai.com/news/", "https://openai.com/index/"]},
            "video": {
                "enabled": True,
                "sources": [
                    {"provider": "douyin_hotlist", "name": "抖音热榜", "url": "https://api.iyuns.com/api/douyinhot"},
                    {"provider": "xhs_hot_search", "name": "小红书热搜", "url": "https://api.justoneapi.com/api/xiaohongshu/hot-search/v1", "requires_token": True},
                ],
            },
        },
    }
