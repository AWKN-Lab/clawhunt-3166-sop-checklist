# SOP 模板新版本上线前检查表（24 项 / 4 组）

> 适用对象：会员空间平台 SOP 工作台（S3-SOP）的 SOP 模板版本发布。
> 版本检查表版本：1.0.0 ｜ 生成日期：2026-11-23
> 配套脚本：`scripts/check_sop_release.py`（自动核验 21 项，人工 2 项，条件自动 1 项）

## 0. 总则

### 0.1 三态判定（不得混用）

| 结果 | 含义 | 谁可以给 |
|---|---|---|
| pass | 脚本已实际执行该检查，条件成立 | 脚本 |
| fail | 脚本已实际执行该检查，条件不成立 | 脚本 |
| manual | 无法由脚本客观判定，需人工确认；**不等于通过** | 脚本标记 + 人工签字 |

铁律：数据缺失、接口不可用、规则未定义时，一律落 `manual`，禁止落 `pass`。

### 0.2 三级金字塔归属

| 层级 | 本表对应内容 |
|---|---|
| 系统层 L1 | 发布门禁目标：四类风险（内容、可行性、数据、发布）在发布前被拦 |
| 组件层 L2 | 本检查表四组共 24 项；每项绑定核对方式、责任角色、不通过处置 |
| 模块层 L3 | 每项对应 `check_sop_release.py` 中一个 `check_*` 函数与一条自检用例 |

### 0.3 使用方式

1. 从 SOP 工作台导出模板版本 JSON；
2. 运行 `python scripts/check_sop_release.py <export.json>`；
3. 按报告处置 `fail` 项，人工完成 `manual` 项并签字；
4. 全部 `pass` 或 `manual` 已签字，方可发布。

### 0.4 责任角色缩写

| 缩写 | 角色 |
|---|---|
| SOP-OWNER | SOP 模板维护人 |
| KB-ADMIN | 知识库管理员 |
| OPS-LEAD | 运营负责人 |
| SHIFT-PLAN | 排班负责人 |
| RELEASE | 发布负责人 |
| QA | 质量复核人 |

## A 组 · 内容完整性（Content Completeness）

| ID | 检查项 | 判定标准 | 核对方式 | 责任角色 | 不通过处置 |
|---|---|---|---|---|---|
| A1 | 每步有责任角色 | 每个步骤 `assigned_role` 非空，且能在 `template.roles` 中找到 | 自动 | SOP-OWNER | 退回模板编辑人补齐角色，重新导出后复跑 |
| A2 | 每步有完成标准 | 每个步骤 `completion_criteria` 非空且不少于 10 个字符 | 自动 | SOP-OWNER | 补写可验收的完成标准，禁止用“完成即可”这类空话 |
| A3 | 每步有必需材料 | 每个步骤 `required_materials` 为非空数组，元素均非空 | 自动 | SOP-OWNER | 补齐材料清单；确实无需材料须写明“无”并说明理由 |
| A4 | 知识库引用有效 | `referenced_kb_articles` 每篇在 KB stub 中存在且 `status=published` | 自动（stub） | KB-ADMIN | 未发布文章先发布，或从模板移除引用后重新导出 |
| A5 | 无占位内容 | 步骤标题、完成标准、材料中不含 TODO、TBD、待补充、xxx、??? 等占位词 | 自动 | SOP-OWNER | 清除占位内容，补成可执行的正式表述 |
| A6 | 前置依赖有效 | `prerequisites` 中每个 step_key 都指向本模板内存在的步骤 | 自动 | SOP-OWNER | 修正或删除悬空依赖，避免执行时找不到前置步骤 |

## B 组 · 执行可行性（Execution Feasibility）

