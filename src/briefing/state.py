from __future__ import annotations

from pathlib import Path
import json


def _load(path: Path) -> dict:
    if not path.exists():
        return {"sent": []}
    return json.loads(path.read_text(encoding="utf-8"))


def should_send(path: Path, key: str) -> bool:
    data = _load(path)
    return key not in data.get("sent", [])


def record_send(path: Path, key: str, status: str) -> None:
    data = _load(path)
    sent = set(data.get("sent", []))
    sent.add(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"sent": sorted(sent), "last_status": status}, ensure_ascii=False, indent=2), encoding="utf-8")
