# AgentXLab

> Research should be exciting. We're making it that way.

> 研究本应令人兴奋。我们正在让它变成那样。

**AgentXLab is a platform for researching anything through scientific methodology and interdisciplinary perspectives.** Pick any combination of disciplines, watch them debate your question through real publication data, and walk away with a direct answer plus the conditions under which that answer holds.

**AgentXLab 是通过科学方法论和跨学科视角研究万事万物的平台。** 任意组合学科，让它们围绕你的问题展开辩论，看真实论文数据如何支撑或反驳每个观点，最后拿到一个直接的答案 + 这个答案在什么条件下成立。

Built on 240M+ academic works from OpenAlex. Chinese and English. Open to everyone.

基于 OpenAlex 的 2.4 亿+ 学术论文构建。中英双语。向所有人开放。

---

## Two Products, One Engine / 两个产品，同一引擎

| | **AXL** (Agent X Lab) | **KPAX** (in development) |
|---|---|---|
| **What** / 是什么 | Open-ended cross-disciplinary research platform | General decision-support product layer on top of AXL |
| **Who** / 给谁用 | Researchers, students, anyone exploring open questions | Anyone facing a decision and wanting it thought through |
| **Output** / 产出 | Research artifacts: hypotheses, papers, debate transcripts | Direct answer + key conditions + actionable next step |
| **Status** / 状态 | Live (Phase 2.5 shipped) | KPAX backend service ready, frontend座谈会 in progress |

AXL is the research platform. KPAX is the decision product on top — same multi-agent debate engine, different output framing. See `KPAX.md` for the full product spec.

AXL 是研究平台，KPAX 是搭在它上面的决策产品 —— 同一个多 agent 辩论引擎，不同的输出形态。完整产品定义见 `KPAX.md`。

---

## Why / 为什么做这个

Human knowledge is fragmented. A breakthrough in marine biology might solve an open problem in materials science. A 1970s cybernetics paper might hold the key to modern AI alignment. These connections exist, but the walls between disciplines keep them hidden.

人类知识是碎片化的。海洋生物学的突破也许能解决材料科学的开放问题。一篇 1970 年代的控制论论文也许是现代 AI 对齐的关键。这些联系客观存在，但学科之间的壁垒让它们一直隐藏着。

We wanted to make exploring those boundaries feel like a game — pick disciplines, watch connections light up, find the blank spots on the map.

我们想让探索这些边界变得像游戏一样 —— 选学科，看联系亮起来，找到地图上的空白。

So we built a platform where AI agents from different fields sit at the same table. They debate. They disagree. A philosopher challenges a physicist's assumptions; a linguist reframes a biologist's question. A moderator tracks where they converge and where they don't.

所以我们搭了一个平台，让来自不同领域的 AI 智能体坐在同一张桌子旁。它们辩论，它们争执。哲学家质疑物理学家的假设；语言学家重新构架生物学家的问题。主持人追踪它们在哪里达成共识，在哪里无法调和。

From the friction between perspectives, ideas emerge that none of them would have produced alone. Original research directions. Hypotheses that connect fields in ways nobody has tried.

从视角的摩擦中，涌现出它们任何一个都无法独自产生的想法。原创的研究方向。以前没人尝试过的方式连接各领域的假设。

The longer we watched this happen, the more it looked like something bigger than a research tool. It looked like a path toward **AI that can genuinely create** — through the collision of multiple minds, multiple traditions, multiple ways of seeing.

我们观察这件事发生得越久，就越觉得它远不止一个研究工具。它看起来像是一条通往 **AI 真正拥有创造力**的路径 —— 通过多种思维、多种传统、多种视角的碰撞。

---

## Product Principles / 产品原则

Four principles, all enforced at prompt level and reviewed every iteration.

四条原则，全部在 prompt 层面落实，每次迭代都重审。

### 1. Answer the question first / 先回答问题

Every debate produces a **Final Answer Layer** at the top: direct answer (Yes / No / Partly / Not yet), key conditions, and one actionable next step. The 4-section research summary (consensus / disagreements / open questions / directions) is supporting material below — collapsed by default.

