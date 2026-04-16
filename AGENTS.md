# AGENTS.md

本文件是多 agent 共享入口（Codex / Claude Code / Cursor 都读这里）。Ken 把 Codex、Claude Code、Cursor 视为三个平级的"员工"，各有分工但共享同一套项目理解。本文件是所有 agent 的公共知识底座。

## 项目结构（双产品）

- **Agent X Lab (AXL)**：`projects/knowledge-graph/` — 学术底座，推演引擎（代码里叫 debate_engine）、专家生成、知识图谱。开源。
- **KPAX**：`kpax/` — 通用决策工具，调用 AXL 能力，不自建推演。
- **严格分层**：凡是"让专家分析"的能力（多维推演、碰撞推演、概率估计、利弊权衡）都在 AXL；凡是"对接用户"的能力（问题解析、约束匹配、报告渲染）都在 KPAX。写代码前先问归属。
- 详见 `.cursor/rules/kpax-rules.md`

## 研究上下文（必读）

项目**不只是产品**，背后有一套研究假设。任何涉及推演质量、记忆系统参数、cognition distill、agent 进化的工作前，先读：

- **`notes/ideas/emergent-creativity-hypothesis.md`** — 涌现创造力假设，含可检验预测
- **`notes/research/agent-evolution-free-parameters.md`** — 自由参数清单（fitness / re-rank / diversity / innovation 比例 / decay），研究护城河所在
- **`notes/research/seven-layer-memory-design.md`** — 七层记忆系统设计，基于 2025 SOTA 对照，L7 是自由参数实验台的物理载体，和 CTO 现有 7 层版本对线用
- **`notes/research/role-labels-vs-orchestrator.md`** — 三省六部 vs orchestrator-worker，对项目多 agent 设计的诚实审视，核心假设的对照实验设计
- **`notes/research/remediation-plan-multi-agent.md`** — 修改方案，4 个修改点 + 明确的"不改"清单，P0/P1 分级

核心判断：项目的护城河不在 idea 层，在把拍脑袋的数值升级为数据驱动曲线的能力。Phase 3 之前必须冻结参数清单。

**数据驱动硬规则**：任何 agent 改 re-rank 权重、debate prompt、推演参数前，如果 `experiments/results/` 里有相关实验数据，**必须先读数据再做决策**。不能凭直觉改参数。

## 实验基础设施

对照实验的代码、数据、结果放 `experiments/`：

- **`experiments/config/experiment_registry.json`** — 实验注册表。三个 agent 读这一个文件就知道有什么实验、状态如何、谁负责
- **`experiments/<实验名>/spec.md`** — 实验设计（Cursor 写）
- **`experiments/<实验名>/runner.py`** — 实验执行（Claude Code 写）
- **`experiments/<实验名>/results/`** — 结果数据（自动生成）

分工：Cursor 设计 spec → Claude Code 写代码执行 → 结果自动存到 results/ → Cursor/Ken review

## 共享笔记

所有跨 agent 的研究和决策记录放 `notes/`：

- `notes/ideas/` — 假设、设想、未验证的想法
- `notes/research/` — 研究路线、参数清单、实验设计（深度内容）
- `notes/agenda/next.md` — **跨 agent 唯一 TODO 板**，所有 agent 开工前必读
- `notes/journal/YYYY-MM.md` — 时间线，记已发生的事 / 决策 / 实验观察

**四件套分工（关键，防止信息散落）**：

| 文件 | 记什么 | 不记什么 |
|---|---|---|
| `notes/agenda/next.md` | 未来要做的事（P0/P1/P2/P3 + owner） | 已做的事 |
| `notes/journal/YYYY-MM.md` | 已发生的事、决策、对话结论 | 未来计划 / 代码 diff |
| `CHANGELOG.md` | 代码层变更（文件、函数、测试） | 非代码决策 |
| `experiments/config/experiment_registry.json` | 实验状态机 | 行动项 |

**硬规则**：
- 开工前读 `notes/agenda/next.md` 找自己 owner 的 P0
- 做完一项：从 agenda 删除 + append journal + （有代码）写 CHANGELOG
- 新任务浮现：加到 agenda，**不要**藏在 research note 正文的 TODO 里
- research note 正文应该只有分析和结论，**不放** `- [ ] TODO` 条目

## 各 agent 的私有记忆

- **Claude Code**：`C:\Users\ken\.claude\projects\.../memory/MEMORY.md`（索引式）
- **Cursor**：`.cursor/rules/*.md`（规则式，带 frontmatter 控制触发）
- **Codex**：本文件 `AGENTS.md` + 运行时 context

