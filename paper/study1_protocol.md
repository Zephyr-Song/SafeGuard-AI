# SafeBARS · Study 1 实验方案与测量工具（CHI 2027）

> 版本：v1.0 ｜ 2026-08-11 ｜ 配套 `experiment_plan.md` 与 `safebars_chi2027_outline.tex`
> 定位：**真人 between-subjects 用户研究**，回答 RQ1–RQ4（论文主力证据）。
> 线上系统：`https://safebars-ai.pages.dev/safebars/mirror`（多模态臂）/ `?cond=text`（文字对照臂）
> 说明：本文件含**设计说明（中文）**与**参与者面件（英文，可直接用于 Prolific / IRB）**两部分。

---

## A. 研究问题与测量主表（RQ → 假设 → 因变量 → 分析）

| RQ | 研究问题 | 假设（pre-registered 主假设） | 主要因变量（DV） | 分析 |
|---|---|---|---|---|
| **RQ1** | 多模态镜是否比文字镜更能促发伦理盲点的**自我发现**？ | H1：多模态臂的"自我归属式发现"（I didn't realize）比例 > 文字臂 | ① 行为：self_discovery 中 `anticipated=not` 占比；② 自陈：Self-Discovery 量表（§E.1） | 2(模态) ANOVA / ANCOVA（协变 pre 稳健度） |
| **RQ2** | "镜只提问、不处方" vs "镜直接陈述问题"，哪种更促发**自我发现**？ | H2：withhold（只提问）条件的自我归属发现 > prescribe（直接陈述）条件 | 同上，但在**张力层面**的 within 对比（见 §B.3） | 混合效应模型（张力为重复测量） |
| **RQ3** | 协作式修订（脚手架、不自动改）是否保留**研究者拥有感**且产出**高质量修订**？ | H3：拥有感高，且修订被独立评分者判为"具体、有伦理依据" | ① 拥有感量表（§E.4）；② 修订质量 rubric（§F.2，编码） | 相关 + 组间比较 |
| **RQ4** | 镜是否**真实改变研究者心智**（而非仅生成报告）？ | H4：post 受影响群体数 > pre；且行为化修订被实际加入计划 | ① 行为：Δ(pre/post 群体数) + 行为化修订计数（§F.1）；② 自陈 Mindset-Change（§E.2） | 配对 t（within）+ 组间 ANOVA |
| **RQ-align**（探索，来自 Vibe Check） | 批判/非谄媚 vs 谄媚对齐，如何影响信任与批判距离？ | 探索：批判镜提升批判距离、不损信任 | 批判距离（§E.5）+ 信任（§E.6） | 2×2 探索性（若 N 允许） |

**预注册（pre-registration）**：在 OSF 注册主假设 H1/H3/H4 与主要 DV（self-discovery 行为率、Δ群体数、拥有感），含分析计划与停止规则。RQ2 / RQ-align 标为**探索性**（exploratory），避免 p-hacking。

---

## B. 实验设计

### B.1 主设计（pre-registered）
- **2（模态：Multimodal vs Text-only）between-subjects**。
- 操纵已实现：
  - **Multimodal 臂**：线上默认链接 `…/safebars/mirror`，Step 4 呈现三视图（利益相关方图 / 价值冲突热力图 / 场景分支树）+ 自发现提问 + 修订前后重渲染。
  - **Text-only 臂**：同站点 `…/safebars/mirror?cond=text`，Step 4 多模态面板整体隐藏，仅保留基线文字/卡片式界面（张力以文字列表呈现，无可视化、无自发现提问）。引擎输出完全一致，仅呈现模态不同 → 干净操纵。
- **随机化**：Prolific 配额随机分臂；朋友 pilot 用随机数字表/在线随机器。

### B.2 被试
- **Pilot**：8–12 人（朋友 + XJTLU 学生），用于流程可行性、题项校准、抓 bug。
- **主研究（Prolific）**：目标 **N = 80–120**（每臂 40–60）。资格：设计过或正在设计 AI / HCI 系统的研究者或研究生（资格题筛选）。
- **功效**：2 臂检测中等效应 d≈.5（α=.05, 1−β=.8）约需 64/臂；本样本对中等以上效应有把握，对小效应可能欠功效——故主对比聚焦 self-discovery 复合分数。
- **伦理**：XJTLU SURF / 校内 IRB 审批；Prolific 研究含知情同意 + 数据匿名 + 报酬。

