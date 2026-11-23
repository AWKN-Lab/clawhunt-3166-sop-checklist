#!/usr/bin/env python3
"""check_sop_release.py - SOP template pre-release automated checker.

Reads one SOP template version export JSON and reports per-item
pass / fail / manual. "manual" never counts as pass.

Usage:
  python scripts/check_sop_release.py samples/sample_pass.json
  python scripts/check_sop_release.py samples/sample_pass.json --format json
  python scripts/check_sop_release.py samples/sample_pass.json --report out.md
  python scripts/check_sop_release.py samples/sample_pass.json --dry-run
  python scripts/check_sop_release.py --self-test

Exit codes:
  0  no fail (pass or manual only)
  1  at least one fail
  2  usage / input / stub error

Requires Python 3.9+. No third-party dependency. No network.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # pragma: no cover
        pass

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KB_STUB = ROOT / "stubs" / "kb_articles.json"
DEFAULT_PROPOSAL_STUB = ROOT / "stubs" / "improvement_proposals.json"

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
STEP_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
FIELD_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
PLACEHOLDER_RE = re.compile(r"TODO|TBD|待补充|待定|占位|xxx|\?\?\?", re.IGNORECASE)
FIELD_TYPES = {"text", "textarea", "number", "select", "multi_select", "date", "datetime", "boolean", "file"}

CheckResult = tuple[str, str]
CheckFn = Callable[[dict, dict, dict], CheckResult]


def _steps(export: dict) -> list:
    steps = export.get("steps")
    return steps if isinstance(steps, list) else []


def _template(export: dict) -> dict:
    tpl = export.get("template")
    return tpl if isinstance(tpl, dict) else {}


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _field_keys(step: dict) -> list[str]:
    fields = step.get("form_fields")
    if not isinstance(fields, list):
        return []
    return [f.get("key") for f in fields if isinstance(f, dict) and isinstance(f.get("key"), str)]


def _collect_failures(steps: list, predicate: Callable[[dict], bool], label: str) -> CheckResult:
    bad = []
    for step in steps:
        if not isinstance(step, dict):
            bad.append("<non-object step>")
            continue
        if not predicate(step):
            bad.append(str(step.get("step_key") or step.get("title") or "<no-key>"))
    if bad:
        return "fail", f"{label} 不满足: {', '.join(bad)}"
    return "pass", f"{len(steps)} 个步骤均满足{label}"


# ---------------------------------------------------------------- A group
def check_a1(export: dict, kb: dict, props: dict) -> CheckResult:
    steps = _steps(export)
    if not steps:
        return "fail", "steps 为空"
    return _collect_failures(steps, lambda s: _nonempty_str(s.get("assigned_role")), "责任角色非空")


def check_a2(export: dict, kb: dict, props: dict) -> CheckResult:
    steps = _steps(export)
    if not steps:
        return "fail", "steps 为空"
    return _collect_failures(
        steps, lambda s: _nonempty_str(s.get("completion_criteria")) and len(s["completion_criteria"].strip()) >= 10, "完成标准(>=10字符)"
    )


def check_a3(export: dict, kb: dict, props: dict) -> CheckResult:
    steps = _steps(export)
    if not steps:
        return "fail", "steps 为空"

    def ok(step: dict) -> bool:
        mats = step.get("required_materials")
        return isinstance(mats, list) and len(mats) > 0 and all(_nonempty_str(m) for m in mats)

    return _collect_failures(steps, ok, "必需材料")


def check_a4(export: dict, kb: dict, props: dict) -> CheckResult:
    refs: list[tuple[str, str]] = []
    for step in _steps(export):
        if not isinstance(step, dict):
            continue
        for ref in step.get("referenced_kb_articles") or []:
            if isinstance(ref, str):
                refs.append((str(step.get("step_key") or "?"), ref))
    if not refs:
        return "pass", "未引用知识库文章"
    if not kb:
        return "manual", "KB stub 不可用，无法确认文章存在与发布状态"
    bad = []
    for step_key, ref in refs:
        entry = kb.get(ref)
        if not isinstance(entry, dict):
            bad.append(f"{step_key}->{ref}(不存在)")
        elif entry.get("status") != "published":
            bad.append(f"{step_key}->{ref}(状态={entry.get('status')})")
    if bad:
        return "fail", "知识库引用不合规: " + ", ".join(bad)
    return "pass", f"{len(refs)} 条知识库引用均存在且已发布"


def check_a5(export: dict, kb: dict, props: dict) -> CheckResult:
    bad = []
    for step in _steps(export):
        if not isinstance(step, dict):
            continue
        texts = [str(step.get("title") or ""), str(step.get("completion_criteria") or "")]
        mats = step.get("required_materials")
        if isinstance(mats, list):
            texts.extend(str(m) for m in mats)
        if any(PLACEHOLDER_RE.search(t) for t in texts):
            bad.append(str(step.get("step_key") or "<no-key>"))
    if bad:
        return "fail", "含占位内容: " + ", ".join(bad)
    return "pass", "未发现占位内容"


def check_a6(export: dict, kb: dict, props: dict) -> CheckResult:
    steps = [s for s in _steps(export) if isinstance(s, dict)]
    keys = {s.get("step_key") for s in steps if _nonempty_str(s.get("step_key"))}
    bad = []
    for step in steps:
        for pre in step.get("prerequisites") or []:
            if pre not in keys:
                bad.append(f"{step.get('step_key')}->{pre}")
    if bad:
        return "fail", "悬空前置依赖: " + ", ".join(bad)
    return "pass", f"{len(steps)} 个步骤的前置依赖均有效"


# ---------------------------------------------------------------- B group
def check_b1(export: dict, kb: dict, props: dict) -> CheckResult:
    steps = _steps(export)

    def ok(step: dict) -> bool:
        sla = step.get("sla_hours")
        return isinstance(sla, int) and not isinstance(sla, bool) and 0 < sla <= 240

    return _collect_failures(steps, ok, "SLA(1-240 整数)")


def check_b2(export: dict, kb: dict, props: dict) -> CheckResult:
    reviewers = _template(export).get("reviewers")
    if not isinstance(reviewers, list):
        return "fail", "reviewers 缺失"
    for rev in reviewers:
        if isinstance(rev, dict) and rev.get("role") == "frontline_rep" and rev.get("decision") == "approved":
            return "pass", f"一线代表 {rev.get('name', '<未署名>')} 已复核通过"
    return "fail", "缺少 role=frontline_rep 且 decision=approved 的复核记录"


def check_b3(export: dict, kb: dict, props: dict) -> CheckResult:
    roles = _template(export).get("roles")
    if not isinstance(roles, list) or not roles:
        return "manual", "template.roles 缺失，无法核对角色登记"
    allowed = {r for r in roles if isinstance(r, str)}
    bad = []
    for step in _steps(export):
        if not isinstance(step, dict):
            continue
        for field in ("assigned_role", "escalation_role"):
            value = step.get(field)
            if value and value not in allowed:
                bad.append(f"{step.get('step_key')}.{field}={value}")
    if bad:
        return "fail", "未登记角色: " + ", ".join(bad)
    return "pass", "责任与升级角色均已登记"


def check_b5(export: dict, kb: dict, props: dict) -> CheckResult:
    return _collect_failures(
        _steps(export),
        lambda s: _nonempty_str(s.get("exception_path")) and len(s["exception_path"].strip()) >= 5,
        "异常路径",
    )


def check_b4(export: dict, kb: dict, props: dict) -> CheckResult:
    hours = _template(export).get("club_operating_hours")
    if isinstance(hours, dict) and hours.get("start") and hours.get("end"):
        return "manual", f"营业时间 {hours.get('start')}-{hours.get('end')}，跨日/节假日/闭馆冲突需人工核对"
    return "manual", "未提供营业时间，无法自动判定，需人工核对"


def check_b6(export: dict, kb: dict, props: dict) -> CheckResult:
    steps = [s for s in _steps(export) if isinstance(s, dict)]
    graph: dict[str, list[str]] = {}
    for step in steps:
        key = step.get("step_key")
        if not _nonempty_str(key):
            continue
        graph[key] = [p for p in (step.get("prerequisites") or []) if p in graph or p in {s.get("step_key") for s in steps}]
    WHITE, GREY, BLACK = 0, 1, 2
    color = {k: WHITE for k in graph}

    def dfs(node: str, stack: list[str]) -> list[str] | None:
        color[node] = GREY
        stack.append(node)
        for nxt in graph.get(node, []):
            if nxt not in color:
                continue
            if color[nxt] == GREY:
                idx = stack.index(nxt) if nxt in stack else 0
                return stack[idx:] + [nxt]
            if color[nxt] == WHITE:
                found = dfs(nxt, stack)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return None

    for node in graph:
        if color[node] == WHITE:
            cycle = dfs(node, [])
            if cycle:
                return "fail", "存在循环依赖: " + " -> ".join(cycle)
    return "pass", "依赖图无环"


# ---------------------------------------------------------------- C group
def check_c1(export: dict, kb: dict, props: dict) -> CheckResult:
    keys = [s.get("step_key") for s in _steps(export) if isinstance(s, dict)]
    dup = sorted({k for k in keys if isinstance(k, str) and keys.count(k) > 1})
    if dup:
        return "fail", "重复 step_key: " + ", ".join(dup)
    return "pass", f"{len(keys)} 个 step_key 唯一"


def check_c2(export: dict, kb: dict, props: dict) -> CheckResult:
    bad = [str(s.get("step_key")) for s in _steps(export) if isinstance(s, dict) and not STEP_KEY_RE.match(str(s.get("step_key") or ""))]
    if bad:
        return "fail", "命名不合规: " + ", ".join(bad)
    return "pass", "step_key 命名均符合 UPPER_SNAKE"


def check_c3(export: dict, kb: dict, props: dict) -> CheckResult:
    bad = []
    for step in _steps(export):
        if not isinstance(step, dict):
            continue
        for field in step.get("form_fields") or []:
            if not isinstance(field, dict):
                bad.append(f"{step.get('step_key')}.<non-object>")
                continue
            key = field.get("key", "<no-key>")
            ftype = field.get("type")
            required = field.get("required")
            if ftype not in FIELD_TYPES:
                bad.append(f"{step.get('step_key')}.{key}.type={ftype!r}")
            if not isinstance(required, bool):
                bad.append(f"{step.get('step_key')}.{key}.required={required!r}")
    if bad:
        return "fail", "字段类型/必填标记缺失: " + ", ".join(bad)
    return "pass", "所有表单字段均有合法 type 与布尔 required"


def check_c4(export: dict, kb: dict, props: dict) -> CheckResult:
    metrics = _template(export).get("review_metrics")
    if not isinstance(metrics, list) or not metrics:
        return "manual", "未声明 review_metrics，无法确认复盘统计字段是否被删，需人工确认"
    existing = {k for step in _steps(export) if isinstance(step, dict) for k in _field_keys(step)}
    missing = []
    for metric in metrics:
        if not isinstance(metric, dict):
            continue
        field = metric.get("field")
        if field not in existing:
            missing.append(str(field))
    if missing:
        return "fail", "复盘统计依赖字段已缺失: " + ", ".join(missing)
    return "pass", f"{len(metrics)} 个复盘统计字段均存在"


def check_c5(export: dict, kb: dict, props: dict) -> CheckResult:
    tpl = _template(export)
    version = tpl.get("version")
    previous = tpl.get("previous_version")
    change_type = tpl.get("change_type")
    if not _nonempty_str(previous):
        return "manual", "缺少 previous_version，无法判断版本递增"
    if not _nonempty_str(version):
        return "fail", "version 缺失"
    m_new, m_old = SEMVER_RE.match(str(version)), SEMVER_RE.match(str(previous))
    if not m_new or not m_old:
        return "fail", f"版本号非 semver: version={version!r} previous={previous!r}"
    new = tuple(int(x) for x in m_new.groups())
    old = tuple(int(x) for x in m_old.groups())
    if new <= old:
        return "fail", f"新版本 {version} 未大于旧版本 {previous}"
    if change_type is None:
        return "manual", f"版本已递增({previous}->{version})，但缺少 change_type，无法核对递增位"
    if change_type == "breaking":
        ok = new[0] > old[0]
    elif change_type == "content":
        ok = new[0] == old[0] and new[1] > old[1]
    elif change_type == "fix":
        ok = new[0] == old[0] and new[1] == old[1] and new[2] > old[2]
    else:
        return "manual", f"未知 change_type={change_type!r}，需人工确认规则"
    if not ok:
        return "fail", f"change_type={change_type} 但递增位不符: {previous}->{version}"
    return "pass", f"{previous}->{version} 符合 change_type={change_type}"


def check_c6(export: dict, kb: dict, props: dict) -> CheckResult:
    bad = []
    for step in _steps(export):
        if not isinstance(step, dict):
            continue
        keys = _field_keys(step)
        dup = sorted({k for k in keys if keys.count(k) > 1})
        if dup:
            bad.append(f"{step.get('step_key')} 重复字段: {', '.join(dup)}")
        for key in keys:
            if not FIELD_KEY_RE.match(key):
                bad.append(f"{step.get('step_key')}.{key} 命名不合规")
    if bad:
        return "fail", "; ".join(bad)
    return "pass", "字段 key 唯一且命名合规"


# ---------------------------------------------------------------- D group
def check_d1(export: dict, kb: dict, props: dict) -> CheckResult:
    changelog = _template(export).get("changelog")
    if not isinstance(changelog, list) or not changelog or not all(_nonempty_str(x) for x in changelog):
        return "fail", "changelog 缺失或存在空条目"
    return "pass", f"{len(changelog)} 条变更记录"


def check_d2(export: dict, kb: dict, props: dict) -> CheckResult:
    linked = _template(export).get("linked_improvement_proposals")
    if not isinstance(linked, list) or not linked:
        return "pass", "未关联改进提案"
    if not props:
        return "manual", "提案 stub 不可用，无法确认提案状态"
    bad = []
    for pid in linked:
        entry = props.get(pid)
        if not isinstance(entry, dict):
            bad.append(f"{pid}(不存在)")
        elif entry.get("status") not in {"accepted", "scheduled"}:
            bad.append(f"{pid}(状态={entry.get('status')})")
    if bad:
        return "fail", "提案状态不合规: " + ", ".join(bad)
    return "pass", f"{len(linked)} 个关联提案均为 accepted/scheduled"


def check_d3(export: dict, kb: dict, props: dict) -> CheckResult:
    text = _template(export).get("release_notice")
    if not _nonempty_str(text) or len(text.strip()) < 20:
        return "fail", "发布通知缺失或不足 20 字符"
    return "pass", f"发布通知 {len(text.strip())} 字符"


def check_d4(export: dict, kb: dict, props: dict) -> CheckResult:
    text = _template(export).get("pilot_conclusion")
    if not _nonempty_str(text) or len(text.strip()) < 20:
        return "fail", "试运行结论缺失或不足 20 字符"
    return "pass", f"试运行结论 {len(text.strip())} 字符"


def check_d5(export: dict, kb: dict, props: dict) -> CheckResult:
    text = _template(export).get("rollback_plan")
    if not _nonempty_str(text) or len(text.strip()) < 20:
        return "fail", "回滚方案缺失或不足 20 字符"
    return "pass", f"回滚方案 {len(text.strip())} 字符"


def check_d6(export: dict, kb: dict, props: dict) -> CheckResult:
    approvals = _template(export).get("approvals")
    if isinstance(approvals, list) and approvals:
        names = ", ".join(str(a.get("name", "<未署名>")) for a in approvals if isinstance(a, dict))
        return "manual", f"已列 {len(approvals)} 条审批记录({names})，签字真伪与授权范围需人工核验"
    return "manual", "未列审批记录，需人工核对签字原件"


CHECKS: list[dict] = [
    {"id": "A1", "group": "Content Completeness", "title": "每步有责任角色", "mode": "auto", "role": "SOP-OWNER", "on_fail": "退回模板编辑人补齐角色，重新导出后复跑", "fn": check_a1},
    {"id": "A2", "group": "Content Completeness", "title": "每步有完成标准", "mode": "auto", "role": "SOP-OWNER", "on_fail": "补写可验收的完成标准", "fn": check_a2},
    {"id": "A3", "group": "Content Completeness", "title": "每步有必需材料", "mode": "auto", "role": "SOP-OWNER", "on_fail": "补齐材料清单或写明无需材料的理由", "fn": check_a3},
    {"id": "A4", "group": "Content Completeness", "title": "知识库引用有效", "mode": "auto", "role": "KB-ADMIN", "on_fail": "先发布文章或移除引用", "fn": check_a4},
    {"id": "A5", "group": "Content Completeness", "title": "无占位内容", "mode": "auto", "role": "SOP-OWNER", "on_fail": "清除 TODO/TBD 等占位内容", "fn": check_a5},
    {"id": "A6", "group": "Content Completeness", "title": "前置依赖有效", "mode": "auto", "role": "SOP-OWNER", "on_fail": "修正或删除悬空依赖", "fn": check_a6},
    {"id": "B1", "group": "Execution Feasibility", "title": "SLA 取值合理", "mode": "auto", "role": "OPS-LEAD", "on_fail": "重定 SLA 或拆步", "fn": check_b1},
    {"id": "B2", "group": "Execution Feasibility", "title": "一线代表已复核", "mode": "auto", "role": "OPS-LEAD", "on_fail": "组织一线复核并记录结论", "fn": check_b2},
    {"id": "B3", "group": "Execution Feasibility", "title": "角色已登记", "mode": "auto", "role": "OPS-LEAD", "on_fail": "补登记角色或改正角色名", "fn": check_b3},
    {"id": "B4", "group": "Execution Feasibility", "title": "不撞营业时间", "mode": "manual", "role": "SHIFT-PLAN", "on_fail": "调整 SLA 或补值班安排，人工签字", "fn": check_b4},
    {"id": "B5", "group": "Execution Feasibility", "title": "有异常路径", "mode": "auto", "role": "SOP-OWNER", "on_fail": "补异常处理与升级路径", "fn": check_b5},
    {"id": "B6", "group": "Execution Feasibility", "title": "依赖无环", "mode": "auto", "role": "SOP-OWNER", "on_fail": "打破循环依赖", "fn": check_b6},
    {"id": "C1", "group": "Data & System", "title": "step_key 唯一", "mode": "auto", "role": "RELEASE", "on_fail": "重命名重复项并同步历史映射", "fn": check_c1},
    {"id": "C2", "group": "Data & System", "title": "step_key 规范", "mode": "auto", "role": "RELEASE", "on_fail": "按 UPPER_SNAKE 重命名", "fn": check_c2},
    {"id": "C3", "group": "Data & System", "title": "表单字段标记齐全", "mode": "auto", "role": "RELEASE", "on_fail": "补齐 type 与 required", "fn": check_c3},
    {"id": "C4", "group": "Data & System", "title": "复盘统计字段未删", "mode": "auto-cond", "role": "QA", "on_fail": "恢复字段或同步修改复盘口径", "fn": check_c4},
    {"id": "C5", "group": "Data & System", "title": "版本号按规则递增", "mode": "auto", "role": "RELEASE", "on_fail": "按 S6-SOPR-014 重定版本号", "fn": check_c5},
    {"id": "C6", "group": "Data & System", "title": "字段 key 唯一规范", "mode": "auto", "role": "RELEASE", "on_fail": "重命名字段并做数据映射", "fn": check_c6},
    {"id": "D1", "group": "Release & Communication", "title": "变更日志已填写", "mode": "auto", "role": "RELEASE", "on_fail": "补写变更条目", "fn": check_d1},
    {"id": "D2", "group": "Release & Communication", "title": "改进提案状态合规", "mode": "auto", "role": "RELEASE", "on_fail": "移出未通过提案或等提案通过", "fn": check_d2},
    {"id": "D3", "group": "Release & Communication", "title": "发布通知已起草", "mode": "auto", "role": "RELEASE", "on_fail": "起草含生效时间与联系人的通知", "fn": check_d3},
    {"id": "D4", "group": "Release & Communication", "title": "试运行结论已归档", "mode": "auto", "role": "QA", "on_fail": "补试运行结论与样本量", "fn": check_d4},
    {"id": "D5", "group": "Release & Communication", "title": "回滚方案已写明", "mode": "auto", "role": "RELEASE", "on_fail": "补回滚步骤与触发条件", "fn": check_d5},
    {"id": "D6", "group": "Release & Communication", "title": "审批签字齐备", "mode": "manual", "role": "OPS-LEAD", "on_fail": "补齐签字，代签或越权不予发布", "fn": check_d6},
]


def load_json(path: Path, label: str, optional: bool = False) -> dict:
    if not path.exists():
        if optional:
            return {}
        raise SystemExit(f"ERROR: {label} not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: {label} is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: {label} root must be an object: {path}")
    return data


def validate_export(export: dict) -> None:
    if not isinstance(export.get("template"), dict):
        raise SystemExit("ERROR: export.template must be an object")
    if not isinstance(export.get("steps"), list):
        raise SystemExit("ERROR: export.steps must be a list")
    if not export["steps"]:
        raise SystemExit("ERROR: export.steps must not be empty")


def run_checks(export: dict, kb: dict, props: dict) -> list[dict]:
    results = []
    for spec in CHECKS:
        try:
            result, detail = spec["fn"](export, kb, props)
        except Exception as exc:  # a crashing check must never look green
            result, detail = "manual", f"检查执行异常，需人工确认: {type(exc).__name__}: {exc}"
        if result not in {"pass", "fail", "manual"}:
            result, detail = "manual", f"检查返回了非法结果 {result!r}，需人工确认"
        results.append({**{k: spec[k] for k in ("id", "group", "title", "mode", "role", "on_fail")}, "result": result, "detail": detail})
    return results


def summarize(results: list[dict]) -> dict:
    summary = {"total": len(results), "pass": 0, "fail": 0, "manual": 0, "auto_verified": 0}
    for r in results:
        summary[r["result"]] += 1
        if r["result"] in {"pass", "fail"}:
            summary["auto_verified"] += 1
    summary["verdict"] = "fail" if summary["fail"] else "ok"
    return summary


def render_markdown(export_path: str, results: list[dict], summary: dict) -> str:
    lines = [
        "# SOP 模板发布核对报告",
        "",
        f"- 输入文件：`{export_path}`",
        f"- 总项数：{summary['total']}；pass {summary['pass']}；fail {summary['fail']}；manual {summary['manual']}",
        f"- 脚本实际核验（pass+fail）：{summary['auto_verified']} 项",
        f"- 结论：{'不通过，存在 fail 项' if summary['fail'] else '通过（manual 项须人工签字确认）'}",
        "",
        "| ID | 组 | 检查项 | 结果 | 证据 | 责任角色 | 不通过处置 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        detail = str(r["detail"]).replace("|", "\\|")
        lines.append(f"| {r['id']} | {r['group']} | {r['title']} | **{r['result']}** | {detail} | {r['role']} | {r['on_fail']} |")
    lines += ["", "> manual 表示脚本无法客观判定，不等于通过；必须由对应责任角色人工核对并留痕。", ""]
    return "\n".join(lines)


def build_payload(export_path: str, results: list[dict], summary: dict) -> dict:
    return {"input": export_path, "summary": summary, "items": results}


def cmd_run(args: argparse.Namespace) -> int:
    export_path = Path(args.export)
    export = load_json(export_path, "export")
    validate_export(export)
    kb = load_json(Path(args.kb_stub), "kb stub", optional=True)
    props = load_json(Path(args.proposal_stub), "proposal stub", optional=True)

    if args.dry_run:
        auto = sum(1 for c in CHECKS if c["mode"] in {"auto", "auto-cond"})
        print(f"DRY-RUN input={export_path} steps={len(export['steps'])} checks={len(CHECKS)} auto={auto} manual={len(CHECKS) - auto}")
        print(f"DRY-RUN kb_stub={'loaded' if kb else 'missing->A4 manual'} proposal_stub={'loaded' if props else 'missing->D2 manual'}")
        for spec in CHECKS:
            print(f"  {spec['id']} [{spec['mode']}] {spec['title']}")
        print("DRY-RUN ok (no report written)")
        return 0

    results = run_checks(export, kb, props)
    summary = summarize(results)

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(render_markdown(str(export_path), results, summary), encoding="utf-8")
    if args.json_report:
        Path(args.json_report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_report).write_text(
            json.dumps(build_payload(str(export_path), results, summary), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if args.format == "json":
        print(json.dumps(build_payload(str(export_path), results, summary), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(str(export_path), results, summary))

    return 1 if summary["fail"] else 0


# ---------------------------------------------------------------- self test
EXPECTED = {
    "sample_pass.json": set(),
    "sample_err_content.json": {"A1", "A2", "A3", "A4", "A5", "A6"},
    "sample_err_data.json": {"C1", "C2", "C3", "C5", "C6"},
    "sample_err_release.json": {"B1", "B3", "B6", "D1", "D2", "D3", "D4", "D5"},
}


def cmd_self_test(args: argparse.Namespace) -> int:
    samples_dir = ROOT / "samples"
    kb = load_json(Path(args.kb_stub), "kb stub", optional=True)
    props = load_json(Path(args.proposal_stub), "proposal stub", optional=True)
    failures: list[str] = []
    checks_run = 0

    def assert_true(cond: bool, msg: str) -> None:
        nonlocal checks_run
        checks_run += 1
        if cond:
            print(f"  ok   {msg}")
        else:
            print(f"  FAIL {msg}")
            failures.append(msg)

    for name, expected in EXPECTED.items():
        path = samples_dir / name
        if not path.exists():
            assert_true(False, f"{name} 存在")
            continue
        export = json.loads(path.read_text(encoding="utf-8"))
        results = run_checks(export, kb, props)
        got = {r["id"] for r in results if r["result"] == "fail"}
        summary = summarize(results)
        assert_true(len(results) == 24, f"{name} 输出 24 项（实际 {len(results)}）")
        assert_true(summary["pass"] + summary["fail"] + summary["manual"] == 24, f"{name} 三态合计为 24")
        assert_true(all(r["result"] in {"pass", "fail", "manual"} for r in results), f"{name} 每项三态合法")
        assert_true(got == expected, f"{name} fail 集合 == {sorted(expected)}（实际 {sorted(got)}）")
        if name == "sample_pass.json":
            assert_true(summary["fail"] == 0, "合规样例 fail=0")
            assert_true(summary["auto_verified"] >= 10, f"合规样例自动核验项 >=10（实际 {summary['auto_verified']}）")
        else:
            assert_true(summary["fail"] >= 1, f"{name} 至少 1 项 fail")

    # mutation test: break a passing sample in memory, the checker must turn red
    base_path = samples_dir / "sample_pass.json"
    if base_path.exists():
        mutated = copy.deepcopy(json.loads(base_path.read_text(encoding="utf-8")))
        mutated["template"]["version"] = mutated["template"]["previous_version"]
        results = run_checks(mutated, kb, props)
        failed_ids = {r["id"] for r in results if r["result"] == "fail"}
        assert_true("C5" in failed_ids, "变异注入(版本号不递增) 必须让 C5 报 fail")

        mutated2 = copy.deepcopy(json.loads(base_path.read_text(encoding="utf-8")))
        mutated2["steps"][0]["assigned_role"] = ""
        results2 = run_checks(mutated2, kb, props)
        failed_ids2 = {r["id"] for r in results2 if r["result"] == "fail"}
        assert_true("A1" in failed_ids2, "变异注入(责任角色清空) 必须让 A1 报 fail")

    print("")
    if failures:
        print(f"SELF-TEST FAIL assertions={checks_run} failed={len(failures)}")
        return 1
    print(f"SELF-TEST PASS assertions={checks_run}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SOP template pre-release checker (pass/fail/manual)")
    parser.add_argument("export", nargs="?", help="SOP template version export JSON")
    parser.add_argument("--kb-stub", default=str(DEFAULT_KB_STUB), help="knowledge base stub JSON")
    parser.add_argument("--proposal-stub", default=str(DEFAULT_PROPOSAL_STUB), help="improvement proposal stub JSON")
    parser.add_argument("--format", choices=["md", "json"], default="md", help="stdout format")
    parser.add_argument("--report", help="write markdown report to this path")
    parser.add_argument("--json-report", help="write JSON report to this path")
    parser.add_argument("--dry-run", action="store_true", help="validate input and list checks, write nothing")
    parser.add_argument("--self-test", action="store_true", help="run built-in anti-false-green self test")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        return cmd_self_test(args)
    if not args.export:
        print("ERROR: export JSON path is required (or use --self-test)", file=sys.stderr)
        return 2
    return cmd_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
