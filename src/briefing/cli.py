from __future__ import annotations

from pathlib import Path
import json
import os
import sys

from .config import AppConfig, FeishuTarget, default_config, load_config
from .models import BriefingBundle, SourceItem
from .render import render_briefing
from .state import record_send, should_send
from .feishu import send_message


def load_bundle(config: AppConfig) -> BriefingBundle:
    ai_items = (
        SourceItem(title="OpenAI 发布新模型动向", url="https://openai.com/news/", score=90, summary="官方更新"),
    )
    video_items = (
        SourceItem(title="爆款视频示例", url="https://example.com/video", score=88, summary="高互动视频"),
    )
    github_items = (
        SourceItem(title="Awesome AI Repo", url="https://github.com/example/repo", score=95, summary="高 star 增长"),
    )
    return BriefingBundle(ai_items=ai_items, video_items=video_items, github_items=github_items)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    config_path = Path(argv[0]) if argv else Path("config/briefing.json")
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(default_config(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"created default config at {config_path}")
        return 0

    config = load_config(config_path)
    bundle = load_bundle(config)
    run_key = "daily-briefing"
    state_path = Path(config.state_path)
    if not should_send(state_path, run_key):
        print("briefing already sent for this window")
        return 0

    briefing = render_briefing(
        title="晨间简报",
        ai_items=list(bundle.ai_items),
        video_items=list(bundle.video_items),
        github_items=list(bundle.github_items),
    )

    for target in config.feishu_targets:
        send_message(target, briefing)

    record_send(state_path, run_key, "ok")
    print("sent briefing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
