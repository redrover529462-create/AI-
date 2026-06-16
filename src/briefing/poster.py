from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .models import SourceItem


@dataclass(frozen=True)
class PosterTheme:
    background: str = "#F6F1E8"
    surface: str = "#FFFDF8"
    text: str = "#151515"
    muted: str = "#645B4E"
    faint: str = "#8E8474"
    accent: str = "#B38A3B"
    line: str = "#D8C8A8"


class PosterRenderer:
    def __init__(self, width: int = 1080, theme: PosterTheme | None = None):
        self.width = width
        self.theme = theme or PosterTheme()
        self.canvas_height = 3600
        self.canvas = Image.new("RGB", (self.width, self.canvas_height), self.theme.background)
        self.draw = ImageDraw.Draw(self.canvas)
        self.font_dir = Path(r"C:\Windows\Fonts")
        self.font_title = self._font(["AlibabaPuHuiTi_2_65_Medium.ttf", "arialbd.ttf"], 92)
        self.font_number = self._font(["AlibabaPuHuiTi_2_65_Medium.ttf", "arialbd.ttf"], 88)
        self.font_section = self._font(["AlibabaPuHuiTi_2_65_Medium.ttf", "arialbd.ttf"], 38)
        self.font_item_title = self._font(["AlibabaPuHuiTi_2_65_Medium.ttf", "arialbd.ttf"], 28)
        self.font_body = self._font(["AlibabaPuHuiTi_2_55_Regular.ttf", "msyh.ttc", "arial.ttf"], 23)
        self.font_small = self._font(["AlibabaPuHuiTi_2_55_Regular.ttf", "msyh.ttc", "arial.ttf"], 18)
        self.font_tiny = self._font(["AlibabaPuHuiTi_2_55_Regular.ttf", "msyh.ttc", "arial.ttf"], 15)
        self.font_spine = self._font(["AlibabaPuHuiTi_2_55_Regular.ttf", "msyh.ttc", "arial.ttf"], 12)

    def _font(self, names: list[str], size: int):
        for name in names:
            candidate = self.font_dir / name
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size=size)
        return ImageFont.load_default()

    def _reset(self) -> None:
        self.canvas = Image.new("RGB", (self.width, self.canvas_height), self.theme.background)
        self.draw = ImageDraw.Draw(self.canvas)

    def _text_height(self, text: str, font, spacing: int = 10) -> int:
        if not text:
            return 0
        bbox = self.draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing)
        return bbox[3] - bbox[1]

    def _wrap_text(self, text: str, font, max_width: int, max_lines: int | None = None) -> str:
        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            current = ""
            for char in paragraph:
                candidate = current + char
                if self.draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = char
                    if max_lines and len(lines) >= max_lines:
                        return "\n".join(lines[:max_lines])
            if current:
                lines.append(current)
            if max_lines and len(lines) >= max_lines:
                return "\n".join(lines[:max_lines])
        return "\n".join(lines)

    def _draw_text(
        self,
        x: int,
        y: int,
        text: str,
        font,
        fill: str,
        max_width: int,
        spacing: int = 10,
        max_lines: int | None = None,
    ) -> int:
        wrapped = self._wrap_text(text, font, max_width, max_lines=max_lines)
        self.draw.multiline_text((x, y), wrapped, font=font, fill=fill, spacing=spacing)
        return y + self._text_height(wrapped, font, spacing)

    def _page_base(self, story_count: int, subtitle: str) -> None:
        self.draw.rectangle((0, 0, self.width, 18), fill=self.theme.accent)
        self.draw.text((92, 54), f"VOL.{date.today().strftime('%Y.%m.%d')}", font=self.font_tiny, fill=self.theme.faint)
        self.draw.text((238, 54), f"{story_count} STORIES", font=self.font_tiny, fill=self.theme.faint)
        self.draw.text((92, 108), "罗宋汤日报", font=self.font_title, fill=self.theme.text)
        self.draw.text((92, 214), date.today().strftime("%Y年%m月%d日"), font=self.font_section, fill=self.theme.text)
        self.draw.text((390, 224), subtitle, font=self.font_small, fill=self.theme.muted)
        self.draw.line((92, 286, 988, 286), fill=self.theme.line, width=2)
        self.draw.multiline_text((28, 332), "\n".join(list("MORNING ISSUE")), font=self.font_spine, fill="#B8B0A2", spacing=1)

    def _section_header(self, number: int, title: str, subtitle: str, count: int, y: int) -> int:
        self.draw.text((34, y), f"{number:02d}", font=self.font_number, fill=self.theme.accent)
        self.draw.text((152, y + 16), title, font=self.font_section, fill=self.theme.text)
        self.draw.text((390, y + 34), subtitle, font=self.font_tiny, fill=self.theme.faint)
        self.draw.text((930, y + 34), f"{count} 篇", font=self.font_small, fill=self.theme.accent)
        return y + 110

    def _source_line(self, item: SourceItem) -> str:
        tags: list[str] = []
        if item.metadata.get("category"):
            tags.append(str(item.metadata["category"]))
        if item.metadata.get("platform"):
            tags.append(str(item.metadata["platform"]))
        elif item.source:
            tags.append(item.source.upper())
        if item.metadata.get("fresh"):
            tags.append("FRESH")
        return "  路  ".join(tags[:2]) or "综合资讯"

    def _item_height(self, item: SourceItem, max_width: int, summary_lines: int, show_link: bool = False) -> int:
        title = self._wrap_text(item.title, self.font_item_title, max_width, max_lines=2)
        summary = self._wrap_text(item.summary or "暂无摘要", self.font_body, max_width, max_lines=summary_lines)
        link_height = 0
        if show_link and item.url:
            link = self._wrap_text(f"URL: {item.url}", self.font_small, max_width, max_lines=2)
            link_height = 18 + self._text_height(link, self.font_small, 6)
        return 34 + self._text_height(title, self.font_item_title, 6) + 28 + self._text_height(summary, self.font_body, 10) + link_height + 30

    def _draw_item(self, x: int, y: int, w: int, item: SourceItem, is_last: bool, summary_lines: int, show_link: bool = False) -> int:
        top = y
        top = self._draw_text(x, top, item.title, self.font_item_title, self.theme.text, w, spacing=6, max_lines=2)
        top += 12
        self.draw.text((x, top), self._source_line(item), font=self.font_tiny, fill=self.theme.faint)
        top += 30
        top = self._draw_text(x, top, item.summary or "暂无摘要", self.font_body, self.theme.text, w, spacing=10, max_lines=summary_lines)
        if show_link and item.url:
            top += 18
            top = self._draw_text(x, top, f"URL: {item.url}", self.font_small, self.theme.accent, w, spacing=6, max_lines=2)
        top += 28
        if not is_last:
            self.draw.line((x, top, x + w, top), fill=self.theme.line, width=1)
            top += 32
        return top

    def _section_box(
        self,
        number: int,
        title: str,
        subtitle: str,
        items: list[SourceItem],
        y: int,
        item_limit: int,
        summary_lines: int,
        show_links: bool = False,
    ) -> int:
        y = self._section_header(number, title, subtitle, len(items), y)
        visible_items = items[:item_limit]
        content_x = 62
        content_w = 916
        box_height = 82
        for item in visible_items:
            box_height += self._item_height(item, content_w, summary_lines, show_link=show_links)
        self.draw.rounded_rectangle((34, y, 1012, y + box_height), radius=18, fill=self.theme.surface, outline=self.theme.line, width=1)
        item_y = y + 36
        for index, item in enumerate(visible_items):
            item_y = self._draw_item(content_x, item_y, content_w, item, is_last=index == len(visible_items) - 1, summary_lines=summary_lines, show_link=show_links)
        return y + box_height + 92

    def _cover_box(self, cover_summary: str, keywords: str, one_line: str, y: int) -> int:
        box_height = 330
        self.draw.rounded_rectangle((92, y, 988, y + box_height), radius=22, fill=self.theme.surface, outline=self.theme.line, width=1)
        top = y + 32
        top = self._draw_text(124, top, "封面摘要", self.font_section, self.theme.text, 820, spacing=8)
        top += 16
        top = self._draw_text(124, top, cover_summary, self.font_body, self.theme.text, 820, spacing=12, max_lines=3)
        top += 34
        top = self._draw_text(124, top, f"本期关键词  {keywords}", self.font_item_title, self.theme.muted, 820, spacing=8, max_lines=2)
        top += 18
        self._draw_text(124, top, one_line, self.font_body, self.theme.text, 820, spacing=12, max_lines=3)
        return y + box_height + 88

    def _crop_to_content(self, y: int) -> Image.Image:
        return self.canvas.crop((0, 0, self.width, max(1800, min(self.canvas_height, y + 120))))

    def render_page_one(self, cover_summary: str, keywords: str, one_line: str, ai_items: list[SourceItem]) -> Image.Image:
        self._reset()
        self._page_base(len(ai_items), "封面 / AI 圈")
        y = self._cover_box(cover_summary, keywords, one_line, 344)
        y = self._section_box(1, "模型发布/更新", "MODEL WATCH", ai_items, y, item_limit=4, summary_lines=3)
        return self._crop_to_content(y)

    def render_page_two(self, video_items: list[SourceItem]) -> Image.Image:
        self._reset()
        self._page_base(len(video_items), "短视频 / 热点")
        y = 344
        y = self._section_box(2, "产品发布/更新", "TREND WATCH", video_items, y, item_limit=6, summary_lines=2, show_links=True)
        return self._crop_to_content(y)

    def render_page_three(self, github_items: list[SourceItem], trend_note: str, action_note: str) -> Image.Image:
        self._reset()
        self._page_base(len(github_items), "开源 / 趋势")
        y = 344
        y = self._section_box(3, "行业动态", "OPEN SOURCE", github_items, y, item_limit=5, summary_lines=3)
        self.draw.line((92, y, 988, y), fill=self.theme.line, width=1)
        y += 42
        y = self._draw_text(92, y, "趋势判断", self.font_section, self.theme.text, 896, spacing=8)
        y += 16
        y = self._draw_text(92, y, trend_note, self.font_body, self.theme.text, 896, spacing=12, max_lines=3)
        y += 42
        y = self._draw_text(92, y, "行动建议", self.font_section, self.theme.text, 896, spacing=8)
        y += 16
        self._draw_text(92, y, action_note, self.font_body, self.theme.text, 896, spacing=12, max_lines=3)
        return self._crop_to_content(y + 180)
