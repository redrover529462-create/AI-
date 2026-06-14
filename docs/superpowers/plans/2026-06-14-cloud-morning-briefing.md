# Cloud Morning Briefing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a cloud-hosted automation that gathers AI news, short-video trends, and GitHub project signals, then sends a deep morning briefing to Feishu chat and DM on a schedule.

**Architecture:** A small Python app will fetch normalized items from a few source adapters, rank and summarize them into a Markdown briefing, and send the result through the existing Feishu CLI/auth flow or direct Feishu API wrapper. GitHub Actions will run the job on a schedule, persist a tiny state file for dedupe, and route failures into logs that can be inspected from the repo.

**Tech Stack:** Python 3.11+, GitHub Actions, Requests/httpx, PyYAML or JSON, Feishu CLI auth state, GitHub Search API.

---

### Task 1: Scaffold project layout

**Files:**
- Create: `src/briefing/__init__.py`
- Create: `src/briefing/config.py`
- Create: `src/briefing/state.py`
- Create: `src/briefing/models.py`
- Create: `src/briefing/cli.py`
- Create: `tests/test_config.py`
- Create: `tests/test_state.py`

- [ ] **Step 1: Write the failing test**

```python
from briefing.config import load_config


def test_load_config_requires_targets(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text('{"timezone":"Asia/Shanghai"}', encoding="utf-8")

    try:
        load_config(config_path)
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "feishu_targets" in str(exc)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL because `load_config` is missing.

- [ ] **Step 3: Write minimal implementation**

```python
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    timezone: str
    feishu_targets: list[str]


