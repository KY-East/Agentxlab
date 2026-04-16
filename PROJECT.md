# Agent X Lab + KPAX — 开发导航

> **一份文件读完全项目**。目标：你/任何 agent 进来 10 分钟内知道"现在在哪 / 下一步是什么 / 要改什么去哪个文件"。
>
> 本文件是**索引+快照**，不重复其他文件的内容。事件详情看 `notes/journal/`，任务清单看 `notes/agenda/next.md`，代码变更看 `CHANGELOG.md`。

---

## 1. 一屏摘要

**一句话**：这是一个双产品项目。**AXL** 是学术底座，跑多学科 AI 辩论引擎。**KPAX** 是通用决策工具，调用 AXL 的能力，帮用户把一件事想透——深度、正确性、全面性。

| 产品 | 定位 | 代码位置 | 用户 | 状态 |
|---|---|---|---|---|
| **AXL** | 跨学科推演底座，开源 | `projects/knowledge-graph/` | 研究者 / KPAX 自己 | 产品 87/100，记忆系统 Phase 2 完成 |
| **KPAX** | 通用决策工具 | `kpax/` | 10 位朋友先行测试 → 扩大 | 骨架完成，v0 形态设计中（座谈会 3D） |

**核心信念**：多 agent 跨学科碰撞能产生涌现创造力。这是一个关于 AI 能力上限的研究假设，正在 `experiments/emergence_decomposition/` 里验证。目标是让 AI 真的能创造新东西，而非更快更省地执行已有任务。

**当前阶段**（2026-04-15 晚）：
- 🟢 涌现实验 Checkpoint 0 真关闭（mini dry run 3/3 验证新 config 单场 $0.91 / –45% / Tier 1 自洽）
- 🟡 Checkpoint 1 pilot 待启（40 场 baseline 扩样后台跑着）
- 🟡 KPAX v0 形态定案（7 席"满席+动态前景"座谈会，维多利亚黑神话质感），美术风格 + 角色图生成中
- 🔴 未启动：pilot 分析 / KPAX 真实 LLM 对接 / 前端 v0

---

## 2. 产品线状态面板

### 2.1 AXL — 学术底座

| 模块 | 状态 | 证据 |
|---|---|---|
| 辩论引擎（7 学科碰撞） | 生产可用 | `debate_engine.py`，今晚刚修 quick max_tokens + 反重复规则（commit `4b35f1e`）|
| 记忆系统 Phase 1+2 | 完成 | 31 pytest 通过（metadata schema / re-rank / 会话压缩）|
| Phase 3（七层记忆 L3+） | 未启动 | 见 `notes/research/seven-layer-memory-design.md` |
| 自由参数实验 | Phase 3 前冻结 | 见 `notes/research/agent-evolution-free-parameters.md` |
| KPAX HTTP API | 3 endpoints mock 就绪 | `projects/knowledge-graph/backend/app/routers/kpax_router.py` + `kpax_api_spec.md` |

### 2.2 KPAX — 消费工具

| 模块 | 状态 |
|---|---|
| `axl_client.py` — HTTP 调 AXL | ✅ 骨架 |
| `token_ledger.py` — 代币账本 | ✅ 骨架（guest 种子 50 / 消费 10/25/60 / 分享+20 / 预留 ChainAdapter）|
| `question_classifier.py` — 题型判别 | ⚠️ 骨架，`_chat_fn` 未接真 LLM（fallback verdict）|
| `context_collector.py` / `expert_builder.py` / `report_generator.py` | ❓ 文件存在未 survey |
| `v1_analyze.py` router | ✅ 已挂 FastAPI `/api/v1/analyze` |
| 前端 | ❌ 未起 |
| v0 形态设计 | ✅ `notes/design/kpax-v0-deliberation-room.md` |

### 2.3 实验线

| Checkpoint | 状态 | 数据位置 |
|---|---|---|
| CP 0 dry run（10 场 baseline）| 5/10 成功（04-14） | `results/dry_run_20260414_173832/` |
| CP 0 mini run（3 场验证新 config）| 3/3 成功（04-15 晚）| `results/dry_run_20260415_171016/mini_dry_run_report.md` |
| CP 0 scaleup（40 场 baseline 方差验证）| 🟡 后台跑（04-15 晚启动，~10h）| `results/` 新目录 |
| CP 1 pilot（baseline + A 组 × 20 题 × 2 run = 80 场）| 未启动，等 scaleup | |
| CP 2–4 全量（6 组 × 50 题 × 3 run = 900 场，估 $815）| 未启动 | |

---