| ID | 检查项 | 判定标准 | 核对方式 | 责任角色 | 不通过处置 |
|---|---|---|---|---|---|
| B1 | SLA 取值合理 | 每步 `sla_hours` 为正整数且不超过 240 小时 | 自动 | OPS-LEAD | 与业务方重定 SLA；超过 240 小时须拆步或走例外审批 |
| B2 | 一线代表已复核 | `reviewers` 中存在 `role=frontline_rep` 且 `decision=approved` 的记录 | 自动 | OPS-LEAD | 组织一线代表复核，记录审批结论后重新导出 |
| B3 | 角色已登记 | 所有 `assigned_role` 与 `escalation_role` 都在 `template.roles` 内 | 自动 | OPS-LEAD | 补登记角色或改正错拼角色名，避免发布后无人可派 |
| B4 | 不撞营业时间 | SLA 起止不落在非营业时段、节假日与临时闭馆日 | 人工 | SHIFT-PLAN | 调整 SLA 或补值班安排；人工签字后方可视为通过 |
| B5 | 有异常路径 | 每个步骤 `exception_path` 非空且说明升级对象 | 自动 | SOP-OWNER | 补异常处理与升级路径，禁止只写正常流程 |
| B6 | 依赖无环 | `prerequisites` 构成的有向图无环 | 自动 | SOP-OWNER | 打破循环依赖，重新排列步骤顺序 |

## C 组 · 数据与系统（Data & System）

| ID | 检查项 | 判定标准 | 核对方式 | 责任角色 | 不通过处置 |
|---|---|---|---|---|---|
| C1 | step_key 唯一 | 全模板 `step_key` 无重复 | 自动 | 发布负责人 | 重命名重复项；重命名须同步历史数据映射 |
| C2 | step_key 规范 | 匹配 `^[A-Z][A-Z0-9_]{2,63}$` | 自动 | 发布负责人 | 按大写下划线规范重命名，禁止空格与中文 |
| C3 | 表单字段标记齐全 | 每个 `form_fields` 元素有非空白名单内 `type` 与布尔 `required` | 自动 | 发布负责人 | 补齐 type 与 required，缺一不可发布 |
| C4 | 复盘统计字段未删 | `template.review_metrics[].field` 均能在当前步骤表单字段中找到；未声明则记 manual | 自动（条件）/ 人工 | QA | 恢复被删字段或同步修改复盘口径并留变更记录 |
| C5 | 版本号按规则递增 | version 与 previous_version 为 semver，新版本严格更大，且按 `change_type` 递增对应位 | 自动 | 发布负责人 | 按 S6-SOPR-014 规则重定版本号；不得原地改内容不升版 |
| C6 | 字段 key 唯一规范 | 同一步内 `form_field.key` 唯一且匹配 `^[a-z][a-z0-9_]{1,63}$` | 自动 | 发布负责人 | 重命名冲突字段；历史数据需做字段映射迁移 |

## D 组 · 发布与沟通（Release & Communication）

| ID | 检查项 | 判定标准 | 核对方式 | 责任角色 | 不通过处置 |
|---|---|---|---|---|---|
| D1 | 变更日志已填写 | `template.changelog` 为非空数组，每条非空 | 自动 | RELEASE | 补写本次变更条目，写清改了什么、为什么改 |
| D2 | 改进提案状态合规 | `linked_improvement_proposals` 每项在 proposal stub 中为 accepted 或 scheduled | 自动（stub） | RELEASE | 提案未通过则不得随本版发布，移出关联或等提案通过 |
| D3 | 发布通知已起草 | `release_notice` 非空且不少于 20 个字符 | 自动 | RELEASE | 起草通知，含生效时间、影响范围、联系人 |
| D4 | 试运行结论已归档 | `pilot_conclusion` 非空且不少于 20 个字符 | 自动 | QA | 补试运行结论与样本量；未试运行不得全量发布 |
| D5 | 回滚方案已写明 | `rollback_plan` 非空且不少于 20 个字符 | 自动 | RELEASE | 补回滚步骤、触发条件与责任人 |
| D6 | 审批签字齐备 | 审批人身份、授权范围与签字原件需人工核验 | 人工 | OPS-LEAD | 补齐签字；代签或越权签字一律不予发布 |

## 附：自动 / 人工统计

| 口径 | 数量 | 明细 |
|---|---:|---|
| 恒自动核验 | 21 | A1–A6、B1–B3、B5–B6、C1–C3、C5–C6、D1–D5 |
| 条件自动 | 1 | C4（有 `review_metrics` 时自动，否则 manual） |
| 恒人工 | 2 | B4、D6 |
| 合计 | 24 | 4 组各 6 项 |