### B.3 RQ2（处方 vs 保留）的实施决策 —— 张力层面 within 设计
为不翻倍样本，RQ2 设计为**同一会话内、张力层面的 within 对比**：
- 每位参与者看到的张力分成两半：一半以 **withhold** 风格渲染（当前默认：红节点 + "你预料到这个群体吗？"，镜不宣判）；另一半以 **prescribe** 风格渲染（镜明确陈述："此群体受影响，而你未覆盖"，再问后果）。
- **所需代码改动（待实现）**：`mirror_multimodal.js` 的 `renderDiscovery()` 增加 `style` 参数（`withhold`|`prescribe`），由后端按张力 `edge.id` 哈希或 `?disc=split` 分配；`self_discovery` 字段增加 `style` 维度便于分组。
- **坍缩规则**：若实现来不及，RQ2 降级为**跨被试**探索（multimodal 臂内随机半数仅 withhold、半数仅 prescribe），或仅在 pilot 内做质性探索，主论文只报告 RQ1/RQ3/RQ4。

### B.4 RQ-align（批判 vs 谄媚）的实施决策
- **可选 2×2（模态 × 对齐）**：对齐条件由 `?align=critical|sycophantic` 控制——`critical`=当前非谄媚文案；`sycophantic`=新增"附和式"文案变体（如张力改写为"你的设计已经很周全，这里仅作提示"）。
- **所需代码改动（待实现）**：新增 `sycophantic` 文案分支（仅文案，不动引擎逻辑）。
- **优先级**：低于 RQ1/RQ2；若 9 月前 N 不足，仅报告批判镜（即当前默认）结果，对齐作为 future work / 探索。

---

## C. 参与者流程（逐步脚本）

> 以下英文为**实际展示给参与者的内容**；中文括号为给研究者的操作提示。

### C.0 招募（Prolific / 朋友）
- 资格筛选题："你是否设计过或正在设计一个 AI 或 HCI 系统？（是 / 否）" → 否则排除。
- 告知时长约 20–30 分钟，报酬按平台标准。

### C.1 知情同意（见 §D，须先签署）
- 展示同意书 → 勾选"我自愿参与，理解可随时退出" → 进入研究。

### C.2 Pre-task（干预前，约 5 分钟）
1. **列出受影响群体**：*"List the groups of people your design affects or could affect (e.g., users, non-users, vulnerable groups). List as many as you can."*（开放文本框，逐行）
2. **自评伦理稳健度**（7 点）：*"How ethically robust do you think your current design is?"*（1=very weak, 7=very strong）
3. **分配到的场景**：给参与者一个**真实研究计划文本**（统一材料，见 §G），或允许粘贴自己的计划（主研究用统一材料以控变异）。

### C.3 干预（使用镜，约 10–15 分钟）
- 打开分配到的链接（多模态臂 / `?cond=text` 文字臂）。
- 指令（英文）：*"Submit the research plan. Walk through the mirror step by step. When you reach 'See the tension', examine the views presented. When prompted whether you anticipated a group, answer honestly. Then revise your design using the scaffold (you stay the author — the tool will not auto-edit)."*
- 系统自动记录：`self_discovery`（anticipated/not + realized 文本）、修订（revisions）、`?cond` 分臂、会话时长。

### C.4 Post-task（干预后，约 5 分钟）
1. **重新列出受影响群体**：*"Now list again the groups your design affects or could affect."*（开放文本）
2. **自由反思**：*"What, if anything, did you realize about your design that you had not considered before? Quote the moment if you can."*（开放文本）
3. **填写后测量表**（§E，7 点 Likert + 操纵检验 + 开放题）。

### C.5 Debrief（见 §H）
- 解释研究目的、多模态 vs 文字操纵、自发现机制；提供联系人；感谢。

---

## D. 知情同意书（英文，参与者面件）

