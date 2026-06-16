from __future__ import annotations

from pathlib import Path

from .models import BriefingBundle
from .poster import PosterRenderer


def build_poster_images(output_dir: str, cover_summary: str, keywords: str, one_line: str, trend_note: str, action_note: str, bundle: BriefingBundle) -> list[Path]:
    renderer = PosterRenderer()
    page_one = renderer.render_page_one(cover_summary, keywords, one_line, list(bundle.ai_items))
    page_two = renderer.render_page_two(list(bundle.video_items))
    page_three = renderer.render_page_three(list(bundle.github_items), trend_note, action_note)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    page_one_path = out_dir / 'briefing-page-1.png'
    page_two_path = out_dir / 'briefing-page-2.png'
    page_three_path = out_dir / 'briefing-page-3.png'
    page_one.save(page_one_path)
    page_two.save(page_two_path)
    page_three.save(page_three_path)
    return [page_one_path, page_two_path, page_three_path]
