# SOP 新版本上线前检查表与自动核对脚本（#3166 / S6-SOPR-015）

交付两件东西：

1. 检查表：24 项 / 4 组，每项写明判定标准、核对方式、责任角色、不通过处置。
2. 自动核对脚本：读一份 SOP 模板版本导出 JSON，逐项输出 `pass / fail / manual`。
   **查不出来一律记 `manual`，绝不记 `pass`。**

## 目录

```text
ACCEPTANCE.md                   验收对照（AC ↔ 实现 ↔ 复跑命令 ↔ 实测结果）
ACCEPTANCE-EVIDENCE.md          实测证据（命令、退出码、原始输出）
MANIFEST.sha256                 干净副本生成的 SHA256 清单
docs/AC-MAPPING.md              平台原文、AC 与证明映射
docs/CHECKLIST.md               检查表（Markdown，唯一真源）
docs/CHECKLIST.xlsx             检查表（Excel，由 Markdown 生成）
scripts/check_sop_release.py    核对脚本
scripts/check_checklist.py      检查表自证（24 项 / 4 组 / 字段齐全）
scripts/build_checklist_xlsx.py 由 Markdown 生成 Excel
scripts/secret_scan.py          密钥 / 隐私 / 本机路径扫描
scripts/build_manifest.py       生成 MANIFEST.sha256（干净副本上运行）
scripts/verify_sha256.ps1       校验 MANIFEST.sha256
samples/sample_pass.json        合规样例
samples/sample_err_content.json 埋错样例：内容完整性 6 项
samples/sample_err_data.json    埋错样例：数据与系统 5 项
samples/sample_err_release.json 埋错样例：执行/发布 8 项
stubs/kb_articles.json          知识库接口桩
stubs/improvement_proposals.json 改进提案接口桩
reports/sample-report.md        样例报告（Markdown）
reports/sample-report.json      样例报告（JSON）
evidence/                       原文、自检、dry-run、反例实录
```

## 怎么跑

要求：Python 3.9+，只用标准库；生成 Excel 需要 `openpyxl`。

```powershell
cd clawhunt-3166-sop-checklist

# 1) 核对一份导出 JSON（默认打印 Markdown 报告）
python scripts/check_sop_release.py samples/sample_pass.json

# 2) 同时落盘 Markdown + JSON 报告
python scripts/check_sop_release.py samples/sample_pass.json `
  --report reports/sample-report.md --json-report reports/sample-report.json

# 3) dry-run：只校验输入并列出 24 项检查，不写报告
python scripts/check_sop_release.py samples/sample_pass.json --dry-run

# 4) 自检：合规样例必须零 fail；3 份埋错样例必须各自报出预设 fail；
#    另含两条内存变异注入，证明脚本不是永远绿灯
python scripts/check_sop_release.py --self-test

# 5) 检查表自证 + 重新生成 Excel
python scripts/check_checklist.py
python scripts/build_checklist_xlsx.py

# 6) 密钥 / 隐私扫描（0 命中才通过；额外黑名单值用 --deny-literal 传入，不落仓）
python scripts/secret_scan.py --deny-literal <value>

