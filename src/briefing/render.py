from __future__ import annotations

from collections import Counter

from .models import SourceItem


def _render_list(items: list[SourceItem]) -> str:
    if not items:
        return "- 暂无可用条目"
    return "\n".join(f"- [{item.title}]({item.url})" for item in items)


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
    return f"- {best.title} 之所以更强，主要因为{'、'.join(keywords)}，且具备明显传播势能。"


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
    return "- 主题聚类：" + "，".join(f"{name}{count}条" for name, count in counter.most_common(3)) + "。"


def _analyze_video_trends(items: list[SourceItem]) -> str:
    if not items:
        return "- 当前暂无可分析的视频样本。"
    hooks = sum(1 for item in items if item.metadata.get("hook_strength", 0) >= 2)
    utility = sum(1 for item in items if item.metadata.get("utility", 0) >= 2)
    emotion = sum(1 for item in items if item.metadata.get("emotion", 0) >= 2)
    repeatable = sum(1 for item in items if item.metadata.get("repeatability", 0) >= 2)
    return (
        f"- 样本里有 {hooks} 条强钩子内容、{utility} 条强工具/教程内容、{emotion} 条强情绪内容。\n"
        f"- 如果重复出现“教程 + 模板 + 对比前后效果”，通常意味着更容易二次扩散。\n"
        f"- 具备高可复用性的内容更适合做成跟踪清单和选题库。"
    )


def render_briefing(title: str, ai_items: list[SourceItem], video_items: list[SourceItem], github_items: list[SourceItem]) -> str:
    ai_trend = _analyze_group(
        ai_items,
        {
            "模型发布": ["模型", "release", "launch", "发布", "model"],
            "Agent/工具": ["agent", "工具", "workflow", "app", "assistant", "插件"],
            "研究/论文": ["paper", "研究", "论文", "benchmark", "eval"],
        },
        "- 当前 AI 样本更偏通用新闻，暂未形成明显主题聚类。",
    )
    github_trend = _analyze_group(
        github_items,
        {
            "LLM/Agent": ["llm", "agent", "chat", "assistant"],
            "开发工具": ["cli", "tool", "workflow", "dev", "sdk"],
            "数据/检索": ["search", "rag", "index", "vector", "db"],
        },
        "- 当前 GitHub 样本暂未形成明显主题聚类。",
    )
    freshness = sum(1 for item in github_items if item.metadata.get("fresh", False))
    return (
        f"# {title}\n\n"
        f"## 今日摘要\n"
        f"- AI 圈：{len(ai_items)} 条\n"
        f"- 爆款视频：{len(video_items)} 条\n"
        f"- GitHub 项目：{len(github_items)} 个\n\n"
        f"## AI 圈新东西\n{_render_list(ai_items)}\n\n"
        f"## AI 圈爆款/趋势\n{ai_trend}\n\n"
        f"## 爆款视频链接\n{_render_list(video_items)}\n\n"
        f"## 爆款原因分析\n{_top_reason(video_items)}\n\n"
        f"## 爆款结构判断\n{_analyze_video_trends(video_items)}\n\n"
        f"## GitHub 优质项目\n{_render_list(github_items)}\n\n"
        f"## GitHub 爆款/趋势\n{github_trend}\n"
        f"- 近更新仓库：{freshness} 个，说明近期 momentum 仍在。\n\n"
        f"## 趋势判断\n"
        f"- 当前信号更偏向“工具化、低门槛、可复制”的内容形态。\n"
        f"- 如果同一主题在多平台同时出现，后续 1-2 个周期内大概率继续发酵。\n\n"
        f"## 行动建议\n"
        f"- 关注可快速复用的提示词、脚本、工作流和轻量工具链。\n"
        f"- 对高热度视频和仓库建立跟踪清单，观察二次传播与 star 增长。\n"
        f"- 重要主题在下次简报中继续对比验证。"
    )
