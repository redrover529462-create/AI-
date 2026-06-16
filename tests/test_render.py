from briefing.render import render_briefing
from briefing.models import SourceItem


def test_render_briefing_uses_poster_sections():
    briefing = render_briefing(
        title="晨报",
        ai_items=[SourceItem(title="OpenAI 发布模型", url="https://example.com", source="ai", metadata={"category": "模型发布", "trend_strength": 3})],
        video_items=[SourceItem(title="爆款视频", url="https://example.com/v", source="video", metadata={"hook_strength": 2, "repeatability": 2})],
        github_items=[SourceItem(title="LLM Agent Repo", url="https://github.com/x/y", source="github", metadata={"fresh": True})],
    )
    assert "罗宋汤日报" in briefing
    assert "01 模型发布/更新" in briefing
    assert "02 产品发布/更新" in briefing
    assert "03 行业动态" in briefing
    assert "MORNING ISSUE" in briefing