def load_config(path: Path) -> AppConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "feishu_targets" not in data:
        raise ValueError("missing required field: feishu_targets")
    return AppConfig(timezone=data.get("timezone", "Asia/Shanghai"), feishu_targets=data["feishu_targets"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/briefing tests/test_config.py tests/test_state.py
git commit -m "feat: scaffold briefing config and state"
```

### Task 2: Implement state and dedupe

**Files:**
- Modify: `src/briefing/state.py`
- Create: `tests/test_state.py`

- [ ] **Step 1: Write the failing test**

```python
from briefing.state import should_send, record_send


def test_should_send_blocks_duplicate_window(tmp_path):
    state_path = tmp_path / "state.json"
    assert should_send(state_path, "morning-20260614") is True
    record_send(state_path, "morning-20260614", "ok")
    assert should_send(state_path, "morning-20260614") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_state.py -v`
Expected: FAIL because `should_send` and `record_send` are missing.

- [ ] **Step 3: Write minimal implementation**

```python
import json
from pathlib import Path


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
    path.write_text(json.dumps({"sent": sorted(sent), "last_status": status}, ensure_ascii=False), encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_state.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/briefing/state.py tests/test_state.py
git commit -m "feat: add briefing send dedupe state"
```

### Task 3: Build source adapters and ranking

**Files:**
- Create: `src/briefing/sources/github.py`
- Create: `src/briefing/sources/web.py`
- Create: `src/briefing/ranking.py`
- Create: `tests/test_ranking.py`

- [ ] **Step 1: Write the failing test**

```python
from briefing.ranking import rank_items


def test_rank_items_prefers_recent_and_popular():
    items = [
        {"title": "A", "score": 5, "published_at": "2026-06-13T10:00:00+08:00"},
        {"title": "B", "score": 20, "published_at": "2026-06-12T10:00:00+08:00"},
    ]
    ranked = rank_items(items)
    assert ranked[0]["title"] == "B"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ranking.py -v`
Expected: FAIL because `rank_items` is missing.

- [ ] **Step 3: Write minimal implementation**

```python
from datetime import datetime


def rank_items(items: list[dict]) -> list[dict]:
    def key(item: dict) -> tuple:
        published = item.get("published_at")
        published_score = datetime.fromisoformat(published).timestamp() if published else 0.0
        return (item.get("score", 0), published_score)

    return sorted(items, key=key, reverse=True)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ranking.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/briefing/sources src/briefing/ranking.py tests/test_ranking.py
git commit -m "feat: rank briefing source items"
```

### Task 4: Render briefing Markdown

**Files:**
- Create: `src/briefing/render.py`
- Create: `tests/test_render.py`

- [ ] **Step 1: Write the failing test**

```python
from briefing.render import render_briefing


def test_render_briefing_contains_required_sections():
    briefing = render_briefing(
        title="晨报",
        ai_items=[{"title": "AI News", "url": "https://example.com"}],
        video_items=[{"title": "爆款视频", "url": "https://example.com/v"}],
        github_items=[{"title": "Repo", "url": "https://github.com/x/y"}],
    )
    assert "今日摘要" in briefing
    assert "爆款原因分析" in briefing
    assert "趋势判断" in briefing
    assert "行动建议" in briefing
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_render.py -v`
Expected: FAIL because `render_briefing` is missing.

- [ ] **Step 3: Write minimal implementation**

```python
from textwrap import dedent


def render_briefing(title: str, ai_items: list[dict], video_items: list[dict], github_items: list[dict]) -> str:
    return dedent(f"""
    # {title}

    ## 今日摘要
    - AI: {len(ai_items)} 条
    - 视频: {len(video_items)} 条
    - GitHub: {len(github_items)} 个

    ## AI 圈新东西
    {chr(10).join(f'- [{item["title"]}]({item["url"]})' for item in ai_items)}

    ## 爆款视频链接
    {chr(10).join(f'- [{item["title"]}]({item["url"]})' for item in video_items)}

    ## 爆款原因分析
    - 从标题、互动和传播路径判断，优先选择具备情绪、利益点和可复用模板的内容。

    ## GitHub 优质项目
    {chr(10).join(f'- [{item["title"]}]({item["url"]})' for item in github_items)}

    ## 趋势判断
    - 关注多平台共振主题。

    ## 行动建议
    - 记录值得跟进的主题，并在下一轮继续观察。
    """).strip()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_render.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/briefing/render.py tests/test_render.py
git commit -m "feat: render briefing markdown"
```

### Task 5: Add Feishu sender integration

**Files:**
- Create: `src/briefing/feishu.py`
- Create: `tests/test_feishu.py`

- [ ] **Step 1: Write the failing test**

```python
from briefing.feishu import build_send_command


def test_build_send_command_for_user_target():
    command = build_send_command(user_id="ou_x", text="hello")
    assert "--as user" in command
    assert "--user-id ou_x" in command
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_feishu.py -v`
Expected: FAIL because `build_send_command` is missing.

- [ ] **Step 3: Write minimal implementation**

```python

def build_send_command(user_id: str | None = None, chat_id: str | None = None, text: str = "") -> str:
    if user_id:
        return f'lark-cli im +messages-send --as user --user-id {user_id} --text "{text}"'
    if chat_id:
        return f'lark-cli im +messages-send --as bot --chat-id {chat_id} --text "{text}"'
    raise ValueError("user_id or chat_id required")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_feishu.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/briefing/feishu.py tests/test_feishu.py
git commit -m "feat: add feishu sending helpers"
```

### Task 6: Wire the scheduled workflow

**Files:**
- Create: `.github/workflows/briefing.yml`
- Create: `scripts/run_briefing.py`
- Modify: `src/briefing/cli.py`

- [ ] **Step 1: Write the workflow file**

```yaml
name: briefing
on:
  schedule:
    - cron: '0 0 * * 1-5'
    - cron: '0 4 * * 1-5'
    - cron: '0 8 * * 1-5'
    - cron: '0 12 * * 1-5'
    - cron: '0 16 * * 1-5'
    - cron: '0 20 * * 1-5'
  workflow_dispatch:

jobs:
  send:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install -r requirements.txt
      - run: python scripts/run_briefing.py
        env:
          FEISHU_USER_ID: ${{ secrets.FEISHU_USER_ID }}
          FEISHU_CHAT_ID: ${{ secrets.FEISHU_CHAT_ID }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: Add runnable entrypoint**

```python
from briefing.render import render_briefing


def main() -> int:
    print(render_briefing("晨间简报", [], [], []))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run a smoke test locally**

Run: `python scripts/run_briefing.py`
Expected: prints a Markdown briefing without crashing.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/briefing.yml scripts/run_briefing.py src/briefing/cli.py
git commit -m "feat: schedule briefing workflow"
```

### Task 7: Add docs and run end-to-end checks

**Files:**
- Create: `README.md`
- Modify: `docs/superpowers/specs/2026-06-14-cloud-morning-briefing-design.md`

- [ ] **Step 1: Document setup**

```md
## Setup
1. Configure Feishu targets
2. Add GitHub token
3. Push to GitHub Actions
4. Verify the first scheduled run
```

- [ ] **Step 2: Run the full test suite**

Run: `pytest -v`
Expected: all tests pass.

- [ ] **Step 3: Verify workflow syntax**

Run: `python -c "import yaml, pathlib; print(yaml.safe_load(pathlib.Path('.github/workflows/briefing.yml').read_text()))"`
Expected: parses without error.

- [ ] **Step 4: Commit docs**

```bash
git add README.md docs/superpowers/specs/2026-06-14-cloud-morning-briefing-design.md
git commit -m "docs: add briefing setup guide"
```
