from __future__ import annotations

import subprocess

from .config import FeishuTarget


def send_message(target: FeishuTarget, markdown: str) -> dict:
    command = [
        "cmd",
        "/c",
        "lark-cli",
        "im",
        "+messages-send",
        "--as",
        "user" if target.kind == "user" else "bot",
    ]
    if target.kind == "user":
        command.extend(["--user-id", target.id])
    else:
        command.extend(["--chat-id", target.id])
    command.extend(["--markdown", markdown, "--json"])
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return {"stdout": result.stdout, "stderr": result.stderr}
