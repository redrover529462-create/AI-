from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .config import FeishuTarget


def _cli_command() -> list[str]:
    if sys.platform == "win32":
        cli_script = Path.home() / "AppData" / "Roaming" / "npm" / "node_modules" / "@larksuite" / "cli" / "scripts" / "run.js"
        return [sys.executable, str(cli_script)] if False else ["node", str(cli_script)]
    return ["lark-cli"]


def _build_message_content(markdown: str) -> str:
    content_lines = []
    for line in markdown.splitlines():
        if line.strip() == "":
            content_lines.append({"tag": "text", "text": "\n"})
        else:
            content_lines.append({"tag": "text", "text": line + "\n"})
    payload = {"zh_cn": {"title": "AI HOT 日报", "content": [content_lines]}}
    return json.dumps(payload, ensure_ascii=False)


def send_message(target: FeishuTarget, markdown: str) -> dict:
    command = _cli_command() + ["im", "+messages-send", "--as", "user" if target.kind == "user" else "bot"]
    if target.kind == "user":
        command.extend(["--user-id", target.id])
    else:
        command.extend(["--chat-id", target.id])
    command.extend(["--msg-type", "post", "--content", _build_message_content(markdown), "--json"])
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    return {"stdout": result.stdout, "stderr": result.stderr}
