from datetime import datetime, timezone

from briefing.state import current_window_key, should_send, record_send


def test_should_send_blocks_duplicate_window(tmp_path):
    state_path = tmp_path / "state.json"
    assert should_send(state_path, "morning-20260614") is True
    record_send(state_path, "morning-20260614", "ok")
    assert should_send(state_path, "morning-20260614") is False


def test_current_window_key_changes_every_four_hours():
    tz = "Asia/Shanghai"
    early = datetime(2026, 6, 16, 7, 59, tzinfo=timezone.utc)
    late = datetime(2026, 6, 16, 8, 0, tzinfo=timezone.utc)
    assert current_window_key(tz, early) != current_window_key(tz, late)


def test_current_window_key_groups_into_four_hour_blocks():
    tz = "Asia/Shanghai"
    first = datetime(2026, 6, 16, 1, 15, tzinfo=timezone.utc)
    second = datetime(2026, 6, 16, 2, 59, tzinfo=timezone.utc)
    assert current_window_key(tz, first) == current_window_key(tz, second)
