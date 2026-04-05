# Changelog

## 2026-04-04 — 数据清理 & 画布重构

### 变更
- **数据库清理**: 删除第一代 Markdown 导入的旧学科数据（43 条 disciplines + 7 条 intersections），仅保留 OpenAlex 标准数据（26 Fields + 270 Subfields = 296 条）
- **画布"生长式"重构**: Canvas 起始为空白画布，用户从左侧选择学科后节点动态出现，2 个以上可查询交叉
- **后端 graph API**: `GET /api/graph` 新增 `?ids=` 参数，不传返回空图，传学科 ID 列表返回对应节点和连线
- **前端**: Canvas 不再依赖 `useGraph` 全量加载，改为 `selectedNodes` 变化时实时拉取
- research/ 目录下论文笔记和方向分析全部保留不动

---

## 2026-04-30 — Phase 4b: 论文分步生成

### 新增
- **PaperDraft / PaperSection 数据模型** + Alembic 迁移 004
- **paper_generator.py** — 大纲生成（整合辩论总结 + Zep 知识 + 相关论文）+ 逐章扩写（注入前序章节/写作指令）+ Markdown 导出
- **paper_gen.py router** — 6 个端点：创建草稿、列表、详情、编辑大纲、生成单章、导出
- **PaperEditor.tsx** — 论文编辑页面（标题编辑、章节展开/折叠、描述+写作指令、逐章生成/重新生成、进度条、新增章节、Markdown 下载）
- **DebateSession.tsx** — 辩论完成后"生成论文大纲"按钮 + 方向输入 + 已有草稿列表
- App.tsx 路由 `/paper/:draftId`

### Bug 修复
- 论文检索相关论文未按学科过滤，改为通过 intersection 联表查询
- draft 状态流转缺少 writing 中间态，首次生成章节时自动 outline → writing
- 章节版本号首次生成偏移为 v2，改为仅重新生成时递增
- PaperEditor 生成章节后 draft status 不及时更新（前端状态推导与后端对齐）
- DebateSession 切换 debate 时 existingDrafts 残留（非 completed 时清空）
- PaperEditor 切换 draftId 时旧草稿短暂残留（加 setDraft(null)）
- Debate.tsx 未使用变量 allDisciplines 及其 setter 调用导致构建失败
- PaperEditor.tsx 未使用导入 Trash2 导致构建失败

---

## 2026-04-30 — Phase 4a: Zep 知识库正式接入

### 新增
- **zep_manager.py 扩展** — push_debate_summary() / push_hypothesis() / retrieve_context()
- **辩论自动灌入 Zep** — 辩论总结 + AI 假设完成后 best-effort 推送到 Zep 知识图谱
- **辩论 Agent 知识注入** — 每轮辩论 1+N 检索（1 次共享主题 + N 次 Agent 学科专属），知识注入 LLM 对话

### Bug 修复
- create_debate intersection_id 校验从 issubset 改为精确匹配
- DebateSession 切换 debateId 时不重置状态（加 setLoading/setDebate/setError reset）
- Debate.tsx getDisciplines/getDebates 无 catch（加 toast 错误提示）

---

## 2026-04-04 — Phase 3: 反向发现引擎

### 新增
- **reverse_discovery.py** — 研究问题 → LLM 分析 → 学科匹配 → 组合推荐 → 研究空白标记
- **POST /api/discover** — 反向发现 API
- **DiscoveryPanel 组件** — 展示发现结果（相关学科 + 相关度 + 推荐组合 + 操作按钮）
- **Canvas.tsx** — 顶部新增发现搜索栏（双入口：首页跳转 + Canvas 原地搜索）
- **Home.tsx** — 搜索框改为调用 discover API

### Bug 修复
- create_debate 未校验无效 discipline id
- 图谱颜色分组算不出根学科（后端新增 root_id）
- Debate.tsx handleSuggestMode/handleCreate 无 catch
- DebateSession 成功操作后不清除过期错误

---

## 2026-04-04 — Phase 2: 多 Agent 学术辩论引擎

### 新增
- **debate_engine.py** — 4 种性格 Agent + Moderator，多轮辩论编排，四段式总结，AI 推荐模式
- **Debate / DebateAgent / DebateMessage** 数据模型 + Alembic 迁移 003
- **debate.py router** — 6 个端点（create/list/get/rounds/summarize/suggest-mode）
- **Debate.tsx** — 学科选择 + 模式选择 + AI 推荐 + Agent 预览 + 历史列表
- **DebateSession.tsx** — Agent 侧边栏 + 消息流 + 轮次分组 + 总结面板

