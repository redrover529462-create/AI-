# 晨间简报自动化

一个面向飞书的 GitHub Actions 晨报自动化：每天工作日按北京时区定时生成 AI / 视频 / GitHub 趋势简报，并优先以两张长图海报发送到飞书私聊和群聊。

## 功能
- 聚合 AI 圈公开源、短视频榜单、GitHub 热门项目
- 生成 Markdown 文本简报
- 生成浅色杂志风两页海报
- 优先发送海报到飞书，失败时自动回退为文本
- 在 GitHub Actions 中定时执行，不依赖本机开机

## 本地预览
生成两张海报预览，不发送飞书：
```bash
$env:PYTHONPATH='src'
python -m briefing.cli --preview-only config/briefing.json
```

预览会输出到：
- `artifacts/briefing-page-1.png`
- `artifacts/briefing-page-2.png`
