"""Download/checksum the public AZT1D V1 archive; extract CSVs only under ignored data."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
FILE_API = "https://data.mendeley.com/public-api/datasets/gk9m674wcx/files?folder_id=root&version=1"


def extract_csvs(archive: Path, destination: Path) -> int:
    base = destination.resolve()
    base.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(archive) as source:
        for member in source.infolist():
            if not member.filename.lower().endswith(".csv") or member.filename.startswith(
                "__MACOSX/"
            ):
                continue
            target = (base / member.filename).resolve()
            if not target.is_relative_to(base) or member.file_size > 100_000_000:
                raise ValueError("archive member escapes destination or exceeds file-size limit")
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open(member) as reader, target.open("wb") as writer:
                while chunk := reader.read(1024 * 1024):
                    writer.write(chunk)
            count += 1
    return count


def main():
    destination = ROOT / "data/raw/azt1d-v1"
    destination.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        response = client.get(FILE_API)
        response.raise_for_status()
        items = response.json()
        if len(items) != 1:
            raise ValueError("expected the single pinned V1 archive")
        details = items[0]["content_details"]
        expected = details["sha256_hash"]
        archive = destination / "source.zip"
        if not archive.exists():
            with client.stream("GET", details["download_url"]) as stream:
                stream.raise_for_status()
                with archive.open("wb") as target:
                    size = 0
                    for chunk in stream.iter_bytes(4 * 1024 * 1024):
                        size += len(chunk)
                        if size > 1_000_000_000:
                            raise ValueError("archive exceeds declared download limit")
                        target.write(chunk)
        with archive.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        if digest != expected or archive.stat().st_size != details["size"]:
            raise ValueError("archive checksum or byte-size mismatch")
    count = extract_csvs(archive, destination / "csv")
    provenance = {
        "doi": "10.17632/gk9m674wcx.1",
        "version": 1,
        "license": "CC BY 4.0",
        "sha256": digest,
        "archive_bytes": archive.stat().st_size,
        "extracted_csv_count": count,
        "role": "reserved_external_test_no_training",
        "metadata_url": FILE_API,
    }
    (destination / "provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(provenance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
