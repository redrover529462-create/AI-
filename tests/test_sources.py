from briefing.sources.github import fetch_github_projects
from briefing.sources.web import fetch_ai_news
from briefing.sources.video import fetch_short_video_trends


def test_fetch_ai_news_has_fallback_item(monkeypatch):
    class Response:
        text = "OpenAI 最新动态"
        def raise_for_status(self):
            return None
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: Response())
    items = fetch_ai_news(["https://openai.com/news/"])
    assert items and items[0].source == "ai"


def test_fetch_short_video_trends_has_item(monkeypatch):
    class Response:
        text = '<a href="https://example.com/video">video</a>'
        def raise_for_status(self):
            return None
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: Response())
    items = fetch_short_video_trends(["https://www.douyin.com/"])
    assert items and items[0].source == "video"


def test_fetch_github_projects_uses_api(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None
        def json(self):
            return {"items": [{"full_name": "octo/repo", "html_url": "https://github.com/octo/repo", "stargazers_count": 12, "updated_at": "2026-06-14T00:00:00Z", "description": "repo", "language": "Python", "forks_count": 1}]}
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: Response())
    items = fetch_github_projects("stars:>10")
    assert items and items[0].source == "github"
