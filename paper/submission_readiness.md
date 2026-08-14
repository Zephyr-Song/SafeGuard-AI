# SafeBARS CHI 2027 — 投稿就绪总清单（AI 已完成 vs 需你本人动作）

> 生成于 2026-08-13。**重大框架变更（当晚）**：论文已从"真人受控实验（Study 1）"重构为
> **系统/技术论文**——以两个真实存档会话（宿舍助手 + CampusMind）+ deep-audit 新旧版对撞
> （版本消融）为证据主干，**不再依赖 IRB / 真人收数即可投稿**。旧的 `⟨ ⟩` 占位符与
> "Study 1 Human-Subject Results" 节已删除。目标：把论文推进到"**可投稿的诚实草稿**"。
> 配套：`safebars_chi2027_draft.tex`、`irb_application.md`、`chi2027_submission_prep.md`、
> `study1_stats.py`、`study1_results_tables.tex`、`引用文献.md`、`插图检查报告.md`。
> 所有文件在桌面 `SafeBARS_论文插图设计/` 与 `D:\WorkBuddy\SafeGuard-AI-clone\paper\` 双份同步。

---

## 0. 🔴 唯一硬约束：CHI 2027 Papers 截止 2026-09-10（AoE）

距今约 **28 天**。论文现已重构为**系统/技术论文（路线 A 实操版）**：证据主干为两个真实存档
会话 + deep-audit 版本消融，**无需 IRB、无需招真人即可在 9/10 前投稿**。若后续想补"真人受控
实验"以增强说服力，则仍是 9/10 极紧；但那已不是投稿前提。

**请先决策（二选一）：**
- **路径 A — 赶 9/10（精简 Study 1）**：把 Study 1 写成"形成性评估"——报告朋友 pilot（n≈5–8）
  的质性发现 + 系统可用性，或跑一个小样本 Prolific 切片（n≈30–40）并明确标 preliminary；
  Study 2 模拟仍是论文主力证据。可行，但 Study 1 贡献变弱。
- **路径 B — 备齐后投下轮/邻近 venue**：所有资产现在就做到提交级，不赶 9/10；
  Prolific 正式 N=80–120 收满、编码、分析后投（CHI 2028 或其他 HCI 顶会）。
  质量最高，但错过 2027。

> 下表里所有"AI 已完成"项对**两条路径都适用**；"需你动作"项在路径 A 下可相应精简。

---

## 1. 完成状态总表

### ✅ AI 已完成（提交就绪，你只需复核/填空）

| 项 | 产物 | 说明 |
|---|---|---|
| 论文初稿全文（路线 A 系统论文） | `safebars_chi2027_draft.tex` | Abstract→Conclusion 完整；Method=Evaluation Design（案例+消融+仿真）；Evaluation=两个真实存档会话 + deep-audit 版本消融（CNTR-001 等真实计数）；贡献点/讨论/局限/结论已全部改写；无 IRB 脚注、无占位符 |
| 引用核验 | `引用文献.md` | 9 条全 ≥2023、零自引、零虚构；ACM DL + CrossRef 双源；BibTeX 齐 |
| 插图定稿 | `figures_export/`（PNG@300DPI + 矢量 PDF）+ `插图检查报告.md` | 矢量性/对比度/WCAG 已验证 |
| IRB 申请表 | `irb_application.md` | 可粘贴进 XJTLU 系统的完整申请表 + 附件清单 |
| 投稿准备包 | `chi2027_submission_prep.md` | 截止日/非匿名/字数/补件/APC/检查表 |
| 统计流水线 | `study1_stats.py` + `study1_results_tables.tex` | demo 跑通，出可粘贴 LaTeX 表 |
| 研究框架/写作指引 | `论文框架.md` | 逐节指引（引文+配图+内容） |
| Study 1 仪器 | `study1_protocol.md` / `.docx` / `osf_preregistration.md` / `pilot_runbook.md` | 方法/问卷/编码/预注册/pilot 全齐 |
| Study 2 模拟 | `analyze_sim_v2.py` + 结果 SVG/CSV | 各画像批判参与梯度已出 |
| **Pilot 覆盖状态图** | `figures_export/fig_pilot_coverage.{pdf,png}` | 修复 pilot 节此前编译缺失；矢量 PDF（Tj 262 / Do 0）|
| **「纠正」证据记录仪** | `study1_plandiff_instrument.md` + 接入 `study1_protocol.md` §C.2/§C.4/§F.4 + 扩展 `study1_stats.py` | before/after 计划 diff 捕获，新增 `corrected_blindspot_rate`（RQ4 纠正维度）；`--demo` 端到端跑通（标注 DEMO）|
| **真实聊天重放附录** | `figures_export/fig_replay_dorm.pdf` + draft `\appendix` | 真人会话逐字重放，佐证"镜面通过聊天浮现研究者没意识到的伦理盲点" |
| **插图矢量性修复** | `fig1_system_architecture.svg` 改 `font-weight="bold"` | Edge 打印对**数值粗体** (`700`/`600`) 会把整张 SVG 栅格化；改关键字后全矢量（9 张图全部 Do=0）|
| **LaTeX 一致性校验** | `_validate_paper.py` | 全过：9 图齐且矢量、`\input` 齐、`\cite`↔`\bibitem`、`\ref`↔`\label`、零 CJK、括号平衡 |

### ⏳ 需你本人动作（AI 无法代做）

| 项 | 动作 | 阻塞程度 | 完成判据 |
|---|---|---|---|
| **IRB 提交与获批**（未来工作） | 仅当后续想补"真人受控实验"时才需；当前路线 A 案例研究不需 IRB | 🟢 非阻塞（路线 A 已不依赖） | 可选：拿 approval # 回填 Limitations |
| **跑真人 Study 1**（未来工作） | 仅未来想补受控实验；当前评估用真实存档会话，不需招人 | 🟢 非阻塞 | 可选：收数后 `study1_stats.py` 出表 |
| **跑统计出表**（未来工作） | 仅未来真人 Study 1 时 | 🟢 非阻塞 | 可选 |
| **PCS 点提交** | 建 CHI 2027 Papers 投稿（**非 2268 表单**），传 PDF+补件 | 🔴 硬卡（最终动作） | 2026-09-10 前提交成功 |
| **本地/Overleaf 编译** | 编译 draft，确认插图不溢出、<12000 词 | 🟡 机械 | PDF 正常生成 |
| **作者信息** | 填 draft 作者块 `[Your Name]`/`[email]`（可加利物浦双署名） | 🟡 机械 | 作者块完整、非占位 |

---

## 2. 一键就绪路径（路径 A 赶 9/10，精简 Study 1）

1. **今天–本周**：填 `irb_application.md` 的 `[ ]` → 提交 XJTLU IRB（同时走 pilot 8/12–8/25 跑通，不等批文也可先 pilot 内部；但正式 Prolific 需批文）。
2. **拿到 IRB #** → 回填 draft 脚注 + IRB 表。
3. **8/26 起**：pilot 完成 → 9/2 起 Prolific 小切片（或仅 pilot 形成性评估，标注 preliminary）。
4. **收数后**：导出 session JSON + 填 roster.csv → `study1_stats.py` 出表 → 覆盖 `study1_results_tables.tex` → draft 占位符换真值。
5. **9/5 前**：Overleaf 编译 → 插图/字数核对 → 视频预览（可选）。
6. **2026-09-10 前**：PCS 提交（Papers track，非匿名，附 OSF 链接 + 补件）。

## 3. 路径 B（投下轮，质量优先）
跳过 9/10 压力：IRB 提交 → Prolific 正式 N=80–120 → 双编码 κ≥.70 → 统计 → 完整 Study 1 结果 → 投 CHI 2028 / 邻近 HCI 顶会。资产已全部就绪，随时可启动。

---

## 4. 文件清单（两份同步）

桌面 `SafeBARS_论文插图设计/` 与 `D:\WorkBuddy\SafeGuard-AI-clone\paper\` 均含：
`00_说明索引.md` · `论文框架.md` · `引用文献.md` · `插图检查报告.md` ·
`fig1/fig2/fig_sim*.{svg,png,csv}` · `shot_step*.png` · `fig_pilot_coverage.{svg,pdf,png}` · `fig_replay_dorm.pdf` · `figures_export/` ·
`safebars_chi2027_draft.tex` · `safebars_pilot_evaluation.tex` · `irb_application.md` · `chi2027_submission_prep.md` ·
`study1_stats.py` · `study1_plandiff_instrument.md` · `study1_results_tables.tex` · `study1_results.json` · `_validate_paper.py` ·
`相关报告/`（两份测试报告）。

---

## 5.  integrity 红线（务必遵守）
- **不伪造 Study 1 数据**：draft 中所有 `⟨ … ⟩` 均为占位符，真人数据未到前不得填数字。
- **不虚构引用**：引用清单零虚构、零自引、全 ≥2023（已核验）。
- **预注册优先**：OSF 预注册须在首位 Prolific 参与者前完成，`analysis_plan.py` 冻结。
