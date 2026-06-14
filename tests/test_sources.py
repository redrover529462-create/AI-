from briefing.sources.video import fetch_short_video_trends


def test_fetch_short_video_trends_scores_features(monkeypatch):
    class Response:
        text = "教程 模板 前后 对比 震惊"
        url = "https://example.com/video"
        def raise_for_status(self):
            return None
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: Response())
    items = fetch_short_video_trends([{"name": "douyin", "url": "https://www.iesdouyin.com/share/video/"}])
    assert items and items[0].metadata["hook_strength"] >= 1
    assert items[0].metadata["repeatability"] >= 1
