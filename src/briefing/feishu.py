from __future__ import annotations

import json
import shutil
import subprocess
import sys
import os
from pathlib import Path

from .config import FeishuTarget


def _cli_command() -> list[str]:
    if sys.platform == 'win32':
        cli_script = Path.home() / 'AppData' / 'Roaming' / 'npm' / 'node_modules' / '@larksuite' / 'cli' / 'scripts' / 'run.js'
        return ['node', str(cli_script)]
    return [shutil.which('feishu-cli') or shutil.which('lark-cli') or 'feishu-cli']


def ensure_cli_available() -> None:
    command = _cli_command()
    executable = command[0]
    if executable == 'node':
        if len(command) < 2 or not Path(command[1]).exists():
            raise FileNotFoundError('feishu-cli entrypoint was not found')
        return
    if shutil.which(executable) is None and not Path(executable).exists():
        raise FileNotFoundError(f'{executable} was not found on PATH')


def ensure_send_credentials() -> None:
    forced_mode = os.getenv("FEISHU_SEND_MODE", "").strip().lower()
    if forced_mode != "bot":
        return
    if not os.getenv("FEISHU_APP_ID"):
        raise RuntimeError("missing FEISHU_APP_ID for bot send mode")
    if not os.getenv("FEISHU_APP_SECRET"):
        raise RuntimeError("missing FEISHU_APP_SECRET for bot send mode")


def _send_as(target: FeishuTarget) -> str:
    forced_mode = os.getenv("FEISHU_SEND_MODE", "").strip().lower()
    if forced_mode in {"bot", "user"}:
        return forced_mode
    return 'user' if target.kind == 'user' else 'bot'


def should_attempt_target(target: FeishuTarget) -> bool:
    forced_mode = os.getenv("FEISHU_SEND_MODE", "").strip().lower()
    if forced_mode == "bot" and target.kind == "user":
        return False
    return True


def _build_post_content(markdown: str) -> str:
    content_lines = []
    for line in markdown.splitlines():
        content_lines.append([{'tag': 'text', 'text': (line + '\n') if line else '\n'}])
    payload = {'zh_cn': {'title': '罗宋汤日报', 'content': content_lines}}
    return json.dumps(payload, ensure_ascii=True)


def send_message(target: FeishuTarget, markdown: str) -> dict:
    command = _cli_command() + ['im', '+messages-send', '--as', _send_as(target)]
    if target.kind == 'user':
        command.extend(['--user-id', target.id])
    else:
        command.extend(['--chat-id', target.id])
    command.extend(['--msg-type', 'post', '--content', _build_post_content(markdown), '--json'])
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
    return {'stdout': result.stdout, 'stderr': result.stderr}


def send_image(target: FeishuTarget, image_path: str) -> dict:
    command = _cli_command() + ['im', '+messages-send', '--as', _send_as(target)]
    if target.kind == 'user':
        command.extend(['--user-id', target.id])
    else:
        command.extend(['--chat-id', target.id])
    command.extend(['--image', image_path, '--json'])
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
    return {'stdout': result.stdout, 'stderr': result.stderr}
