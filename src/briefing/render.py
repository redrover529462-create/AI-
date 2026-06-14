from __future__ import annotations

from collections import Counter
from datetime import date

from .models import SourceItem


def _render_item_card(item: SourceItem, index: int, total: int) -> str:
    tags = []
    if item.source:
        tags.append(item.source.upper())
    if item.metadata.get("category"):
        tags.append(str(item.metadata["category"]))
    if item.metadata.get("rank"):
        tags.append(f"RANK {item.metadata['rank']}")
    if item.metadata.get("fresh"):
        tags.append("FRESH")
    tag_line = " / ".join(tags) if tags else "SOURCE"
    summary = item.summary or "暂无摘要"
    return (
        f"**{item.title}**  \n"
        f"`{tag_line}`  \n"
        f"{summary}  \n"
        f"[{item.url}]({item.url})"
    )


def _render_section(number: int, title: str, subtitle: str, items: list[SourceItem]) -> str:
    header = f"## {number:02d} {title}  \n*{subtitle}*  \n`{len(items)} 篇`"
    if not items:
        return header + "\n\n- 暂无可用条目"
    blocks = []
    for index, item in enumerate(items, start=1):
        blocks.append(_render_item_card(item, index, len(items)))
    return header + "\n\n" + "\n\n---\n\n".join(blocks)


def _top_reason(items: list[SourceItem]) -> str:
    if not items:
        return "- 当前暂无样本，后续轮次会补充趋势判断。"
    best = items[0]
    keywords = []
    if best.score >= 100:
        keywords.append("高热度")
    if best.summary:
        keywords.append("信息密度高")
    if best.metadata.get("hook_strength", 0) >= 2:
        keywords.append("强钩子")
    if best.metadata.get("repeatability", 0) >= 2:
        keywords.append("可复用")
    if not keywords:
        keywords.append("具备传播势能")
    return f"{best.title} 更强的原因：{'、'.join(keywords)}。"


def _analyze_group(items: list[SourceItem], groups: dict[str, list[str]], fallback: str) -> str:
    if not items:
        return fallback
    counter: Counter[str] = Counter()
    for item in items:
        text = f"{item.title} {item.summary or ''}".lower()
        for label, keywords in groups.items():
            if any(keyword.lower() in text for keyword in keywords):
                counter[label] += 1
    if not counter:
        return fallback
    top = counter.most_common(3)
    return "；".join(f"{name}{count}条" for name, count in top)


def _analyze_video_trends(items: list[SourceItem]) -> str:
    if not items:
        return "暂无视频样本。"
    hooks = sum(1 for item in items if item.metadata.get("hook_strength", 0) >= 2)
    utility = sum(1 for item in items if item.metadata.get("utility", 0) >= 2)
    emotion = sum(1 for item in items if item.metadata.get("emotion", 0) >= 2)
    repeatable = sum(1 for item in items if item.metadata.get("repeatability", 0) >= 2)
    return f"强钩子 {hooks} | 强工具 {utility} | 强情绪 {emotion} | 高复用 {repeatable}"


def _hero_line(day: str, title: str, story_count: int) -> str:
    return (
        f"VOL.{day} · {story_count} STORIES · {title.upper()} DAILY\n\n"
        f"# AI HOT 日报\n\n"
        f"{date.today().strftime('%Y年%m月%d日')}  ·  每日晨间简报"
    )


def _cover_summary(ai_items: list[SourceItem], video_items: list[SourceItem], github_items: list[SourceItem]) -> str:
    all_items = ai_items + video_items + github_items
    if not all_items:
        return "今日没有可用内容样本。"
    top = all_items[0]
    if top.source == "video":
        return f"今天最强的信号来自视频侧，{top.title} 具备明显钩子与复用特征。"
    if top.source == "github":
        return f"今天最强的信号来自 GitHub 侧，{top.title} 展示出持续 momentum。"
    return f"今天最强的信号来自 AI 圈，{top.title} 更像是后续扩散的起点。"


