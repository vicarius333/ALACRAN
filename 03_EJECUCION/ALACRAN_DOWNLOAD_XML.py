#!/usr/bin/env python3
"""Download and verify the authorized HebrewBible.xml source.

The manifest SHA is the Git blob SHA, not a plain SHA-256 digest.
The original XML is never committed to ALACRAN.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_MANIFEST = Path("BIBLIA/FUENTE_XML_MANIFIESTO.json")
DEFAULT_OUTPUT = Path("BIBLIA/input/HebrewBible.xml")
CHUNK_SIZE = 1024 * 1024


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def git_blob_sha256(path: Path) -> str:
    size = path.stat().st_size
    digest = hashlib.sha1()
    digest.update(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "ALACRAN-corpus-ingestor/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temp.open("wb") as out:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                out.write(chunk)
        temp.replace(destination)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise


def main() -> int:
    manifest_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MANIFEST
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    manifest = load_manifest(manifest_path)
    url = manifest.get("raw_url") or manifest.get("url")
    expected_sha = manifest.get("sha")

    if not url or not expected_sha:
        raise SystemExit("ERROR: URL o SHA ausente en el manifiesto. INGESTA BLOQUEADA.")

    print(f"FUENTE: {url}")
    print(f"DESTINO LOCAL: {output_path}")
    print("DESCARGANDO...")
    download(url, output_path)

    actual_sha = git_blob_sha256(output_path)
    print(f"GIT-BLOB-SHA OBTENIDO: {actual_sha}")
    print(f"GIT-BLOB-SHA DECLARADO: {expected_sha}")

    if actual_sha.lower() != expected_sha.lower():
        output_path.unlink(missing_ok=True)
        raise SystemExit("ERROR: Git blob SHA no coincide. Archivo eliminado. INGESTA BLOQUEADA.")

    print("VERIFICACION: OK")
    print("ESTADO: FUENTE_LOCAL_VALIDADA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
