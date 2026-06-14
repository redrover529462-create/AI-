from briefing.render import render_briefing
from briefing.models import SourceItem


def main() -> int:
    print(render_briefing("³¿¼ä¼ò±¨", [SourceItem(title="A", url="https://a")], [], []))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
