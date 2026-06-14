from __future__ import annotations

from pathlib import Path
import json
import sys

from .config import AppConfig, default_config, load_config
from .models import BriefingBundle
from .render import render_briefing
from .state import record_send, should_send
from .feishu import send_message
from .sources.github import fetch_github_projects
from .sources.web import fetch_ai_news
from .sources.video import fetch_short_video_trends


def load_bundle(config: AppConfig) -> BriefingBundle:
    sources = config.sources
    ai_items = tuple(fetch_ai_news(sources.get("ai", {}).get("urls")))
    video_items = tuple(fetch_short_video_trends(sources.get("video", {}).get("sources"), xhs_hot_token=config.xhs_hot_token))
    github_items = tuple(fetch_github_projects(config.github_query))
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
