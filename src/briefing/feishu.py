from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from .config import FeishuTarget


OPEN_BASE_URL = "https://open.feishu.cn/open-apis"


def ensure_cli_available() -> None:
    return


def ensure_send_credentials() -> None:
    if not os.getenv("FEISHU_APP_ID"):
        raise RuntimeError("missing FEISHU_APP_ID for bot send mode")
    if not os.getenv("FEISHU_APP_SECRET"):
        raise RuntimeError("missing FEISHU_APP_SECRET for bot send mode")


def should_attempt_target(target: FeishuTarget) -> bool:
    return target.kind == "chat"


def _tenant_access_token() -> str:
    response = requests.post(
        f"{OPEN_BASE_URL}/auth/v3/tenant_access_token/internal",
        json={
            "app_id": os.getenv("FEISHU_APP_ID", ""),
            "app_secret": os.getenv("FEISHU_APP_SECRET", ""),
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 0:
        raise RuntimeError(f"failed to get tenant access token: {payload}")
    return str(payload["tenant_access_token"])


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def _build_post_content(markdown: str) -> str:
    content_lines = []
    for line in markdown.splitlines():
        content_lines.append([{"tag": "text", "text": (line + "\n") if line else "\n"}])
    payload = {"zh_cn": {"title": "罗宋汤日报", "content": content_lines}}
    return json.dumps(payload, ensure_ascii=False)


def send_message(target: FeishuTarget, markdown: str) -> dict:
    token = _tenant_access_token()
    response = requests.post(
        f"{OPEN_BASE_URL}/im/v1/messages",
        params={"receive_id_type": "chat_id"},
        headers={**_headers(token), "Content-Type": "application/json; charset=utf-8"},
        json={
            "receive_id": target.id,
            "msg_type": "post",
            "content": _build_post_content(markdown),
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 0:
        raise RuntimeError(f"failed to send post message: {payload}")
    return payload


def send_image(target: FeishuTarget, image_path: str) -> dict:
    token = _tenant_access_token()
    image_file = Path(image_path)
    with image_file.open("rb") as file_handle:
        upload_response = requests.post(
            f"{OPEN_BASE_URL}/im/v1/images",
            headers=_headers(token),
            files={
                "image_type": (None, "message"),
                "image": (image_file.name, file_handle, "image/png"),
            },
            timeout=60,
        )
    upload_response.raise_for_status()
    upload_payload = upload_response.json()
    if upload_payload.get("code") != 0:
        raise RuntimeError(f"failed to upload image: {upload_payload}")
    image_key = upload_payload["data"]["image_key"]

    message_response = requests.post(
        f"{OPEN_BASE_URL}/im/v1/messages",
        params={"receive_id_type": "chat_id"},
        headers={**_headers(token), "Content-Type": "application/json; charset=utf-8"},
        json={
            "receive_id": target.id,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key}, ensure_ascii=False),
        },
        timeout=30,
    )
    message_response.raise_for_status()
    message_payload = message_response.json()
    if message_payload.get("code") != 0:
        raise RuntimeError(f"failed to send image message: {message_payload}")
    return message_payload