每场辩论顶层产出 **Final Answer Layer**：直接答案（能 / 不能 / 部分能 / 暂时不能）+ 关键条件 + 一句可执行的下一步。四段研究综述（共识 / 分歧 / 开放问题 / 研究方向）作为下方支撑材料，默认折叠。

### 2. No moral filter / 不做道德审判

The platform models questions, it does not judge them. We do not refuse to engage with sensitive or unconventional questions, do not insert "this might be dangerous / not advised" warnings, do not narrow the question on the user's behalf. Limits exist only at three places: product scope, model boundary, executability.

平台对问题做建模，不做价值判断。不拒绝任何敏感或非常规问题，不插入"这可能危险 / 不建议"类警告，不替用户收窄问题。约束只来自三处：产品范围、模型边界、可执行性。

### 3. Debate ≠ Free / 两种碰撞模式各有职责

Conflict between agents is the point — but conflict serves different goals.

agent 之间的冲突是核心 —— 但冲突服务于不同目标。

- **Debate mode** (Popperian / 破坏性检验): agents attack each other's frames; output is a verdict that survives the stress test.
- **Free mode** (Kuhnian / 建设性综合): agents fix gaps in each other's models; output is a runnable spec (variables / assumptions / observables / falsification conditions / next steps).

`debate` 模式（波普尔式 / 破坏性检验）：agent 互相攻击对方框架，产出经过压力测试仍站得住的判断。`free` 模式（库恩式 / 建设性综合）：agent 互相补全对方模型的缺口，产出可跑的 spec。

Choosing debate vs free is not a UI option — it's a **product-form choice**.

debate vs free 不是 UI 选项，是**产品形态选择**。

### 4. Neutral framing on entry / 入口不锁定目标函数

When the system rephrases your question into a research framing, it stays neutral: "build a model of X / analyze the relationship among Y" — never "maximize X / avoid Y / prevent Z" on your behalf. If your question admits multiple readings (mechanism modeling, simulation, audit detection, adversarial reasoning, decision boundaries), the system picks the widest one and lets agents fan out from there.

系统把你的问题改写成研究框架时保持中性：「建立...的仿真模型 / 分析...之间的关系」，不替你写成「最大化 X / 规避 Y / 防止 Z」。如果你的问题有多种解读（机制建模、仿真、审计检测、对抗推演、决策边界），系统选最宽的，让 agent 自己分流。

---

## Version Timeline / 版本时间线

Each phase ships in main; previous phases stay in the codebase as foundations.

每个版本都进主线；之前的版本作为基础保留在代码库里，不擦除。

### Phase 0 — Multi-Agent Foundations / 多 agent 基础（2026-04 之前）

The 5 core capabilities of AXL went live:

AXL 的 5 个核心能力上线：

- Knowledge Graph (force-directed, OpenAlex 240M+ works) / 知识图谱
- Multi-Agent Debate Engine (Professor / Associate / Assistant ranks, persona system) / 多 agent 辩论引擎
- Conversational Research Advisor / 对话式研究顾问
- Paper Drafting Pipeline / 论文起草流程
- Forum + Points / 论坛 + 积分系统

### Phase 1 — Mode Bifurcation / 模式分叉（2026-04-23）

Discovered that `debate` and `free` modes were producing nearly identical output (the only difference was an 80-character stance block). Phase 1 split them at every level:

发现 `debate` 和 `free` 模式输出几乎一样（唯一差异是 80 字的 stance 段）。Phase 1 在每一层做了真正的分叉：

- Separate `FREE_ROUND_OPENERS` and `FREE_MODERATOR_PROMPTS` (Kuhnian co-build mindset, not Popperian stress test)
- Agent mission section diverges by mode (debate = adversarial / free = collaborative)
- Moderator role diverges (Director vs Coordinator)
- G+F constraint to prevent same-discipline Prof / Assoc producing identical output (cross-LLM-family + 3-column digest)
- `raw_question` field added so the user's original wording is never overwritten by AI rephrasing

### Phase 2 — Final Answer Layer / 最终答案层（2026-04-27）

Even with mode bifurcation, both modes produced research summaries — never a direct answer. Phase 2 added a top-level Final Answer Layer above the existing 4-section summary.

即使做了模式分叉，两种模式仍然产出研究综述 —— 从来不直接给答案。Phase 2 在 4 段综述之上新增 Final Answer Layer。

