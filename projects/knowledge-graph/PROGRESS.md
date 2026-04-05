# Agent X Lab — 开发进度

> 最后更新: 2026-04-30

## 总览

| Phase | 名称 | 状态 | 开始时间 | 完成时间 | 备注 |
|-------|------|------|----------|----------|------|
| 0 | 项目管理基础设施 | 已完成 | 2026-04-03 | 2026-04-03 | PROGRESS / rules / ARCHITECTURE |
| 1 | 数据层 + 全新 UI | 已完成 | 2026-04-03 | 2026-04-04 | OpenAlex + Zep + 前端重写 + bug 修复 |
| 2 | 多 Agent 学术辩论引擎 | 已完成 | 2026-04-04 | 2026-04-04 | 辩论核心 + 前端界面 |
| 3 | 反向发现引擎 | 已完成 | 2026-04-04 | 2026-04-04 | 研究问题 → LLM 分析 → 学科推荐 → 画布展示 |
| 4a | Zep 知识库正式接入 | 已完成 | 2026-04-30 | 2026-04-30 | 自动灌入 + 1+N 检索 + Agent 知识注入 |
| 4b | 论文分步生成 | 已完成 | 2026-04-30 | 2026-04-30 | 提纲生成 + 大纲编辑 + 逐章扩写 + Markdown 导出 |
| 4c | Agent 阵容层级化 | 已完成 | 2026-04-04 | 2026-04-04 | 每学科团队(教授+副教授) + 权重 + 随机性格 |
| 5 | 论坛 + 社区功能 | 已完成 | 2026-04-04 | 2026-04-04 | 两区制(AI/社区) + OAuth + 积分 + 排行榜 |
| 5.5 | AI 想象力实验 | 已完成 | 2026-04-04 | 2026-04-04 | 火花采集 + Agent 记忆 + 实验面板 |

---

## Phase 0: 项目管理基础设施

- [x] 创建 PROGRESS.md
- [x] 创建 .cursor/rules/ 开发规则
- [x] 创建 ARCHITECTURE.md
- [x] 更新 CHANGELOG.md
- [x] 更新 .env（添加 DeepSeek / Zep API Key）

---

## Phase 1: 数据层 + 全新 UI

### 1.1 数据模型重构
- [x] Discipline 模型新增 level / openalex_id / description / works_count
- [x] Paper 模型新增 openalex_id / doi / citation_count / published_year
- [x] Scholar 模型新增 openalex_id / orcid / affiliation / works_count / cited_by_count
- [x] Alembic 迁移 002 (batch_alter_table)

### 1.2 OpenAlex 数据拉取
- [x] backend/app/services/openalex.py
- [x] sync_taxonomy() — 拉取 26 Fields + 252 Subfields
- [x] sync_works() — 按 Subfield 拉高引论文 (已验证 subfields/1702)
- [x] sync_authors_from_works() — 从论文中提取作者
- [x] backend/app/routers/openalex.py

### 1.3 Zep Cloud 集成
- [x] backend/app/services/zep_manager.py
- [x] backend/app/routers/zep.py (push-disciplines, push-scholars, search)
- [ ] 实际数据灌入 Zep（待集成测试）

### 1.4 全新前端
- [x] 多页面路由 (react-router: Home / Canvas / Debate / Forum)
- [x] Layout 组件 (导航栏: Agent X Lab logo + 四个 tab)
- [x] 首页 ("今天想发现点什么?" + 搜索框 + 热门学科标签 + 功能卡片)
- [x] 画布页 (侧边栏学科树 + D3 力导图 + 详情面板 — 从旧版迁移)
- [x] 辩论页 (占位 — Phase 2 上线)
- [x] 论坛页 (占位 — Phase 5 上线)
- [x] framer-motion 动画
- [x] 侧边栏: Field(26) + Subfield 展开（OpenAlex 数据已连通）
- [x] 图谱: 选几个放几个 + 动态加载（2026-04-04 完成）

---

## Phase 2: 多 Agent 学术辩论引擎

### 2.1 数据模型
- [x] debates / debate_agents / debate_messages / debate_discipline 四表
- [x] Alembic 迁移 003
- [x] ORM 模型注册到 models/__init__.py

