from __future__ import annotations

import argparse
import ssl
import urllib.error
import urllib.request

from corpus_common import read_records, valid_url


def main() -> int:
    parser = argparse.ArgumentParser(description="Check corpus URL format and optionally make online HEAD/GET requests.")
    parser.add_argument("--online", action="store_true", help="Perform network requests; default is format-only.")
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()
    failures = []
    checked = set()

    for item in read_records():
        for field in ("original_url", "official_url"):
            url = item.get(field, "")
            if not url or url in checked:
                continue
            checked.add(url)
            if not valid_url(url):
                failures.append(f"{item['source_id']} {field}: malformed URL")
                continue
            if not args.online:
                continue
            request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "jin-zicai-views/0.1"})
            try:
                with urllib.request.urlopen(request, timeout=args.timeout, context=ssl.create_default_context()) as response:
                    print(f"OK {response.status} {url}")
            except urllib.error.HTTPError as exc:
                if exc.code in {403, 405}:
                    try:
                        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-0"})
                        with urllib.request.urlopen(request, timeout=args.timeout) as response:
                            print(f"OK {response.status} {url}")
                            continue
                    except Exception as retry_exc:
                        failures.append(f"{url}: {retry_exc}")
                else:
                    failures.append(f"{url}: HTTP {exc.code}")
            except Exception as exc:
                failures.append(f"{url}: {exc}")

    for failure in failures:
        print(f"ERROR: {failure}")
    if failures:
        return 1
    mode = "online" if args.online else "format-only"
    print(f"PASS: {len(checked)} unique URLs ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
