from __future__ import annotations

from briefing.models import SourceItem
from briefing.render import render_briefing


def main() -> int:
    print(render_briefing("晨间简报", [SourceItem(title="A", url="https://a")], [], []))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
