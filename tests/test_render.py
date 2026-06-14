from briefing.render import render_briefing
from briefing.models import SourceItem


def test_render_briefing_contains_required_sections():
    briefing = render_briefing(
        title="晨报",
        ai_items=[SourceItem(title="AI News", url="https://example.com")],
        video_items=[SourceItem(title="爆款视频", url="https://example.com/v")],
        github_items=[SourceItem(title="Repo", url="https://github.com/x/y")],
    )
    assert "今日摘要" in briefing
    assert "爆款原因分析" in briefing
    assert "趋势判断" in briefing
    assert "行动建议" in briefing
