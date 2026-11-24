# 交付物路径对照表（DELIVERABLE PATH MAP）

> **为什么有这张表**：投标时提交的第一版提案里写的是"计划中的文件路径"；本仓落地时
> 部分文件做了更准确的命名或换了位置（**同一实现**）。买家若按提案里的路径找会找不到，
> 本表给出**一一对应**。
>
> - 提案原文（第一版）：`proposals/3166-proposal.md`
> - 平台现行提案：2026-11-24 修订版，`sha256=94fb7ecb45faa8fc2cb015e5ad8f69f9203ae1838182aa32ca3824321b89fc7c`
>   （修订后即按本表"本仓实际路径"书写）
> - 逐条验收对照见 `ACCEPTANCE.md`；证据见 `ACCEPTANCE-EVIDENCE.md`；24 项检查表索引见 `docs/AC-MAPPING.md`

## 一、路径对照

| 提案里写的路径 | 本仓实际路径 | 说明 |
|---|---|---|
| `docs/sop_release_checklist.md` | `docs/CHECKLIST.md` | 24 项 / 4 组检查表（检查方法 / 责任角色 / 不通过处置） |
| `docs/sop_release_checklist.xlsx` | `docs/CHECKLIST.xlsx` | 同一张表的 Excel 版（`scripts/build_checklist_xlsx.py` 生成） |
| `scripts/check_sop_release.py` | `scripts/check_sop_release.py` | 同名：读模板版本导出 JSON，逐项输出 `pass`/`fail`/`manual` |
| `samples/sop_release_ok.json` | `samples/sample_pass.json` | 1 份合格样例 |
| `samples/sop_release_bad_dup_step_key.json` | `samples/sample_err_content.json` | 埋错样例 A：内容类错误 |
| `samples/sop_release_bad_deleted_field.json` | `samples/sample_err_data.json` | 埋错样例 B：复盘统计依赖字段被删 |
| `samples/sop_release_bad_rejected_proposal.json` | `samples/sample_err_release.json` | 埋错样例 C：关联提案状态非 accepted/scheduled |
| `samples/report_ok.md` / `report_bad_*.md` | `reports/sample-report.md` / `reports/sample-report.json` | 样例报告（Markdown + JSON 两份） |
| `tests/`（脚本级回归） | **本仓无 `tests/` 目录** | 自测入口是 `scripts/check_sop_release.py --self-test`、`scripts/check_checklist.py`；逐次运行输出在 `evidence/selftest.log`、`evidence/checklist-check.log`、`evidence/sample-run.log`、`evidence/dryrun.log`、`evidence/reverse-case.log` |

## 二、提案未列、但本仓实际提供

| 路径 | 用途 |
|---|---|
| `ACCEPTANCE.md` / `ACCEPTANCE-EVIDENCE.md` | 逐条 AC ↔ 实现 ↔ 复跑命令 ↔ 实测输出 |
| `docs/AC-MAPPING.md` | 24 项检查表 ↔ 实现位置 ↔ 样例 ↔ 证据 的索引 |
| `evidence/problem-3166.raw.json` | 需求原件（清单内纳入） |
| `evidence/*.log` | 各次真实运行日志（按 README 说明，**不纳入** `MANIFEST.sha256`，因其会随复跑变化） |
| `scripts/build_manifest.py` / `scripts/build_checklist_xlsx.py` / `scripts/secret_scan.py` | 清单生成 / Excel 生成 / 秘密扫描 |
| `scripts/verify_sha256.ps1` | Windows 侧清单校验 |
| `stubs/kb_articles.json`、`stubs/improvement_proposals.json` | 只读数据桩（不含真实客户数据） |

## 三、复跑命令（与提案一致）

```bash
python scripts/check_sop_release.py samples/sample_pass.json     # 合格样例
python scripts/check_sop_release.py --self-test                  # 自测
python scripts/check_checklist.py                                # 检查表自检
python scripts/build_checklist_xlsx.py                           # 重建 Excel
python scripts/secret_scan.py                                    # 秘密扫描
python scripts/build_manifest.py                                 # 重算 MANIFEST.sha256
```

## 四、变更说明

本表为**新增说明文件**，不改动任何实现、样例或证据；
`MANIFEST.sha256` 已按本仓规则重算（`python scripts/build_manifest.py`）。
