# Agent X Lab

> What if AI could discover the next great research breakthrough -- by finding the connections scientists haven't seen yet?

> 如果 AI 能帮助发现下一个重大研究突破 -- 通过找到科学家们尚未看见的联系？

Agent X Lab is an interdisciplinary research platform where AI agents debate across academic boundaries, uncover hidden connections between fields, and help you write the papers that bridge them.

Agent X Lab 是一个跨学科研究平台。AI 智能体跨越学科边界展开辩论，发掘领域之间隐藏的联系，帮你写出连接它们的论文。

Built on real academic data. Powered by multi-agent intelligence. Research exploration that feels like discovery.

基于真实学术数据构建。由多智能体驱动。让研究探索回归发现的兴奋感。

---

## The Idea / 核心理念

Human knowledge is fragmented. A breakthrough in marine biology might solve an open problem in materials science. A 1970s cybernetics paper might hold the key to modern AI alignment. But researchers stay in their lanes, read their journals, cite their peers.

人类知识是碎片化的。海洋生物学的突破也许能解决材料科学的开放问题。一篇 1970 年代的控制论论文也许是现代 AI 对齐的关键。但研究者们守着自己的领域，读自己的期刊，引用自己的同行。

Agent X Lab breaks those walls down.

Agent X Lab 打破这些墙。

You pick disciplines -- any combination, from Quantum Mechanics to Philosophy of Language to Cancer Research. The platform shows you what exists at their intersection: shared publications, known tensions, open questions. And where nothing exists? That's where it gets interesting.

你选学科 -- 任意组合，从量子力学到语言哲学到癌症研究。平台展示它们交叉处已有的东西：共有论文、已知张力、开放问题。而那些什么都没有的地方？那才是有意思的开始。

AI agents -- each representing a different discipline, each with a distinct persona and expertise -- engage in structured academic debate over your research question. They argue, challenge, synthesize. A moderator distills the insights. And from that collision of perspectives, new hypotheses emerge.

AI 智能体 -- 每个代表不同学科，每个有独特的人格和专长 -- 围绕你的研究问题展开结构化学术辩论。它们争论、质疑、综合。主持人提炼洞见。在视角的碰撞中，新的假设诞生。

---

## What You Can Do / 你能做什么

### Explore the Knowledge Graph / 探索知识图谱

A living, interactive map of academic disciplines connected by real publication data from OpenAlex (240M+ works). Select nodes, watch connections form. Solid lines mean established research. Dashed lines mean research gaps -- territory no one has mapped yet.

一张活的、可交互的学科地图，基于 OpenAlex 的真实论文数据（2.4 亿+ 篇）连接。选中节点，看联系浮现。实线代表已有研究，虚线代表研究空白 -- 没人踏足的领地。

The graph is not decoration. Every edge carries data: shared paper counts, intersection metadata, core tensions between fields. Click an edge and you're looking at the frontier of human knowledge.

图谱不是装饰。每条边都承载数据：共有论文数量、交叉点元信息、学科间的核心张力。点击一条边，你看到的就是人类知识的前沿。

### Run Multi-Agent Debates / 运行多智能体辩论

Pick 2-7 disciplines. AI generates a team of agents: professors, associates, assistants -- each with a unique persona (pioneer, critic, synthesizer, bridge-builder). They debate your research question across multiple rounds, with a moderator tracking consensus, disagreements, and open threads.

选 2-7 个学科。AI 生成一支智能体团队：教授、副教授、助理 -- 每人有独特人格（开拓型、批判型、综合型、桥梁型）。它们围绕你的研究问题进行多轮辩论，主持人跟踪共识、分歧和开放线索。

Debates run in Chinese or English. You control the discipline weights. Every debate produces a structured summary: consensus points, key disagreements, open questions, and future research directions.

辩论支持中英文。你控制学科权重。每场辩论产出结构化摘要：共识要点、关键分歧、开放问题、未来研究方向。

### Chat with a Research Advisor / 与研究顾问对话

The Detail Panel doubles as a conversation interface. Ask the AI to explore research angles. Pick from suggested directions. Type natural language commands to manipulate the canvas:

Detail Panel 同时也是对话界面。让 AI 探索研究角度，从建议方向中选择，用自然语言指令操控画布：

- "add Neuroscience" / "加上神经科学"
- "remove Philosophy" / "去掉哲学"
- "start debate" / "发起辩论"

The AI understands context: what's selected, what's been discussed, what hypotheses have been generated.

AI 理解上下文：当前选中了什么，讨论了什么，已经生成了哪些假设。

### Generate Research Papers / 生成研究论文

From debate summaries and confirmed hypotheses, generate structured academic paper outlines. The pipeline is conversational -- discuss, refine, iterate with AI before committing to a structure.

从辩论摘要和已确认的假设出发，生成结构化学术论文大纲。整个过程是对话式的 -- 先讨论、完善、迭代，再确定结构。

