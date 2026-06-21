from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from corpus_common import (
    CORPUS, DATE_RE, FIELDS, ROOT, SOURCE_ID_RE, VERIFICATION,
    V1_ORIGIN_TYPES, V1_ACCESS_TYPES, V1_QUALITY_TIERS, V1_CONTENT_SCOPES,
    V1_SUBJECT_CONFIRMED,
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

        # Required fields presence
        missing = [field for field in FIELDS if field not in item]
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(missing)}")

        # ID format
        if not SOURCE_ID_RE.fullmatch(item.get("source_id", "")):
            errors.append(f"{label}: invalid source_id format")

        # Dates
        for field in ("publication_date", "retrieval_date", "date_published", "date_accessed"):
            value = item.get(field, "")
            if not DATE_RE.fullmatch(value):
                errors.append(f"{label}: invalid {field}: {value!r}")

        # URLs
        for field in ("original_url", "official_url"):
            if not valid_url(item.get(field, "")):
                errors.append(f"{label}: invalid {field}")

        # Verification status
        if item.get("verification_status") not in VERIFICATION:
            errors.append(f"{label}: invalid verification_status: {item.get('verification_status')!r}")

        # V1: source origin type
        so_type = item.get("source_origin_type", "")
        if so_type not in V1_ORIGIN_TYPES:
            errors.append(f"{label}: invalid source_origin_type: {so_type!r}")

        # V1: access type
        acc_type = item.get("access_type", "")
        if acc_type not in V1_ACCESS_TYPES:
            errors.append(f"{label}: invalid access_type: {acc_type!r}")

        # V1: source quality
        quality = item.get("source_quality", "")
        if quality not in V1_QUALITY_TIERS:
            errors.append(f"{label}: invalid source_quality: {quality!r}")

        # V1: content scope
        scope = item.get("content_scope", "")
        if scope not in V1_CONTENT_SCOPES:
            errors.append(f"{label}: invalid content_scope: {scope!r}")

        # V1: subject confirmed
        subj = item.get("subject_confirmed", "")
        if subj not in V1_SUBJECT_CONFIRMED:
            errors.append(f"{label}: invalid subject_confirmed: {subj!r}")

        # topic_tags
        if not isinstance(item.get("topic_tags"), list) or not item.get("topic_tags"):
            errors.append(f"{label}: topic_tags must be a non-empty list")

        # excerpt length
        excerpt = item.get("relevant_excerpt", "")
        if len(excerpt) > args.max_excerpt_chars:
            errors.append(f"{label}: excerpt is {len(excerpt)} chars (limit {args.max_excerpt_chars})")

        # local file
        local_file = item.get("local_file", "")
        if local_file and not (ROOT / local_file).is_file():
            errors.append(f"{label}: local_file does not exist: {local_file}")

        # checksum
        actual = sha256_file(local_file)
        if actual and item.get("content_checksum") != actual:
            errors.append(f"{label}: content_checksum mismatch")

        # verification warning
        if item.get("verification_status") not in ("verified",):
            warnings.append(f"{label}: evidence not fully verified ({item.get('verification_status')})")

        # Consistency checks between V1 fields
        if so_type == "ordinary_reprint" and not item.get("original_publication"):
            warnings.append(f"{label}: ordinary_reprint without original_publication")
        if item.get("verification_status") == "verified" and scope != "full_text":
            warnings.append(f"{label}: verified but content_scope is {scope}, expected full_text")

    # Duplicate IDs
    for value, count in Counter(ids).items():
        if value and count > 1:
            errors.append(f"duplicate source_id: {value} ({count})")

    # Cross-file references
    known = set(ids)
    for path in [ROOT / "references" / "timeline.md", ROOT / "references" / "method.md"]:
        if not path.exists():
            errors.append(f"missing reference file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for ref in sorted(set(REFERENCE_RE.findall(text)) - known):
            errors.append(f"{path.relative_to(ROOT)}: unknown source_id {ref}")

    # Summary
    verified_count = sum(x.get("verification_status") == "verified" for x in records)
    quality_dist = Counter(x.get("source_quality", "?") for x in records)
    print(f"records={len(records)} verified={verified_count} quality={dict(quality_dist)}")
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
