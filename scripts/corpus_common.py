from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "references" / "corpus"
INDEX_JSONL = CORPUS / "index.jsonl"
INDEX_CSV = CORPUS / "index.csv"

FIELDS = [
    "source_id", "title", "publication_date", "source_origin_type", "access_type",
    "publisher", "author", "speaker", "original_url", "official_url",
    "original_publication", "original_authors", "original_date",
    "fund_name", "fund_code", "reporting_period", "manager_signed",
    "source_quality", "content_scope", "subject_confirmed",
    "relevant_excerpt", "summary", "topic_tags",
    "retrieval_date", "date_accessed", "language",
    "verification_status", "copyright_note", "local_file", "content_checksum",
    # deprecated V0 fields — preserved for backward compatibility
    "deprecated_source_type", "deprecated_primary_source",
]

V1_ORIGIN_TYPES = {
    "official_report", "original_interview", "authorized_reprint",
    "ordinary_reprint", "official_profile", "other",
}

V1_ACCESS_TYPES = {
    "official_site", "third_party_reprint", "pdf_download", "other",
}

V1_QUALITY_TIERS = {"A", "B", "C", "D"}

V1_CONTENT_SCOPES = {"full_text", "excerpt", "abstract_only"}

V1_SUBJECT_CONFIRMED = {"confirmed", "inferred", "unconfirmed"}

SOURCE_ID_RE = re.compile(r"^JZC-\d{4}-[A-Z0-9-]+-\d{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_SCHEMES = {"http", "https"}
VERIFICATION = {"verified", "metadata_only", "pending", "restricted", "failed", "inaccessible", "rejected"}


def read_records(path: Path = INDEX_JSONL) -> list[dict]:
    records = []
    if not path.exists():
        return records
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            item = json.loads(line)
            item["_line"] = number
            records.append(item)
    return records


def clean_record(record: dict) -> dict:
    list_fields = {"topic_tags"}
    out = {}
    for field in FIELDS:
        if field in list_fields:
            out[field] = record.get(field, [])
        else:
            out[field] = record.get(field, "")
    return out


def valid_url(value: str) -> bool:
    if not value:
        return True
    parsed = urlparse(value)
    return parsed.scheme in URL_SCHEMES and bool(parsed.netloc)


def sha256_file(relative_path: str) -> str:
    if not relative_path:
        return ""
    path = ROOT / relative_path
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(records: list[dict], path: Path = INDEX_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for record in records:
            row = clean_record(record)
            row["topic_tags"] = "|".join(row["topic_tags"])
            writer.writerow(row)
