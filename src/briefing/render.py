from __future__ import annotations

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
    keywords.append("可复用")
    return f"- {best.title} 之所以更强，主要因为{'、'.join(keywords)}，且具备明显传播势能。"


def render_briefing(title: str, ai_items: list[SourceItem], video_items: list[SourceItem], github_items: list[SourceItem]) -> str:
    return (
        f"# {title}\n\n"
        f"## 今日摘要\n"
        f"- AI 圈：{len(ai_items)} 条\n"
        f"- 爆款视频：{len(video_items)} 条\n"
        f"- GitHub 项目：{len(github_items)} 个\n\n"
        f"## AI 圈新东西\n{_render_list(ai_items)}\n\n"
        f"## 爆款视频链接\n{_render_list(video_items)}\n\n"
        f"## 爆款原因分析\n{_top_reason(video_items)}\n\n"
        f"## GitHub 优质项目\n{_render_list(github_items)}\n\n"
        f"## 趋势判断\n"
        f"- 当前信号更偏向“工具化、低门槛、可复制”的内容形态。\n"
        f"- 如果同一主题在多平台同时出现，后续 1-2 个周期内大概率继续发酵。\n\n"
        f"## 行动建议\n"
        f"- 关注可快速复用的提示词、脚本、工作流和轻量工具链。\n"
        f"- 对高热度视频和仓库建立跟踪清单，观察二次传播与 star 增长。\n"
        f"- 重要主题在下次简报中继续对比验证。"
    )
