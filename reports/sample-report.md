# SOP 模板发布核对报告

- 输入文件：`samples\sample_pass.json`
- 总项数：24；pass 22；fail 0；manual 2
- 脚本实际核验（pass+fail）：22 项
- 结论：通过（manual 项须人工签字确认）

| ID | 组 | 检查项 | 结果 | 证据 | 责任角色 | 不通过处置 |
|---|---|---|---|---|---|---|
| A1 | Content Completeness | 每步有责任角色 | **pass** | 4 个步骤均满足责任角色非空 | SOP-OWNER | 退回模板编辑人补齐角色，重新导出后复跑 |
| A2 | Content Completeness | 每步有完成标准 | **pass** | 4 个步骤均满足完成标准(>=10字符) | SOP-OWNER | 补写可验收的完成标准 |
| A3 | Content Completeness | 每步有必需材料 | **pass** | 4 个步骤均满足必需材料 | SOP-OWNER | 补齐材料清单或写明无需材料的理由 |
| A4 | Content Completeness | 知识库引用有效 | **pass** | 4 条知识库引用均存在且已发布 | KB-ADMIN | 先发布文章或移除引用 |
| A5 | Content Completeness | 无占位内容 | **pass** | 未发现占位内容 | SOP-OWNER | 清除 TODO/TBD 等占位内容 |
| A6 | Content Completeness | 前置依赖有效 | **pass** | 4 个步骤的前置依赖均有效 | SOP-OWNER | 修正或删除悬空依赖 |
| B1 | Execution Feasibility | SLA 取值合理 | **pass** | 4 个步骤均满足SLA(1-240 整数) | OPS-LEAD | 重定 SLA 或拆步 |
| B2 | Execution Feasibility | 一线代表已复核 | **pass** | 一线代表 一线代表A 已复核通过 | OPS-LEAD | 组织一线复核并记录结论 |
| B3 | Execution Feasibility | 角色已登记 | **pass** | 责任与升级角色均已登记 | OPS-LEAD | 补登记角色或改正角色名 |
| B4 | Execution Feasibility | 不撞营业时间 | **manual** | 营业时间 09:00-18:00，跨日/节假日/闭馆冲突需人工核对 | SHIFT-PLAN | 调整 SLA 或补值班安排，人工签字 |
| B5 | Execution Feasibility | 有异常路径 | **pass** | 4 个步骤均满足异常路径 | SOP-OWNER | 补异常处理与升级路径 |
| B6 | Execution Feasibility | 依赖无环 | **pass** | 依赖图无环 | SOP-OWNER | 打破循环依赖 |
| C1 | Data & System | step_key 唯一 | **pass** | 4 个 step_key 唯一 | RELEASE | 重命名重复项并同步历史映射 |
| C2 | Data & System | step_key 规范 | **pass** | step_key 命名均符合 UPPER_SNAKE | RELEASE | 按 UPPER_SNAKE 重命名 |
| C3 | Data & System | 表单字段标记齐全 | **pass** | 所有表单字段均有合法 type 与布尔 required | RELEASE | 补齐 type 与 required |
| C4 | Data & System | 复盘统计字段未删 | **pass** | 2 个复盘统计字段均存在 | QA | 恢复字段或同步修改复盘口径 |
| C5 | Data & System | 版本号按规则递增 | **pass** | 2.2.0->2.3.0 符合 change_type=content | RELEASE | 按 S6-SOPR-014 重定版本号 |
| C6 | Data & System | 字段 key 唯一规范 | **pass** | 字段 key 唯一且命名合规 | RELEASE | 重命名字段并做数据映射 |
| D1 | Release & Communication | 变更日志已填写 | **pass** | 2 条变更记录 | RELEASE | 补写变更条目 |
| D2 | Release & Communication | 改进提案状态合规 | **pass** | 2 个关联提案均为 accepted/scheduled | RELEASE | 移出未通过提案或等提案通过 |
| D3 | Release & Communication | 发布通知已起草 | **pass** | 发布通知 47 字符 | RELEASE | 起草含生效时间与联系人的通知 |
| D4 | Release & Communication | 试运行结论已归档 | **pass** | 试运行结论 45 字符 | QA | 补试运行结论与样本量 |
| D5 | Release & Communication | 回滚方案已写明 | **pass** | 回滚方案 50 字符 | RELEASE | 补回滚步骤与触发条件 |
| D6 | Release & Communication | 审批签字齐备 | **manual** | 已列 1 条审批记录(运营负责人B)，签字真伪与授权范围需人工核验 | OPS-LEAD | 补齐签字，代签或越权不予发布 |

> manual 表示脚本无法客观判定，不等于通过；必须由对应责任角色人工核对并留痕。
