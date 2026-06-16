from briefing.ranking import rank_items


def test_rank_items_prefers_recent_and_popular():
    items = [
        {"title": "A", "score": 5, "published_at": "2026-06-13T10:00:00+08:00"},
        {"title": "B", "score": 20, "published_at": "2026-06-12T10:00:00+08:00"},
    ]
    ranked = rank_items(items)
    assert ranked[0]["title"] == "B"
