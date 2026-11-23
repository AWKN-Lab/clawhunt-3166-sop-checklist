# ACCEPTANCE EVIDENCE — SOP New Version Pre-Release Checklist

本文件记录实测证据：命令、退出码、原始输出摘录。所有命令均在仓库根目录执行。

## E-AC. Acceptance criteria (English, verbatim) with evidence

Source: `GET https://clawhunt.store/api/problems/3166`, field `acceptance_criteria` (raw copy: `evidence/problem-3166.raw.json`).

**AC1.** "The checklist contains 24 items across 4 groups, each with a verification method, responsible role, and handling procedure for non-compliance."

- Evidence: `docs/CHECKLIST.md` (source of truth) and `docs/CHECKLIST.xlsx` contain 24 items in 4 groups; every row has verification method, responsible role and non-compliance handling. The root-level index in E-AC1 below lists all 24 items so they are readable without opening `docs/`.
- Rerun: `python scripts/check_checklist.py` -> `RESULT pass items=24 groups=4 xlsx=ok missing_fields=0`, exit 0.
- Observed: pass (see E2).

**AC2.** "The script automatically verifies at least 10 items; the compliant sample results are only pass or manual, and the 3 samples with embedded errors each report the corresponding fail."

- Evidence: `scripts/check_sop_release.py` registers 24 checks, 22 of them auto/conditional-auto. `samples/sample_pass.json` -> pass 22 / fail 0 / manual 2. Error samples report exactly: content `A1,A2,A3,A4,A5,A6`; data `C1,C2,C3,C5,C6`; release `B1,B3,B6,D1,D2,D3,D4,D5`.
- Rerun: `python scripts/check_sop_release.py --self-test` -> `SELF-TEST PASS assertions=23`, exit 0.
- Observed: pass (see E3/E4/E5).

**AC3.** "Each item in the report is marked with one of three results: pass, fail, or manual."

- Evidence: every report row and JSON item carries `result ∈ {pass, fail, manual}`; `pass + fail + manual = 24`; `manual` is never counted as pass.
- Rerun: `python scripts/check_sop_release.py samples/sample_pass.json --format json` -> `items=24 tri_state_ok=True pass+fail+manual=24 auto_verified=22`, exit 0.
- Observed: pass (see E4, `evidence/ac3-check.log`).

### E-AC1. Root-level index of all 24 checklist items

Auto-check command for every row: `python scripts/check_sop_release.py samples/sample_pass.json --format json` (results below are the observed results for the compliant sample).

| ID | Item | Pass criteria | Auto-check command | Observed |
|---|---|---|---|---|
| A1 | Every step has an assigned role | `assigned_role` non-empty for every step | `check_a1` via command above | pass |
| A2 | Every step has completion criteria | `completion_criteria` non-empty, at least 10 chars | `check_a2` via command above | pass |
| A3 | Every step has required materials | `required_materials` is a non-empty list | `check_a3` via command above | pass |
| A4 | Referenced KB articles exist and are published | Each ID exists in KB stub with `status=published` | `check_a4` via command above | pass |
| A5 | No placeholder content | No TODO/TBD/待补充/待定/占位/xxx/??? in title, criteria or materials | `check_a5` via command above | pass |
| A6 | Prerequisites are valid | Every prerequisite points to an existing `step_key` | `check_a6` via command above | pass |
| B1 | SLA value is reasonable | Integer `sla_hours` in 1..240 for every step | `check_b1` via command above | pass |
| B2 | Front-line representative reviewed | `reviewers` contains `role=frontline_rep`, `decision=approved` | `check_b2` via command above | pass |
| B3 | Roles are registered | Assigned and escalation roles exist in `template.roles` | `check_b3` via command above | pass |
| B4 | SLA does not conflict with club operating hours | Cross-day, holiday and closure conflicts need human judgement | manual (human sign-off) | manual |
| B5 | Exception path is defined | `exception_path` non-empty, at least 5 chars | `check_b5` via command above | pass |
| B6 | No dependency cycles | Prerequisite graph has no cycle | `check_b6` via command above | pass |
| C1 | `step_key` is unique | No duplicate `step_key` | `check_c1` via command above | pass |
| C2 | `step_key` naming is compliant | Matches `^[A-Z][A-Z0-9_]{2,63}$` | `check_c2` via command above | pass |
| C3 | Form fields have type and required markers | Every field has a valid `type` and boolean `required` | `check_c3` via command above | pass |
| C4 | Retrospective metric fields are not deleted | Fields in `review_metrics` still exist; no metrics -> manual | `check_c4` via command above | pass |
| C5 | Version increments per S6-SOPR-014 | Semver grows and the incremented position matches `change_type` | `check_c5` via command above | pass |
| C6 | Field keys are unique and compliant | Unique per step, matches `^[a-z][a-z0-9_]{1,63}$` | `check_c6` via command above | pass |
| D1 | Change log is filled | Non-empty changelog, no empty entries | `check_d1` via command above | pass |
| D2 | Linked proposals are accepted or scheduled | Every linked proposal status is `accepted` or `scheduled` | `check_d2` via command above | pass |
| D3 | Release notice is drafted | `release_notice` non-empty, at least 20 chars | `check_d3` via command above | pass |
| D4 | Pilot run conclusion is archived | `pilot_conclusion` non-empty, at least 20 chars | `check_d4` via command above | pass |
| D5 | Rollback plan is documented | `rollback_plan` non-empty, at least 20 chars | `check_d5` via command above | pass |
| D6 | Approvals are complete | Identity, authority scope and signatures need human verification | manual (human sign-off) | manual |

