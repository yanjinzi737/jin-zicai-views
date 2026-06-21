from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    errors = []
    checked = 0
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            checked += 1
            local = (path.parent / target).resolve()
            if not local.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing {target}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"PASS: {checked} local Markdown links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