- 4 new fields: `direct_answer / why / conditions / next_steps`
- Hard rule: `direct_answer` first sentence must start with Yes / No / Partly / Not-yet — no pseudo-clarity dressed up as a verdict
- Mode-specific prompts: debate's `why` is what survived the stress test; free's `conditions` includes aggregated falsification conditions from the transcript
- Frontend: hero serif headline + supporting sections, detailed analysis collapsed by default

### Phase 2.5 — Product Calibration / 产品校准（2026-04-28）

Edge-case testing revealed entry-level framing was narrowing user questions prematurely. Phase 2.5 fixed four product-layer issues without touching the schema.

边缘问题测试发现入口层把用户问题过早窄化。Phase 2.5 在不动 schema 的前提下修了 4 个产品层问题。

- **2.5-A**: Entry rephrasing must stay neutral — no objective-function lock-in, no moral filter words
- **2.5-D**: Final Answer UI compressed from 4 sections to 3 visual blocks (Direct Answer hero with `why` as a light supporting line beneath)
- **2.5-B**: Debate moderator pressures toward a "minimal runnable model" structure in Round 2/3, not Round 1 (preserves exploration)
- **2.5-C**: Numeric evidence in final answer auto-tagged as "(pending verification)" when LLM cites specific thresholds / paper years / sample sizes
- **Permanent rule**: No moral filtering on the platform's prompts. Limits only on product scope, model boundary, executability. See `notes/design.md §axl-debate-mode-design > 产品原则：道德层严令禁止`.

### Roadmap / 路线图

- KPAX v0 end-to-end (frontend deliberation room + 7-chair avatar system)
- Avatar layer — Hall of Time scene with discipline / persona / wild-expert avatars
- Simulation sandbox + experiment-design renderer (free mode Round 3 → executable spec)
- Phase 1.1 (`useEffect` priority fix for Discovery → Debate hand-off)
- Phase 1.2 (Round 3 length tightening)
- Moderator bias multi-question audit (does Complex Systems always win?)

详见 `notes/next.md` 和 `CHANGELOG.md`。

---

## What You Can Do Today / 你今天能做什么

### Explore the Knowledge Graph / 探索知识图谱

A living, interactive map of academic disciplines connected by real publication data from OpenAlex (240M+ works). Solid lines = established research. Dashed lines = research gaps no one has mapped.

一张活的、可交互的学科地图，基于 OpenAlex 真实论文数据（2.4 亿+ 篇）。实线代表已有研究，虚线代表研究空白 —— 没人踏足的领地。

Every edge carries data: shared paper counts, intersection metadata, core tensions between fields. Click an edge and you're looking at the frontier of human knowledge.

每条边都承载数据：共有论文数量、交叉点元信息、学科间的核心张力。点击一条边，你看到的就是人类知识的前沿。

### Run Multi-Agent Debates / 运行多智能体辩论

Pick disciplines (AXL: 2-7; KPAX uses 3 / 5 / 7 odd numbers for verdict-ability). Choose mode: **debate** for stress test, **free** for co-building a runnable spec. Each round produces structured output; after Round 3 the system generates a Final Answer Layer at the top + a 4-section research summary below.

选学科（AXL 2-7 个；KPAX 用 3 / 5 / 7 奇数便于形成判断）。选模式：`debate` 做压力测试，`free` 共建可跑 spec。每轮产出结构化输出；第 3 轮结束后系统生成 Final Answer Layer 在顶部 + 4 段研究综述在下方。

Debates run in Chinese or English. You control discipline weights. Every debate is archived to `knowledge_graph.db` and survives any code reload.

辩论支持中英文。你控制学科权重。每场辩论自动归档到 `knowledge_graph.db`，代码重启不丢。

### Chat with a Research Advisor / 与研究顾问对话

The Detail Panel doubles as a conversation interface. Ask the AI to explore research angles. Pick from suggested directions. Type natural language commands to manipulate the canvas:

Detail Panel 同时也是对话界面。让 AI 探索研究角度，从建议方向中选择，用自然语言指令操控画布：

- "add Neuroscience" / "加上神经科学"
- "remove Philosophy" / "去掉哲学"
- "start debate" / "发起辩论"

The AI understands context: what's selected, what's been discussed, what hypotheses have been generated.

