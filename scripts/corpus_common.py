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
    "source_id", "title", "publication_date", "source_type", "publisher",
    "author", "speaker", "original_url", "official_url", "fund_name",
    "fund_code", "reporting_period", "primary_source", "manager_signed",
    "relevant_excerpt", "summary", "topic_tags", "retrieval_date",
    "verification_status", "copyright_note", "local_file", "content_checksum",
]

SOURCE_ID_RE = re.compile(r"^JZC-\d{4}-[A-Z0-9-]+-\d{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_SCHEMES = {"http", "https"}
VERIFICATION = {"verified", "metadata_only", "pending", "restricted", "failed"}


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
    return {field: record.get(field, [] if field == "topic_tags" else "") for field in FIELDS}


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
