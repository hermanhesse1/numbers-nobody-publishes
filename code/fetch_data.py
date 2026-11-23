"""Check, and optionally download, the large inputs listed in data/manifest.csv.

  python3 code/fetch_data.py              verify sizes and SHA-256 of files present
  python3 code/fetch_data.py --download   also download missing files that have a URL
"""
import csv
import hashlib
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.csv"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def download(url, dest, expected_bytes):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    # data.gov.ro has cut downloads short while reporting success, so size is checked before keeping the file.
    if tmp.stat().st_size != expected_bytes:
        print(f"  size {tmp.stat().st_size:,} differs from {expected_bytes:,}: truncated or a newer snapshot")
    tmp.replace(dest)


def main():
    fetch = "--download" in sys.argv
    bad = 0
    for row in csv.DictReader(open(MANIFEST, encoding="utf-8")):
        path, size = ROOT / row["path"], int(row["bytes"])
        if not path.exists():
            if fetch and row["url"].startswith("http"):
                print(f"downloading {row['path']}")
                download(row["url"], path, size)
            else:
                print(f"MISSING  {row['path']}  <- {row['url']}")
                bad += 1
                continue
        if path.stat().st_size != size:
            print(f"SIZE     {row['path']}: {path.stat().st_size:,} bytes, manifest {size:,}")
            bad += 1
        elif sha256(path) != row["sha256"]:
            print(f"CHECKSUM {row['path']}: same size, different content, so a different snapshot")
            bad += 1
        else:
            print(f"ok       {row['path']}")
    print("all inputs match the manifest" if not bad else f"{bad} input(s) differ; outputs may not reproduce")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
