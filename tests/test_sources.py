from briefing.sources.video import fetch_short_video_trends
from briefing.sources.web import fetch_ai_news
from briefing.sources.github import fetch_github_projects


def test_fetch_short_video_trends_scores_features(monkeypatch):
    class Response:
        json_data = {"data": [{"title": "教程 模板 前后 对比 震惊", "url": "https://example.com/video", "hot_value": 900000}]}
        def raise_for_status(self):
            return None
        def json(self):
            return self.json_data
    monkeypatch.setattr("briefing.sources.video.requests.get", lambda *args, **kwargs: Response())
    items = fetch_short_video_trends([{"provider": "douyin_hotlist", "name": "抖音热榜", "url": "https://api.example.com"}])
    assert items and items[0].metadata["hook_strength"] >= 1
    assert items[0].metadata["repeatability"] >= 1


def test_fetch_ai_news_marks_trend(monkeypatch):
    class Response:
        text = "OpenAI 发布新模型"
        def raise_for_status(self):
            return None
    monkeypatch.setattr("briefing.sources.web.requests.get", lambda *args, **kwargs: Response())
    items = fetch_ai_news(["https://openai.com/news/"])
    assert items and items[0].metadata["trend_strength"] >= 1


def test_fetch_github_projects_tracks_momentum(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None
        def json(self):
            return {"items": [{"full_name": "octo/repo", "html_url": "https://github.com/octo/repo", "stargazers_count": 12, "updated_at": "2026-06-14T00:00:00Z", "description": "repo", "language": "Python", "forks_count": 1}]}
    monkeypatch.setattr("briefing.sources.github.requests.get", lambda *args, **kwargs: Response())
    items = fetch_github_projects("stars:>10")
    assert items and items[0].metadata["momentum"] >= 12