---

## 2026-04-03 — Phase 1: 数据层 + 全新 UI

### 新增
- **OpenAlex 集成** — 拉取 26 Fields + 254 Subfields + 高引论文 + 作者
- **Zep Cloud 集成** — 学科/学者数据推送 + 语义搜索
- **全新前端** — 多页面路由（Home/Canvas/Debate/Forum）+ Layout 组件 + D3 力导图迁移 + framer-motion 动画

### Bug 修复
- Canvas.tsx PanelRightClose 未使用导致 build 失败
- 首页搜索/热门标签跳转参数未被消费
- 生成假设后 DetailPanel 不刷新
- /api/ai/hypothesis + /api/intersections/query 超集命中
- 图谱叶子节点颜色退回默认灰色
- Zep 硬依赖拖垮后端启动
- 前后端接口类型漂移
- Canvas URL 参数一次性消费
- 查询交叉为空时 UI 卡死
- Canvas 异步操作无 error catch
- ForceGraph tooltip innerHTML 注入风险
- DetailPanel 请求失败保留过期数据
- useDisciplines 加载失败无 error 状态

---

## 2026-04-03 — Agent X Lab 产品升级：学术辩论引擎 + 全新 UI + 论坛

### 产品重定义

- **Slogan**: "今天想发现点什么？" — 让学术变得有趣的交叉学科发现平台
- **产品形态**: 从全量图谱导航转为对话优先入口 + 图谱逐步生长
- **核心交互**: 用户选几个学科放几个节点，已有联系自动实线连接，未知交叉虚线闪烁标注
- **视觉风格**: Duolingo 式温暖友好感 + 学术专业底色（圆角卡片、明亮配色、微动画）

### 架构升级计划

- **AI 模型**: 从 OpenAI/Anthropic 切换为 DeepSeek（via LiteLLM）
- **Agent 记忆**: 接入 Zep Cloud（Graph RAG 检索）
- **学术数据**: 接入 OpenAlex API（4 Domain / 26 Field / 254 Subfield / 4,516 Topic）
- **侧边栏策略**: 固定展示 Field（26 个）+ 点击展开 Subfield（约 10 个/组），Topic 交给搜索/AI

### 新增功能规划

- 多 Agent 学术辩论引擎（正向探索：选学科 → Agent 辩论 → 研究方向）
- 反向发现引擎（输入问题 → 自动匹配交叉学科 → 推荐研究路径）
- 论文分步生成（提纲 → 人工调整 → 逐章扩展 → 导出）
- 内置论坛（交叉领域讨论区 + AI 辩论自动生成帖 + 用户自由发帖）
- 社区功能（热门方向 + 论文排行榜 + 发现点积分 + 活跃用户排行）

### 新增项目管理文件

- `projects/knowledge-graph/PROGRESS.md` — 开发进度追踪
- `projects/knowledge-graph/.cursor/rules/dev-rules.md` — 项目级开发规则
- `projects/knowledge-graph/ARCHITECTURE.md` — 系统架构说明

---

## 2026-04-02 — 交叉学科知识图谱项目创建

### 新增
- `projects/knowledge-graph/`：全栈 Web 应用，交叉学科知识图谱可视化平台
  - **后端**（FastAPI + PostgreSQL + Alembic + LiteLLM）
    - 数据模型：Discipline（自引用树）、Scholar、Paper、Intersection（多对多超边）、AIHypothesis
    - API：学科树 / 交叉点查询 / 图数据 / 研究空白检测 / AI 假说生成
    - 数据导入脚本：从仓库 Markdown 文件（disciplines.md / papers.md / crossroads.md）解析并导入全部学科、学者、论文和 11 个交叉节点
  - **前端**（React 18 + TypeScript + Vite + D3.js + Tailwind CSS）
    - 三栏布局：学科树面板 / D3 力导向图画板 / 交叉详情面板
    - 力导向图：节点=学科，边=交叉关系，边粗细反映交叉密度，虚线标注研究空白
    - 交互：缩放、拖拽、tooltip、多学科组合查询、AI 假说生成
  - **部署**（Docker Compose：Nginx + FastAPI + PostgreSQL）

---

## 2026-03-30 — 学科谱系标注与分类修正

### 变更
- README.md 研究方向表格"涉及学科"列：每个子学科标注上位学科门类（如 **哲学**: Philosophy of Language），附英文标准名，替换原先笼统的中文标签
- README.md 理论覆盖经典文献部分：按学科门类（Philosophy / Linguistics / Literary Studies / Rhetoric / Psychology / Sociology / Cybernetics / Computer Science / Mathematics / Electrical Engineering）重新分类全部 71+ 位学者

