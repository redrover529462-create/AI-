from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

from .config import AppConfig, default_config, load_config
from .image_export import build_poster_images
from .models import BriefingBundle
from .render import briefing_keywords, briefing_one_line, briefing_cover_summary, render_briefing
from .state import record_send, should_send
from .feishu import send_image, send_message
from .sources.github import fetch_github_projects
from .sources.web import fetch_ai_news
from .sources.video import fetch_short_video_trends


def load_bundle(config: AppConfig) -> BriefingBundle:
    sources = config.sources
    ai_items = tuple(fetch_ai_news(sources.get('ai', {}).get('urls')))
    video_items = tuple(fetch_short_video_trends(sources.get('video', {}).get('sources'), xhs_hot_token=config.xhs_hot_token))
    github_items = tuple(fetch_github_projects(config.github_query))
    return BriefingBundle(ai_items=ai_items, video_items=video_items, github_items=github_items)


def safe_load_bundle(config: AppConfig) -> BriefingBundle:
    sources = config.sources
    try:
        ai_items = tuple(fetch_ai_news(sources.get('ai', {}).get('urls')))
    except Exception:
        ai_items = tuple()
    try:
        video_items = tuple(fetch_short_video_trends(sources.get('video', {}).get('sources'), xhs_hot_token=config.xhs_hot_token))
    except Exception:
        video_items = tuple()
    try:
        github_items = tuple(fetch_github_projects(config.github_query))
    except Exception:
        github_items = tuple()
    return BriefingBundle(ai_items=ai_items, video_items=video_items, github_items=github_items)


def _build_outputs(bundle: BriefingBundle) -> tuple[str, list[Path]]:
    ai_items = list(bundle.ai_items)
    video_items = list(bundle.video_items)
    github_items = list(bundle.github_items)
    briefing = render_briefing(
        title='晨间简报',
        ai_items=ai_items,
        video_items=video_items,
        github_items=github_items,
    )
    poster_paths = build_poster_images(
        output_dir='artifacts',
        cover_summary=briefing_cover_summary(ai_items, video_items, github_items),
        keywords=briefing_keywords(ai_items, video_items, github_items),
        one_line=briefing_one_line(ai_items, video_items, github_items),
        trend_note='当前信号更偏向“工具化、低门槛、可复制”的内容形态。如果同一主题在多平台同时出现，后续 1-2 个周期内大概率继续发酵。',
        action_note='关注可快速复用的提示词、脚本、工作流和轻量工具链。对高热度视频和仓库建立跟踪清单，观察二次传播与 star 增长。重要主题在下次简报中继续对比验证。',
        bundle=bundle,
    )
    return briefing, poster_paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', nargs='?', default='config/briefing.json')
    parser.add_argument('--preview-only', action='store_true')
    args = parser.parse_args(argv)

    config_path = Path(args.config_path)
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(default_config(), ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'created default config at {config_path}')
        return 0

    config = load_config(config_path)
    bundle = safe_load_bundle(config)
    briefing, poster_paths = _build_outputs(bundle)

    if args.preview_only:
        print('preview briefing saved to:')
        for poster_path in poster_paths:
            print(poster_path)
        sys.stdout.buffer.write(briefing.encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b'\n')
        return 0

    run_key = 'daily-briefing'
    state_path = Path(config.state_path)
    if not should_send(state_path, run_key):
        print('briefing already sent for this window')
        return 0

    for target in config.feishu_targets:
        try:
            for poster_path in poster_paths:
                send_image(target, str(poster_path))
        except Exception:
            try:
                send_message(target, briefing)
            except Exception as error:
                print(f'failed to send briefing to {target.kind}:{target.label or target.id}: {error}', file=sys.stderr)
                continue

    record_send(state_path, run_key, 'ok')
    print('sent briefing')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
