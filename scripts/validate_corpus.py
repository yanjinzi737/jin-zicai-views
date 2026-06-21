from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from corpus_common import (
    CORPUS, DATE_RE, FIELDS, ROOT, SOURCE_ID_RE, VERIFICATION,
    read_records, sha256_file, valid_url,
)

REFERENCE_RE = re.compile(r"\bJZC-\d{4}-[A-Z0-9-]+-\d{3}\b")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate corpus schema and cross-file references.")
    parser.add_argument("--max-excerpt-chars", type=int, default=500)
    args = parser.parse_args()
    records = read_records()
    errors: list[str] = []
    warnings: list[str] = []
    ids = [item.get("source_id", "") for item in records]

    for item in records:
        label = item.get("source_id") or f"line {item.get('_line')}"
        missing = [field for field in FIELDS if field not in item]
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")
        if not SOURCE_ID_RE.fullmatch(item.get("source_id", "")):
            errors.append(f"{label}: invalid source_id format")
        for field in ("publication_date", "retrieval_date"):
            value = item.get(field, "")
            if not DATE_RE.fullmatch(value):
                errors.append(f"{label}: invalid {field}: {value!r}")
        for field in ("original_url", "official_url"):
            if not valid_url(item.get(field, "")):
                errors.append(f"{label}: invalid {field}")
        if item.get("verification_status") not in VERIFICATION:
            errors.append(f"{label}: invalid verification_status")
        if not isinstance(item.get("primary_source"), bool):
            errors.append(f"{label}: primary_source must be boolean")
        if not isinstance(item.get("topic_tags"), list) or not item.get("topic_tags"):
            errors.append(f"{label}: topic_tags must be a non-empty list")
        excerpt = item.get("relevant_excerpt", "")
        if len(excerpt) > args.max_excerpt_chars:
            errors.append(f"{label}: excerpt is {len(excerpt)} chars (limit {args.max_excerpt_chars})")
        local_file = item.get("local_file", "")
        if local_file and not (ROOT / local_file).is_file():
            errors.append(f"{label}: local_file does not exist: {local_file}")
        actual = sha256_file(local_file)
        if actual and item.get("content_checksum") != actual:
            errors.append(f"{label}: content_checksum mismatch")
        if item.get("verification_status") != "verified":
            warnings.append(f"{label}: evidence not fully verified ({item.get('verification_status')})")

    for value, count in Counter(ids).items():
        if value and count > 1:
            errors.append(f"duplicate source_id: {value} ({count})")

    known = set(ids)
    for path in [ROOT / "references" / "timeline.md", ROOT / "references" / "method.md"]:
        if not path.exists():
            errors.append(f"missing reference file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for ref in sorted(set(REFERENCE_RE.findall(text)) - known):
            errors.append(f"{path.relative_to(ROOT)}: unknown source_id {ref}")

    print(f"records={len(records)} verified={sum(x.get('verification_status') == 'verified' for x in records)}")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print("PASS: corpus schema, IDs, local files, checksums, excerpts, and references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
