from briefing.feishu import send_message
from briefing.config import FeishuTarget


def test_send_message_builds_command(monkeypatch):
    calls = {}

    class Result:
        stdout = "{}"
        stderr = ""

    def fake_run(command, check, capture_output, text, encoding):
        calls["command"] = command
        return Result()

    monkeypatch.setattr("subprocess.run", fake_run)
    result = send_message(FeishuTarget(kind="user", id="ou_x"), "hello")
    assert "--msg-type" in calls["command"]
    assert "--content" in calls["command"]
    assert result["stdout"] == "{}"