### 新增
- `research/disciplines.md`：独立的学科谱系文档，含学科层级树、学科 × 方向交叉矩阵、学者 × 学科归属完整索引

---

## 2026-03-30 — 仓库结构升级

### 变更
- 研究方向目录去掉数字前缀，改用语义化 slug 命名
  - `01-language-and-meaning/` → `language-and-meaning/`
  - `02-thinking-and-creativity/` → `thinking-and-creativity/`
  - `03-subjectivity-and-intentionality/` → `subjectivity-and-intentionality/`
  - `04-sociality-and-context/` → `sociality-and-context/`
  - `05-systems-and-architecture/` → `systems-and-architecture/`
  - `06-formal-foundations/` → `formal-foundations/`
- 笔记文件名简化：`classics_notes.md` → `classics.md`，`frontier_notes.md` → `frontier.md`
- `papers.md` 头部描述移入各方向 `README.md`，papers.md 仅保留论文索引
- `research/synthesis.md` 拆分为 `research/synthesis/` 目录：
  - `README.md`（总体图景 + 经典与前沿对话 + 导航）
  - `crossroads.md`（核心交叉节点）
  - `debates.md`（关键论争地图）
  - `roadmap.md`（研究路线图）
  - `concept-map.md`（概念关系图与理论线索）
- `notes/` 引入分类结构：
  - `agenda/`（按期管理课题，`research_agenda.md` → `agenda/phase-01.md`）
  - `journal/`（研究日志）
  - `ideas/`（灵感与种子）

### 新增
- 每个研究方向新增 `README.md` 作为入口（含方向概述、文件导航、开放问题）
- `projects/README.md`（项目索引与新建规范）
- `STRUCTURE.md`（仓库结构说明、命名规则、操作流程）
- 根 `README.md` 重写，反映新目录结构，链接至 `STRUCTURE.md`

---

## 2026-03-30 — Agent X Lab 品牌升级

### 变更
- 全仓库品牌更名：Ken's Lab → Agent X Lab
- 重写 README.md：从 39 行基础介绍升级为完整的 Lab 概览
  - 新增三层研究议程可视化
  - 新增各方向覆盖规模统计
  - 新增完整知识库结构说明
  - 新增经典文献（71+）和前沿研究（65+）的分类一览
- 更新 synthesis.md、research_agenda.md、CHANGELOG.md 中的 Lab 名称引用

---

## 2026-03-30 — 第二轮缺口补充：文学理论、RLHF机制、叙事身份、美学

### 新增
- 全面补充六个方向的理论缺口，新增论文索引、经典笔记和前沿笔记：
  - **01-语言与意义**：新增经典 10 部（Peirce, Bakhtin, Aristotle, Perelman & Olbrechts-Tyteca, Toulmin, Shklovsky, Jakobson, Genette, Stockwell, Tsur），前沿 12 篇（Peirce符号学与AI、心理语言学LLM对比、模型同质化/坍缩、计算修辞学）
  - **02-思维与创造力**：新增经典 3 部（Kant, Dewey, Goodman）
  - **03-主体性与意向性**：新增经典 5 部（Ricoeur, Bruner, McAdams, Allport, Goldberg），前沿 7 篇（数字孪生系列、偏好学习、认知决策模型）
  - **04-社会性与语境**：前沿 2 篇（LLM对人类表达的同质化效应、人工蜂群效应）
  - **05-系统与架构**：前沿 8 篇（Anthropic奖励劫持、谄媚放大、奖励模型过优化、BSPO、偏差发现、机械可解释性综述、稀疏自编码器）
  - **06-形式基础**：前沿 3 篇（模型坍缩Nature 2024、知识坍缩、任务依赖同质化）
- 下载新增 PDF 约 20 篇至各方向 `pdfs/` 目录
- 更新 `research/synthesis.md`：
  - 总体图景新增两段（Peirce、RLHF、叙事身份、美学、模型坍缩）
  - 新增节点 9（RLHF与语言扭曲）、10（叙事身份与个人复制）、11（陌生化与AI语言贫困）
  - 经典与前沿对话新增四个方向段落
  - 论争地图新增 3 项（模型趋同、叙事身份vs特质还原、审美判断先验vs情境）
  - 路线图新增 Q4.5（RLHF语言扭曲诊断）、Q9（个人化Agent叙事身份架构）
  - 概念关系图更新、新增线索六（语言风格的多层决定）
