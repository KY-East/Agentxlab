# Agent X Lab + KPAX — 单一入口

> **一份文件读完全项目**。任何 agent（cc / cursor / codex / ken）进来 10 分钟内知道"现在在哪 / 下一步是什么 / 要改什么去哪个文件 / 项目的硬规则是什么"。
>
> 本文件 2026-04-17 吸收原 `AGENTS.md` 内容，成为唯一的内部总入口。`AGENTS.md` 现在是一个 2 行 redirect 文件，为了 Codex 约定俗成的入口习惯保留。
>
> 事件详情看 `notes/journal/`，任务清单看 `notes/next.md`，代码变更看 `CHANGELOG.md`。

---

## 目录

1. [一屏摘要](#1-一屏摘要)
2. [产品线状态面板](#2-产品线状态面板)
3. [仓库导航：我要做 X，去哪](#3-仓库导航我要做-x去哪)
4. [Onboarding — 新 agent 第一次进来先读哪 3 个](#4-onboarding--新-agent-第一次进来先读哪-3-个)
5. [硬规则总汇](#5-硬规则总汇)
6. [角色分工（Ken 2026-04-17 拍板）](#6-角色分工ken-2026-04-17-拍板)
7. [研究上下文 + 实验基础设施 + 共享笔记分工](#7-研究上下文--实验基础设施--共享笔记分工)
8. [写作规则（含 11 条反模式）](#8-写作规则含-11-条反模式)
9. [AXL 日志规范](#9-axl-日志规范)
10. [编码纪律](#10-编码纪律)
11. [文件命名规则](#11-文件命名规则)
12. [关键决策速查](#12-关键决策速查)
13. [文件生命周期](#13-文件生命周期)
14. [各 agent 的私有记忆](#14-各-agent-的私有记忆)
15. [下一步](#15-下一步)

---

## 1. 一屏摘要

**一句话**：**AXL（AgentXLab）是通过科学方法论和跨学科视角研究万事万物的平台。KPAX 是 AXL 的产品入口之一**——复用 AXL 的能力作为学术底座，帮用户把一件事想透（深度 / 正确性 / 全面性）。

| 产品 | 定位 | 代码位置 | 用户 | 状态 |
|---|---|---|---|---|
| **AXL**（AgentXLab） | 通过科学方法论和跨学科视角研究万事万物的平台，开源 | `projects/knowledge-graph/` | 研究者 / 产品入口（如 KPAX） | 产品 87/100，记忆系统 Phase 2 完成 |
| **KPAX** | AXL 的产品入口：单次决策问答（复用 AXL 作学术底座）| `kpax/` | 10 位朋友先行测试 → 扩大 | 骨架完成（有 5 处 monorepo 违规待 cursor 修），v0 形态设计锁定 |

**核心信念**：多 agent 跨学科碰撞能产生涌现创造力。这是一个关于 AI 能力上限的研究假设，正在 `experiments/emergence_decomposition/` 里验证。目标是让 AI 真的能创造新东西，而非更快更省地执行已有任务。

**当前阶段**（2026-04-17 凌晨）：
- 🟢 涌现实验 Checkpoint 0 全部完成（20 场 scaleup mean $0.99/场 / CV 17% / 全部成功）
- 🟢 Pilot judge rubric v0.1 落地（AXL 递归 dogfooding 产出，递交 cursor 独立审得 v0.1-reviewed）
- 🟡 Checkpoint 1 pilot 待启（前置：cursor 修 5 处 monorepo 违规 + 实现 judge.py + rubric 外审）
- 🟡 KPAX v0 形态定案（7 席满席动态前景座谈会，维多利亚黑神话质感）；Ken 手动设计 7 角色图中
- 🔴 **新识别关键问题**：自进化量化闭环缺失（Lucas 2026-04-17 观察）——需要 judge 打分数据才能定义"往哪个方向强化"。见 `notes/research.md#quantification-gap`
- 🔴 **新分工生效**：cc = 战略 / PRD / UX 审核；cursor = 所有开发编程；codex = code review；ken = 战略终审 + 产品终审 + 外部决策

---

## 2. 产品线状态面板

### 2.1 AXL — 研究平台（通过科学方法论和跨学科视角研究万事万物）

| 模块 | 状态 | 证据 |
|---|---|---|
| 辩论引擎（多 agent 碰撞，数量 / 身份 / 模型可配置） | 生产可用 | `debate_engine.py`；2026-04-15 晚修 quick max_tokens (1500→800) + 反重复规则（commit `4b35f1e`）|
| 记忆系统 Phase 1+2 | 完成 | 31 pytest 通过（metadata schema / re-rank / 会话压缩）|
| Phase 3（L3+ 七层记忆） | 未启动 | 见 `notes/research.md#seven-layer-memory-design` |
| 自由参数实验 | Phase 3 前冻结 | 见 `notes/research.md#agent-evolution-free-parameters` |
| KPAX HTTP API | 3 endpoints mock 就绪 | `projects/knowledge-graph/backend/app/routers/kpax_router.py` + `kpax_api_spec.md` |
| 结构化 JSON 日志基建 | 已落地 2026-04-17 凌晨 | `app/utils/logging_setup.py` + FastAPI `RequestIdMiddleware` + AGENTS.md 规范 |
| Judge.py 实现 | 未开始 | 归 cursor（新分工）。依据：`experiments/emergence_decomposition/results/dry_run_20260416_165636/pilot_judge_rubric_v0.1.md` |

### 2.2 KPAX — AXL 的产品入口（单次决策问答，复用 AXL 作学术底座）

| 模块 | 状态 |
|---|---|
| `axl_client.py` — HTTP 调 AXL | ✅ 骨架（cc 2026-04-15 晚写）|
| `token_ledger.py` — 代币账本 | ✅ 骨架（guest 种子 50 / 消费 10/25/60 / 分享+20 / 预留 ChainAdapter）|
| `question_classifier.py` — 题型判别 | ✅ `_chat_fn` 已接 `llm_client.chat_completion`（cursor 2026-04-17）|
| `llm_client.py` — KPAX 独立 LLM 客户端 | ✅ litellm 薄封装（cursor 2026-04-17 新建，独立于 AXL `ai_provider`）|
| `v1_analyze.py` router | ✅ 已挂 FastAPI `/api/v1/analyze`，classifier 真实分类 |
| `services/question_parser.py` / `expert_builder.py` / `report_generator.py` | ✅ 合规（cursor 2026-04-17 切 `kpax_svc.clients.llm_client`）|
| `routers/analyze.py` / `report.py`（legacy）| ⚠️ **例外登记**：违反硬规则 #6 但按路径 D 冻结至 KPAX v0 PRD 完成日，新功能禁止进。详见 §5.1 规则 #6 例外段 |
| 前端 | ⚠️ 基于 legacy 5 步流程的 7 文件骨架（`api/client.ts` + `Analyze.tsx` + 5 components），**v0 座谈会形态未起** |
| v0 形态设计 | ✅ `notes/design.md#kpax-v0-deliberation-room` |
| v0 知识源架构 | ✅ `notes/research.md#kpax-knowledge-source-architecture`（三条输入线 + v0/v1/v2 phasing）|

### 2.3 实验线

| Checkpoint | 状态 | 数据位置 |
|---|---|---|
| CP 0 初始 dry run（10 场 baseline）| 5/10 成功（04-14）| `results/dry_run_20260414_173832/` |
| CP 0 mini run（3 场验证新 config）| 3/3 成功（04-15 晚）| `results/dry_run_20260415_171016/mini_dry_run_report.md` |
| CP 0 scaleup（20 场方差验证）| 20/20 成功（04-16）| `results/dry_run_20260416_083829/scaleup_report.md`（含 §0 content-layer 观察）|
| CP 0 meta_01（AXL 自设计 judge rubric）| 2 轮 timeout 但有完整产出（04-16 晚）| `results/dry_run_20260416_165636/pilot_judge_rubric_v0.1.md` |
| **CP 0 总状态** | ✅ 真关闭 | `experiments/config/experiment_registry.json` |
| CP 1 pilot（baseline + A 组 × 20 题 × 2 run = 80 场）| 未启动，前置 cursor 修 monorepo + 实现 judge.py + rubric 外审 | - |
| CP 2–4 全量（6 组 × 50 题 × 3 run = 900 场，估 $891）| 未启动 | - |

---

## 3. 仓库导航：我要做 X，去哪

| 我要... | 去读 | 改哪里 |
|---|---|---|
| 改辩论 prompt / 学科 | `projects/knowledge-graph/backend/app/services/debate_engine.py` | 同 |
| 改 KPAX HTTP API | `projects/knowledge-graph/backend/app/routers/kpax_api_spec.md` | `kpax_router.py` |
| 加一个新实验 | `experiments/README.md` + 参考 `emergence_decomposition/spec.md` | 新建 `experiments/<name>/` |
| 改记忆系统 | `notes/research.md#seven-layer-memory-design` | `projects/knowledge-graph/backend/app/services/{zep_manager,session_memory}.py` |
| 改 KPAX 前端 / 形态 | `notes/design.md#kpax-v0-deliberation-room` | （v0 未起）|
| 改 KPAX 知识源 | `notes/research.md#kpax-knowledge-source-architecture` | KPAX backend `graph_client.py`（待新建）|
| 改代币规则 | `kpax/backend/kpax_svc/services/token_ledger.py` | 同 |
| 查"为什么这么做 X" | `notes/journal/project-log-YYYY-MM.md`（按日期倒序）| journal 末尾 append |
| 查"下一步做什么" | `notes/next.md`（唯一 TODO 板）| 加 / 减 item |
| 查实验当前 checkpoint | `experiments/config/experiment_registry.json` | 同 |
| 查代码层变更历史 | `CHANGELOG.md` | commit 后同步 |
| 查 AXL 产品完成度 | `projects/knowledge-graph/PROGRESS.md` | Ken 手动评分更新 |
| 看公开市场定位（AXL）| `README.md` | 公开宣言，改要慎 |
| 看 KPAX 产品定位 | `KPAX.md` | 同 |
| 读外部参考雷达 | `notes/radar.md` | cc 看到新链接时 append |
| 读所有研究笔记 | `notes/research.md`（跳对应 ## 节）| 任何 agent |
| 读所有设计文档 | `notes/design.md`（跳对应 ## 节）| 任何 agent |

---

## 4. Onboarding — 新 agent 第一次进来先读哪 3 个

### Claude Code（cc）
1. 本文件 `PROJECT.md`
2. `notes/next.md` 找 `@cc` owner 任务
3. `notes/journal/project-log-YYYY-MM.md`（最新月）末尾几条，理解当前战略脉络

私有 memory 入口：`C:\Users\ken\.claude\projects\.../memory/MEMORY.md`

### Cursor
1. 本文件 `PROJECT.md`（尤其 §6 角色分工 + §8 写作规则 + §10 编码纪律）
2. `.cursor/rules/coding-discipline.md` + `.cursor/rules/workflow.md`
3. `notes/next.md` 找 `@cursor` owner 任务

新分工下 cursor 承担所有业务代码实现（见 §6）。

### Codex
1. `AGENTS.md`（它的原生主入口，内容是 redirect 到本文件）
2. 本文件 `PROJECT.md`
3. `notes/next.md` 找 `@codex`（review 任务清单）+ 待 review 的 PR

新分工下 codex 承担 code review（见 §6）。

### Ken
1. 本文件 `PROJECT.md` §1 一屏摘要 + §2 状态面板
2. `notes/next.md` 找 `@ken`（要 Ken 拍板 / 评分 / 外部动作）
3. `notes/journal/project-log-YYYY-MM.md`（月度时间线）

---

## 5. 硬规则总汇

改硬规则必须在 `notes/journal/` 记原因 + 日期 + 谁拍板。

### 5.1 KPAX 六条（Ken 2026-04-15 拍板，2026-04-17 晚由 Ken 修订去二极管化表述）

1. **产品承诺 = "把这个问题帮你想透"**——深度 / 正确性 / 全面性。**正面回答用户的问题是基础**（用户问 A/B 就先答 A 或 B，不要答非所问）；**能给出用户没想到过的角度是锦上添花加分**。两者并存，不是排他。

2. **当前 spec 涉及 5 种题型**（是否 / 概率 / 选择 / 策略 / 评估）。这 5 种之间的**包含 / 并列 / 正交关系尚未完全拆清**，是一个开放问题。不是 "5 种都必须是基础功能" 也不是 "只能 5 种"。未来 spec 迭代时可能合并、拆分、或新增。

3. **不绑定某个垂直领域**（比如金融 / 医疗 / 教育）。KPAX 当前定位为**通用决策工具**。这不排除未来某个垂直场景如果验证效果特别好、可以针对性专攻。

4. **代币是主要付费机制**（分享赚代币 / 消费代币 / dex 或合约买）。**不排斥**传统法币订阅、传统注册等机制并存。钱包不是唯一身份，是之一。

5. **成功判据 = 10 朋友 7 说"有帮助"**（v0 测试阶段）。

6. **KPAX ↔ AXL Day 1 走 HTTP**，代码 / DB / 部署全分开。**禁止 monorepo import**——这条是明确的硬规则。

   **例外登记（2026-04-17 by Ken，路径 D）**：以下 2 个文件因 v0 座谈会替代品就位前产品形态与前端 7 文件强耦合，明示豁免存在。**新功能禁止进这 2 文件**；任何增量能力必须进 `kpax_svc/routers/v1_analyze.py` 或未来的 `kpax_svc/routers/v1_session.py`。
   - `kpax_svc/routers/analyze.py`
   - `kpax_svc/routers/report.py`
   - （相关基础设施 `kpax_svc/__init__.py` sys.path hack、`services/context_collector.py` 内存 session store 随同保留至替换日）
   
   **替换触发点**：KPAX v0 前端协议 PRD 完成日。由 @cc 出 PRD + AXL 侧 `kpax_router.py` 从 mock 改真（含流式端点 `/axl/v1/debate/stream` + `/axl/v1/debate/{id}/messages`）→ @cursor 在 `v1_session.py` 重建走 HTTP 的 session 流程 → 同步删 legacy + 清 sys.path hack + 本例外登记。
   
   **复查负责人**：@cursor（路径 B 迁移），@ken（触发点判断）。详见 `kpax/backend/kpax_svc/legacy_routers_assessment.md` 路径 D 段。

### 5.2 实验硬规则

- **当前 50 题 benchmark 选定了 7 学科**（物理 / 数学 / 经济 / 心理 / 社科 / CS / 艺术人文）。由来：cc 建议 7 为上限（奇数避免投票打平），Ken 在 cc 给的候选里选出这 7 个。**emergence_decomposition 实验期间这 7 个固定**，保证 controlled comparison 有效。
- **学科不是永久冻结**。如果未来新题目 / 新实验需要其他学科（比如生物医学 / 工程 / 法律），**允许小规模精确测试加入或替换**。触发条件：(a) 现有 7 学科对新题明显覆盖不足 (b) 有明确可检验的研究问题 (c) 新增学科样本规模足够做独立结论（不污染 emergence_decomposition 主实验）。
- **moderator 目前用 Claude Opus 4.6**（Ken 2026-04-15 拍板）。未来有更合适的模型可替换，但替换需要跑对照实验验证。
- **主 judge 固定 API 模型（GPT-5 / Gemini 2.x 选一个）**，不本地 fine-tune judge（理由：judge 模型能力必须 ≥ 被判模型）。
- 实验状态必须 `checkpoint_<N>_<phase>` 格式。
- **数据驱动**：任何 agent 改 re-rank 权重 / debate prompt / 推演参数前，若 `experiments/results/` 有相关数据**必须先读数据再做决策**。

### 5.3 战场选择：侧翼打，不打正面（Ken 2026-04-16 拍板）

**核心原则**：不打正面战场，打侧翼战场。不是避战，是选战场。

| 维度 | 正面战场（不打） | 侧翼战场（打） |
|---|---|---|
| 性质 | 没资格 / 没积累 | 有能力干 |
| 例子 | 大模型 / IDC / 能源 / Claude Code / Cursor / OpenClaw Agent 这类通用 agent | AXL 多学科碰撞 / KPAX 通用决策 / 3D 座谈会 / 顾问 IK / 代币经济 |
| 判据 | 已经巨大的蓝海，头部玩家密集 | 大玩家不会专门做、需要特定积累 / 产品视角的细分角度 |

**具体"不做"**（Ken 2026-04-17 晚注：下面这些"本身就不会做"，列出来主要是**防止新人误伤** / **防止 cc 等 agent 因误解而启动这类工作**；列出来本身意义不大，但保留为备忘）：
- ❌ 训练 / post-train 基础模型
- ❌ 自建 IDC / 大规模推理基建
- ❌ 通用 coding agent（Claude Code / Cursor / OpenClaw 这类）
- ❌ 自建文献索引 / 自研板式解析模型（用开箱工具按内容分场景选，2026-04-16 晚规则调整，原"绝不 OCR"已作废）
- ❌ DCA 端侧百万长序列
- ❌ 把 KPAX 扩成通用科研工具

**具体"做"**：
- ✅ 多学科 agent 碰撞（AXL 独门）
- ✅ 通用决策产品（KPAX 承诺"帮你想透"）
- ✅ 3D 座谈会形态 vs 聊天框窠臼
- ✅ 七层记忆 + 自由参数 L7 元进化
- ✅ 代币经济 / 钱包身份
- ✅ 任何基于现成 LLM / agent framework 之上的差异化产品层

**立场说明（关键）**：上面每一条"不做"都是**能力约束型**决定——没有对应积累，做不过现成方案或大玩家。**不是战略回避竞争**。**有好工具就用，有能力就上正面**（Ken 原话 2026-04-16 晚："我们没有这个积累，有了立马就用"）。

**每周一自检**：这周在打正面还是侧翼？正面立刻停手。

理由和更长论证见 `notes/research.md#wisland-analysis-and-positioning`。

---

## 6. 角色分工（Ken 2026-04-17 拍板）

### 背景
2026-04-17 Ken 拍板调整分工。触发原因："cc 的用户界面没有办法支持大型项目，我作为人类几乎两眼一码黑，完全无法进行项目管理"。三省六部制有其分歧（见 `notes/research.md#role-labels-vs-orchestrator`），但 solo dev 瓶颈在"人类项目管理带宽"，不在"AI 能否多工种"。

### 新分工

| 角色 | 职责 | 不做 |
|---|---|---|
| **cc**（Claude Code） | 战略规划 / 任务分工 / PRD / 逻辑闭环 / UX 审核 / 架构文档 | **不直接写业务代码**（cc 自己验证自己写的工具、基础设施、日志框架类除外）|
| **cursor** | 所有业务代码开发实现。接 cc 的 PRD + 任务清单 → 实现 | 不做战略决策 / 不写 PRD |
| **codex** | Code review / 代码质量审核。接 cursor 的 PR → 审 | 不写业务代码 |
| **ken** | 战略终审 / 产品终审 / 外部决策（融资 / 上链 / 招募）/ 关键 UX 拍板（例如角色视觉设计） | 不做日常项目管理（这是 cc 的活）|

### 历史分工（2026-04-17 前）
- cc：写代码 + 写 PRD + 写文档 + 实验 + 战略（过载）
- cursor：写 spec + 部分代码 + review
- codex：主要 review

新分工下 cc 的主要产出是**决策 / 文档 / 审核**，cursor 的主要产出是**可运行代码 + PR**，codex 的主要产出是**review 意见 + 建议**。

### 项目管理的可视化痛点（待解）

Ken 指出：cc 的 text-only 界面对大型项目的可视化太差，人类几乎两眼一码黑。此痛点**暂无完美解**，候选路径：

- **路 A**：cursor 做本地 HTML dashboard，读 repo 里的 `PROJECT.md` / `notes/next.md` / `notes/journal/*.md` / `experiment_registry.json` / `notes/radar.md`，渲染成 kanban / timeline / 状态面板。单文件 HTML + JS，无后端。
- **路 B**：接外部工具（Linear / Notion / GitHub Projects）。cc / cursor 定期 sync 项目状态。
- **路 C**：recursive dogfooding——把 KPAX 座谈会 UI 扩展一个"项目 domain"，把自己管起来。野但有趣，可能是 v1 之后的事。

该决策已进 `notes/next.md` 待 Ken 拍板。

---

## 7. 研究上下文 + 实验基础设施 + 共享笔记分工

### 7.1 研究上下文（必读）

项目**不只是产品**，背后有一套研究假设。任何涉及推演质量、记忆系统参数、cognition distill、agent 进化的工作前，先读 `notes/research.md` 对应节：

- **涌现创造力假设** (`#emergent-creativity-hypothesis`) — 理论起点，含可检验预测
- **自由参数清单** (`#agent-evolution-free-parameters`) — fitness / re-rank / diversity 坍缩 / innovation 比例 / decay，研究护城河所在
- **七层记忆** (`#seven-layer-memory-design`) — 基于 2025 SOTA 对照，L7 是自由参数实验台的物理载体
- **架构自审** (`#role-labels-vs-orchestrator`) — 三省六部 vs orchestrator-worker，对项目多 agent 设计的诚实审视
- **修改方案** (`#remediation-plan-multi-agent`) — 4 个修改点 + 明确的"不改"清单，P0 / P1 分级
- **WisLand 对位** (`#wisland-analysis-and-positioning`) — 外部项目分析，侧翼战场策略的依据
- **KPAX 知识源架构** (`#kpax-knowledge-source-architecture`) — 三条输入线（学术 / 行业 curated / 社区经验）
- **自进化量化闭环问题** (`#quantification-gap`) — Lucas 2026-04-17 观察，A→E 5 层路径

**核心判断**：项目的护城河不在 idea 层，在把拍脑袋的数值升级为数据驱动曲线的能力。Phase 3 之前必须冻结参数清单。

### 7.2 实验基础设施

对照实验的代码、数据、结果放 `experiments/`：

- **`experiments/config/experiment_registry.json`** — 实验注册表。三个 agent 读这一个文件就知道有什么实验、状态如何、谁负责
- **`experiments/<实验名>/spec.md`** — 实验设计
- **`experiments/<实验名>/runner.py`** — 实验执行
- **`experiments/<实验名>/results/`** — 结果数据（自动生成）

2026-04-17 分工调整：**spec 和 runner 都归 cursor 写**，cc 写 PRD + 战略 + 审核。Ken review 结果。

### 7.3 共享笔记分工（四件套）

所有跨 agent 的研究和决策记录放 `notes/`：

```
notes/
├── next.md              # 跨 agent 唯一 TODO 板，所有 agent 开工前必读
├── journal/project-log-YYYY-MM.md   # 项目全记录时间线：决策 / 对话结论 / 实验观察。月底换新文件
├── research.md          # 所有研究笔记（2026-04-17 从 notes/research/ 合并到此单一文件，## 节分段）
├── design.md            # 所有设计文档（2026-04-17 同）
└── radar.md             # 外部参考雷达（开源项目 / 推文 / 市场信号）
```

**四件套分工（关键，防止信息散落）**：

| 文件 | 记什么 | 不记什么 |
|---|---|---|
| `notes/next.md` | 未来要做的事（P0/P1/P2/P3 + owner） | 已做的事 |
| `notes/journal/project-log-YYYY-MM.md` | 已发生的事、决策、对话结论 | 未来计划 / 代码 diff |
| `CHANGELOG.md` | 代码层变更（文件、函数、测试） | 非代码决策 |
| `experiments/config/experiment_registry.json` | 实验状态机 | 行动项 |

**硬规则**：
- 开工前读 `notes/next.md` 找自己 owner 的 P0
- 做完一项：从 next.md 删除（或打 ✅）+ append journal +（有代码）写 CHANGELOG
- 新任务浮现：加到 next.md，**不要**藏在 research 节正文的 TODO 里
- research 节正文应该只有分析和结论，**不放** `- [ ] TODO` 条目

---

## 8. 写作规则（五层 AI 味框架 + 具体反例）

所有 agent 都要遵守 Ken 的风格。

### 8.0 五层 AI 味框架（2026-04-19 整合：鸭哥 @grapeot 翻译腔分析 + Ken 反复纠正）

AI 味不是单一问题，是五层叠加。从表层往深层：

| 层 | 名称 | 鸭哥覆盖？ | 主要症状 |
|---|---|---|---|
| 1 | **句法翻译腔** | ✓ 四套路 | 英文句法骨架 + 中文皮 |
| 2 | **词汇评价** | 部分 | 充膨大词 / 装腔单字 / 身体感觉 |
| 3 | **论证结构** | × | 不是 X 是 Y / 对仗 / 三段排比 |
| 4 | **态度姿态** | × | 迎合 / 自嗨 / 二极管 |
| 5 | **动机方法** | × | 替 Ken 编战略叙事 / 不问根本问题就开写 |

**层 1：句法翻译腔——鸭哥四套路**（2026-04-19 新增，来自 @grapeot "写作中的AI味是哪儿来的"）

AI 写中文时先用英文句法想清楚，再逐字换中文。结果：每个字都是中文，骨架是英文。

1. **物理动作描述思考**——把 catch/sharp/break 等英文里靠物理生活经验支撑的动词，直译成悬空的中文
   - ❌ "三条反馈我都接住" / "更锋利的重构" / "context 不崩" / "claim 更硬" / "你比他**狠**的地方"
   - ✅ "这几条我都收到了" / "换一种更准的讲法" / "上下文不会乱掉" / "这个判断可以说得再重一点" / "你比他**强**的地方"
   - 黑名单动词：接住、击穿、拆解、收口、承担、撑不住、不崩、不爆、打穿、收紧、扛住、狠、锋利、锐利
   - 自查：写完圈所有动词，看哪个在中文日常里不会这样用

2. **形容词 + 冒号抢判断**——用形容词先替读者下结论，冒号引出内容
   - ❌ "逻辑很清晰：" / "问题很直接：" / "更干净：" / "更锋利的重构："
   - ✅ 直接删形容词那半句，让后面的事实自己说话
   - 测试：删掉形容词那一节，读者照样理解，读得更顺
   - 如果非想留形容词，多半是后面没讲清楚，回去补内容

3. **抽象名词做主语 + 形容词收尾**——"X 的 Y 比 Z 更 W"骨架
   - ❌ "工程上的现实比这些数字难看" / "The reality is uglier than..."
   - ✅ 让人 / 动作 / 具体对象做主语，让事实自己说话："这些数字只反映了采用面；真往下看各家怎么接，早就对不齐了"
   - 碰到这个骨架直接重写

4. **有中文译法的英文词混入**——context/state/cache/claim 这类
   - ❌ "context 不崩、state 可恢复、cache 命中率高" / "claim 更硬"
   - ✅ 上下文 / 状态 / 缓存 / 断言
   - 例外：中文圈还没收敛到通用译法的词（prompt / embedding / tokenizer / harness 等）保留英文合理

**句法层修法总则**：别在原句上修修补补，**重写**。先把意思理清楚，用中文本来会怎么说这件事重说一遍（翻译学里叫"归化"）。

**层 2-5 的具体反例清单见下 §8.1**。原 11 条按层归属：
- 层 1（句法）：#4 中英混合（对应鸭哥套路 4）
- 层 2（词汇）：#2 装腔单字、#3 形容词单字、#11 身体感觉、#10 emoji
- 层 3（论证）：#1 "不是 X 是 Y"、#9 "不是而是"、#7 步骤化罗列、#5 表格强迫症
- 层 4（态度）：#6 长篇认错、#8 不必要确认反问
- 层 5（动机）：见 §8.2 其他硬规则 + `feedback_no_strategic_narrative.md` + `feedback_ai_smell_patterns.md` 模式 13（二极管）/ 模式 14（PRD 前不答根本问题）

### 8.1 禁止的具体模式（带反例）

1. **对仗"不是 X，是 Y"**
   - ❌ "慢是特性不是 bug" / "结构是输出，聊天框消灭结构" / "不是拼盘"
   - ✅ 写原因："15 分钟本身就是产品的一部分" / "输出本身带结构，聊天框把它压成一段文字就丢了"

2. **装腔的单字收尾**（不是所有单字都有问题）
   - 自然的单字（保留，这是汉语口语）："不要动" / "停" / "走吧" / "等等" / "来"
   - 装酷的单字（改）：❌ "开干" / "撤" / "落盘" / "锁" / "commit 落地"
   - 修正：✅ "我去把 X 改了" / "这段我撤回" / "commit 已提交，hash 是 xxx"
   - 测试：如果我是普通中国人聊天，会这么说吗

3. **形容词 / 副词用单字代替**
   - ❌ "未降反锐" / "凛然"
   - ✅ "没有下降反而比之前更锋利" / 正常双字词

4. **中英混合装专业**
   - ❌ "agent 按 relevance_score 动态入席"
   - ✅ "按相关性分数决定谁入席（字段叫 relevance_score）"
   - 只在真技术术语 / 专有名词时混英语

5. **过度版式强迫症**
   - ❌ 每条回复都用表格；分点超过 3 条
   - ✅ 简单问题一两句话解决。表格 > 5 行先想"一段话能不能讲清楚"

6. **开场长篇认错铺垫**
   - ❌ "你说得对，我刚才..."（接 200 字自我解释）
   - ✅ 一句认错 + 直接方案，不表演心路

7. **步骤化罗列代替口语**
   - ❌ "1. 改 X  2. 跑 Y  3. 对比"
   - ✅ "我去把 X 改了，跑三场看看，数据回来再说"

8. **不必要的确认反问**
   - ❌ 每条回复末尾"你 OK 吗 / 你拍一下 / 你倾向哪个"
   - ✅ 带着判断走。错了 Ken 会说。

9. **"不是而是" / "not only ... but ..."**（和 1 重合但中英都算，包括 "isn't just...it's"、"而不是..."）

10. **Emoji**——任何地方都不能出现

11. **身体感觉拟人化 / 互联网夸张形容词**——用精确中文形容词
    - 黑名单：痛、痛死、爽、舒服、香、真香、炸裂、离谱、拉跨、起飞、丝滑、牛逼、绝了
    - ❌ "跨组件跑起来就会痛" / "方案很丝滑" / "数据炸裂"
    - ✅ "跨组件运行会非常混乱 / 难以定位" / "方案非常流畅" / "数据远超预期"
    - 测试：找形容词问自己——是精确描述还是情绪化夸张？

### 8.2 其他写作硬规则
- 直接、精准、深刻
- 不迎合，该指出问题就指出
- 只改要求的部分，不扩大修改范围
- 先确认是不是 bug 再动手
- 中文要说人话，不要品类标签感
- 叙事循序渐进，不要上来就亮底牌
- **实验报告必须先 content，后 cost**（Ken 已纠正 cc 三次）

### 8.3 Claude Code 补充私有清单
`C:\Users\ken\.claude\projects\.../memory/feedback_ai_smell_patterns.md` 有具体原句反例 + Ken 正样本 + 每次生成前 5 秒 self-check。cursor / codex 可以借鉴对应部分。

---

## 9. AXL 日志规范（2026-04-16 晚起施行）

AXL backend 已安装结构化 JSON 日志基建（`projects/knowledge-graph/backend/app/utils/logging_setup.py`）。

**所有 agent 在 AXL 代码里写 logging 时的规范**：

1. **获取 logger 的方式不变**：`logger = logging.getLogger(__name__)` 或 `logging.getLogger("axl.xxx")`
2. **带结构化字段用 `extra=`**：
   ```python
   logger.info("round complete", extra={"step": "round_end", "round": 2, "debate_id": 5})
   ```
   `extra` 里的字段会自动出现在 JSON 输出里
3. **不要手工把结构字段拼到 msg 里**。❌ `logger.info(f"round {n} complete")` → ✅ `logger.info("round complete", extra={"round": n})`
4. **request_id 自动继承**。FastAPI 请求里任何 logger 调用都会自动带上 req_id。跨 await 也保持
5. **后台任务或实验 runner 手动设 req_id**：
   ```python
   from app.utils.logging_setup import set_request_id
   token = set_request_id(f"exp_{question_id}")
   try:
       ...  # 所有内部 log 会带这个 id
   finally:
       pass  # ContextVar 生命周期自然结束，不强制 reset
   ```
6. **异常用 `logger.exception(...)`**：自动把 traceback 抓到 `exc` 字段

**输出形态**：每条 log 一行 JSON，字段包括 `ts` / `level` / `logger` / `req_id` / `msg` / 以及 `extra=` 里传的任何字段。可直接用 `jq` 或 grep 查询。

**不要做的事**：
- ❌ 不要 `import logging; logging.basicConfig(...)` —— 会冲突
- ❌ 不要 `print()` —— 日志不出现在 JSON 流里
- ❌ 不要在日志里 f-string 拼结构化数据 —— 用 `extra=`

**例子**：好的 log 一行大约这样：
```json
{"ts":"2026-04-17T01:31:13.263Z","level":"INFO","logger":"app.services.debate_engine","req_id":"abc123def456","msg":"agent response","step":"round_1_speak","agent_id":42,"tokens":512}
```

---

## 10. 编码纪律（试行 2026-04-14 起）

两条规则，效果不好再改。详细版本见 `.cursor/rules/coding-discipline.md`。

### 10.1 Simplicity First

写代码时用最少的代码解决任务。不写没要求的功能，不加预防性错误处理，不顺手重构相邻模块。

**三 scope 分离**（关键，防止规则退化成字典式执行者）：
- **代码 scope** 严格最小
- **建议 scope** 放宽——讨论做法 / 提替代方案时本规则不生效
- **质疑 scope** 强制放宽——需求本身有问题时必须先质疑，不要字面执行

**反模式禁止**：字面最小解释需求、事后补刀（"其实更好的做法是 Z，只是你没问我"）、预防性代码、假设型 error handling、顺手优化相邻代码。

### 10.2 Goal-Driven Execution

多步任务必须拆成带验证点的 checkpoint 执行。每一步有明确成功判据。

**适用**：实验 runner、跨多文件改造、> 3 步的长任务、跨 session 接续。

**不适用**：单次 edit、纯讨论、研究型笔记。

**禁止**："我改好了"作为验证，必须有可观测信号（测试 / grep / 文件内容 / 实际命令输出）。

---

## 11. 命名规则（Ken 2026-04-15 拍板 + 2026-04-24 扩展到条目标题）

### 11.1 文件命名

- **名字本身要说清这是什么**。第三个人看文件名就知道用途，不用打开内容猜。
- ❌ `radar.md` / `review.md` / `notes.md` —— 抽象代号
- ✅ `external-references-radar.md` / `kpax-v0-deliberation-room.md` / `wisland-analysis-and-positioning.md` —— 带内容定位
- **例外**：约定俗成的短名可以（README.md / CHANGELOG.md / AGENTS.md / PROJECT.md / next.md / journal/ / research.md / design.md / radar.md）——2026-04-17 合并整合后这几个短名在项目内语义已经明确
- 本项目默认用 English kebab-case

### 11.2 条目标题（Ken 2026-04-24 拍板）

**硬规则：日期不能做条目的主标识，必须有内容关键词可被检索。**

Ken 原话：
> "不要用日期，所有东西都说准确什么内容的，不然你怎么检索"

- ❌ `### 2026-04-24 新条目` / `### 4.24 评估` / `### dry_run_20260416_165636`（只有时间戳）
- ⚠️ `### [2026-04-24] 修复 bug`（日期 + 模糊描述，勉强）
- ✅ `### atypica.ai — AI research agent 模拟用户访谈做 PMF 验证`
- ✅ `### [2026-04-24] AXL 第二次辩论 G+F 修复后评估`（日期作辅助元数据 + 完整内容描述）
- ✅ `### cp0-mini-3q-success-report`（内容 + 可辅以日期后缀）

**判据**：Ctrl+F 搜条目关键内容能搜到吗？搜"atypica"能找到？搜"如何科学的统治世界"能找到？搜"G+F 修复"能找到？能 → ✓；只能搜日期 → ✗。

**适用范围**：radar.md / journal/*.md / research.md / design.md 里的所有 `## / ###` 条目 + experiments/ 下所有实验目录名。

**已有不合规的不强制改**（改动风险大于收益），但下次引用或更新时顺手修正。

### 11.3 journal 自动留档（Ken 2026-04-24 拍板）

**硬规则：cc 看到以下类型内容时自动写 journal，不等 Ken 说"留档"。**

Ken 原话：
> "以后就自动化"

**必须自动留档的类型**：
1. 正式评估稿（如 AXL 多轮辩论质量评估）
2. P0/P1 bug 根因定位 + 修复验证（如 G+F 修复前后对比）
3. 外部观点多方对照（如 cc vs GPT vs Codex 同题评估，两份/多份都保留）
4. 方法论级纠正（如 `feedback_no_moral_posturing.md` 那次 Ken 永久指令）
5. Ken 对某战略/产品/技术方向的明确拍板

**不需要自动留档**（各自有去处）：
- 日常代码改动 → CHANGELOG.md
- 单条外部参考 → radar.md
- 研究结论更新 → research.md
- 设计方案修改 → design.md
- 任务增减 → next.md
- 普通对话 / 疑问 → 不留

**留档格式**：
- 标题按 §11.2 条目标题规则（内容关键词 + 可选日期前缀）
- 多方观点对照时全部保留，不只保留 cc 自己的版本
- 放在 `notes/journal/project-log-YYYY-MM.md` 对应月份文件里

---

## 12. 关键决策速查

| 日期 | 决策 | 原文 |
|---|---|---|
| 2026-04-13 | 辩论引擎从正反方改学科碰撞 | `CHANGELOG.md` 04-13 |
| 2026-04-14 | 记忆系统 Phase 1+2 完成（31 pytest）| `CHANGELOG.md` 04-14 |
| 2026-04-15 | 7 基础学科定版（Ken）| `notes/journal/project-log-2026-04.md` 04-15 |
| 2026-04-15 | KPAX 六条硬规则 | `notes/next.md` 顶部 + 本文件 §5.1 |
| 2026-04-15 晚 | 冗长重复修复，quick max_tokens (1500,1000)→(800,600)，单场 $1.65→$0.91 | `CHANGELOG.md` 04-15 晚 + mini_dry_run_report |
| 2026-04-15 晚 | 降本裁剪方案全作废（mini run 证实不需要）| mini_dry_run_report §4 |
| 2026-04-15 晚 | KPAX v0 形态 = 7 席座谈会（3D 维多利亚书房 + 黑神话 UE5 质感）| `notes/design.md#kpax-v0-deliberation-room` |
| 2026-04-15 晚 | 7 人设定 = 5 男 2 女 + 2 东亚（数学 + CS），不要印度 | 同上 §7 |
| 2026-04-16 | 侧翼战场 vs 正面战场原则（Ken 纠正 cc 三次错框）| 本文件 §5.3 + `notes/research.md#wisland-analysis-and-positioning` |
| 2026-04-16 | "绝不 OCR" 硬规则撤回（cc 错误外推）| `notes/research.md#wisland-analysis-and-positioning` B.3 修订版 |
| 2026-04-16 | KPAX 三条知识线架构（Lucas 提醒 cc 漏此层）| `notes/research.md#kpax-knowledge-source-architecture` |
| 2026-04-16 晚 | 20 场 scaleup 完成，mean $0.99 / CV 17% | `experiments/.../scaleup_report.md` |
| 2026-04-16 晚 | AXL 结构化 JSON 日志基建 + request_id middleware | `projects/knowledge-graph/backend/app/utils/logging_setup.py` |
| 2026-04-16 晚 | Pilot judge rubric v0.1 落地（AXL 递归 dogfooding 自设计）| `experiments/.../pilot_judge_rubric_v0.1.md` |
| 2026-04-16 晚 | KPAX backend survey：5 处 monorepo 违规 | `notes/journal/project-log-2026-04.md` 04-16 深夜 |
| 2026-04-17 凌晨 | 新分工生效：cc 战略 / cursor 开发 / codex review / ken 终审 | 本文件 §6 + `notes/journal/project-log-2026-04.md` 04-17 |
| 2026-04-17 凌晨 | Lucas 量化闭环问题识别（5 层 A→E 路径）| `notes/research.md#quantification-gap` |
| 2026-04-17 凌晨 | 文件合并整合：research/ + ideas/ + design/ 合一；AGENTS.md 并入 PROJECT.md | 本 commit |

历史决策详见 `notes/journal/project-log-YYYY-MM.md` 按日期倒序。

---

## 13. 文件生命周期

| 文件 | 更新频率 | 谁改 |
|---|---|---|
| `notes/next.md` | 每次开工前 / 完工后 | 任意 agent |
| `notes/journal/project-log-YYYY-MM.md` | 每次做完要事 / 每次重要对话 | 任意 agent。**月底换新文件**，旧文件归档 |
| `CHANGELOG.md` | 每次代码 commit | commit 者 |
| `experiments/config/experiment_registry.json` | 实验状态变化 | 实验 owner |
| `projects/knowledge-graph/PROGRESS.md` | AXL 产品评分变动 | Ken 手动 |
| `notes/design.md` | 设计方案大改动 | 设计者。小改动直接编辑对应节，大版本升级在同文件加 v2 节 |
| `notes/research.md` | 研究结论更新 | 同上 |
| `notes/radar.md` | cc 看到值得记录的外部链接时 append | cc 主，任何 agent 可补 |
| `PROJECT.md`（本文件）| 大阶段切换 / 结构变化 / 硬规则调整 | 任意 agent，不高频改 |
| `README.md` | 对外宣言调整 | 慎改 |
| `AGENTS.md` | 已退化为 redirect，一般不改 | - |
| `KPAX.md` | 产品定位调整 | 慎改 |

---

## 14. 各 agent 的私有记忆

- **Claude Code**：`C:\Users\ken\.claude\projects\.../memory/MEMORY.md`（索引式，含多个 feedback_*.md 反模式清单）
- **Cursor**：`.cursor/rules/*.md`（规则式，带 frontmatter 控制触发）
- **Codex**：本文件 + `AGENTS.md`（redirect 入口）+ 运行时 context

**硬规则**：**私有记忆里不放跨 agent 共享的研究内容，全部 reference `notes/` 下的文件**，避免三边同步。

---

## 15. 下一步

**不在本文件写**。打开 `notes/next.md` 找你 owner 的 P0。

本文件只在你**确实迷路**时回来看"我们在干嘛整体"。

---

*最后更新：2026-04-17 凌晨 by Claude Code。本文件合并整合了原 `AGENTS.md`。大结构改动请 Ken 拍板。*
