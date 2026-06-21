"""
Migrate corpus index.jsonl from V0 source_type to V1 source_origin_type + access_type.

V0 problem: source_type conflates content origin with access method.
  - "authoritative_media_interview" = origin (interview) + quality judgment (authoritative)
  - "media_interview_reprint" = origin (interview) + access (reprint)
  - JZC-2022-INTERVIEW-004 was "media_interview_reprint" but treated as primary_source

V1 fix: separate three axes:
  - source_origin_type: what the indexed source IS (official_report, original_interview, ...)
  - access_type: how we got it (official_site, third_party_reprint, pdf_download, ...)
  - source_quality: evidence tier derived from content provenance (A/B/C/D)

Usage:
  python scripts/migrate_v1_source_type.py           # dry-run: show changes
  python scripts/migrate_v1_source_type.py --apply   # write changes to index.jsonl + index.csv
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_JSONL = ROOT / "references" / "corpus" / "index.jsonl"
INDEX_CSV = ROOT / "references" / "corpus" / "index.csv"

# ── mapping tables ──────────────────────────────────────────────────

SOURCE_TYPE_TO_ORIGIN: dict[str, str] = {
    "fund_annual_report": "official_report",
    "fund_interim_report": "official_report",
    "fund_quarterly_report": "official_report",
    "authoritative_media_interview": "original_interview",
    "media_interview_reprint": "ordinary_reprint",
}

SOURCE_TYPE_TO_ACCESS: dict[str, str] = {
    "fund_annual_report": "pdf_download",
    "fund_interim_report": "pdf_download",
    "fund_quarterly_report": "pdf_download",
    "authoritative_media_interview": "official_site",
    "media_interview_reprint": "third_party_reprint",
}

# Content provenance quality, independent of access method or verification
def derive_source_quality(record: dict) -> str:
    """A=official filing, B=original interview, C=reprint/other, D=unattributable"""
    origin = record.get("source_origin_type", "")
    if origin == "official_report":
        return "A"
    if origin == "original_interview":
        return "B"
    if origin == "ordinary_reprint":
        # If it reprints an original interview with known provenance, upgrade to B
        if record.get("original_publication") and record.get("original_authors"):
            return "B"
        return "C"
    if origin in ("authorized_reprint", "official_profile"):
        return "B"
    return "D"


# ── per-record overrides for fields the mapping table can't infer ──

OVERRIDES: dict[str, dict] = {
    "JZC-2022-INTERVIEW-004": {
        "source_origin_type": "ordinary_reprint",
        "access_type": "third_party_reprint",
        "original_publication": "证券时报",
        "original_authors": "詹晨、赵梦桥",
        "original_date": "2022-08-02",
        "original_url": "https://stcn.com/article/detail/787283.html",
        "source_quality": "B",  # content is original interview, verified
    },
}


# ── helpers ──────────────────────────────────────────────────────────

def read_records(path: Path) -> list[dict]:
    records = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def write_records(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def migrate_record(record: dict) -> dict:
    """Return a new record with V1 fields added; old fields preserved as deprecated_*."""
    new = deepcopy(record)

    source_id = record.get("source_id", "")
    old_source_type = record.get("source_type", "")

    # Apply overrides first, fall back to mapping tables
    override = OVERRIDES.get(source_id, {})

    new["source_origin_type"] = override.get(
        "source_origin_type",
        SOURCE_TYPE_TO_ORIGIN.get(old_source_type, "other"),
    )
    new["access_type"] = override.get(
        "access_type",
        SOURCE_TYPE_TO_ACCESS.get(old_source_type, "other"),
    )

    # Original provenance (for reprints)
    new["original_publication"] = override.get(
        "original_publication",
        record.get("original_publication", ""),
    )
    new["original_authors"] = override.get(
        "original_authors",
        record.get("original_authors", ""),
    )
    new["original_date"] = override.get(
        "original_date",
        record.get("original_date", ""),
    )
    new["original_url"] = override.get(
        "original_url",
        record.get("original_url", ""),
    )

    # For original_interview records, the publisher IS the original publication
    if new["source_origin_type"] == "original_interview" and not new["original_publication"]:
        new["original_publication"] = record.get("publisher", "")
        new["original_authors"] = record.get("author", "")

    # Source quality
    new["source_quality"] = override.get(
        "source_quality",
        derive_source_quality(new),
    )

    # Content scope
    if record.get("verification_status") == "verified":
        new["content_scope"] = "full_text"
    elif record.get("local_file"):
        new["content_scope"] = "excerpt"
    else:
        new["content_scope"] = "abstract_only"

    # Subject confirmation
    new["subject_confirmed"] = (
        "confirmed"
        if record.get("manager_signed") in ("confirmed",)
        else "inferred"
        if record.get("verification_status") == "verified"
        else "unconfirmed"
    )

    # Dates
    new["date_published"] = record.get("publication_date", "")
    new["date_accessed"] = record.get("retrieval_date", "")
    new["language"] = "zh-CN"

    # Demote old fields — remove from active use, preserve as deprecated_
    old_source_type = new.pop("source_type", "")
    new["deprecated_source_type"] = old_source_type
    if "primary_source" in new:
        new["deprecated_primary_source"] = new.pop("primary_source")

    return new


def validate_migration(original: list[dict], migrated: list[dict]) -> list[str]:
    """Return list of validation errors (empty = clean)."""
    errors = []
    if len(migrated) != len(original):
        errors.append(f"Record count mismatch: {len(original)} → {len(migrated)}")
    for rec in migrated:
        sid = rec.get("source_id", "???")
        if "source_origin_type" not in rec:
            errors.append(f"{sid}: missing source_origin_type")
        if "source_quality" not in rec:
            errors.append(f"{sid}: missing source_quality")
        if "access_type" not in rec:
            errors.append(f"{sid}: missing access_type")
        if rec.get("source_origin_type") not in {
            "official_report", "original_interview", "authorized_reprint",
            "ordinary_reprint", "official_profile", "other",
        }:
            errors.append(f"{sid}: invalid source_origin_type: {rec.get('source_origin_type')}")
    return errors


# ── main ─────────────────────────────────────────────────────────────

def main():
    apply_flag = "--apply" in sys.argv

    print("Reading index.jsonl...")
    original = read_records(INDEX_JSONL)
    print(f"  {len(original)} records found\n")

    migrated = [migrate_record(r) for r in original]

    # Show changes
    for orig, mig in zip(original, migrated):
        sid = orig["source_id"]
        old_st = orig.get("source_type", "")
        new_so = mig.get("source_origin_type", "")
        new_at = mig.get("access_type", "")
        new_sq = mig.get("source_quality", "")
        old_ps = orig.get("primary_source", "")
        print(f"{sid}:")
        print(f"  source_type:       {old_st} → source_origin_type={new_so}, access_type={new_at}")
        print(f"  source_quality:    {new_sq}")
        if old_ps:
            print(f"  primary_source:    {old_ps} → (removed, derived from source_quality={new_sq})")
        if mig.get("original_publication"):
            print(f"  original_pub:      {mig['original_publication']} / {mig.get('original_authors', '')}")
        print()

    # Validate
    errors = validate_migration(original, migrated)
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
        if apply_flag:
            print("\nABORTING: fix errors before --apply")
            sys.exit(1)
    else:
        print("Validation: OK")

    if apply_flag:
        print("\nWriting migrated records...")
        write_records(migrated, INDEX_JSONL)

        # Regenerate CSV
        from corpus_common import write_csv as rebuild_csv
        rebuild_csv(migrated, INDEX_CSV)
        print(f"  index.jsonl: {INDEX_JSONL}")
        print(f"  index.csv:   {INDEX_CSV}")
        print("Done. Verify with: python scripts/validate_corpus.py")
    else:
        print("Dry run. Use --apply to write changes.")


if __name__ == "__main__":
    main()