AI 理解上下文：当前选中了什么，讨论了什么，已经生成了哪些假设。

### From Insight to Paper / 从洞见到论文

Debate summaries, confirmed hypotheses, and open questions flow into a conversational paper drafting pipeline — discuss the structure with AI, iterate, then output.

辩论摘要、已确认的假设、开放问题汇入对话式论文起草流程 —— 和 AI 讨论结构，反复迭代，最终输出。

The paper is a byproduct. The real output is the creative leap — the research direction that didn't exist before the collision.

论文是副产物。真正的产出是那个创造性跳跃 —— 碰撞之前根本不存在的研究方向。

### Join the Community / 加入社区

**What We Think** — A forum for sharing experimental results, research directions, and cross-disciplinary insights. Upvote, comment, earn points for valuable contributions.

**Experiment Archive** — Published debate results and AI-generated hypotheses become community resources.

**Leaderboard** — Points for posting, commenting, running experiments. Researchers who contribute most to the collective knowledge base rise to the top.

发帖、评论、运行实验都获得积分。对集体知识库贡献最大的研究者排名最高。

---

## KPAX (in development) / KPAX 平台层（开发中）

KPAX is the **general decision-support product** that sits on top of AXL's debate engine. Same engine, different framing — built for someone facing a real decision, not someone exploring research questions.

KPAX 是搭在 AXL 辩论引擎之上的**通用决策产品**。同样的引擎，不同的输出形态 —— 给真实面对决策的人用，不是给做研究的人用。

### Avatar System: Hall of Time / 化身体系：时间博物馆

KPAX participants are not generic "AI assistants" — they are **avatars** drawn from three sources:

KPAX 里参与讨论的不是单一"AI 助手"，而是一组**化身（Avatar）**，按来源分三类：

1. **Discipline avatars** — agents trained on a discipline (physicist / economist / psychologist…). Knowledge from academic papers and structured professional sources.
2. **Persona avatars** — decision frames distilled from real public figures (Buffett / Musk / Jobs / Plato / Wang Yangming / Feynman…). Knowledge from public statements, books, interviews, biographies.
3. **Wild avatars** — high-quality individuals identified from community data (Reddit / Zhihu / X regulars who consistently produce sharp judgments). Knowledge from structured extraction of public posts.

1. **学科化身** — 基于学科训练的 agent（物理学家 / 经济学家 / 心理学家…）。知识源是学术论文和结构化专业资料。
2. **真人化身** — 从公开材料里萃取出具体人物的决策框架（巴菲特 / Musk / 乔布斯 / 柏拉图 / 王阳明 / 费曼…）。知识源是公开言论、著作、访谈、股东信、传记。
3. **野生化身** — 从社区大样本里识别出的高水平个体。知识源是公开发言的结构化抽取。

All three coexist in one session. Plato can sit next to Musk. Feynman can question a wild Reddit investor. The scene framing is **Hall of Time** — a space holding avatars from different eras side by side, not a chatbox where you talk to one AI at a time.

三类化身在同一场讨论里**共存**。柏拉图可以和 Musk 同席，费曼可以对着一个野生 Reddit 投资者追问细节。场景叙事是**「时间博物馆（Hall of Time）」** —— 一个容纳不同时代化身共存的空间，不是对话框里和单个 AI 聊天。

The room has 7 fixed chairs (discipline-completeness commitment); each session seats **3 / 5 / 7 avatars** (odd numbers force verdict-ability, minimum 3 to prevent thin discussions; moderator not counted). Avatars not summoned to speak this round may still be in the hall, doing other things.

议事厅 7 张固定的椅子（学科完整性承诺）；每场坐 **3 / 5 / 7 位化身**发言（奇数便于决断，最少 3 位避免对话太薄；moderator 不计入）。没被召唤的化身可能在厅里做自己的事。

### Five Question Types / 五种问题类型

Decision questions reduce to five types, each with a tailored report template:

人的决策问题归纳为五种，每种对应不同的报告模板：

