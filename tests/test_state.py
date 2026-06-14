from briefing.state import should_send, record_send


def test_should_send_blocks_duplicate_window(tmp_path):
    state_path = tmp_path / "state.json"
    assert should_send(state_path, "morning-20260614") is True
    record_send(state_path, "morning-20260614", "ok")
    assert should_send(state_path, "morning-20260614") is False
