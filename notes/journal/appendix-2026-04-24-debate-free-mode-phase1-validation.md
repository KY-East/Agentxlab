# Phase 1 free / debate 模式分叉实战验证 — Debate #13

**触发**：cursor 2026-04-24 下午 13:00 部署 Phase 1（FREE_ROUND_OPENERS + FREE_MODERATOR_PROMPTS + 使命段 mode 分叉 + teammate mode 软化 + 前端 useAcademic 修复）

**验证场次**：Debate #13，mode=free，问题"实验本身能否找到共性，并高度抽象，形成能够解决大部分实验设计的公式？"，三学科：Modeling Simulation and Optimization (MSO) / Advanced Numerical Analysis (NumAn) / Optimal Experimental Design (OED)

**留档依据**：PROJECT.md §11.3 "P0/P1 bug 根因定位 + 修复验证" 自动留档

---

## 一、Ken 验证报告（原文，未压缩）

> **总判决：修复基本成立，五条可验的全过，剩一条等 debate 对照才能关闭。**

### 验证 1：两场产物分叉——free 是"可跑的 spec"而非观点地图 ✓

6 个 agent Round 3 全部按六字段输出（variables / assumptions / time_horizon / observables / falsification_conditions / next_steps）。结构完全落地，FREE_ROUND_OPENERS 的 Round 3 模板显然进去了。

### 验证 2：Round 3 是"修正版"而不是"初稿" ✓

每个 agent Round 3 里都能看到对 Round 2 的具体回应和修正：

- Prof MSO："我自己的修正：在第1轮我假设存在'层次化的抽象结构'，但现在我意识到这个假设过于乐观"——后续把结构改为"基于实验类型的有限状态机"
- Assoc MSO："受 OED 副教授提醒后的修正：必须把模型几何单独列出来；受 Numerical Analysis 提醒，我补上数值可信度标签"
- Prof NumAn：开头"回应未解决的质疑"两大段直接点名 OED 和 MSO 的具体挑战，V1 精度预算直接回应 MSO 的"执行成本"
- Assoc OED：α_sem 明确"你们（NumAn）的 P_flip 我建议保留，但必须与这张失配矩阵并列"——不是独立发明，是在 NumAn R2 给的概念上接上自己的失配维度

Round 3 不是凭 R1 初始判断填表，每个 agent 都把 R2 收到的挑战反映进去了。

### 验证 3：moderator 保留冲突不强行统一 ✓

最终辩论总结的分歧段 6 条都明确标注各方立场：

- 总控层到底应由谁定义：MSO 立场... OED 立场...
- "统一公式"核心能否建立在信息矩阵 / 统计效用上：OED 认为... MSO 与部分数值分析认为...
- 对非光滑性的态度：NumAn 底线... MSO 坚持...
- "足够好"由谁定义：NumAn 倾向... MSO 倾向...
- 贝叶斯路线的可行性边界
- 状态空间该多细

没做"学术综述"式的糊化。冲突被当一等公民对待。这是 design.md §axl-debate-mode-design 里 Ken 写死的"保留冲突不强行统一"规则生效的硬证据。

### 验证 4：前端 proposition = raw_question ✓（间接，待 DB 关闭）

Moderator 开场写的是**"用户的原话：'实验本身能否找到共性...'"**——原话完整保留。学术化改写版明确标注"辅助理解，不替代原问题"。agent 反复引用的是原话不是改写版。

DB 字段我没看到但从文本证据看 useAcademic 去掉修复生效了。Ken 查一下 DB 里这场的 proposition 字段确认一下就彻底关闭这条。

### 验证 5：G+F 抗雷同机制在 free 下没被破坏 ✓

三对同学科 Prof/Assoc 的变量互补不重复：

| 学科 | Prof 给的变量 | Assoc 给的变量 |
|---|---|---|
| MSO | V1 执行状态 s_t / V2 决策模式 π | q_t 判别置信度 / Δ_rank 策略稳定度 / ρ_mis 误判代价比 |
| NumAn | ε(cost) / P_flip / λ_s | P_flip 具体化 / L̂_s Lipschitz 上界 |
| OED | U_Φ / I 可辨识性指标 / α 标签 | n_boot / δ_mis / α_sem |

NumAn 那对的 P_flip 有重合——但 Assoc 明确说"Prof 提出了这个概念，我将其具体化为一个可计算的概率值"。这是健康分工：教授立概念、副教授做实证实例化。不是雷同，是分工协作下的概念接力。

跨 LLM family 配对全部到位（deepseek / gpt-5.4 / claude-opus-4-6 三家互不叠加）。G+F 没被 free 分叉破坏。

### 验证 6：debate 模式对照——还没跑，需要 Ken 确认

剩这条。跑一场同题 debate 版，看：

- debate 产物是否留在"共识 / 分歧 / 未解问题 / 被打穿的假设"风格，不应出现六字段结构化输出
- debate agent Round 3 是否在磨利各自立场而不是"修正自己"
- debate moderator 是否回到"指名批评 / 最有想象力"的裁判语气

