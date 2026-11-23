# ACCEPTANCE — SOP New Version Pre-Release Checklist and Automated Verification

本文件把平台验收标准（AC）逐条映射到实现位置、可复跑命令、预期输出与实测结果。
原始需求与 AC 原文见 [docs/AC-MAPPING.md](docs/AC-MAPPING.md)；完整原始输出见 [ACCEPTANCE-EVIDENCE.md](ACCEPTANCE-EVIDENCE.md)。

## 1. 验收判据来源

- 接口：`GET https://clawhunt.store/api/problems/3166`（匿名只读，HTTP 200）
- 原件：`evidence/problem-3166.raw.json`（9598 字节，SHA256 `00fef6a4b03b5844a6eedbb353cfae6747b9569a41df74a2fb15c1f38b109795`，与二次拉取逐字节一致）
- 实现只对这份原件负责。

## 2. AC 对照表

| AC | 平台要求 | 实现位置 | 可复跑命令 | 预期输出 | 实测结果 |
|---|---|---|---|---|---|
| AC1 | 检查表 24 项、4 组；每项含核对方式、责任角色、不通过处置 | `docs/CHECKLIST.md`（唯一真源）、`docs/CHECKLIST.xlsx`（由 MD 生成）；根目录 [ACCEPTANCE-EVIDENCE.md](ACCEPTANCE-EVIDENCE.md) 的 E-AC1 内联全部 24 项索引 | `python scripts/check_checklist.py` | `RESULT pass items=24 groups=4 xlsx=ok missing_fields=0`，退出码 0 | 通过（见 E2） |
| AC2a | 脚本自动核验至少 10 项 | `scripts/check_sop_release.py` 的 `CHECKS` 注册表（24 项，22 项自动/条件自动） | `python scripts/check_sop_release.py samples/sample_pass.json --format json` | `summary.auto_verified = 22`，`fail = 0`，退出码 0 | 通过（见 E4） |
| AC2b | 合规样例结果只有 pass 或 manual | `samples/sample_pass.json` | 同上 | 24 项 = pass 22 + manual 2 + fail 0 | 通过（见 E4） |
| AC2c | 3 份埋错样例各自报出对应 fail | `samples/sample_err_content.json`、`sample_err_data.json`、`sample_err_release.json` | `python scripts/check_sop_release.py --self-test` | 三份 fail 集合分别为 `A1-A6`、`C1,C2,C3,C5,C6`、`B1,B3,B6,D1-D5`；`SELF-TEST PASS assertions=23`，退出码 0 | 通过（见 E3/E5） |
| AC3 | 报告每项标记为 pass / fail / manual 三态之一 | 报告渲染 `render_markdown` / `build_payload`，JSON 每项 `result` 字段 | `python scripts/check_sop_release.py samples/sample_pass.json --format json` | 每项 `result ∈ {pass,fail,manual}`；`pass+fail+manual = 24` | 通过（见 E4） |

## 3. 平台交付物清单

| 平台 [Deliverables] | 本仓文件 |
|---|---|
| Checklist (Markdown + Excel) | [docs/CHECKLIST.md](docs/CHECKLIST.md)、[docs/CHECKLIST.xlsx](docs/CHECKLIST.xlsx) |
| check_sop_release.py | [scripts/check_sop_release.py](scripts/check_sop_release.py) |
| 1 passing + 3 error-seeded sample JSON | [samples/sample_pass.json](samples/sample_pass.json)、[samples/sample_err_content.json](samples/sample_err_content.json)、[samples/sample_err_data.json](samples/sample_err_data.json)、[samples/sample_err_release.json](samples/sample_err_release.json) |
| a sample report | [reports/sample-report.md](reports/sample-report.md)、[reports/sample-report.json](reports/sample-report.json) |
| README（运行与测试方法） | [README.md](README.md) |

## 4. 边界与不冒充项

- 知识库文章与改进提案走接口桩（`stubs/`），未接入生产 S3-KB；stub 缺失时对应项落 `manual`，不落 `pass`。
- B4（营业时间冲突）、D6（审批签字）固定 `manual`，脚本不代签、不假绿。
- 版本号规则按 S6-SOPR-014 的占位 semver 规则实现，接真实规则只需改 `check_c5`。
- 未调用平台提交接口；仓库为公开源码仓。
- 样例数据全部虚构，不含真实企业或个人信息。
