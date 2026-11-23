#!/usr/bin/env python3
"""Verify the checklist deliverables against AC1.

Checks:
  - docs/CHECKLIST.md parses to exactly 24 items in 4 groups
  - every item has non-empty: item, criteria, method, role, on_fail
  - method is one of 自动 / 人工 / 自动（stub） / 自动（条件）/ 人工 (prefix match)
  - docs/CHECKLIST.xlsx has the same 24 IDs and 7 columns
Exit 0 when all good, 1 on any violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:  # pragma: no cover
    print("ERROR: openpyxl is required", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "CHECKLIST.md"
XLSX_PATH = ROOT / "docs" / "CHECKLIST.xlsx"

GROUP_RE = re.compile(r"^## ([A-D]) 组")
ROW_RE = re.compile(r"^\| ([A-D]\d{1,2}) \|(.+)\|\s*$")
ITEM_ID_RE = re.compile(r"^[A-D][1-6]$")


def parse_md() -> tuple[list[dict], int]:
    rows: list[dict] = []
    groups = 0
    for raw in MD_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if GROUP_RE.match(line):
            groups += 1
        m = ROW_RE.match(line)
        if not m or not ITEM_ID_RE.match(m.group(1)):
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        if len(cells) != 5:
            rows.append({"id": m.group(1), "cells": cells, "bad_shape": True})
            continue
        rows.append(
            {
                "id": m.group(1),
                "item": cells[0],
                "criteria": cells[1],
                "method": cells[2],
                "role": cells[3],
                "on_fail": cells[4],
                "bad_shape": False,
            }
        )
    return rows, groups


def main() -> int:
    errors: list[str] = []
    rows, groups = parse_md()
    if len(rows) != 24:
        errors.append(f"MD item count {len(rows)} != 24")
    if groups != 4:
        errors.append(f"MD group count {groups} != 4")
    expected_ids = [f"{g}{n}" for g in "ABCD" for n in range(1, 7)]
    got_ids = [r["id"] for r in rows]
    if sorted(got_ids) != sorted(expected_ids):
        errors.append(f"MD item ids mismatch: {got_ids}")
    for r in rows:
        if r.get("bad_shape"):
            errors.append(f"{r['id']}: column count != 5")
            continue
        for field in ("item", "criteria", "method", "role", "on_fail"):
            if not r[field]:
                errors.append(f"{r['id']}: empty field {field}")
        if not r["method"].startswith(("自动", "人工")):
            errors.append(f"{r['id']}: method not 自动/人工: {r['method']}")

    if not XLSX_PATH.exists():
        errors.append("missing docs/CHECKLIST.xlsx")
    else:
        wb = load_workbook(XLSX_PATH, read_only=True)
        ws = wb["Checklist"]
        data = list(ws.iter_rows(values_only=True))
        if not data:
            errors.append("xlsx empty")
        else:
            header = [str(c) if c is not None else "" for c in data[0]]
            if header != ["ID", "组别", "检查项", "判定标准", "核对方式", "责任角色", "不通过处置"]:
                errors.append(f"xlsx header mismatch: {header}")
            xlsx_ids = [str(row[0]) for row in data[1:] if row and row[0]]
            if sorted(xlsx_ids) != sorted(expected_ids):
                errors.append(f"xlsx ids mismatch: {xlsx_ids}")
            for row in data[1:]:
                if not row or not row[0]:
                    continue
                if any(v is None or str(v).strip() == "" for v in row[:7]):
                    errors.append(f"xlsx row {row[0]} has empty cell")

    if errors:
        for e in errors:
            print(f"FAIL {e}")
        print(f"RESULT fail errors={len(errors)}")
        return 1
    print(f"RESULT pass items={len(rows)} groups={groups} xlsx=ok missing_fields=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
