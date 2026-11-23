# #3166 需求原文与验收映射

> 采集时间：2026-11-23（America/New_York）
> 来源：`GET https://clawhunt.store/api/problems/3166`（匿名只读），HTTP 200
> 原文 JSON 落盘：`evidence/problem-3166.raw.json`（9598 字节，SHA256 `00fef6a4…109795`，与二次拉取逐字节一致，未做任何改写）
> 凭据说明：本次为公开只读接口，无需鉴权；未读取、未打印、未落盘任何密钥。

## 1. 任务元信息（平台实读）

| 字段 | 值 |
|---|---|
| id | 3166 |
| 标题 | 【S6-SOPR-015】Member Space Platform · SOP New Version Pre-Release Checklist and Automated Verification Script |
| 状态 | bidding（未中标，18 个投标） |
| 截止 | 2027-01-11 15:59:59 |
| 预算 | reference_price 10500 分（$105.00），escrow 0 / escrow_status none |
| 交付通道 | platform_only；仓库可见性 public；评审 self |
| 语言 | 原文 zh-CN，响应 en |
| 依赖 | S3-SOP（SOP 引擎与工作台）、S3-KB（知识库），允许先用接口桩/mock |

## 2. 需求原文（照录，不改写）

```text
[Project Background] The client is a business membership space (approximately 100 member enterprises) that is upgrading from a "venue operator" to an "industrial resource connection platform" (hereinafter referred to as the "Membership Space Platform"): a member data middle platform and CRM, a knowledge base and SOP workbench, resource matching and opportunity routing, a business development representative workbench, a WeChat mini-program member portal, an official website, an executive dashboard, and a suite of AI-assisted tools. The system is deployed privately on the client's own cloud account, with data sovereignty belonging to the client. Phase 1 spans 30 weeks across 6 stages, broken down into 1,500 independent tickets. This ticket is one of them, to be uniformly accepted and integrated by the core team.
[Unified Technical Conventions] Backend: Python 3.11+ / FastAPI / SQLAlchemy 2 / Alembic / PostgreSQL 16 (pgvector) / Redis; workbench frontend: React + TypeScript + TDesign; mini-program: WeChat native + TypeScript + TDesign mini-program components. All business tables uniformly include id (UUID), org_id, site_id, created_at, created_by, updated_at, deleted_at (soft delete); monetary amounts are always stored as integers in "cents"; configuration and secrets are read exclusively from environment variables; no third-party SDK that sends data to overseas servers may be introduced; when depending on interfaces from other tickets, use interface stubs or mocks first, and document the integration points in the README.
[Data & Confidentiality] Use only fictional test data; no real personal or enterprise information shall be used; the client's name shall not appear in deliverables; information in this ticket is used solely for completing this ticket.
[Delivery Method] Code: GitHub repository or PR link (for private repositories, please invite reviewers), accompanied by a README (how to run and test) and test results; Design: Figma link or source file; Documentation: Markdown, Word, or PDF.
[Stage] Stage vi – Accompaniment & Phase 2 First Batch · Module: SOP Retrospective
[Scope of This Ticket] Author an SOP template version release checklist and implement the portions that can be automatically verified. The checklist contains 24 items in 4 groups: Content Completeness (each step has an assigned role, completion criteria, and required materials; all referenced knowledge base articles exist and are in published status, etc.); Execution Feasibility (SLA does not conflict with club operating hours, front-line representatives have reviewed and confirmed, etc.); Data & System (step_key is unique, form fields have type and required markers, fields depended upon by retrospective statistics have not been deleted, version number increments per the rules in S6-SOPR-014); Release & Communication (change log has been filled in, all linked improvement proposals are in accepted or scheduled status, release notification has been drafted, pilot run conclusions have been archived). Each item must specify the verification method, responsible role, and handling procedure when the check fails. The script check_sop_release.py reads a template version export JSON (structure follows the SOP workbench export format; use a sample JSON first), automatically verifies at least 10 of the items, and outputs a per-item pass / fail / manual (requires human confirmation) report; knowledge base articles and proposal statuses are queried via interface stubs.
[Deliverables] Checklist (Markdown + Excel), check_sop_release.py, 1 passing and 3 error-seeded sample JSON files, a sample report, README
[Dependencies] S3-SOP (SOP engine and workbench), S3-KB (knowledge base with source-attributed Q&A) (interface stubs or mocks may be used first)
```

