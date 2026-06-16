from pathlib import Path

from briefing import cli
from briefing.config import AppConfig, FeishuTarget
from briefing.models import BriefingBundle, SourceItem


def _config(state_path: Path) -> AppConfig:
    return AppConfig(
        timezone="Asia/Shanghai",
        feishu_targets=(FeishuTarget(kind="chat", id="oc_x", label="team"),),
        state_path=str(state_path),
        sources={},
    )


def _bundle() -> BriefingBundle:
    item = SourceItem(title="A", url="https://example.com", source="ai")
    return BriefingBundle(ai_items=(item,), video_items=(), github_items=())


def _config_with_targets(state_path: Path, targets: tuple[FeishuTarget, ...]) -> AppConfig:
    return AppConfig(
        timezone="Asia/Shanghai",
        feishu_targets=targets,
        state_path=str(state_path),
        sources={},
    )


def test_main_skips_second_send_within_same_window(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"timezone":"Asia/Shanghai","feishu_targets":[{"kind":"chat","id":"oc_x"}]}', encoding="utf-8")
    state_path = tmp_path / "state.json"

    monkeypatch.setattr(cli, "load_config", lambda path: _config(state_path))
    monkeypatch.setattr(cli, "safe_load_bundle", lambda config: _bundle())
    monkeypatch.setattr(cli, "build_poster_images", lambda **kwargs: [tmp_path / "poster.png"])
    monkeypatch.setattr(cli, "render_briefing", lambda **kwargs: "briefing")
    monkeypatch.setattr(cli, "briefing_cover_summary", lambda *args: "summary")
    monkeypatch.setattr(cli, "briefing_keywords", lambda *args: "keywords")
    monkeypatch.setattr(cli, "briefing_one_line", lambda *args: "one line")
    monkeypatch.setattr(cli, "send_image", lambda *args, **kwargs: {"stdout": "ok", "stderr": ""})
    monkeypatch.setattr(cli, "send_message", lambda *args, **kwargs: {"stdout": "ok", "stderr": ""})

    assert cli.main([str(config_path)]) == 0
    assert cli.main([str(config_path)]) == 0


def test_main_returns_error_when_delivery_fails(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"timezone":"Asia/Shanghai","feishu_targets":[{"kind":"chat","id":"oc_x"}]}', encoding="utf-8")
    state_path = tmp_path / "state.json"

    monkeypatch.setattr(cli, "load_config", lambda path: _config(state_path))
    monkeypatch.setattr(cli, "safe_load_bundle", lambda config: _bundle())
    monkeypatch.setattr(cli, "build_poster_images", lambda **kwargs: [tmp_path / "poster.png"])
    monkeypatch.setattr(cli, "render_briefing", lambda **kwargs: "briefing")
    monkeypatch.setattr(cli, "briefing_cover_summary", lambda *args: "summary")
    monkeypatch.setattr(cli, "briefing_keywords", lambda *args: "keywords")
    monkeypatch.setattr(cli, "briefing_one_line", lambda *args: "one line")
    monkeypatch.setattr(cli, "send_image", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(cli, "send_message", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))

    assert cli.main([str(config_path)]) == 1


def test_check_only_verifies_cli(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"timezone":"Asia/Shanghai","feishu_targets":[{"kind":"chat","id":"oc_x"}]}', encoding="utf-8")
    state_path = tmp_path / "state.json"

    monkeypatch.setattr(cli, "load_config", lambda path: _config(state_path))
    monkeypatch.setattr(cli, "safe_load_bundle", lambda config: _bundle())
    monkeypatch.setattr(cli, "build_poster_images", lambda **kwargs: [tmp_path / "poster.png"])
    monkeypatch.setattr(cli, "render_briefing", lambda **kwargs: "briefing")
    monkeypatch.setattr(cli, "briefing_cover_summary", lambda *args: "summary")
    monkeypatch.setattr(cli, "briefing_keywords", lambda *args: "keywords")
    monkeypatch.setattr(cli, "briefing_one_line", lambda *args: "one line")
    monkeypatch.setattr(cli, "ensure_cli_available", lambda: None)

    assert cli.main([str(config_path), "--check-only"]) == 0


def test_main_skips_user_target_in_bot_mode(monkeypatch, tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"timezone":"Asia/Shanghai","feishu_targets":[{"kind":"user","id":"ou_x"},{"kind":"chat","id":"oc_x"}]}', encoding="utf-8")
    state_path = tmp_path / "state.json"
    calls = []

    monkeypatch.setenv("FEISHU_SEND_MODE", "bot")
    monkeypatch.setattr(
        cli,
        "load_config",
        lambda path: _config_with_targets(
            state_path,
            (
                FeishuTarget(kind="user", id="ou_x", label="me"),
                FeishuTarget(kind="chat", id="oc_x", label="team"),
            ),
        ),
    )
    monkeypatch.setattr(cli, "safe_load_bundle", lambda config: _bundle())
    monkeypatch.setattr(cli, "build_poster_images", lambda **kwargs: [tmp_path / "poster.png"])
    monkeypatch.setattr(cli, "render_briefing", lambda **kwargs: "briefing")
    monkeypatch.setattr(cli, "briefing_cover_summary", lambda *args: "summary")
    monkeypatch.setattr(cli, "briefing_keywords", lambda *args: "keywords")
    monkeypatch.setattr(cli, "briefing_one_line", lambda *args: "one line")
    monkeypatch.setattr(cli, "send_image", lambda target, *args, **kwargs: calls.append(target.kind) or {"stdout": "ok", "stderr": ""})
    monkeypatch.setattr(cli, "send_message", lambda *args, **kwargs: {"stdout": "ok", "stderr": ""})

    assert cli.main([str(config_path)]) == 0
    assert calls == ["chat"]
