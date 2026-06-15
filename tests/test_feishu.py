from briefing.feishu import send_message, send_image
from briefing.config import FeishuTarget


def test_send_message_builds_command(monkeypatch):
    calls = {}

    class Result:
        stdout = '{}'
        stderr = ''

    def fake_run(command, check, capture_output, text, encoding):
        calls['command'] = command
        return Result()

    monkeypatch.setattr('subprocess.run', fake_run)
    result = send_message(FeishuTarget(kind='user', id='ou_x'), '中文测试')
    assert '--msg-type' in calls['command']
    assert '--content' in calls['command']
    assert '\\u4e2d\\u6587' in calls['command'][-2]
    assert result['stdout'] == '{}'


def test_send_image_builds_command(monkeypatch):
    calls = {}

    class Result:
        stdout = '{}'
        stderr = ''

    def fake_run(command, check, capture_output, text, encoding):
        calls['command'] = command
        return Result()

    monkeypatch.setattr('subprocess.run', fake_run)
    result = send_image(FeishuTarget(kind='chat', id='oc_x'), 'artifacts/briefing-poster.png')
    assert '--as' in calls['command']
    assert 'bot' in calls['command']
    assert '--image' in calls['command']
    assert 'artifacts/briefing-poster.png' in calls['command']
    assert result['stdout'] == '{}'


def test_send_message_to_user_uses_user_identity(monkeypatch):
    calls = {}

    class Result:
        stdout = '{}'
        stderr = ''

    def fake_run(command, check, capture_output, text, encoding):
        calls['command'] = command
        return Result()

    monkeypatch.setattr('subprocess.run', fake_run)
    send_message(FeishuTarget(kind='user', id='ou_x'), 'hello')
    assert '--as' in calls['command']
    assert 'user' in calls['command']