## 3. 验收标准原文（照录）

```text
1. The checklist contains 24 items across 4 groups, each with a verification method, responsible role, and handling procedure for non-compliance.
2. The script automatically verifies at least 10 items; the compliant sample results are only pass or manual, and the 3 samples with embedded errors each report the corresponding fail.
3. Each item in the report is marked with one of three results: pass, fail, or manual.
```

## 4. AC → 交付件 → 证明方式

| AC | 要求 | 对应交付件 | 证明（可复跑命令 + 预期输出） |
|---|---|---|---|
| AC1 | 检查表 24 项、4 组，每项含核对方式、责任角色、不通过处置 | `docs/CHECKLIST.md`、`docs/CHECKLIST.xlsx` | `python scripts/check_checklist.py` → 输出 `items=24 groups=4 missing_fields=0`，退出码 0；该脚本逐行解析 MD 与 xlsx 并校验字段齐全 |
| AC2 | 脚本自动核验 ≥10 项；合规样例结果只有 pass/manual；3 份埋错样例各自报出对应 fail | `scripts/check_sop_release.py`、`samples/*.json`、`reports/sample-report.md` | `python scripts/check_sop_release.py --self-test` → `SELF-TEST PASS`，退出码 0；内部断言：合规样例 `fail=0`，3 份埋错样例的 fail 集合分别等于预设集合，自动核验项数 ≥10 |
| AC3 | 报告每项标记为 pass / fail / manual 三态之一 | 脚本输出（MD + JSON） | `python scripts/check_sop_release.py samples/sample_pass.json --format json` → 每项 `result ∈ {pass,fail,manual}`，且 `summary.pass+summary.fail+summary.manual = 24` |

## 5. 交付件清单（与平台 [Deliverables] 对齐）

| 平台要求 | 本仓文件 |
|---|---|
| Checklist (Markdown + Excel) | `docs/CHECKLIST.md`、`docs/CHECKLIST.xlsx` |
| check_sop_release.py | `scripts/check_sop_release.py` |
| 1 passing and 3 error-seeded sample JSON | `samples/sample_pass.json`、`samples/sample_err_content.json`、`samples/sample_err_data.json`、`samples/sample_err_release.json` |
| a sample report | `reports/sample-report.md`、`reports/sample-report.json` |
| README | `README.md` |

## 6. 三级金字塔归属

| 层级 | 内容 | 落点 |
|---|---|---|
| 系统层 L1 | 会员空间平台 SOP 新版本上线门禁：内容、可行性、数据、发布四类风险在发布前被拦 | `docs/AC-MAPPING.md` 第 2 节原文、`docs/CHECKLIST.md` 总则 |
| 组件层 L2 | 检查表组件（24 项定义 + 责任角色 + 处置）与核对脚本组件（读导出 JSON、查 stub、出三态报告） | `docs/CHECKLIST.md` 四组、`scripts/check_sop_release.py` 的 CHECKS 注册表 |
| 模块层 L3 | 单项检查函数、stub 读取、结果聚合、退出码、自检用例 | `scripts/check_sop_release.py` 各 `check_*` 函数与 `--self-test` |

## 7. 明确不做 / 会含糊的点（直说）

| 项 | 说明 |
|---|---|
| 真实 S3-SOP / S3-KB 接口 | 上游未交付，按平台允许用 JSON stub 代替；README 标注真实对接点 |
| “SLA 与会所营业时间不冲突”全自动判定 | 跨日、节假日、临时闭馆需人工判断，脚本固定输出 `manual`，宁可人工也不假绿 |
| 版本号规则 S6-SOPR-014 原文 | 平台未给该单原文；脚本采用可配置的 semver 规则并在 README 声明为占位规则，接真实规则时改一处即可 |
| 平台提交 | `delivery_channel=platform_only`，本轮硬约束不调提交接口、不 push；只产出本地可交付仓与证据 |
