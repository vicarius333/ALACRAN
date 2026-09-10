#!/usr/bin/env python3
"""Download and verify the authorized Ethiopian Ge'ez source.

ALACRAN policy:
- Ge'ez manuscript text is the primary corpus candidate.
- Transliteration, English, glosses and project claims are kept outside
  the primary textual layer.
- The source file is never committed to ALACRAN; only its manifest is.
- Verification uses both the source Git blob SHA and a local SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_MANIFEST = Path("BIBLIA/input/ETHIOPIAN_BIBLE/SOURCE_MANIFEST.json")
DEFAULT_OUTPUT = Path("BIBLIA/input/ETHIOPIAN_BIBLE/SOURCE/geez-complete.md")
CHUNK_SIZE = 1024 * 1024


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def git_blob_sha(path: Path) -> str:
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
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
        with urllib.request.urlopen(request, timeout=180) as response, temp.open("wb") as out:
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

    url = manifest.get("raw_url")
    expected_git_sha = manifest.get("git_blob_sha")
    expected_sha256 = manifest.get("sha256")

    if not url or not expected_git_sha or not expected_sha256:
        raise SystemExit("ERROR: manifiesto incompleto. INGESTA BLOQUEADA.")

    print(f"FUENTE: {url}")
    print(f"DESTINO LOCAL: {output_path}")
    print("DESCARGANDO TEXTO GE'EZ PRIMARIO...")
    download(url, output_path)

    actual_git_sha = git_blob_sha(output_path)
    actual_sha256 = sha256(output_path)
    print(f"GIT-BLOB-SHA OBTENIDO: {actual_git_sha}")
    print(f"SHA-256 OBTENIDO: {actual_sha256}")

    if actual_git_sha.lower() != expected_git_sha.lower():
        output_path.unlink(missing_ok=True)
        raise SystemExit("ERROR: Git blob SHA no coincide. Archivo eliminado. INGESTA BLOQUEADA.")

    if actual_sha256.lower() != expected_sha256.lower():
        output_path.unlink(missing_ok=True)
        raise SystemExit("ERROR: SHA-256 no coincide. Archivo eliminado. INGESTA BLOQUEADA.")

    print("VERIFICACION: OK")
    print("ESTADO: FUENTE_GEEZ_LOCAL_VALIDADA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