### 2.2 辩论引擎
- [x] app/services/debate_engine.py
- [x] 4 种性格 (Pioneer / Rigorous / Pragmatic / Skeptic) + Moderator
- [x] generate_agents() — 按学科和模式自动生成 Agent 阵容
- [x] run_round() — 多轮辩论编排，每 Agent 看完整历史后发言
- [x] generate_summary() — 四段式总结 (共识/分歧/开放问题/建议方向)
- [x] suggest_mode() — AI 推荐自由讨论 vs 正反辩论

### 2.3 API
- [x] app/routers/debate.py (6 个端点: create, list, get, rounds, summarize, suggest-mode)
- [x] app/schemas.py 追加辩论 schema
- [x] app/services/ai_provider.py 追加通用 chat_completion()

### 2.4 前端
- [x] Debate.tsx 重写 — 学科选择 + 模式选择 + AI 推荐 + Agent 预览 + 历史列表
- [x] DebateSession.tsx — Agent 侧边栏 + 消息流 + 轮次分组 + 总结面板
- [x] App.tsx 路由 /debate/:debateId
- [x] api/client.ts + types/index.ts 辩论类型和方法
- [x] DetailPanel 新增"发起辩论"按钮 → 跳转辩论入口

### 2.5 Bug 修复（Phase 1-2 期间）
- [x] Canvas.tsx PanelRightClose 未使用导致 build 失败
- [x] 首页搜索/热门标签跳转到 Canvas 后参数未被消费
- [x] 生成假设后 DetailPanel 不刷新
- [x] /api/ai/hypothesis + /api/intersections/query 超集命中问题
- [x] 图谱叶子节点颜色退回默认灰色
- [x] Zep 硬依赖拖垮后端启动
- [x] 前后端接口类型漂移
- [x] Canvas URL 参数一次性消费导致重复导航失效
- [x] 查询交叉为空时 UI 卡死在中间态（现自动触发假设生成）
- [x] Canvas 异步操作无 error catch（添加 toast 提示）
- [x] ForceGraph tooltip innerHTML 注入风险（改用 textContent）
- [x] DetailPanel 请求失败保留过期数据
- [x] useDisciplines 加载失败无 error 状态

---

## Phase 3: 反向发现引擎

### 3.1 后端服务
- [x] app/services/reverse_discovery.py
  - [x] discover() — 主管线：拉取学科目录 → LLM 分析 → 匹配验证 → 数据补全
  - [x] _build_discipline_catalogue() — 将叶子学科格式化为 LLM prompt
  - [x] _validate_and_filter() — 过滤 LLM 返回的无效学科 ID
  - [x] _enrich_results() — 查询 DB 补全学科详情 + 已有交叉点 + 研究空白标记
  - [x] _find_exact_intersection() — 精确匹配学科组合对应的交叉点

### 3.2 API
- [x] app/routers/discovery.py — POST /api/discover
- [x] app/schemas.py — DiscoverRequest / MatchedDiscipline / RecommendedCombo / DiscoveryResult
- [x] main.py 注册 discovery router

### 3.3 前端
- [x] types/index.ts — DiscoveryResult / MatchedDiscipline / RecommendedCombo / ComboDiscipline
- [x] api/client.ts — discover() 方法
- [x] Home.tsx — 搜索框改为调用 discover API（loading + 错误提示 + sessionStorage 传递结果）
- [x] Canvas.tsx — 顶部新增搜索栏（双入口：首页跳转 + Canvas 原地搜索）
- [x] Canvas.tsx — 发现模式（?discover=1 参数 → 读取 sessionStorage → 自动选中学科 → 右侧面板展示）
- [x] DiscoveryPanel 组件 — 展示发现结果（研究问题 / 相关学科 + 相关度 / 推荐组合 + 操作按钮）

### 3.4 Bug 修复（Phase 2 遗留）
- [x] create_debate 未校验无效 discipline id（静默丢弃 → 现 400 报错）
- [x] 图谱颜色分组算不出根学科（后端新增 root_id 字段，前端直接使用）
- [x] Debate.tsx handleSuggestMode/handleCreate 无 catch（添加 toast）
- [x] DebateSession 成功操作后不清除过期错误（try 成功分支加 setError(null)）

---

## Phase 4a: Zep 知识库正式接入

### 4a.1 zep_manager.py 扩展
- [x] push_debate_summary() — 辩论四段式总结灌入 Zep
- [x] push_hypothesis() — AI 假设灌入 Zep
- [x] retrieve_context() — 通用检索，返回格式化上下文字符串

