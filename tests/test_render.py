from briefing.render import render_briefing
from briefing.models import SourceItem


def test_render_briefing_contains_required_sections():
    briefing = render_briefing(
        title="晨报",
        ai_items=[SourceItem(title="OpenAI 发布模型", url="https://example.com", metadata={"category": "模型发布", "trend_strength": 3})],
        video_items=[SourceItem(title="爆款视频", url="https://example.com/v", metadata={"hook_strength": 2, "repeatability": 2})],
        github_items=[SourceItem(title="LLM Agent Repo", url="https://github.com/x/y", metadata={"fresh": True})],
    )
    assert "AI 圈爆款/趋势" in briefing
    assert "爆款结构判断" in briefing
    assert "GitHub 爆款/趋势" in briefing
    assert "趋势判断" in briefing
    assert "行动建议" in briefing