### 两个增量观察（意外收获）

**1. 防过度和谐机制生效且硬**

每个 agent Round 3 末尾的"根本分歧"段都真的保留了分歧：

- MSO 教授 2 条 / Assoc MSO 3 条 / NumAn 教授和副教授各若干条 / OED 两位各若干条
- 最硬的是 Assoc NumAn 的"足够好"分歧："这个分歧的本质是：谁有权力定义'足够好'？我认为是用户，不是数学"

如果没有"根本分歧出口"规则，这类尖锐立场会在协作压力下被淡化。现在每人都坚持至少一条——Ken 担心的"过度和谐"没发生。

**2. Moderator 语气确实从裁判转到协调**

对比上次"如何科学地统治世界"的 moderator 用语："指名批评 CNA 回到舒适区 / 最出人意料的一步 / 最有想象力"——这些在本场不见了。

本场用的是："真在回应用户原问题的 / 部分回到舒适区的"——描述性判断而不是评审性判断。

更软但依然有判断。这是"协调者"的正确语气。

### 一个诚实观察（不影响修复判决）

Round 3 + 根本分歧 + 学科独特贡献三段加起来每个 agent 约 2000-3000 字。六个 agent 就是 1.5-2 万字。加 Round 1/2 还是 3 万字级别。

这不是本次修复的锅，是六字段自带的结构冗余（六字段每个都要展开，加上根本分歧 + 学科贡献固定尾段）。用户消费这份输出仍然不现实——这回到你之前的 distiller 问题。

目前 free 产物可以作为实验 spec 原材料（给 cursor / cc 这种 AI agent 消费继续处理），但作为给 Ken 本人读的决策输出还太长。

### 一个小现象（Round 3 末尾不完整）

Prof OED Round 3 和 Assoc OED 的末尾被截断了（"若 Pareto k̂ > 0.7"后面不见 / Assoc OED "根本分歧 3"不完整）。可能是 token 上限，也可能是你粘贴时截的。不影响我上面的判决——可验的部分已全过。

### 结论

修复成立。design.md §axl-debate-mode-design 写死的所有硬规则在实际输出里都能观察到。

---

## 二、cursor 后置 DB 核实：验证 4 实际未通过

Ken 验证报告交付后，cursor 跑 SQL 核实 Debate #13 字段：

```
raw_question : '实验本身能否找到共性，并高度抽象，形成能够解决大部分实验设计的公式？'
proposition  : '开发一个数学框架，将最优实验设计原则与数值模拟相结合，以创建实验设计的元模型。'
identical?   : False
```

**proposition 字段仍然是 AI 改写版**。验证 4 实际**未通过**。

### 根因（cursor 自查）

cursor 2026-04-24 中午部署 Phase 1 时只修了 `Debate.tsx::handleCreate::finalProposition = inputText`（暗中替换那一支），但**没修** `Debate.tsx::useEffect L94-104` 的自动填充优先级：

```tsx
useEffect(() => {
  const candidate =
    navCtx.hypothesis || navCtx.coreTension || navCtx.direction || navCtx.discoveryQuestion || "";
  if (candidate && !proposition) {
    setProposition(candidate);
    ...
```

Discovery 跳转进 Debate 页时，`navCtx.hypothesis`（AI 改写版）优先于 `navCtx.discoveryQuestion`（用户原话）被填进 `proposition` 输入框。所以 `inputText` 的默认值就已经是改写版——cursor 中午的修复"finalProposition = inputText"对这种情况无效。

### 历史追因

这条 bug 2026-04-17 修 raw_question 字段时就在 `notes/next.md` P2 挂着，原文：

> "Discovery / 跳转带 hypothesis 进来的辩论，`Debate.tsx:95` 的 useEffect 会自动填 proposition。这种情况下'Ken 的原话'其实是来自 Discovery 阶段的 AI 改写，不是本次他敲入的。**短期可接受**，长期建议在输入框上方加一个 hint。"

Ken 2026-04-24 的产品哲学拍板（design.md §axl-debate-mode-design "free 不能写成友好讨论 / 必须是建设性综合 + 保留硬分歧"）+ 中午"useAcademic bug 一并修掉"的指令，把这条从"短期可接受"升级为"必须修"。`proposition == raw_question` 是 Phase 1 验证 4 通过的硬条件。

### 修法（待 Ken 拍板）

a) **useEffect 优先级反转**：`navCtx.discoveryQuestion || navCtx.hypothesis || ...`，原话优先填输入框；改写版降级为"Discovery 推荐了这个学术化版本，要采用吗"卡片，用户点采用才覆盖输入框

b) **完全去掉 navCtx.hypothesis 自动填充**：只用 `discoveryQuestion`，hypothesis 字段在 Discovery 页消化掉，不再跨页传入