> **Informed Consent — SafeBARS Ethical Mirror Study (CHI 2027)**
>
> **Purpose.** We are studying how different ways of presenting ethical feedback help researchers notice blind spots in their own AI/HCI designs. You will use a web tool called the "Ethical Mirror," then answer a few questions.
>
> **What you will do.** (1) List who your design affects; (2) Use the mirror with a research plan for ~10–15 minutes; (3) List affected groups again and answer a short questionnaire (~20–30 min total).
>
> **Data & privacy.** Your responses and tool interactions (including free-text you type) are recorded for research. Data are stored anonymously / pseudonymously and reported in aggregate. No decision about you is made from this study. You may withdraw at any time without penalty by closing the window (note: already-submitted data may be retained per IRB policy).
>
> **Risks & benefits.** Risk is minimal (reflecting on your own design). Benefit is a chance to improve your design's ethics. There is no cost to you.
>
> **Voluntary participation.** Participation is voluntary. You may skip any question or stop at any time.
>
> **Contact.** [PI name / lab / email]. This study is approved by [XJTLU IRB / SURF], approval #[#].
>
> **Consent.** By clicking "I agree," you confirm you are 18+ and consent to participate.

---

## E. 后测量表（英文，7 点 Likert：1=Strongly disagree … 7=Strongly agree，除非注明）

### E.1 Self-Discovery of blind spots（RQ1/RQ2 主 DV，自陈）
- SD1. *The mirror helped me **see** a gap in my own design, rather than just being told about it.*
- SD2. *At least once, I thought "I hadn't realized this design would affect this group."*
- SD3. *I noticed stakeholder groups I had not considered before using the mirror.*
- SD4. *The insight felt like my own realization, not something the tool asserted for me.*（反向验证"自发现"而非"被宣判"）

### E.2 Mindset change（RQ4 自陈）
- MC1. *My understanding of who my design affects changed after using the mirror.*
- MC2. *I made concrete changes to my plan because of what I saw.*
- MC3. *I would revise my actual research plan based on this session.*

### E.3 Revision quality —— **编码项，不自陈**（见 §F.2）

### E.4 Agency / ownership（RQ3）
- AG1. *I felt in control of the changes made to my design.*（adapted Perceived Ownership）
- AG2. *The mirror did not take authorship away from me.*
- AG3. *The final revised design feels like mine.*
- AG4. *The tool scaffolded my thinking rather than replacing it.*

### E.5 Critical distance（我们的贡献构念，RQ-align）
- CD1. *The mirror pushed back on my assumptions rather than simply agreeing with me.*
- CD2. *The mirror felt impartial and critical, not flattering.*
- CD3. *I would have liked the mirror to challenge me even more.*（反向：低分=已足够批判）

### E.6 Trust / acceptance（RQ-align，adapted Trust in Automation / UTAUT）
- TR1. *I trusted the mirror's feedback.*
- TR2. *I would use a tool like this in my real research.*
- TR3. *The mirror's suggestions were useful for my design.*

### E.7 Aha / insight moment（RQ2 机制）
- AH1. *I experienced a clear "aha" moment while using the mirror.*（adapted Insight/EMA）
- AH2. *At least one visualization or scenario made me reconsider my design.*

### E.8 操纵检验（Manipulation checks）
- MK1 (模态). *The tool used interactive visualizations (diagrams/maps) to show impacts.* → 多模态臂应高、文字臂应低。
- MK2 (RQ2, 若实现). *At some points the tool directly told me a problem; at other points it only asked me a question.*
- MK3 (对齐, 若实现). *The tool's tone felt agreeable/flattering vs critical.*（语义差分）

### E.9 开放题（质性，编码用）
- OP1. *Quote the moment you realized a blind spot (if any).*
- OP2. *Anything you'd change about the tool?*

---

## F. 编码方案（行为化证据，2 编码者）

### F.1 心智改变（RQ4，行为）
- **Δ群体数**：比较 pre（C.2.1）与 post（C.4.1）列出的群体集合，计 **新增群体数**（post 有、pre 无）。
- **行为化修订计数**：从 `revisions` 提取——计 `add_safeguard` / `consult_stakeholders` / 实际写入计划的护栏文本条数（vs 仅 `revise_design` 措辞）。
- 指标：added_groups、safeguard_actions。

### F.2 修订质量 rubric（RQ3，2 评分者）
对每个修订按 4 维评分（1–5）：
1. **Specificity** 具体性（是否指明具体群体/机制）
2. **Ethical grounding** 伦理依据（是否引用价值/风险）
3. **Feasibility** 可行性（研究中可落地）
4. **Stakeholder coverage** 覆盖度（是否覆盖被漏群体）
计分：quality_mean（4 维均）。**评分者间信度目标 Kappa / ICC ≥ .70**，否则协商或加第 3 人。

