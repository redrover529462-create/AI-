from briefing.config import load_config
from briefing.render import render_briefing
from briefing.models import SourceItem


def test_load_config_merges_env_targets(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"timezone":"Asia/Shanghai","feishu_targets":[]}', encoding="utf-8")
    monkeypatch.setenv("FEISHU_USER_ID", "ou_env")
    monkeypatch.setenv("FEISHU_CHAT_ID", "oc_env")
    config = load_config(config_path)
    assert {target.kind for target in config.feishu_targets} == {"user", "chat"}


def test_render_briefing_contains_required_sections():
    briefing = render_briefing(
        title="晨报",
        ai_items=[SourceItem(title="AI News", url="https://example.com")],
        video_items=[SourceItem(title="爆款视频", url="https://example.com/v", metadata={"hook_strength": 2, "repeatability": 2})],
        github_items=[SourceItem(title="Repo", url="https://github.com/x/y")],
    )
    assert "今日摘要" in briefing
    assert "爆款原因分析" in briefing
    assert "爆款结构判断" in briefing
    assert "趋势判断" in briefing
    assert "行动建议" in briefing