### Join the Community / 加入社区

**What We Think / 我们怎么想** -- A forum for sharing experimental results, research directions, and cross-disciplinary insights. Upvote, comment, earn points for valuable contributions.

一个分享实验结果、研究方向和跨学科洞见的论坛。点赞、评论，有价值的贡献获得积分奖励。

**Experiment Archive / 实验归档** -- Published debate results and AI-generated hypotheses become community resources. See what others have explored, build on their work.

发布的辩论结果和 AI 生成的假设成为社区公共资源。看看别人探索了什么，在他们的工作上继续前进。

**Leaderboard / 排行榜** -- Points for posting, commenting, running experiments. The researchers who contribute most to the collective knowledge base rise to the top.

发帖、评论、运行实验都获得积分。对集体知识库贡献最大的研究者排名最高。

---

## Architecture / 架构

```
+------------------+-------------------------+------------------+
|                  |                         |                  |
|  Discipline      |     Force-Directed      |  Detail Panel    |
|  Tree            |     Knowledge Graph     |  + AI Chat       |
|  (searchable,    |     (D3.js)             |  + Agent         |
|   collapsible,   |                         |    Commands      |
|   custom nodes)  |                         |                  |
+------------------+-------------------------+------------------+
     resizable              center                resizable
```

Three resizable panels. Left: full discipline taxonomy (OpenAlex-based, user-extensible). Center: real-time force-directed graph. Right: intersection details, AI hypotheses, and an always-on chat that doubles as a command line.

三个可调整大小的面板。左：完整学科分类体系（基于 OpenAlex，用户可扩展）。中：实时力导向图。右：交叉详情、AI 假设，以及兼作命令行的常驻对话框。

### Tech Stack / 技术栈

| Layer | What |
|-------|------|
| Frontend | React 19, TypeScript, Vite, D3.js, Tailwind CSS, Framer Motion |
| Backend | Python FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2 |
| AI | DeepSeek via LiteLLM (swappable to OpenAI / Anthropic / any provider) |
| Academic Data | OpenAlex API (240M+ works, 250K+ concepts) |
| Auth | Google OAuth 2.0 + JWT |
| i18n | Chinese / English, auto-detect |
| Deploy | Docker Compose |

Backend: 62 API routes, 13 routers -- disciplines, intersections, graph construction, AI hypothesis (one-shot + conversational), multi-agent debate engine (SSE streaming), reverse discovery, paper generation, forum (voting / points / leaderboard), OpenAlex sync, Zep memory.

后端：62 个 API 路由，13 个路由模块 -- 学科管理、交叉点查询、图谱构建、AI 假设生成（单次 + 对话式）、多智能体辩论引擎（SSE 流式）、反向发现、论文生成、论坛（投票 / 积分 / 排行榜）、OpenAlex 同步、Zep 记忆。

---

## Quick Start / 快速启动

```bash
# Backend / 后端
cd projects/knowledge-graph/backend
pip install -r requirements.txt
cp .env.example .env          # fill in DEEPSEEK_API_KEY / 填入 API 密钥
uvicorn app.main:app --reload

# Seed data / 导入数据
python -m scripts.import_from_markdown

# Frontend / 前端
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

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | Yes | Powers all AI features / 驱动所有 AI 功能 |
| `DATABASE_URL` | No | Default: SQLite / 默认 SQLite 本地开发 |
| `ZEP_API_KEY` | No | Agent memory / 智能体记忆 |
| `GOOGLE_CLIENT_ID` | No | Google OAuth login / Google 登录 |

---

## Repository / 仓库结构

This repo contains both the research foundation and the application built on top of it.

本仓库同时包含研究基础和基于其构建的应用。

```
/
├── research/                 Academic literature & notes / 学术文献与笔记
│   ├── README.md             71+ classics, 65+ frontier papers / 71+ 经典，65+ 前沿
│   ├── 6 research directions / 6 个研究方向
│   └── synthesis/            Cross-direction analysis / 跨方向综合分析
│
├── projects/
│   └── knowledge-graph/      The web application / Web 应用
│       ├── backend/          FastAPI, 62 routes, 11 migrations
│       └── frontend/         React 19, D3.js, Brutalist UI
│
├── notes/                    Research journal / 研究日志
├── CHANGELOG.md
└── STRUCTURE.md              Repo conventions / 仓库规范
```

The research corpus -- from Frege (1892) to 2026 frontier papers on AI alignment, computational creativity, and symbol grounding -- feeds directly into the knowledge graph. Theory drives the product. The product validates the theory.

研究语料库 -- 从 Frege（1892）到 2026 年 AI 对齐、计算创造力和符号接地的前沿论文 -- 直接驱动知识图谱。理论驱动产品，产品验证理论。

---

## Author / 发起人

**KY.East**

## License

MIT
