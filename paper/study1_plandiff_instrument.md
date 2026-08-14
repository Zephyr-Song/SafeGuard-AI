# SafeBARS · Study 1 Plan-Diff Instrument（before/after 计划 diff 记录仪）

> 版本：v1.0 ｜ 2026-08-13 ｜ 配套 `study1_protocol.md` §F.4 与 `study1_stats.py`
> 用途：**捕获"网站是否真的帮研究者纠正了计划"的行为证据**，补齐 Pilot 暴露的缺口
> 诚实背景：Pilot 中 R1 的修订台账记录了决策（add\_safeguard / consult\_stakeholders），
> 但写明 `"No concise changed passage was recorded"`——即**决定有了，计划文本改动没被记录**。
> 本仪器让"纠正"可被客观测量，而非依赖研究者自陈。

---

## 1. 为什么需要这台仪器（motivation）

论文主线主张是 *SafeBARS 帮研究者"发现并纠正"伦理盲点*。Pilot 已证明"发现"：
真实会话里镜面浮现了 ≥9 条伦理条目、≥3 个盲点、1 处内部矛盾、5 个真实败例类比。
但"纠正"在 Pilot 中**证据为空**——台账只记了决策类别，没记计划文本前后变化。

如果论文要 claim "帮助发现并纠正"，必须能回答三个问题（来自真实数据，非自陈）：
1. 进入 mirror **之前**，研究计划原文是什么？
2. 离开 mirror **之后**，修订后的计划原文是什么？
3. 每条修订**对应 AI 的哪个发现**（finding id）？

本仪器就是为这三个问题提供结构化、可编码、可统计的捕获方案。

---

## 2. 捕获时点（接入流程）

在 `study1_protocol.md` 的现有流程上**新增两个捕获点**，不打断原设计：

| 时点 | 现有步骤 | 新增捕获 |
|---|---|---|
| 干预前 | C.2 Pre-task：列出受影响群体 + 自评稳健度 | **新增 `plan_before`**：粘贴/提交的研究计划**全文**（研究者将拿去跑 mirror 的那一版） |
| 干预后 | C.4 Post-task：重新列出群体 + 自由反思 | **新增 `plan_after`**：经 mirror 协作修订后的研究计划**全文** |
| 修订中 | C.3 干预：系统记录 revisions / ledger | **新增 `revision_links`**：每条 revision 标注它响应了哪个 finding（见 §3） |

> 实现提示：现有 `mirror` 已在 `revisions` / `replay_history` 记录决策类别；
> 只需在 UI 增加两个文本框（提交计划前的 `plan_before`、提交修订后的 `plan_after`），
> 并把 `revision.id ↔ edge/lens id` 的映射写进 `revision_links`。`GET /api/.../sessions/{id}`
> 已能导出整段 session，故取数接口无需新增。

---

## 3. 数据 schema（JSON，随 session 导出）

```json
{
  "plan_before": "研究者进入 mirror 前提交的研究计划全文（自由文本）",
  "plan_after":  "研究者离开 mirror 后修订完成的研究计划全文（自由文本）",
  "revision_links": [
    {
      "finding_id": "EDGE-001 | lens:privacy | CNTR-001 | AUD-EDGE-002",
      "finding_summary": "镜面浮现的该条发现的一句话摘要（用于前后文匹配）",
      "revision_text":   "plan_after 中实际回应此发现的具体文本片段（逐字摘录）",
      "link_type":       "add_safeguard | contest_with_evidence | consult_stakeholders | none",
      "resolved_state":  "action_linked | claimed | none"
    }
  ]
}
```

字段说明：
- `finding_id`：镜面给出的发现标识（张力边 / 镜头 / 矛盾 / 审计边），用于溯源到具体 AI 输出。
- `finding_summary`：该发现的自然语言摘要，用于判定它是否原本就存在于 `plan_before`
  （即"盲点"判定：summary 不是 `plan_before` 的子串 → 该发现是研究者未写下的盲点）。
- `revision_text`：研究者实际写进 `plan_after` 的对应片段（编码者据此判断"是否真的改了"）。
- `resolved_state`：编码者判定该修订把价值落到了什么程度
  （`action_linked`=有具体护栏动作；`claimed`=仅声明；`none`=未改）。

---

## 4. 计算指标（行为化，非自陈）

对每条 `revision_link`：

```
was_blind   = finding_summary 不在 plan_before 中（大小写不敏感）
addressed   = resolved_state == "action_linked" 且 revision_text 出现在 plan_after 中
corrected_blind += (was_blind and addressed)
surfaced_blind  += was_blind
```

汇总到研究者层面：

```
corrected_blindspot_rate = corrected_blind / surfaced_blind      # 盲点纠正率
unresolved_blind         = surfaced_blind - corrected_blind      # 仍漏掉的盲点
```

组间对比（RQ4 的"纠正"维度）：

```
多模态臂 corrected_blindspot_rate  vs  文字臂 corrected_blindspot_rate
```

> 该指标与 `study1_protocol.md` §F.1 的 Δ群体数、行为化修订计数**互补**：
> Δ群体数测"想到了更多受影响的群体"，corrected_blindspot_rate 测"把镜面指出的盲点真的写进了计划"。
> 两者共同构成 RQ4 的**行为化心智改变**证据，避免只靠自陈（MC1–MC3）。

---

## 5. 编码方案（2 编码者，接 §F 的 IRR 要求）

对每个 `revision_link` 独立编码：

| 维度 | 取值 | 判定依据 |
|---|---|---|
| was_blind | 0/1 | finding\_summary 是否为 plan\_before 已覆盖（子串匹配 + 人工确认） |
| resolved\_state | action\_linked / claimed / none | revision\_text 是否给出具体护栏 / 仅声明 / 未出现于 plan\_after |
| link\_valid | 0/1 | finding\_id 是否真实对应镜面输出（防止编造关联） |

- **评分者间信度**：κ ≥ .70（与 §F.2 同标准）；不达标则协商或加第 3 人。
- **主 DV（RQ4 纠正）**：`corrected_blindspot_rate`，report M/SD + 组间 Welch t + Cohen's d（见 `study1_stats.py` 输出 `tab:h4corr`）。

---

## 6. 与统计流水线的衔接

`study1_stats.py` 已扩展：
- 新增 `correction_metrics(session)`：从上述 schema 直接计算 `corrected_blindspot_rate`；
  session 缺字段时优雅返回 `None`（不影响其他表）。
- `_run_tests` 新增 **RQ4 纠正表**（`tab:h4corr`）：多模态 vs 文字臂的盲点纠正率。
- 汇总 JSON（`study1_results.json`）含 `RQ4_correction` 字段，可直接进 OSF 补充材料。
- `--demo` 已带 plan\_before/after + revision\_links，端到端可跑通（标注 DEMO）。

运行（真实数据就位后）：
```bash
python study1_stats.py roster.csv session1.json session2.json ...
```
