import json

from briefing.config import FeishuTarget
from briefing.feishu import ensure_send_credentials, send_image, send_message, should_attempt_target


def test_send_message_uses_chat_api(monkeypatch):
    calls = []

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        if "tenant_access_token" in url:
            return Response({"code": 0, "tenant_access_token": "token"})
        return Response({"code": 0, "data": {"message_id": "om_x"}})

    monkeypatch.setenv("FEISHU_APP_ID", "app_id")
    monkeypatch.setenv("FEISHU_APP_SECRET", "app_secret")
    monkeypatch.setattr("briefing.feishu.requests.post", fake_post)

    payload = send_message(FeishuTarget(kind="chat", id="oc_x"), "hello")
    assert payload["code"] == 0
    assert calls[-1][0].endswith("/im/v1/messages")
    assert calls[-1][1]["params"]["receive_id_type"] == "chat_id"
    assert calls[-1][1]["json"]["receive_id"] == "oc_x"
    assert calls[-1][1]["json"]["msg_type"] == "post"
    assert json.loads(calls[-1][1]["json"]["content"])["zh_cn"]["title"] == "罗宋汤日报"


def test_send_image_uploads_then_sends(monkeypatch, tmp_path):
    calls = []
    image_path = tmp_path / "poster.png"
    image_path.write_bytes(b"fake-image")

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        if "tenant_access_token" in url:
            return Response({"code": 0, "tenant_access_token": "token"})
        if url.endswith("/im/v1/images"):
            return Response({"code": 0, "data": {"image_key": "img_x"}})
        return Response({"code": 0, "data": {"message_id": "om_x"}})

    monkeypatch.setenv("FEISHU_APP_ID", "app_id")
    monkeypatch.setenv("FEISHU_APP_SECRET", "app_secret")
    monkeypatch.setattr("briefing.feishu.requests.post", fake_post)

    payload = send_image(FeishuTarget(kind="chat", id="oc_x"), str(image_path))
    assert payload["code"] == 0
    assert any(url.endswith("/im/v1/images") for url, _ in calls)
    assert calls[-1][0].endswith("/im/v1/messages")
    assert json.loads(calls[-1][1]["json"]["content"])["image_key"] == "img_x"


def test_only_chat_targets_are_attempted():
    assert should_attempt_target(FeishuTarget(kind="user", id="ou_x")) is False
    assert should_attempt_target(FeishuTarget(kind="chat", id="oc_x")) is True


def test_send_requires_app_credentials(monkeypatch):
    monkeypatch.delenv("FEISHU_APP_ID", raising=False)
    monkeypatch.delenv("FEISHU_APP_SECRET", raising=False)
    monkeypatch.delenv("FEISHU_CHAT_ID", raising=False)
    try:
        ensure_send_credentials()
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "FEISHU_APP_ID" in str(exc)


def test_send_requires_chat_id(monkeypatch):
    monkeypatch.setenv("FEISHU_APP_ID", "app_id")
    monkeypatch.setenv("FEISHU_APP_SECRET", "app_secret")
    monkeypatch.delenv("FEISHU_CHAT_ID", raising=False)
    try:
        ensure_send_credentials()
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "FEISHU_CHAT_ID" in str(exc)