Implementation: each `check_*` function lives in `scripts/check_sop_release.py`; the `CHECKS` registry maps IDs, groups, roles and non-compliance handling.

## E0. 环境

| 项 | 值 |
|---|---|
| 操作系统 | Windows |
| 终端 | PowerShell 7 |
| Python | 3.14.3（脚本声明兼容 3.9+，仅用标准库） |
| openpyxl | 3.1.5（仅生成/校验 Excel 需要） |
| 网络 | 仅第 1 步拉取公开需求；其余全部离线 |

## E1. 需求原文取证

```text
GET https://clawhunt.store/api/problems/3166   -> HTTP 200
evidence/problem-3166.raw.json  size=9598  sha256=00fef6a4b03b5844a6eedbb353cfae6747b9569a41df74a2fb15c1f38b109795
二次拉取同接口 -> 同 size、同 sha256（逐字节一致）
```

## E2. AC1：检查表 24 项 / 4 组 / 字段齐全

命令：`python scripts/check_checklist.py`

```text
RESULT pass items=24 groups=4 xlsx=ok missing_fields=0
checklist_rc=0
```

该校验逐行解析 `docs/CHECKLIST.md`，并读取 `docs/CHECKLIST.xlsx` 核对 24 个 ID、7 列表头与空单元格。

## E3. AC2：自检（合规样例 + 3 份埋错样例 + 2 条变异注入）

命令：`python scripts/check_sop_release.py --self-test`

```text
  ok   sample_pass.json fail 集合 == []（实际 []）
  ok   合规样例 fail=0
  ok   合规样例自动核验项 >=10（实际 22）
  ok   sample_err_content.json fail 集合 == ['A1','A2','A3','A4','A5','A6']
  ok   sample_err_data.json fail 集合 == ['C1','C2','C3','C5','C6']
  ok   sample_err_release.json fail 集合 == ['B1','B3','B6','D1','D2','D3','D4','D5']
  ok   变异注入(版本号不递增) 必须让 C5 报 fail
  ok   变异注入(责任角色清空) 必须让 A1 报 fail

SELF-TEST PASS assertions=23
selftest_rc=0
```

（以上为摘录，完整 23 条见 `evidence/selftest.log`。）

## E4. AC2 + AC3：合规样例报告

命令：

```text
python scripts/check_sop_release.py samples/sample_pass.json `
  --report reports/sample-report.md --json-report reports/sample-report.json