| Type / 类型 | What you're asking / 用户在问什么 | Report output / 报告核心 |
|---|---|---|
| **Yes/No** / 是否题 | Should I do it? / 做不做 | Pro/con + key prerequisites |
| **Probability** / 概率题 | Will it happen? / 会不会发生 | Probability + factor breakdown |
| **Choice** / 选择题 | Which option? / 选哪个 | Multi-axis comparison |
| **Strategy** / 策略题 | How to do it? / 怎么做 | Phased roadmap + risk points |
| **Evaluation** / 评估题 | What's it worth / what's the risk? / 怎么样 | Multi-dimensional scoring |

### Business Model / 商业模式

- **Core product is free** / 主产品免费
- **BYOM** (Bring Your Own Model) — connect your own LLM API key, or pay platform to run yours / 接你自己的 LLM API key，或付平台代付
- **Skill marketplace** — third-party agents and persona avatars / Skill 市场：第三方 agent 和真人化身
- **Token economics** — earn by sharing, spend on advanced skills / 代币经济：分享赚，消费用
- **Wallet as one identity option** — not the only way to log in / 钱包是身份方式之一，不是唯一登录方式

KPAX is being developed as a separate frontend product surface (`kpax/frontend/`). The backend service (`kpax/backend/kpax_svc/`) is live and connects to AXL via HTTP. See `KPAX.md` for the full product spec.

KPAX 作为独立的前端产品在开发（`kpax/frontend/`），后端服务（`kpax/backend/kpax_svc/`）已可用，通过 HTTP 接 AXL。完整产品规格见 `KPAX.md`。

---

## Architecture / 架构

```
+---------------------+         HTTP        +---------------------+
|  KPAX (in dev)      |  <----------------> |  AXL (live)         |
|  decision product   |                     |  research platform  |
|                     |                     |                     |
|  - 5 question types |                     |  - knowledge graph  |
|  - avatar system    |                     |  - debate engine    |
|  - report renderers |                     |  - paper drafting   |
|  - token ledger     |                     |  - forum + points   |
+---------------------+                     +---------------------+
                                                    |
                                            +---------------+
                                            |  OpenAlex API |
                                            |  240M+ works  |
                                            +---------------+
```

Two services, one HTTP boundary. AXL is the engine (research platform). KPAX is the product (decision tool). Hard rule: KPAX never imports AXL Python code directly — only HTTP.

两个服务，一个 HTTP 边界。AXL 是引擎（研究平台），KPAX 是产品（决策工具）。硬规则：KPAX 不直接 import AXL 的 Python 代码 —— 只走 HTTP。

### Tech Stack / 技术栈

| Layer | What |
|-------|------|
| Frontend | React 19, TypeScript, Vite, D3.js, Tailwind CSS, Framer Motion, ReactMarkdown |
| Backend | Python FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| AI | LiteLLM (DeepSeek / GPT / Claude / Gemini swappable; BYOM supported on KPAX) |
| Academic Data | OpenAlex API (240M+ works, 250K+ concepts) |
| Auth | Google OAuth 2.0 + Email/Password + JWT (dev bypass available) |
| Payments | Stripe (card) + USDT/Crypto (manual wallet) |
| i18n | Chinese / English, auto-detect |
| Deploy | Docker Compose |

AXL backend: 62+ API routes, 15 routers — disciplines, intersections, graph construction, AI hypothesis (one-shot + conversational), multi-agent debate engine (SSE streaming), reverse discovery, paper generation, forum, subscription, OpenAlex sync, Zep memory.

AXL 后端：62+ 个 API 路由，15 个路由模块。

KPAX backend service: question classifier (5 types), context collector, expert builder, report generator, token ledger (KPAX token + LLM cost dual-event audit), AXL HTTP client, LiteLLM client.

KPAX 后端服务：题型分类、上下文采集、专家构建、报告生成、代币账本（KPAX 代币 + LLM 成本双事件审计）、AXL HTTP 客户端、LiteLLM 客户端。

---

## Quick Start / 快速启动

```bash
# AXL Backend / AXL 后端
cd projects/knowledge-graph/backend
pip install -r requirements.txt
cp .env.example .env          # fill in DEEPSEEK_API_KEY / 填入 API 密钥
alembic upgrade head          # apply migrations / 跑 schema 迁移
uvicorn app.main:app --reload

# Seed data / 导入数据
python -m scripts.import_from_markdown

# AXL Frontend / AXL 前端
cd projects/knowledge-graph/frontend
npm install
npm run dev                   # http://localhost:5173
```