## 3. 仓库导航：我要做 X，去哪

| 我要... | 去读 | 改哪里 |
|---|---|---|
| 改辩论 prompt / 学科 | `projects/knowledge-graph/backend/app/services/debate_engine.py` | 同 |
| 改 KPAX HTTP API | `projects/knowledge-graph/backend/app/routers/kpax_api_spec.md` | `kpax_router.py` |
| 加一个新实验 | `experiments/README.md` + 参考 `emergence_decomposition/spec.md` | 新建 `experiments/<name>/` |
| 改记忆系统 | `notes/research/seven-layer-memory-design.md` | `projects/knowledge-graph/backend/app/services/{zep_manager,session_memory}.py` |
| 改 KPAX 前端 / 形态 | `notes/design/kpax-v0-deliberation-room.md` | （v0 未起）|
| 改代币规则 | `kpax/backend/kpax_svc/services/token_ledger.py` | 同 |
| 查"为什么这么做 X" | `notes/journal/YYYY-MM.md`（按日期倒序）| journal 末尾 append |
| 查"下一步做什么" | `notes/agenda/next.md`（唯一 TODO 板） | 加/减 item |
| 查实验当前 checkpoint | `experiments/config/experiment_registry.json` | 同 |
| 查代码层变更历史 | `CHANGELOG.md` | commit 后同步 |
| 查 AXL 产品完成度 | `projects/knowledge-graph/PROGRESS.md` | Ken 手动评分更新 |
| 看公开市场定位（AXL）| `README.md` | 公开宣言，改要慎 |
| 看 KPAX 产品定位 | `KPAX.md` | 同 |
| 读 agent 协作规则 | `AGENTS.md` | 同 |

---

## 4. Onboarding — 新 agent 第一次进来先读哪 3 个

### Claude Code
1. `PROJECT.md`（本文件）
2. `AGENTS.md` §当前状态快照 + 写作规则 + 编码纪律
3. `notes/agenda/next.md` P0

### Cursor
1. `PROJECT.md`
2. `.cursor/rules/coding-discipline.md` + `.cursor/rules/workflow.md`
3. `notes/agenda/next.md` 找 `@cursor` owner

### Codex
1. `AGENTS.md`（它的原生主入口）
2. `PROJECT.md`
3. `notes/agenda/next.md` 找 `@codex`

### Ken
1. `PROJECT.md` §1 一屏摘要 + §2 状态面板
2. `notes/agenda/next.md` 找 `@ken`（要你拍板 / 评分 / 外部动作）
3. `notes/journal/YYYY-MM.md`（月度时间线）

---

## 5. 硬规则总汇（所有 agent 遵守，改规则要在 journal 记原因）

### 5.1 KPAX 六条（Ken 2026-04-15 拍板）
1. 产品承诺 = "把这个问题帮你想透"——深度/正确/全面，不是"给你没想到过的角度"
2. 5 题型（是否/概率/选择/策略/评估）全是基础功能，不做 MVP 5 选 1
3. 不锁 decision_domain 垂直，通用决策工具
4. 付费 = 代币（消费/分享/dex+合约买）。不做法币订阅、不做传统注册，钱包即身份
5. 成功判据 = 10 朋友 7 说"有帮助"
6. KPAX ↔ AXL Day 1 走 HTTP，代码/DB/部署全分开，**禁止 monorepo import**

### 5.2 实验硬规则
- **7 学科冻结**（物理/数学/经济/心理/社科/CS/艺术人文），不可再改（2026-04-15 Ken 拍板）
- **moderator 必须 Claude Opus 4.6**，不换其他模型
- **主 judge 固定 API 模型（GPT-5 / Gemini 2.x 选一个）**，不本地 fine-tune judge（模型能力必须 ≥ 被判模型）
- 实验状态必须 `checkpoint_<N>_<phase>` 格式

### 5.3 代码纪律
- **Simplicity First**：代码 scope 严格最小 / 建议 scope 放宽 / 质疑 scope 强制放宽
- **Goal-Driven**：> 3 步任务拆 checkpoint，每步有可观测成功判据，**禁"我改好了"式验证**
- 任何改 re-rank / debate prompt / 推演参数前，若 `experiments/results/` 有相关数据**必须先读**
- 文档里不藏 TODO，抽到 `notes/agenda/next.md`

### 5.4 写作（所有 agent + Ken 自己）
- 禁"不是而是"句式 / 禁 emoji / 禁翻译腔 / 禁 AI 味
- 直接、精准、深刻；不迎合；该指出问题就指出
- 只改要求的部分，不扩大修改范围