### 4a.2 自动灌入
- [x] debate_engine.py generate_summary() 完成后 → best-effort 调 push_debate_summary()
- [x] ai.py create_hypothesis 完成后 → best-effort 调 push_hypothesis()
- [x] 所有 Zep 调用 best-effort：失败只打 warning，不阻断主流程

### 4a.3 辩论 Agent 知识注入（1+N 检索）
- [x] _retrieve_zep_contexts() — 每轮 1 次共享检索（辩论主题）+ N 次专属检索（各 Agent 学科）
- [x] _build_knowledge_message() — 格式化知识为 LLM context message
- [x] run_round() — Agent 发言前注入检索到的知识上下文

### 4a.4 Bug 修复（Phase 3 遗留）
- [x] create_debate intersection_id 校验从 issubset 改为精确匹配
- [x] DebateSession 切换 debateId 时不重置状态（加 setLoading/setDebate/setError reset）
- [x] Debate.tsx getDisciplines/getDebates 无 catch（加 toast 错误提示）

---

## Phase 4b: 论文分步生成

### 4b.1 数据模型
- [x] PaperDraft / PaperSection 模型（paper_draft.py）
- [x] Debate.paper_drafts back_populates 关系
- [x] Alembic 迁移 004
- [x] models/__init__.py 注册

### 4b.2 大纲生成
- [x] paper_generator.py — generate_outline()
  - [x] 整合辩论总结 + Zep 知识 + 相关论文（OpenAlex 数据）
  - [x] LLM 生成 5-8 章节结构化大纲
  - [x] 解析 JSON → PaperDraft + PaperSection 写入 DB

### 4b.3 逐章扩写
- [x] paper_generator.py — generate_section_content()
  - [x] 每章独立生成，注入前序章节摘要保持连贯
  - [x] 综合 Zep 知识 + DB 论文 + 辩论总结 + 用户写作指令
  - [x] 版本号自增，支持重新生成
  - [x] 全部章节完成后自动更新 draft status = completed

### 4b.4 导出
- [x] export_markdown() — 整篇论文导出为 Markdown 文本

### 4b.5 API
- [x] paper_gen.py router（6 端点）
  - [x] POST /api/papers/drafts — 创建草稿（生成大纲）
  - [x] GET /api/papers/drafts — 列表（可按 debate_id 过滤）
  - [x] GET /api/papers/drafts/:id — 详情
  - [x] PATCH /api/papers/drafts/:id — 编辑大纲（标题/章节标题/描述/写作指令/新增章节）
  - [x] POST /api/papers/drafts/:id/sections/:sid/generate — 生成单章内容
  - [x] GET /api/papers/drafts/:id/export — 导出 Markdown
- [x] schemas.py — DraftCreate / DraftOut / DraftBrief / SectionOut / SectionUpdate / DraftUpdate
- [x] main.py 注册 paper_gen router

### 4b.6 前端
- [x] types/index.ts — PaperSectionOut / DraftBrief / DraftOut / SectionUpdate / DraftUpdatePayload
- [x] api/client.ts — createDraft / listDrafts / getDraft / updateDraft / generateSection / exportDraft
- [x] DebateSession.tsx — "生成论文大纲" 按钮 + 方向输入 + 已有草稿列表
- [x] PaperEditor.tsx — 完整论文编辑页面
  - [x] 标题编辑（点击修改）
  - [x] 章节可展开/折叠卡片列表
  - [x] 章节标题双击编辑
  - [x] 章节描述 + 写作指令输入（失焦自动保存）
  - [x] 单章 AI 生成 + 重新生成
  - [x] 进度条（已完成章节 / 总章节）
  - [x] 新增章节
  - [x] Markdown 导出下载
- [x] App.tsx 路由 /paper/:draftId

---

## 数据清理 & 画布重构 (2026-04-04)

### 数据清理
- [x] 删除第一代 Markdown 导入的旧学科数据（7 根学科 + 36 子学科 = 43 条）
- [x] 删除关联的 7 个旧 intersection + 关联 join 行
- [x] 保留 OpenAlex 学科数据（26 Fields + 270 Subfields = 296 条）
- [x] research/ 目录下论文笔记和方向分析全部保留不动

### 画布"生长式"重构
- [x] 后端 graph API 改为按 discipline_ids 参数动态查询（不传 = 空图）
- [x] 前端 Canvas 不再全量加载 graph，改为根据 selectedNodes 实时拉取
- [x] 空画布引导提示（选学科 → 节点出现 → 查询交叉 → 连线出现）
- [x] 移除 useGraph hook 依赖，graph 数据由 Canvas 内部 useEffect 管理

