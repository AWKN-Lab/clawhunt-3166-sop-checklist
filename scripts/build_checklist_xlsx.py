#!/usr/bin/env python3
"""Build docs/CHECKLIST.xlsx from docs/CHECKLIST.md (single source of truth).

ASCII filename required by ticket. No network, no external data.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
except ImportError:  # pragma: no cover
    print("ERROR: openpyxl is required (pip install openpyxl)", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "CHECKLIST.md"
XLSX_PATH = ROOT / "docs" / "CHECKLIST.xlsx"

GROUP_RE = re.compile(r"^## ([A-D]) 组[ ·]+(.+)$")
ROW_RE = re.compile(r"^\| ([A-D]\d{1,2}) \|(.+)\|\s*$")
ITEM_ID_RE = re.compile(r"^[A-D][1-6]$")


def parse_markdown() -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    groups: list[str] = []
    current_group = ""
    for raw in MD_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        m = GROUP_RE.match(line)
        if m:
            current_group = f"{m.group(1)} 组 · {m.group(2).strip()}"
            groups.append(current_group)
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        item_id = m.group(1)
        if not ITEM_ID_RE.match(item_id):
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        if len(cells) != 5:
            raise SystemExit(f"ERROR: row {item_id} has {len(cells)} cells, expected 5")
        rows.append(
            {
                "id": item_id,
                "group": current_group,
                "item": cells[0],
                "criteria": cells[1],
                "method": cells[2],
                "role": cells[3],
                "on_fail": cells[4],
            }
        )
    return rows, groups


def main() -> int:
    rows, groups = parse_markdown()
    if len(rows) != 24:
        raise SystemExit(f"ERROR: parsed {len(rows)} items, expected 24")
    if len(groups) != 4:
        raise SystemExit(f"ERROR: parsed {len(groups)} groups, expected 4")

    wb = Workbook()
    ws = wb.active
    ws.title = "Checklist"
    headers = ["ID", "组别", "检查项", "判定标准", "核对方式", "责任角色", "不通过处置"]
    ws.append(headers)
    for row in rows:
        ws.append(
            [
                row["id"],
                row["group"],
                row["item"],
                row["criteria"],
                row["method"],
                row["role"],
                row["on_fail"],
            ]
        )

    head_fill = PatternFill("solid", fgColor="1F4E78")
    head_font = Font(color="FFFFFF", bold=True)
    for cell in ws[1]:
        cell.fill = head_fill
        cell.font = head_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    widths = [8, 26, 22, 52, 14, 12, 44]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = width
    for row_cells in ws.iter_rows(min_row=2):
        for cell in row_cells:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:G{ws.max_row}"

    meta = wb.create_sheet("Legend")
    meta.append(["项", "值"])
    meta.append(["检查表版本", "1.0.0"])
    meta.append(["项数", len(rows)])
    meta.append(["组数", len(groups)])
    meta.append(["三态", "pass / fail / manual（manual 不等于通过）"])
    meta.append(["配套脚本", "scripts/check_sop_release.py"])
    meta.append(["生成方式", "由 docs/CHECKLIST.md 解析生成，禁止手工双维护"])
    meta.column_dimensions["A"].width = 18
    meta.column_dimensions["B"].width = 68

    XLSX_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(XLSX_PATH)
    print(f"WROTE {XLSX_PATH.relative_to(ROOT).as_posix()} items={len(rows)} groups={len(groups)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
