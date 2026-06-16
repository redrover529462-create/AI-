from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
from zoneinfo import ZoneInfo


def _load(path: Path) -> dict:
    if not path.exists():
        return {"sent": []}
    return json.loads(path.read_text(encoding="utf-8"))


def window_key_for(moment: datetime, timezone_name: str) -> str:
    local_moment = moment.astimezone(ZoneInfo(timezone_name))
    window_start_hour = (local_moment.hour // 4) * 4
    return f"daily-briefing-{local_moment:%Y%m%d}-{window_start_hour:02d}"


def current_window_key(timezone_name: str, moment: datetime | None = None) -> str:
    return window_key_for(moment or datetime.now(tz=ZoneInfo(timezone_name)), timezone_name)


def current_window_start(timezone_name: str, moment: datetime | None = None) -> datetime:
    local_moment = (moment or datetime.now(tz=ZoneInfo(timezone_name))).astimezone(ZoneInfo(timezone_name))
    window_start_hour = (local_moment.hour // 4) * 4
    return local_moment.replace(hour=window_start_hour, minute=0, second=0, microsecond=0)


def should_send(path: Path, key: str) -> bool:
    data = _load(path)
    return key not in data.get("sent", [])


def record_send(path: Path, key: str, status: str) -> None:
    data = _load(path)
    sent = set(data.get("sent", []))
    sent.add(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"sent": sorted(sent), "last_status": status}, ensure_ascii=False, indent=2), encoding="utf-8")
