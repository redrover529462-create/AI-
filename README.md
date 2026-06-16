# 罗宋汤日报自动化

这是一个面向飞书群聊的 GitHub Actions 晨报自动化：工作日按北京时间分时生成 AI / 短视频 / GitHub 趋势简报，并优先以海报形式发送到飞书。

## 发送时间

GitHub Actions 的 `cron` 使用 UTC。当前配置为工作日：

- `0 0 * * 1-5`：北京时间 `08:00`
- `0 4 * * 1-5`：北京时间 `12:00`
- `0 8 * * 1-5`：北京时间 `16:00`
- `0 12 * * 1-5`：北京时间 `20:00`
- `0 16 * * 1-5`：北京时间 `00:00`
- `0 20 * * 1-5`：北京时间 `04:00`

注意：
- GitHub Actions 定时任务可能会有数分钟级别的偏移
- 当前代码会在北京时间 12 点窗口增加门禁，保证消息不会早于 12:00 发出

## 发送目标

云端正式发送只使用 `FEISHU_CHAT_ID` 指向的群聊目标。  
服务端发送凭据来自：

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_CHAT_ID`

## 输出内容

- AI 圈公开信息：`aihot.virxact.com` RSS
- 短视频热榜：抖音 / 小红书公开榜单配置
- GitHub 热门项目：GitHub Search API
- 海报输出：
  - `artifacts/briefing-page-1.png`
  - `artifacts/briefing-page-2.png`
  - `artifacts/briefing-page-3.png`

## 本地预览

```powershell
$env:PYTHONPATH='src'
python -m briefing.cli --preview-only config/briefing.json
```

## 手动触发云端发送

```bash
gh workflow run briefing.yml --repo redrover529462-create/AI- --ref codex/cloud-morning-briefing
```

查看最近运行：

```bash
gh run list --repo redrover529462-create/AI- --workflow briefing.yml --limit 5
```

## 本地测试

```powershell
$env:PYTHONPATH='src'
python -m pytest tests -q
```
