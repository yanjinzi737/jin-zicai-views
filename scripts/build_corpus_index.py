from __future__ import annotations

import argparse
import json

from corpus_common import INDEX_JSONL, clean_record, read_records, sha256_file, write_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize JSONL and rebuild corpus CSV index.")
    parser.add_argument("--check", action="store_true", help="Do not write; report whether normalization is needed.")
    args = parser.parse_args()

    records = [clean_record(item) for item in read_records()]
    records.sort(key=lambda item: (item["publication_date"], item["source_id"]))
    for item in records:
        checksum = sha256_file(item["local_file"])
        if checksum:
            item["content_checksum"] = checksum

    rendered = "".join(json.dumps(item, ensure_ascii=False, sort_keys=False) + "\n" for item in records)
    current = INDEX_JSONL.read_text(encoding="utf-8") if INDEX_JSONL.exists() else ""
    if args.check:
        if rendered != current:
            print("FAIL: index.jsonl needs normalization or checksum refresh")
            return 1
        print(f"PASS: {len(records)} normalized records")
        return 0

    INDEX_JSONL.parent.mkdir(parents=True, exist_ok=True)
    INDEX_JSONL.write_text(rendered, encoding="utf-8")
    write_csv(records)
    print(f"WROTE: {len(records)} records to index.jsonl and index.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
