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


def test_render_briefing_uses_poster_sections():
    briefing = render_briefing(
        title="晨报",
        ai_items=[SourceItem(title="OpenAI 发布模型", url="https://example.com", source="ai", metadata={"category": "模型发布", "trend_strength": 3})],
        video_items=[SourceItem(title="爆款视频", url="https://example.com/v", source="video", metadata={"hook_strength": 2, "repeatability": 2})],
        github_items=[SourceItem(title="LLM Agent Repo", url="https://github.com/x/y", source="github", metadata={"fresh": True})],
    )
    assert "AI HOT 日报" in briefing
    assert "封面摘要" in briefing
    assert "本期关键词" in briefing
    assert "一句话总评" in briefing
    assert "01 模型发布/更新" in briefing
    assert "02 产品发布/更新" in briefing
    assert "03 行业动态" in briefing