def _keywords(ai_items: list[SourceItem], video_items: list[SourceItem], github_items: list[SourceItem]) -> str:
    keywords: list[str] = []
    for item in (ai_items[:2] + video_items[:2] + github_items[:2]):
        if item.metadata.get("category"):
            keywords.append(str(item.metadata["category"]))
        elif item.source == "video":
            keywords.extend(["爆款", "钩子", "复用"])
        elif item.source == "github":
            keywords.extend(["开源", "趋势", "Momentum"])
        else:
            keywords.extend(["动态", "发布", "更新"])
    seen: list[str] = []
    for keyword in keywords:
        if keyword not in seen:
            seen.append(keyword)
    return " / ".join(seen[:5]) if seen else "AI / 视频 / GitHub"


def _one_line_summary(ai_items: list[SourceItem], video_items: list[SourceItem], github_items: list[SourceItem]) -> str:
    if not (ai_items or video_items or github_items):
        return "当前没有足够样本，但自动化链路已就绪。"
    parts = []
    if ai_items:
        parts.append(f"AI 圈偏 {ai_items[0].title}")
    if video_items:
        parts.append(f"视频侧最值得跟的是 {video_items[0].title}")
    if github_items:
        parts.append(f"GitHub 里 momentum 最强的是 {github_items[0].title}")
    return "；".join(parts) + "。"


def render_briefing(title: str, ai_items: list[SourceItem], video_items: list[SourceItem], github_items: list[SourceItem]) -> str:
    ai_trend = _analyze_group(
        ai_items,
        {
            "模型发布": ["模型", "release", "launch", "发布", "model"],
            "Agent/工具": ["agent", "工具", "workflow", "app", "assistant", "插件"],
            "研究/论文": ["paper", "研究", "论文", "benchmark", "eval"],
        },
        "当前 AI 样本更偏通用新闻，暂未形成明显主题聚类。",
    )
    github_trend = _analyze_group(
        github_items,
        {
            "LLM/Agent": ["llm", "agent", "chat", "assistant"],
            "开发工具": ["cli", "tool", "workflow", "dev", "sdk"],
            "数据/检索": ["search", "rag", "index", "vector", "db"],
        },
        "当前 GitHub 样本暂未形成明显主题聚类。",
    )
    freshness = sum(1 for item in github_items if item.metadata.get("fresh", False))
    sections = [
        _hero_line(date.today().strftime('%Y.%m.%d'), title, len(ai_items) + len(video_items) + len(github_items)),
        f"### 封面摘要\n{_cover_summary(ai_items, video_items, github_items)}",
        f"### 本期关键词\n{_keywords(ai_items, video_items, github_items)}",
        f"### 一句话总评\n{_one_line_summary(ai_items, video_items, github_items)}",
        _render_section(1, "模型发布/更新", "MODEL RELEASES", ai_items),
        f"### AI 圈爆款/趋势\n{ai_trend}",
        _render_section(2, "产品发布/更新", "PRODUCT", video_items),
        f"### 爆款原因分析\n{_top_reason(video_items)}\n\n### 爆款结构判断\n{_analyze_video_trends(video_items)}",
        _render_section(3, "行业动态", "INDUSTRY", github_items),
        f"### GitHub 爆款/趋势\n{github_trend}\n\n近更新仓库：{freshness} 个",
        "### 趋势判断\n当前信号更偏向“工具化、低门槛、可复制”的内容形态。如果同一主题在多平台同时出现，后续 1-2 个周期内大概率继续发酵。",
        "### 行动建议\n关注可快速复用的提示词、脚本、工作流和轻量工具链。对高热度视频和仓库建立跟踪清单，观察二次传播与 star 增长。重要主题在下次简报中继续对比验证。",
    ]
    return "\n\n".join(sections)