- 更新 `notes/research_agenda.md`：三层各新增论文条目和"新增理论资源"分析

---

## 2026-03-30 — 前沿论文笔记与跨方向综合

### 新增
- 六个方向各新增 `frontier_notes.md`，基于已下载 PDF 全文提取核心论点、原文金句与通俗解读
  - 01-语言与意义：10 篇（结构共振回路、符号接地系列、语用学与LLM系列）
  - 02-思维与创造力：5 篇（人工创造力定义、GS-3、CRPO、VLM组合创造力、集体行为）
  - 03-主体性与意向性：5 篇（含 Nagel 1974、Searle 1980 经典全文摘要 + 中文房间系列前沿）
  - 04-社会性与语境：2 篇（AI能动性的关系性分析、社会技术生态）
  - 05-系统与架构：4 篇（Agentic AI综述、自进化Agent、多智能体RL、MAS有效性与安全性）
  - 06-形式基础：6 篇（含 Turing 1936、Shannon 1948 经典全文 + ZebraLogic、推理评估前沿）
- 新增 `research/synthesis.md` 跨方向综合文档，包含：
  - 总体图景：六方向如何构成一个连贯的研究纲领
  - 8 个核心交叉节点（意义接地、具身性、创造力可计算边界、社会性与意义、Agent与心灵、控制论闭环、观察者问题、形式与自然语言鸿沟）
  - 经典与前沿的对话（每个方向）
  - 8 项跨方向关键论争地图
  - 9 个研究路线图问题（基础层→中间层→应用层）
  - 概念关系图（文本版）

---

## 2026-03-30 — 经典文献摘要

### 新增
- 六个方向各新增 `classics_notes.md`，收录未获取全文的经典文献核心思想与原文金句
  - 01-语言与意义：10 部（Frege, Wittgenstein, Austin, Grice, Searle, Kripke, Harnad, Saussure, Sperber & Wilson, Stalnaker）
  - 02-思维与创造力：7 部（Turing, Hofstadter, Boden, Koestler, Kahneman, Csikszentmihalyi, Lakoff & Johnson）
  - 03-主体性与意向性：9 部（Brentano, Dennett, Chalmers, Husserl, Heidegger, Merleau-Ponty, Dreyfus, Putnam, Fodor）
  - 04-社会性与语境：9 部经典 + 2 篇付费墙前沿论文（Goffman, Berger & Luckmann, Garfinkel, Bourdieu, Latour, Bijker et al., Haraway, Bernstein, Labov）
  - 05-系统与架构：9 部（Wiener, Ashby ×2, von Foerster, Beer, Minsky, Brooks, Simon, Newell & Simon）
  - 06-形式基础：7 部（Gödel, Church, Tarski, Shannon & Weaver, Wittgenstein Tractatus, Frege Begriffsschrift, Kripke）
- 共计 53 部经典文献的系统性摘要，含原文金句及中文翻译

---

## 2026-03-30 — 论文下载

### 新增
- 下载 33 篇论文 PDF 至各方向 `pdfs/` 目录
  - 01-语言与意义：11 篇（含 Reiter 2025 结构共振回路、符号接地系列、语用学与LLM系列）
  - 02-思维与创造力：5 篇（含 Nature 2026 集体行为、CRPO 创造力对齐）
  - 03-主体性与意向性：5 篇（含 Nagel 1974、Searle 1980 经典 + 前沿中文房间系列）
  - 04-社会性与语境：2 篇（AAAI/AIES 能动性分析、社会技术生态）
  - 05-系统与架构：4 篇（含 Agentic AI 综述、自进化Agent综述）
  - 06-形式基础：6 篇（含 Turing 1936、Shannon 1948 经典 + ZebraLogic 2025）

### 变更
- 重写 README.md，改为 Agent X Lab 正式定位陈述
- 重写全部六份 papers.md，统一为学术文风

---

## 2026-03-30 — Agent X Lab 创建

### 新建
- 项目初始化：README.md（Agent X Lab 宣言）
- 建立六大研究主题目录结构
  - `research/01-language-and-meaning/` — 语言与意义
  - `research/02-thinking-and-creativity/` — 思维与创造力
  - `research/03-subjectivity-and-intentionality/` — 主体性与意向性
  - `research/04-sociality-and-context/` — 社会性与语境
  - `research/05-systems-and-architecture/` — 系统与架构
  - `research/06-formal-foundations/` — 形式基础
- 每个主题完成论文索引（papers.md），含经典论文 + 2024-2026前沿论文
- `notes/` 和 `projects/` 目录预留
