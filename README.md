# 罗宋汤日报自动化

一个面向飞书的 GitHub Actions 晨报自动化：工作日按北京时区定时生成 AI / 短视频 / GitHub 趋势简报，并优先以浅色杂志风海报发送到飞书。

## 发送时间

GitHub Actions 的 cron 使用 UTC。当前配置为：

- `0 0 * * 1-5`：北京时间工作日 `08:00`
- `0 4 * * 1-5`：北京时间工作日 `12:00`
- `0 8 * * 1-5`：北京时间工作日 `16:00`
- `0 12 * * 1-5`：北京时间工作日 `20:00`

注意：GitHub Actions 定时任务可能会延迟几分钟到几十分钟，尤其在整点高峰期；它不依赖本机开机。

## 发送目标

当前配置文件：`config/briefing.json`

- 私聊：`ou_47c247d6040acf2c059fe70cc3d322ca`
- 群聊：`oc_f3c3daf69dc2455b8eaa9b5d72c5ae7b`

云端运行时会安装 `feishu-cli`，并通过 bot 身份向群聊发送。私聊如果缺少用户登录态可能失败，但不会阻塞群聊发送。

## 输出内容

- AI 圈公开源：`aihot.virxact.com` RSS
- 短视频热榜：抖音 / 小红书公开榜单配置
- GitHub 热门项目：GitHub Search API
- 海报输出：三张图片，避免内容过挤
  - `artifacts/briefing-page-1.png`：封面 + AI 圈
  - `artifacts/briefing-page-2.png`：产品发布 / 短视频热点
  - `artifacts/briefing-page-3.png`：GitHub + 趋势判断

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
python -m pytest tests/test_render.py tests/test_feishu.py -q
```
