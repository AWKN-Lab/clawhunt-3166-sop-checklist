#!/usr/bin/env python3
"""build_manifest.py - build MANIFEST.sha256 for the deliverable tree.

Covers every deliverable file. Excluded on purpose:
  - .git, __pycache__, node_modules, virtualenvs
  - MANIFEST.sha256 itself (cannot hash itself)
  - evidence/*.log (runtime run logs are produced after the manifest and are
    excluded so the manifest stays stable; the raw task JSON is included)
  - .env* files

Usage:
  python scripts/build_manifest.py
  python scripts/build_manifest.py --root <clean-copy-dir> --output <path>

Verify with: pwsh -File scripts/verify_sha256.ps1
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
MANIFEST_NAME = "MANIFEST.sha256"


def included(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if path.name == MANIFEST_NAME:
        return False
    if path.name.startswith(".env"):
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    if any(part in SKIP_DIRS for part in rel.parts):
        return False
    if rel.parts and rel.parts[0] == "evidence" and path.suffix.lower() == ".log":
        return False
    return True


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(root: Path) -> list[str]:
    files = [p for p in root.rglob("*") if p.is_file() and included(p, root)]
    lines = []
    for path in sorted(files, key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        lines.append(f"{sha256(path)}  {rel}")
    return lines


def main(argv: list[str] | None = None) -> int:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Build MANIFEST.sha256")
    parser.add_argument("--root", default=str(default_root), help="tree to hash (default: repo root)")
    parser.add_argument("--output", help="output file (default: <root>/MANIFEST.sha256)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2
    output = Path(args.output) if args.output else root / MANIFEST_NAME
    lines = build(root)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"MANIFEST {output.name} files={len(lines)} root={root.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
