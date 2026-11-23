#!/usr/bin/env python3
"""secret_scan.py - fail-closed secret / privacy scan for this repository.

Scans tracked-style text files for:
  - private key blocks, cloud / GitHub / OpenAI-style tokens
  - generic secret assignments (api_key / secret / password / token)
  - internal IPv4 ranges (10/8, 172.16/12, 192.168/16)
  - local absolute paths (Windows drive paths, /home, /Users)
  - e-mail addresses
  - bid / agent identifiers written as key:value pairs
  - optional deny literals passed on the command line (never stored in repo)
  - non-ASCII file names

Usage:
  python scripts/secret_scan.py
  python scripts/secret_scan.py --deny-literal <value> [--deny-literal <value> ...]

Exit codes:
  0  no hit
  1  at least one hit
  2  usage / IO error
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # pragma: no cover
        pass

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea"}
SKIP_NAMES = {".env", ".env.local", ".env.production", "MANIFEST.sha256"}
TEXT_EXTS = {
    ".md", ".py", ".json", ".ps1", ".txt", ".yml", ".yaml", ".csv", ".log",
    ".html", ".js", ".ts", ".sh", ".cfg", ".toml", ".ini", ".sql",
}

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    (
        "generic-secret-assignment",
        re.compile(r"(?i)\b(?:api[_-]?key|secret|password|passwd|access[_-]?token)\b\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']"),
    ),
    (
        "internal-ipv4",
        re.compile(
            r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|192\.168\.\d{1,3}\.\d{1,3}"
            r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
        ),
    ),
    (
        "local-abs-path",
        re.compile(r"(?i)(?:[a-z]:[\\/](?:users|documents and settings|awkn-lab)[\\/]|/(?:home|users)/[a-z0-9._-]+/)"),
    ),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("bid-identifier", re.compile(r"(?i)\bbid(?:[_-]?(?:id|no|number))?\b\s*[:=#]?\s*\d{2,}")),
    ("agent-identifier", re.compile(r"(?i)\bagent[_-]?(?:id|no|number)\b\s*[:=]\s*[\"']?[A-Za-z0-9_-]{3,}")),
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_NAMES or path.suffix.lower() not in TEXT_EXTS:
            continue
        files.append(path)
    return sorted(files)


def scan_text(text: str) -> list[tuple[str, int, str]]:
    hits: list[tuple[str, int, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for name, pattern in PATTERNS:
            if pattern.search(line):
                hits.append((name, lineno, line.strip()[:160]))
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed secret / privacy scan")
    parser.add_argument("--deny-literal", action="append", default=[], help="extra literal that must not appear")
    parser.add_argument("--skip-ascii-check", action="store_true", help="do not fail on non-ASCII file names")
    args = parser.parse_args(argv)

    hits: list[str] = []
    files = iter_files()
    scanned = 0

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if not args.skip_ascii_check and any(ord(ch) > 127 for ch in rel):
            hits.append(f"non-ascii-name {rel}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            hits.append(f"non-utf8-text {rel}")
            continue
        scanned += 1
        for name, lineno, line in scan_text(text):
            hits.append(f"{name} {rel}:{lineno}: {line}")
        for literal in args.deny_literal:
            if literal and literal in text:
                hits.append(f"deny-literal {rel}: contains supplied deny literal")
        for literal in args.deny_literal:
            if literal and literal in rel:
                hits.append(f"deny-literal {rel}: file name contains supplied deny literal")

    print(f"SECRET-SCAN files={scanned} deny_literals={len(args.deny_literal)} hits={len(hits)}")
    for hit in hits:
        print(f"  HIT {hit}")
    if hits:
        print("RESULT fail")
        return 1
    print("RESULT pass (0 hits)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