```

报告头：

```text
- 总项数：24；pass 22；fail 0；manual 2
- 脚本实际核验（pass+fail）：22 项
- 结论：通过（manual 项须人工签字确认）
sample_rc=0
```

三态完整性（JSON 输出程序化核对，日志 `evidence/ac3-check.log`）：

```text
check_rc=0
items=24 tri_state_ok=True pass+fail+manual=24 auto_verified=22
```

`manual` 两项为 B4（营业时间冲突）与 D6（审批签字），均明确要求人工确认，未记为 pass。

## E5. AC2：3 份埋错样例各自报出对应 fail

命令：`python scripts/check_sop_release.py samples/<sample>.json`

| 样例 | 预设 fail 集合 | 实测 fail 集合 | 退出码 |
|---|---|---|---|
| `sample_err_content.json` | A1,A2,A3,A4,A5,A6 | A1,A2,A3,A4,A5,A6 | 1 |
| `sample_err_data.json` | C1,C2,C3,C5,C6 | C1,C2,C3,C5,C6 | 1 |
| `sample_err_release.json` | B1,B3,B6,D1,D2,D3,D4,D5 | B1,B3,B6,D1,D2,D3,D4,D5 | 1 |

代表性 fail 证据（完整报告见 `evidence/reverse-case.log`）：

```text
A4  fail  知识库引用不合规: MATERIAL_CHECK->KB-9999(不存在)
C1  fail  重复 step_key: KYC_REVIEW
C5  fail  新版本 2.2.0 未大于旧版本 2.2.0
B6  fail  存在循环依赖: KYC_REVIEW -> REVIEW_ARCHIVE -> TERRITORY_ASSIGN -> KYC_REVIEW
D2  fail  提案状态不合规: IP-1003(状态=rejected)
```

## E6. 密钥 / 隐私扫描

命令（两个额外黑名单值由命令行传入，不写入仓库）：

```text
python scripts/secret_scan.py --deny-literal <bid> --deny-literal <account-id>
```

覆盖：私钥块、AWS/GitHub/OpenAI 形态密钥、secret/password/token 赋值、内网 IPv4、本机绝对路径、邮箱、bid/agent 标识、非 ASCII 文件名。

```text
SECRET-SCAN files=30 deny_literals=2 hits=0
RESULT pass (0 hits)
secret_scan_rc=0
```

## E7. MANIFEST.sha256（干净副本生成 + 重新克隆复验）

生成（干净副本，排除 `.git`、缓存、`*.log`、清单自身）：

```text
python scripts/build_manifest.py --root <clean-copy> --output <clean-copy>/MANIFEST.sha256
MANIFEST MANIFEST.sha256 files=23
```

干净副本内校验：

```text
pwsh -File scripts/verify_sha256.ps1 -Root <clean-copy>
RESULT ok=23 bad=0 missing=0
verify_rc=0
```

重新克隆复验：

```text
git clone <public-repo> <fresh-dir>
cd <fresh-dir>
pwsh -File scripts/verify_sha256.ps1
RESULT ok=23 bad=0 missing=0
verify_rc=0
```

## E8. 交付纪律

| 项 | 实测 |
|---|---|
| 平台提交接口 | 未调用 |
| 推送方式 | 普通 `git push`，未 force |
| 文件名 | 全 ASCII（扫描器校验） |
| 排除项 | `.env`、缓存、`node_modules` 未入库 |
| 样例数据 | 全部虚构，无真实企业/个人信息 |

## E9. 原始日志索引

| 文件 | 内容 |
|---|---|
| `evidence/problem-3166.raw.json` | 平台需求原文（逐字） |
| `evidence/build-xlsx.log` | Excel 生成 |
| `evidence/checklist-check.log` | 检查表自证 |
| `evidence/selftest.log` | 23 条自检断言 |
| `evidence/sample-run.log` | 合规样例完整报告 |
| `evidence/reverse-case.log` | 3 份埋错样例完整报告 |
| `evidence/ac3-check.log` | 三态完整性程序化核对 |
| `evidence/secret-scan.log` | 密钥扫描 |
| `evidence/clean-verify.log` | 干净副本清单校验 |
| `evidence/reclone-verify.log` | 重新克隆后清单校验 |