### 5.5 战场选择：侧翼打，不打正面（Ken 2026-04-16 拍板）

**核心原则**：不打正面战场，打侧翼战场。不是避战，是选战场。

| 维度 | 正面战场（不打） | 侧翼战场（打） |
|---|---|---|
| 性质 | 没资格 / 没积累 | 有能力干 |
| 例子 | 大模型 / IDC / 能源 / Claude Code / Cursor / OpenClaw Agent 这类通用 agent | AXL 多学科碰撞 / KPAX 通用决策 / 3D 座谈会 / 顾问 IK / 代币经济 |
| 判据 | 已经巨大的蓝海，头部玩家密集 | 大玩家不会专门做、需要特定积累 / 产品视角的细分角度 |

**具体"不做"**：
- ❌ 训练 / post-train 基础模型
- ❌ 自建 IDC / 大规模推理基建
- ❌ 通用 coding agent（Claude Code / Cursor / OpenClaw 这类）
- ❌ 自建文献索引 / 自研板式解析模型
- ❌ DCA 端侧百万长序列
- ❌ 把 KPAX 扩成通用科研工具

**具体"做"**：
- ✅ 多学科 agent 碰撞（AXL 独门）
- ✅ 通用决策产品（KPAX 承诺"帮你想透"）
- ✅ 3D 座谈会形态 vs 聊天框窠臼
- ✅ 七层记忆 + 自由参数 L7 元进化
- ✅ 代币经济 / 钱包身份
- ✅ 任何基于现成 LLM / agent framework 之上的差异化产品层

**每周一自检**：这周在打正面还是侧翼？正面立刻停手。

理由和更长论证见 `notes/research/wisland-analysis-and-positioning.md`。

---

## 6. 关键决策速查（近两周）

| 日期 | 决策 | 原文 |
|---|---|---|
| 2026-04-13 | 辩论引擎从正反方改学科碰撞 | `CHANGELOG.md` 04-13 |
| 2026-04-14 | 记忆系统 Phase 1+2 完成（31 pytest）| `CHANGELOG.md` 04-14 |
| 2026-04-15 | 7 基础学科定版（Ken）| `notes/journal/2026-04.md` 04-15 |
| 2026-04-15 | KPAX 六条硬规则 | `notes/agenda/next.md` 顶部 |
| 2026-04-15 晚 | 冗长重复修复，quick max_tokens (1500,1000)→(800,600)，单场 $1.65→$0.91 | `CHANGELOG.md` 04-15 晚 + mini_dry_run_report |
| 2026-04-15 晚 | 降本裁剪方案全作废（mini run 证实不需要）| mini_dry_run_report §4 |
| 2026-04-15 晚 | KPAX v0 形态 = 7 席座谈会（3D 维多利亚书房 + 黑神话 UE5 质感）| `notes/design/kpax-v0-deliberation-room.md` |
| 2026-04-15 晚 | 7 人设定 = 5 男 2 女 + 2 东亚（数学 + CS），不要印度 | 同上 §7 |

历史决策详见 `notes/journal/YYYY-MM.md` 按日期倒序。

---

## 7. 文件生命周期

| 文件 | 更新频率 | 谁改 |
|---|---|---|
| `notes/agenda/next.md` | 每次开工前/完工后 | 任意 agent |
| `notes/journal/YYYY-MM.md` | 每次做完要事 / 每次重要对话 | 任意 agent。**月底换新文件**，旧文件归档 |
| `CHANGELOG.md` | 每次代码 commit | commit 者 |
| `experiments/config/experiment_registry.json` | 实验状态变化 | 实验 owner |
| `projects/knowledge-graph/PROGRESS.md` | AXL 产品评分变动 | Ken 手动 |
| `notes/design/<topic>.md` | 设计方案大改动 | 设计者。**小改动直接编辑**，大版本升级加"v2.md" |
| `notes/research/<topic>.md` | 研究结论更新 | 同上 |
| `PROJECT.md`（本文件）| 大阶段切换 / 结构变化 | 任意 agent，**不高频**改 |
| `README.md` | 对外宣言调整 | 慎改 |
| `AGENTS.md` | 协作规则升级 | 慎改 |
| `KPAX.md` | 产品定位调整 | 慎改 |

---

## 8. 下一步

**不在本文件写**。打开 `notes/agenda/next.md` 找你 owner 的 P0。

本文件只在你**确实迷路**时回来看"我们在干嘛整体"。

---

*最后更新：2026-04-15 晚 by Claude Code。结构大改请 Ken 拍板。*