# 7) 生成并校验文件清单（清单在干净副本上生成）
python scripts/build_manifest.py
pwsh -File scripts/verify_sha256.ps1
```

## 怎么读结果

| 结果 | 含义 | 必须的动作 |
|---|---|---|
| `pass` | 脚本实际执行了该检查，条件成立 | 无 |
| `fail` | 脚本实际执行了该检查，条件不成立 | 按报告“不通过处置”列整改后复跑 |
| `manual` | 脚本无法客观判定（缺数据、需人判断、接口不可用） | 由责任角色人工核对并留痕，**不得当成通过** |

报告头部的 `脚本实际核验（pass+fail）` 就是自动核验项数。合规样例为 22 项，满足 AC 的“至少 10 项”。

### 退出码

| 码 | 含义 |
|---|---|
| 0 | 无 `fail`（允许存在 `manual`） |
| 1 | 至少 1 项 `fail` |
| 2 | 参数、输入或 stub 读取错误 |

脚本内部做了兜底：某个检查函数抛异常时，该项记 `manual` 并写明异常类型，不会因为崩溃而变绿。

## 导出 JSON 结构

真实接口未交付，按平台允许先用样例。字段定义如下（`docs/CHECKLIST.md` 的检查项一一对应）：

```json
{
  "template": {
    "template_id": "SOP-MEMBER-ONBOARD",
    "version": "2.3.0",
    "previous_version": "2.2.0",
    "change_type": "content",
    "roles": ["member_ops", "ops_manager"],
    "club_operating_hours": {"start": "09:00", "end": "18:00"},
    "reviewers": [{"role": "frontline_rep", "name": "...", "decision": "approved"}],
    "approvals": [{"role": "ops_manager", "name": "...", "signed_at": "..."}],
    "changelog": ["..."],
    "release_notice": "...",
    "pilot_conclusion": "...",
    "rollback_plan": "...",
    "linked_improvement_proposals": ["IP-1001"],
    "review_metrics": [{"name": "一次通过率", "field": "review_result"}]
  },
  "steps": [
    {
      "step_key": "KYC_REVIEW",
      "title": "...",
      "assigned_role": "member_ops",
      "escalation_role": "ops_manager",
      "completion_criteria": "...",
      "required_materials": ["..."],
      "sla_hours": 24,
      "exception_path": "...",
      "prerequisites": [],
      "form_fields": [{"key": "company_name", "type": "text", "required": true}],
      "referenced_kb_articles": ["KB-1001"]
    }
  ]
}
```

## 接口桩与真实对接点

| 检查项 | 现在怎么查 | 接真实系统时改哪里 |
|---|---|---|
| A4 知识库文章 | 读 `stubs/kb_articles.json` 的 `status` | 把 `load_json(kb_stub)` 换成 S3-KB 的文章详情接口；字段保持 `status=published` |
| D2 改进提案状态 | 读 `stubs/improvement_proposals.json` 的 `status` | 换成提案系统详情接口；合法状态为 `accepted` / `scheduled` |
| B4 营业时间 | 固定 `manual` | 有排班系统后，可接入节假日表再降级为自动 |

stub 文件缺失时：A4 与 D2 落 `manual`，不落 `pass`。

## 版本号规则

S6-SOPR-014 原文未随本单提供。脚本先用可替换的 semver 占位规则：

- `change_type=fix`：只递增 patch；
- `change_type=content`：递增 minor；
- `change_type=breaking`：递增 major；
- 缺少 `change_type` 或版本号非法：落 `manual` / `fail`。

接真实规则时只需改 `check_c5` 一处，检查表 C5 的判定标准同步更新。

## 自检为什么能证明“不是永远绿灯”

`--self-test` 共 23 条断言：

1. 合规样例：`fail=0`，自动核验 22 项（≥10）。
2. 三份埋错样例的 fail 集合必须**精确等于**预设集合：
   - content：`A1,A2,A3,A4,A5,A6`
   - data：`C1,C2,C3,C5,C6`
   - release：`B1,B3,B6,D1,D2,D3,D4,D5`
3. 内存变异注入：把合规样例的版本号改成不递增，C5 必须报 `fail`；清空责任角色，A1 必须报 `fail`。

任何一条不满足，自检退出码为 1。

## 限制（直说）

- 真实 S3-SOP / S3-KB 未接入，知识库与提案走 stub；报告不冒充“已对接生产”。
- B4（营业时间冲突）与 D6（审批签字）固定人工，脚本不给绿灯。
- 未调平台提交接口；仓库为公开源码仓，交付由核心团队统一验收。
- 样例数据全部虚构，不含任何真实企业或个人信息。
- `MANIFEST.sha256` 覆盖全部交付件；不含自身，也不含 `evidence/*.log`（运行日志在清单之后产生且会随复跑变化，故不纳入；`evidence/problem-3166.raw.json` 原件纳入）。
