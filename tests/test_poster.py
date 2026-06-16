from briefing.poster import PosterRenderer
from briefing.models import SourceItem


def test_poster_renderer_uses_readable_chinese_labels():
    renderer = PosterRenderer(width=720)
    page = renderer.render_page_one(
        cover_summary="今天最强的信号来自 AI 圈。",
        keywords="模型发布 / 爆款",
        one_line="一句话总评。",
        ai_items=[SourceItem(title="OpenAI 发布模型", url="https://example.com", summary="摘要", source="ai")],
    )
    assert page.size[0] == 720
    assert renderer._source_line(SourceItem(title="A", url="https://example.com", summary="摘要", source="", metadata={})) == "综合资讯"
