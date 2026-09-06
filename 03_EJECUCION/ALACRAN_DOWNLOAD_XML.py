#!/usr/bin/env python3
"""Download the authorized HebrewBible.xml source without storing it in ALACRAN.

The downloader is intentionally conservative:
- downloads only the URL declared in the source manifest
- streams to a local file
- verifies SHA-256 when the manifest contains one
- never modifies the source manifest
- fails closed on checksum mismatch
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


def download(url: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(destination.suffix + ".part")
    digest = hashlib.sha256()

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ALACRAN-corpus-ingestor/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response, temp.open("wb") as out:
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                out.write(chunk)
                digest.update(chunk)
        temp.replace(destination)
    except Exception:
        if temp.exists():
            temp.unlink()
        raise

    return digest.hexdigest()


def main() -> int:
    manifest_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MANIFEST
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    manifest = load_manifest(manifest_path)
    url = manifest.get("raw_url") or manifest.get("url")
    expected_sha = manifest.get("sha")

    if not url:
        raise SystemExit("ERROR: el manifiesto no contiene URL de descarga.")
    if not expected_sha:
        raise SystemExit("ERROR: el manifiesto no contiene SHA esperado; descarga bloqueada.")

    print(f"FUENTE: {url}")
    print(f"DESTINO LOCAL: {output_path}")
    print("DESCARGANDO...")
    actual_sha = download(url, output_path)
    print(f"SHA-256 OBTENIDO: {actual_sha}")
    print(f"SHA DECLARADO:    {expected_sha}")

    if actual_sha.lower() != expected_sha.lower():
        output_path.unlink(missing_ok=True)
        raise SystemExit("ERROR: SHA-256 no coincide. Archivo eliminado. INGESTA BLOQUEADA.")

    print("VERIFICACION: OK")
    print("ESTADO: FUENTE_LOCAL_VALIDADA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