cursor 倾向 (a)，保留改写版的可发现性，但默认尊重原话。

---

## 三、cursor 后置 DB 核实：截断观察确认是 token 触顶

实测 Round 3 各 agent 长度：

| msg# | rank | model | length (chars) | tail（最后 50 字符）|
|---|---|---|---|---|
| 152 | professor | deepseek-chat | 4164 | "...这个分歧的本质是：**谁有权力定义"足够好"？** 我认为是用户，不是数学" |
| 153 | associate | gpt-5.4 | 4471 | "...**误判代价、策略迁移稳定性、软状态决策** 这类真正决定 spec 能否在实验板块落地的运行指标" |
| 154 | professor | claude-opus-4-6 | 4898 | "...：我坚持分片 Lipschitz 是**不可再退让的底线**。若连片内 Lipschitz 都不满" ⚠ |
| 155 | associate | deepseek-chat | 3400 | "...我们预设。这在**根本上**决定了 spec 是服务于用户的决策工具，还是服务于数学优雅性的理论模型" |
| 156 | professor | claude-opus-4-6 | 5129 | "...：若 Pareto $\\hat{k} > 0.7$（Vehtari et al.）或 ELBO ga" ⚠⚠ |
| 157 | associate | gpt-5.4 | 4672 | "...但只有我们能把"什么叫实验上真的更好/更坏"落到可验证的统计—科学判据上" ⚠ |
| 158 | professor | gpt-5.4 | 2305 | "...若闸门不过，不进入优化设计，而是改模型/改观测" |

**判定**：msg#154/156/157 末尾不完整（"若连片内 Lipschitz 都不满"未收尾、"ELBO ga..."明显被截、"判据上"硬刹车）。

**结论**：Ken 看到的"末尾被截断"**不是粘贴截断，是后端 max_tokens 触顶**。professor max_tokens=4000、associate=3000 是按 debate 模式输出量校准的（debate Round 3 = 最终答案 + 跨学科启发，约 2-3k 字）。free 模式 Round 3 = 六字段 + 根本分歧 + 学科贡献，输出量 4-5k 字，standard depth 预算不够。

### 修法（待 Ken 拍板）

a) **free 模式专用调高 max_tokens**：free prof=6000 / assoc=4500（按 1.5x 调）

b) **free Round 3 prompt 加硬上限**："六字段每条 ≤ 80 字 / 根本分歧每条 ≤ 50 字"——把六字段做成纲要式而非展开式。和 distiller 方向一致

cursor 倾向 (b)。理由：长度问题不是只在 Round 3——R1/R2 + 总结也长。如果只调 max_tokens，3 万字根问题没解；如果改 prompt 收紧，单条变短自然多个轮次都受益，且与 P1 顶格"沙盘 / 推演实验设计 renderer"方向对齐——renderer 消费的是结构化纲要，不是论文。

---

## 四、判决（cursor）

| 验证 | Ken 初判 | DB 核实后 |
|---|---|---|
| 1 产物分叉成六字段 | ✓ | ✓ |
| 2 Round 3 是修正版 | ✓ | ✓ |
| 3 moderator 保留冲突 | ✓ | ✓ |
| 4 proposition = raw_question | ✓（间接） | ✗（待修 useEffect 优先级）|
| 5 G+F 抗雷同未破坏 | ✓ | ✓ |
| 6 debate 同题对照 | 待跑 | 待跑 |

**4/6 真过**，验证 4 暴露上午没修干净的同源 bug，验证 6 等 Ken 跑。

**Phase 1 修复整体方向成立**——design.md §axl-debate-mode-design 写死的产品哲学硬规则在实际输出里全部可观察到，包括 Ken 担心的"过度和谐"未发生（防过度和谐机制有硬证据）。

**两条遗留进 next.md**：

- **P1**（验证 4 反转）：`Debate.tsx::useEffect` 自动填充优先级反转，`navCtx.discoveryQuestion` 优先于 `hypothesis`
- **P2**（截断）：free 模式 Round 3 长度问题，倾向用 prompt 收紧六字段而非调高 max_tokens

---

## 五、关联

- 上游修复：`CHANGELOG.md` 2026-04-24 下午"free / debate 模式语义彻底分叉上线（Phase 1）"
- 产品哲学锚点：`notes/design.md #axl-debate-mode-design`
- 修复方案 handoff：`notes/journal/appendix-2026-04-24-debate-free-mode-semantic-fix-handoff.md`
- 六字段理论来源：`notes/journal/appendix-2026-04-24-axl-debate-experiment-commonality.md`
- Phase 1 上线日志：`notes/journal/project-log-2026-04.md` 2026-04-24
- 待跑：debate 模式同题对照（验证 6 待 Ken 跑）

---

*记录：cursor，基于 Ken 2026-04-24 下午 14:55 验证报告 + 后续 DB 核实。所有数据来自 Debate #13 实测，可重复查询。*
