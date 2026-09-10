#!/usr/bin/env python3
"""Download and verify the authorized Ethiopian Ge'ez source.

ALACRAN policy:
- Ge'ez manuscript text is the primary corpus candidate.
- Transliteration, English, glosses and project claims stay outside it.
- The source file is not committed to ALACRAN; only provenance/manifests are.
- Verification uses the upstream Git blob SHA and computes a local SHA-256.
"""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_MANIFEST = Path("BIBLIA/input/ETHIOPIAN_BIBLE/SOURCE_MANIFEST.json")
DEFAULT_OUTPUT = Path("BIBLIA/input/ETHIOPIAN_BIBLE/SOURCE/geez-complete.md")
DEFAULT_VERIFICATION = Path("BIBLIA/input/ETHIOPIAN_BIBLE/VERIFICATION.json")
CHUNK_SIZE = 1024 * 1024

def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def git_blob_sha(path: Path) -> str:
    size = path.stat().st_size
    digest = hashlib.sha1()
    digest.update(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()

def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "ALACRAN-corpus-ingestor/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response, temp.open("wb") as out:
            while chunk := response.read(CHUNK_SIZE):
                out.write(chunk)
        temp.replace(destination)
    except Exception:
        temp.unlink(missing_ok=True)
        raise

def write_verification(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main() -> int:
    manifest_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MANIFEST
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    verification_path = Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_VERIFICATION
    manifest = load_manifest(manifest_path)
    url = manifest.get("raw_url")
    expected_git_sha = manifest.get("git_blob_sha")
    if not url or not expected_git_sha:
        raise SystemExit("ERROR: manifiesto incompleto. INGESTA BLOQUEADA.")
    print(f"FUENTE: {url}")
    print(f"DESTINO LOCAL: {output_path}")
    print("DESCARGANDO TEXTO GE'EZ PRIMARIO...")
    download(url, output_path)
    actual_git_sha = git_blob_sha(output_path)
    actual_sha256 = sha256(output_path)
    print(f"GIT-BLOB-SHA OBTENIDO: {actual_git_sha}")
    print(f"GIT-BLOB-SHA DECLARADO: {expected_git_sha}")
    print(f"SHA-256 LOCAL: {actual_sha256}")
    if actual_git_sha.lower() != expected_git_sha.lower():
        output_path.unlink(missing_ok=True)
        raise SystemExit("ERROR: Git blob SHA no coincide. Archivo eliminado. INGESTA BLOQUEADA.")
    write_verification(verification_path, {
        "source_id": manifest.get("source_id"),
        "status": "FUENTE_GEEZ_LOCAL_VALIDADA",
        "source_path": manifest.get("source_path"),
        "local_path": str(output_path),
        "git_blob_sha_expected": expected_git_sha,
        "git_blob_sha_obtained": actual_git_sha,
        "sha256_obtained": actual_sha256,
        "byte_size": output_path.stat().st_size,
        "interpretation": "NO REALIZADA",
        "translation_used_as_primary": False,
        "verified": True
    })
    print("VERIFICACION: OK")
    print("ESTADO: FUENTE_GEEZ_LOCAL_VALIDADA")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