### F.3 自我发现归属编码（RQ1/RQ2 行为 DV）
来源：`self_discovery` 字段（anticipated/not + realizedText）+ post OP1/OP2 + 修订 rationale。
- 对每个张力/发现编码为：
  - **SELF**（自我归属）："I didn't realize / I hadn't thought of this group" 类表述 → 计 self_attributed。
  - **SYSTEM**（系统归属）："the tool told me / the tool showed that…" 类表述 → 计 system_attributed。
- **主行为 DV**：self_attributed_rate = self_attributed / (self_attributed + system_attributed)。
- 与自陈 SD1–SD4 三角验证。

---

## G. 统一研究计划材料（控变异）
- 主研究用**统一提供的计划文本**（避免自建计划质量差异污染）。建议两条：
  - **低敏感**：宿舍公平小助手（R1，便于上手）。
  - **高敏感**：CampusMind 校园心理危机静默早筛（R2，张力更强，盲点更易触发）。
  - 随机分配一条给参与者（或全用 R2 以最大化效应；pilot 内测试哪条效应更强）。
- 朋友 pilot 可允许粘贴自己的计划（探索生态效度）。

---

## H. Debrief（英文）
> **Debrief.** Thank you. This study compares a **multimodal** ethical mirror (interactive maps/heatmaps/trees + a prompt that lets *you* discover gaps) against a **text-only** version. We are testing whether *seeing* a gap (vs being told) helps researchers notice their own blind spots and change their designs. Your free-text and interactions were recorded anonymously. If you'd like the results or have questions, contact [PI]. You may withdraw by emailing [PI] within [window].

---

## I. 量化分析计划（细节）
- **主模型（RQ1）**：`self_attributed_rate ~ modality + pre_robustness`（ANCOVA）；自陈 SD 复合 ~ 同上。
- **RQ2**：`discovery_style(withhold vs prescribe) × modality` 混合模型，张力为随机截距。
- **RQ3**：AG 复合 vs 质量 rubric（相关）；组间比较 multimodal vs text 在 AG 上（预期不劣）。
- **RQ4**：Δ群体数、safeguard_actions 配对 t（within 所有参与者）；组间 ANOVA 在 MC 复合。
- **RQ-align**：探索性 2×2（模态 × 对齐）在 CD/TR 上。
- **效应量**：η² / Cohen's d，报 95% CI。
- **多重比较**：主对比不校正（pre-reg）；探索性 RQ 用 Holm/Bonferroni 校正并标注 exploratory。
- **预注册**：OSF 存本文件 + 分析脚本 + 停止规则（pilot 后冻结主分析）。

---

## J. Pilot 手册（8/12–8/25）
- **目的**：流程可行性、题项理解、抓 bug、估时长、选 R1/R2 材料。
- **检查清单**：
  1. 两臂链接都能开、`?cond=text` 面板隐藏、self_discovery 落库（服务端可取）。
  2. 参与者能否理解 SD/MC 题项（有无歧义）。
  3. 时长是否 20–30 min（超则删题）。
  4. 编码者（2 人）对 F.1–F.3 的 Kappa 是否 ≥ .70（pilot 内练）。
  5. **停止规则**：任一两臂技术失败率 > 20% 或中位时长 > 40 min → 修后重测。
- **产出**：校准后题项 + 冻结的主分析脚本（pre-reg 用）。

---

## K. 数据伦理与处理
- 匿名/假名化存储；free-text 可能含个人信息 → 编码去标识。
- IRB 审批号在同意书/论文注明。
- 公开：编码方案 + 去标识数据 + 分析脚本随论文放出（OSF），符合 CHI 开放科学。

---

## L. 待实现的代码改动（实验使能，非论文文字）
| 项 | 用途 | 文件 | 状态 |
|---|---|---|---|
| RQ2 张力层面 withhold/prescribe 风格 | `renderDiscovery(style)` + `?disc=split` + self_discovery.style | `mirror_multimodal.js` / `mirror_engine.py` | 待实现 |
| RQ-align 批判/谄媚文案 | `?align=critical|sycophantic` 文案分支 | `mirror_multimodal.js` + 模板 | 待实现（低优先） |
| 服务端取数接口 | 导出 session 的 self_discovery + revisions 供编码 | `mirror_api.py` | 已有（GET session） |