---

## Phase 4c: Agent 阵容层级化

- [x] DebateAgent 新增 rank (professor/associate/assistant) + weight (0-100) 列
- [x] Alembic migration 006
- [x] generate_agents 重构: 用户手动指定权重 > LLM 推断 > 平均分配
- [x] 灵活团队规模: 权重 >= 40 → 2 人(教授+副教授), < 40 → 1 人(教授), 上限 8 人
- [x] Persona 随机分配 (random.shuffle), 与学科完全解耦
- [x] System prompt 区分 rank/weight: 教授有指导权, 副教授可补充或反对
- [x] 发言顺序: 第 1 轮 Professor 优先, 后续轮次交错发言
- [x] 教授 max_tokens=1500, 副教授/助理 max_tokens=1000
- [x] 前端预览: 按学科团队分组, 核心方向带星标
- [x] 前端权重设置: 折叠面板, 核心/辅助切换, 不设置则 AI 自动判断
- [x] DebateSession 侧边栏: 按学科分组 + rank 徽章

**Future (已记录)**: Agent 职能维度 (theorist/experimentalist) — 理论 vs 实验是分工而非性格, 需独立 role 维度, 待层级化稳定后实施。

---

## Phase 5: 论坛 + 社区（两区制）

### 5.1 用户系统
- [x] User 模型 (google_sub, email, display_name, avatar_url, did_address, points, role)
- [x] Google OAuth 登录 (可选依赖, 缺 google-auth 时降级不影响核心 API)
- [x] JWT 签发/验证 (PyJWT)
- [x] 前端 AuthContext + Layout 登录按钮/用户菜单
- [x] Profile 页面 (积分/角色/发帖历史占位)
- [x] Alembic migration 009

### 5.2 论坛数据模型
- [x] ForumPost (zone: ai_generated/community, post_type, status, discipline_tags JSON)
- [x] ForumComment (树状回复, comment_type: normal/claim_experiment/submit_result)
- [x] ForumVote (帖子/评论投票, 唯一约束, 翻转/撤销)
- [x] PointLog (积分变动记录)
- [x] Alembic migration 010

### 5.3 API
- [x] POST /api/auth/google, GET /api/auth/me, PATCH /api/auth/me
- [x] GET /api/forum/posts (zone/post_type/status/discipline_tag 筛选 + 排序 + 分页)
- [x] GET/POST/PATCH /api/forum/posts/{id}
- [x] GET/POST /api/forum/posts/{id}/comments (树状)
- [x] POST /api/forum/vote (帖子/评论投票)
- [x] GET /api/forum/stats, GET /api/forum/hot-tags
- [x] GET /api/points/log, GET /api/points/leaderboard

### 5.4 辩论自动生帖
- [x] forum_auto.py: 辩论总结后自动创建 AI 区帖子 (附火花列表)
- [x] 高分火花 (novelty_score >= 0.8) 额外创建置顶帖
- [x] debate_engine.py generate_summary() 末尾集成

### 5.5 积分系统
- [x] 积分表: 发帖(+10) / 评论(+3) / 被赞(+2) / 认领实验(+20) / 验证结果(+2000) / 证伪(+800) / 每日登录(+5)
- [x] 各 API 端点自动触发积分发放
- [x] 排行榜 API

### 5.6 前端
- [x] Forum.tsx: 两区 tab (What AI Found / What We Think) + 筛选 + 排序
- [x] ForumPostDetail.tsx: 帖子详情 + 树状评论 + 投票 + 认领实验
- [x] 侧栏: 积分排行榜 + 论坛统计 + 热门标签
- [x] 发帖弹窗 (类型选择 + Markdown 内容)

### 5.7 Bug 修复
- [x] google-auth 硬依赖改为可选降级 (和 Zep 同模式)
- [x] reverse_discovery.py 对重复 discipline_ids 去重
- [x] ai.py + debate.py 对重复 discipline_ids 去重
- [x] forum.py discipline_tag 过滤改为精确 JSON token 匹配
- [x] Profile.tsx 引用不存在的 did_provider 字段 (TS 构建失败)

---

## Phase 5.5: AI 想象力实验

> 核心目标：把 Agent X Lab 变成一个可测量、可分析的"AI 想象力"实验平台。

### Step 1: 火花采集 + 存储

