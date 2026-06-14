from briefing.config import load_config
from briefing.render import render_briefing
from briefing.models import SourceItem


def test_load_config_requires_targets(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"timezone":"Asia/Shanghai"}', encoding="utf-8")

    try:
        load_config(config_path)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "feishu_targets" in str(exc)


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