Docker:

```bash
cd projects/knowledge-graph
cp backend/.env.example backend/.env
docker compose up -d          # http://localhost
```

KPAX backend service (optional, talks to AXL via HTTP):

```bash
cd kpax/backend
pip install -r requirements.txt
uvicorn kpax_svc.main:app --port 8001 --reload
```

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | Yes | Powers default debate engine / 驱动默认辩论引擎 |
| `OPENAI_API_KEY` | Optional | For multi-LLM-family G+F constraint / 用于跨 LLM 家族约束 |
| `ANTHROPIC_API_KEY` | Optional | For Claude in debate pool / Claude 加入辩论池 |
| `DATABASE_URL` | No | Default: SQLite / 默认 SQLite 本地开发 |
| `ZEP_API_KEY` | No | Agent memory / 智能体记忆 |
| `GOOGLE_CLIENT_ID` | No | Google OAuth login / Google 登录 |
| `AUTH_BYPASS_DEV_MODE` | No (dev only) | Short-circuit auth + quota for local dev / 本地开发短路认证和配额 |

---

## Repository / 仓库结构

```
/
├── projects/knowledge-graph/    AXL — research platform (live)
│   ├── backend/                  FastAPI, 62+ routes, 15 routers
│   └── frontend/                 React 19, D3.js
│
├── kpax/                        KPAX — decision product (in dev)
│   ├── backend/kpax_svc/         FastAPI service, talks to AXL via HTTP
│   └── frontend/                 React 19 (deliberation room WIP)
│
├── notes/                       Internal design + research notes
│   ├── design.md                 Product philosophy (axl-debate-mode-design + Final Answer Layer + 道德层产品原则)
│   ├── research.md               Research notes (KPAX knowledge sources, avatar system, agent evolution)
│   ├── radar.md                  External references (open-source projects, papers, tools)
│   ├── next.md                   Action board across agents (cc / cursor / codex / ken)
│   └── journal/                  Time-ordered project log + appendix evaluations
│
├── experiments/                 Experimental runs (emergence_decomposition + cp0/pilot baselines)
├── PROJECT.md                   Project navigation + agent role split + writing rules + naming conventions
├── KPAX.md                      KPAX product spec (avatars, 5 question types, business model)
├── CHANGELOG.md                 Phase 0 → 2.5 changelog
└── README.md                    This file
```

### Research Background / 研究背景

This project grew out of an extensive cross-disciplinary literature review spanning 71+ classic works (Frege 1892 to present) and 65+ frontier papers (2024-2026) across philosophy of language, cognitive science, cybernetics, computational creativity, AI alignment, and symbol grounding. That foundational research — 6 directions, 90+ annotated PDFs, synthesis notes, and a full discipline taxonomy — is preserved in the [`archive/early-research`](https://github.com/KY-East/Agentxlab/tree/archive/early-research) branch.

本项目源于一次大规模的跨学科文献综述，涵盖 71+ 部经典著作（从 Frege 1892 至今）和 65+ 篇前沿论文（2024-2026），横跨语言哲学、认知科学、控制论、计算创造力、AI 对齐和符号接地。这些基础研究 —— 6 个方向、90+ 篇注释 PDF、综合笔记和完整学科谱系 —— 保存在 [`archive/early-research`](https://github.com/KY-East/Agentxlab/tree/archive/early-research) 分支中。

### Intellectual Lineage / 思想血缘

AXL's multi-agent debate idea did not appear from nowhere. It descends from:

AXL 的多 agent 辩论思想不是凭空出现的，它的血缘是：

- **OASIS** (CAMEL-AI's Open Agent Social Interaction Simulations) — the underlying multi-agent simulation framework
- **MiroFish** (Shanda Group) — group-prediction engine on top of OASIS
- **AXL** (this project) — forks toward **multi-disciplinary expert collision for emergent creativity**, instead of group-prediction

OASIS 是底层多 agent 仿真框架；MiroFish 在 OASIS 上做群体预测；AXL 从这条线分叉，方向变成**多学科专家碰撞产生涌现创造力**。详见 `notes/research.md §axl-intellectual-lineage`。

---

## Author / 发起人

**KY.East**

## License

MIT