- [x] Spark 数据模型 + Alembic migration (007)
  - 字段: content, source_discipline_id, target_discipline_id, novelty_type (analogy/transfer/fusion/inversion), novelty_score (0-1), debate_id, message_id, agent_id, verification_status, reasoning
- [x] spark_extractor 服务: 每个 Agent 发言后用 LLM 提取跨领域火花 + 评估新颖度
- [x] run_round 集成火花提取: Agent 发言后 best-effort 调用 spark_extractor
- [x] 基础 API: GET /api/sparks (列表+过滤) + GET /api/sparks/stats (聚合统计)
- [x] 前端类型 + API client (Spark, SparkStats, listSparks, getSparkStats)

### Step 2: Agent 持久记忆

- [x] agent_memory 服务: Zep 按 Agent 身份分区 (user_id = `agent-{discipline_id}-{rank}`)
  - 三层认知架构: [FACT] / [ARGUMENT] / [SPARK] 前缀标签
  - push_agent_cognition / retrieve_agent_cognition / format_agent_cognition_for_prompt
- [x] cognition_distiller 服务: 辩论总结后自动对比已有认知 + 新信息, 输出合并后认知
  - 事实层/论证层: LLM 重写, 覆盖门槛 > 写入门槛
  - 火花层: _merge_sparks 永不删条目, 只追加新的
  - generate_summary 完成后 best-effort 调用 distill_all_agents
- [x] generate_agents 时 _load_agent_cognition 加载历史认知注入 system prompt

### Step 3: 实验面板

- [x] DebateExperimentMeta 模型 + Alembic migration (008)
  - 记录: 学科数/Agent 数/轮次/消息数/性格分布/职级分布/权重分布/火花数/平均新颖度
- [x] experiment_tracker 服务: 辩论总结后自动采集实验元数据
- [x] API: GET /api/sparks/experiments (列表) + GET /api/sparks/experiments/{debate_id} (单场)
- [x] 辩论结束页 SparkPanel 组件: 火花列表 + 统计摘要 + 类型分布
- [x] 前端类型 + API client (ExperimentMeta, getExperimentMeta, listExperiments)
- [ ] 全局统计页: 跨辩论趋势分析, 条件对比, Agent 学习曲线 (Future)

---

---

## 2026-03-30 更新

### Bug Fix: Spark 语言不随辩论语言切换

- `spark_extractor.py`: `EXTRACTION_PROMPT` 拆分为中英双版本 `EXTRACTION_PROMPTS`
- `extract_sparks_from_message` 新增 `language` 参数
- `debate_engine.py`: 传 `lang` 给 spark extractor，中文辩论现在生成中文火花

### 新功能: 论文生成对话式重设计

**之前**: 辩论完成 -> 手动输入研究方向 -> 跳转 PaperEditor -> 逐章手动生成
**现在**: 辩论完成 -> AI 自动推荐方向 -> 对话式修改大纲 -> 一键全文生成 (SSE 进度)

后端新增:
- `POST /api/papers/drafts/suggest-directions` — AI 基于辩论推荐 2-3 个研究方向
- `POST /api/papers/drafts/chat-refine` — 自然语言修改大纲
- `POST /api/papers/drafts/{id}/generate-all` — SSE 逐章生成，实时推送进度
- `paper_generator.py` 新增: `suggest_directions()`, `refine_outline_via_chat()`, `generate_all_sections()`

前端:
- 新组件 `PaperChat` — 对话流 + 方向卡片 + 可编辑大纲 + 写作进度条
- `DebateSession` 辩论完成后展开 PaperChat 面板（替代旧的文本框输入）
- `PaperEditor` 全面 Brutalist 风格化
- i18n: `paperChat` 命名空间中英双语完整

### 修复: schemas.py 缺失定义

补全之前遗留的缺失 schema:
- `DisciplineCreate`, `DraftBrief`, `DraftCreate`, `DraftOut`, `DraftUpdate`, `SectionOut`
- `SparkOut`, `ExperimentMetaOut`
- `ForumPostCreate`, `ForumPostUpdate`, `ForumPostOut`, `ForumCommentCreate`, `ForumCommentOut`, `ForumAuthor`, `VoteRequest`, `VoteResponse`
- `PointLogOut`, `LeaderboardEntry`

后端从 46 路由恢复到 61 路由（forum + points 重新上线）

---

## 阻塞点 & 待决事项

_暂无_