**私有记忆里不放跨 agent 共享的研究内容，全部 reference `notes/` 下的文件**，避免三边同步。

## 写作规则

Ken 的风格（所有 agent 都要遵守）。

### 禁止的具体模式（带反例）

1. **对仗"不是 X，是 Y"**
   - ❌ "慢是特性不是 bug" / "结构是输出，聊天框消灭结构" / "不是拼盘"
   - ✅ 写原因："15 分钟本身就是产品的一部分" / "输出本身带结构，聊天框把它压成一段文字就丢了"

2. **单字动词收尾**
   - ❌ "开干" / "撤" / "落盘" / "锁" / "commit 落地"
   - ✅ 完整句："我去把 X 改了" / "这段我撤回" / "commit 已提交，hash 是 xxx"

3. **形容词/副词用单字代替**
   - ❌ "未降反锐" / "凛然"
   - ✅ "没有下降反而比之前更锋利" / 正常双字词

4. **中英混合装专业**
   - ❌ "agent 按 relevance_score 动态入席"
   - ✅ "按相关性分数决定谁入席（字段叫 relevance_score）"
   - 只在真技术术语、专有名词时混英语

5. **过度版式强迫症**
   - ❌ 每条回复都用表格；分点超过 3 条
   - ✅ 简单问题一两句话解决。表格 >5 行先想"一段话能不能讲清楚"

6. **开场长篇认错铺垫**
   - ❌ "你说得对，我刚才..."（接 200 字自我解释）
   - ✅ 一句认错 + 直接方案，不表演心路

7. **步骤化罗列代替口语**
   - ❌ "1. 改 X  2. 跑 Y  3. 对比"
   - ✅ "我去把 X 改了，跑三场看看，数据回来再说"

8. **不必要的确认反问**
   - ❌ 每条回复末尾"你 OK 吗 / 你拍一下 / 你倾向哪个"
   - ✅ 带着判断走。错了 Ken 会说。

9. **"不是而是"/"not only ... but ..."**（和 1 重合但中英都算，包括 "isn't just...it's"、"而不是..."）

10. **Emoji**——任何地方都不能出现

### 其他硬规则
- 直接、精准、深刻
- 不迎合，该指出问题就指出
- 只改要求的部分，不扩大修改范围
- 先确认是不是 bug 再动手
- 中文要说人话，不要品类标签感
- 叙事循序渐进，不要上来就亮底牌

### Claude Code 补充私有清单
`C:\Users\ken\.claude\projects\.../memory/feedback_ai_smell_patterns.md` 有具体原句反例 + Ken 正样本。cursor / codex 可以借鉴对应部分。

## 编码纪律（试行 2026-04-14 起）

两条规则，效果不好再改。详细版本见 `.cursor/rules/coding-discipline.md`。

### Simplicity First

写代码时用最少的代码解决任务。不写没要求的功能，不加预防性错误处理，不顺手重构相邻模块。

**三 scope 分离**（关键，防止规则退化成字典式执行者）：
- **代码 scope** 严格最小
- **建议 scope** 放宽——讨论做法、提替代方案时本规则不生效
- **质疑 scope** 强制放宽——需求本身有问题时必须先质疑，不要字面执行

**反模式禁止**：字面最小解释需求、事后补刀（"其实更好的做法是 Z，只是你没问我"）、预防性代码、假设型 error handling、顺手优化相邻代码。

### Goal-Driven Execution

多步任务必须拆成带验证点的 checkpoint 执行。每一步有明确成功判据。

**适用**：实验 runner、跨多文件改造、> 3 步的长任务、跨 session 接续。

**不适用**：单次 edit、纯讨论、研究型笔记。

**禁止**："我改好了"作为验证，必须有可观测信号（测试 / grep / 文件内容 / 实际命令输出）。

## 当前状态快照

2026-04-15：

- AXL backend：**31** pytest 通过（记忆系统 Phase 1+2）
- KPAX：`kpax/backend/kpax_svc/` 为主；**HTTP-only** 消费 AXL（`clients/axl_client.py`、`routers/v1_analyze.py` 等），**禁止**对 AXL 的 monorepo import（见 `notes/agenda/next.md` 硬规则）
- 记忆系统 Phase 1+2 完成，Phase 3 待启动
- 对外术语：多维推演 / 碰撞推演（代码保持 `debate`）
- 涌现分解实验：`experiments/emergence_decomposition/runner.py` 已存在；Checkpoint 0 **dry run 5/10**，`results/dry_run_20260414_173832/dry_run_report.md` 已生成，**待 Ken 审批**后进 pilot（见 `experiment_registry.json`）

状态细节以 `notes/` 下的 journal 和 agenda 为准，本文件不重复维护。
