from __future__ import annotations

import argparse
import re
from collections import defaultdict
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from corpus_common import read_records

TRACKING_PREFIXES = ("utm_", "spm", "from", "source", "share")


def canonical_url(url: str) -> str:
    if not url:
        return ""
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if not k.lower().startswith(TRACKING_PREFIXES)]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))


def normalized_title(value: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", value.lower())


def main() -> int:
    parser = argparse.ArgumentParser(description="Find duplicate originals, mirrors, and near-identical titles.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any duplicate candidate is found.")
    args = parser.parse_args()
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)
    records = read_records()
    for item in records:
        for field in ("official_url", "original_url"):
            value = canonical_url(item.get(field, ""))
            if value:
                buckets[(field, value)].append(item["source_id"])
        buckets[("title", normalized_title(item.get("title", "")))].append(item["source_id"])

    duplicates = [(kind, value, ids) for (kind, value), ids in buckets.items() if value and len(set(ids)) > 1]
    for kind, value, ids in duplicates:
        print(f"DUPLICATE-CANDIDATE {kind}: {', '.join(sorted(set(ids)))} :: {value}")
    if not duplicates:
        print(f"PASS: no duplicate candidates among {len(records)} records")
        return 0
    return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
