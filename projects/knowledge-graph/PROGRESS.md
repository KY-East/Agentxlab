# Agent X Lab — 开发进度

> 最后更新: 2026-03-30

## 产品完成度评估

**目标: 120 / 100** — 功能代码完成度约 50%，生产就绪度约 35%

### 已完成 (~50 分)

| 得分 | 模块 | 说明 |
|------|------|------|
| 8 | 数据层 (OpenAlex) | 26 fields / 252 subfields / 4516 topics + 论文关联 |
| 8 | 知识图谱画布 | 学科树 + 力导图 + 连线交互 + EdgeDetailPanel + AI 对话 |
| 7 | 多 Agent 辩论引擎 | 4 性格 + 层级团队 + Zep 记忆 + 火花采集 |
| 5 | 反向发现引擎 | 研究问题 → LLM → 学科推荐 → 画布 |
| 5 | 论文生成 | 对话式方向推荐 + 大纲 + SSE 逐章扩写 |
| 6 | 社区论坛 | 双区 + 实验验证 + 积分 + 翻译 |
| 4 | 认证 + 订阅 + 支付 | Google + 邮箱 + Stripe + Crypto + Token 配额 |
| 3 | 安全修复 + i18n | 权限链路 + 中英双语 |
| 4 | UI/UX (Brutalist) | 基本风格统一，但缺 loading/empty/error 状态设计 |

### 缺失部分 — 达到 100 分需要 (~50 分)

| 优先级 | 模块 | 预估分值 | 说明 |
|--------|------|----------|------|
| P0 | DB 迁移补全 | 3 | Subscription/PaymentRecord/TranslationCache/User 字段无 migration |
| P0 | .env.example 完善 | 1 | 缺 20+ 配置项，新环境无法启动 |
| P0 | 核心路径测试 | 8 | 前后端测试 = 0，认证/支付/辩论/论坛需覆盖 |
| P0 | Stripe 实际接入 | 2 | Dashboard 配置 + webhook + 真实 key |
| P1 | 全局错误处理 | 4 | Error Boundary + loading skeleton + empty state + SSE 重连 |
| P1 | 前端代码清理 | 2 | 死代码 hook + 硬编码英文 + i18n 补全 |
| P1 | 全局统计页 | 8 | 跨辩论趋势 + 条件对比 + Agent 学习曲线 — 验证核心假说 |
| P1 | Zep 集成测试 | 3 | 代码全通但从未真实环境验证 |
| P1 | 管理后台 | 5 | 用户/支付/帖子/辩论管理，目前靠直接打 API |
| P2 | 部署流水线 | 4 | CI/CD + Docker 完善 + 一键部署 |
| P2 | SEO / OG / PWA | 2 | 元标签 + 社交分享卡 + 离线支持 |
| P2 | 监控 + 日志 | 3 | APM + 结构化日志 + 异常告警 |
| P2 | 文档站 | 2 | API 文档 + 用户指南 + 开发者文档 |
| P2 | 性能优化 | 3 | 懒加载 + 虚拟列表 + 图谱大数据渲染 + 后端缓存 |

### 超出预期 — 冲 120 分 (~20 分)

| 模块 | 预估分值 | 说明 |
|------|----------|------|
| Agent 人格进化系统 | 5 | Agent 跨辩论积累经验，形成独特学术人格，可被社区评价 |
| 实时协作辩论 | 4 | WebSocket 多人同时观看/参与辩论，弹幕式评论 |
| 知识图谱 3D 可视化 | 3 | Three.js 沉浸式图谱，VR-ready |
| AI 创造力量化仪表盘 | 5 | 项目核心假说的可视化证明——AI 跨学科碰撞的创造力指标体系 |
| 开放 API + 插件系统 | 3 | 第三方接入，让其他研究者基于平台做实验 |

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
| 6 | 订阅 + Token 配额 + 支付 | 已完成 | 2026-03-30 | 2026-03-30 | Free/Pro/Lifetime + Stripe + Crypto + 配额计量 |
| 6.1 | 安全修复 | 已完成 | 2026-03-30 | 2026-03-30 | 邮箱验证权限统一 + 论坛状态保护 + 支付安全 |
| 6.2 | 代码归档 | 已完成 | 2026-03-30 | 2026-03-30 | 早期研究文档归档到 archive/early-research 分支 |
| 7 | 工程基础设施 | 未开始 | — | — | DB 迁移补全 + .env + 测试 + 错误处理 |
| 8 | 全局统计 + 管理后台 | 未开始 | — | — | AI 创造力仪表盘 + 后台管理 |
| 9 | 部署 + 运维 | 未开始 | — | — | CI/CD + 监控 + 文档 |
| 10 | 超预期功能 | 未开始 | — | — | Agent 进化 + 实时协作 + 3D 图谱 |

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

## 2026-03-30 更新 (续) — OpenAlex Topics 迁移 & 学科树重构

### OpenAlex Topics (depth=2) 整合

- [x] `fetch_openalex_topics.py` — 从 OpenAlex API 拉取 4516 个 topics，挂到对应 subfield 下
- [x] `openalex_taxonomy.json` 新增 topics 层 (field → subfield → topic 三层体系)
- [x] `disciplines.py` 写入 DB: 26 fields / 252 subfields / 4516 topics，各带 `openalex_id`
- [x] `fetch_openalex_topics.py` 幂等修复 — 重跑前先清空 subfield 已有 children，防止重复追加
- [x] `paper_discipline` 标签同步 — 4516 个 topic 全部有论文关联

### 学科树前端重构

- [x] `DisciplineTree` 只展示两层 (field → subfield)，不再显示 topic 名称（避免信息过载）
- [x] 学科树默认折叠
- [x] 智能搜索 + 发光高亮 (search + glowing)
- [x] 用户自定义学科支持（任意层级添加，视觉区分，绑定用户）

### 旧种子数据修复

- [x] `import_from_markdown.py` 新增 `_NAME_ALIASES` 映射表 — 旧 scholar/intersection 名称到 OpenAlex 官方 taxonomy 的模糊匹配
- [x] `_build_disc_resolver(db)` — 别名优先 + 精确匹配 fallback
- [x] `insert_scholars` / `insert_intersections` 使用 resolver + 去重，修复 66/66 scholars 和 143/147 intersections 的学科关联

### 画布入口优化

- [x] 从 field 入口进画布时，按 `works_count` 降序排列 subfield，取前 15 个（之前是随机 8 个）

---

## 2026-03-30 更新 (续) — 图谱交互 & 社区集成

### EdgeDetailPanel — 连线详情面板

- [x] 新组件 `EdgeDetailPanel` — 点击图谱连线展示 topic 级交叉明细
- [x] 显示两个节点之间的共享论文数 + topic 交叉对列表
- [x] 操作按钮：辩论、探索
- [x] 内置对话式 AI 聊天区（可调大小）
- [x] `buildContextPrefix` — 自动注入当前交叉学科上下文到 AI 对话首条消息

### 后端 API 新增

- [x] `GET /api/graph/edge-detail` — topic 级交叉明细查询
- [x] `POST /api/ai/edge-chat` — 连线上下文 AI 对话
- [x] `POST /api/ai/canvas-chat` — 画布上下文 AI 对话（支持无选中学科时的自由探索）
- [x] `POST /api/debates/{id}/share-to-forum` — 分享辩论结果到论坛
- [x] `POST /api/debates/{id}/sparks/{spark_id}/request-experiment` — 从火花创建实验请求帖

### Schema 新增

- [x] `EdgeChatRequest`, `CanvasChatRequest`, `TopicCrossPair`, `EdgeDetail`

### DetailPanel 对话式增强

- [x] 支持无 intersection 时通过 `canvasChat` 与 AI 对话
- [x] 支持无选中学科时的自由探索模式（AI 推荐学科方向）
- [x] Placeholder 更新为引导性提示："描述你的研究方向，或输入指令如「加上XX」「去掉XX」「发起辩论」"

### 社区集成

- [x] `DebateSession` 新增"分享到社区"按钮 + "查看帖子"跳转
- [x] `SparkBlock` 新增"请求实验"按钮
- [x] `forum_auto.py` 辩论完成自动创建帖子逻辑

### AI 上下文修复

- [x] `ai_provider.py` `chat_hypothesis` 重构 — 首轮对话将 context + user_message 合并为单条消息，避免 AI 忽略用户问题
- [x] `DetailPanel` / `EdgeDetailPanel` chatHistory 管理修复 — 防止首条消息 history 非空导致上下文丢失

---

## 2026-03-30 更新 (续) — System Prompt & 指令匹配优化

### AI System Prompt 重写

- [x] `EXPLORE_SYSTEM_PROMPTS` 中英双版本重写：
  - 用户选定方向后立刻收敛，输出 hypothesis，不再无限建议替代方案
  - suggestions 改为简短操作标签（每条不超 15 字），不再是长篇分析
  - 明确识别"辩论/开始/就做这个/进入辩论"等信号词为方向已定

### 指令匹配放宽

- [x] `DetailPanel` 辩论指令匹配从精确等于 `辩论` 扩展为包含匹配：`进入辩论`、`去辩论`、`辩论一下` 等均可触发

### 清理

- [x] 移除 `ai_provider.py` 中的临时 debug 日志

---

## 2026-03-30 更新 (续) — 图谱数据层 Bug 修复

### Bug Fix: 父层 intersection 投影错误 (高优先级)

**问题**: `build_graph` 中父层 intersection（关联 subfield/field 级 discipline）被投影时，对每个成员只 `min(candidates)` 挑一个 topic 做代表。导致 subfield 级交叉被画成两个随机 topic 的连线，语义完全错误。

**修复**: 每个 intersection 成员映射到画布上**所有匹配的节点** (`member_groups`)，在不同成员组之间做 cross-join 画线。

### Bug Fix: edge-detail 面板假设节点是 subfield (中优先级)

**问题**: `get_edge_detail` 硬编码查 `parent_id == a, depth == 2` 子节点。当 a/b 本身是 topic (depth=2) 时查不到子节点，面板永远显示"无 topic 级明细"。

**修复**: 新增 `_collect_topics` 函数 — 无 depth=2 子节点的节点返回自身。两个 topic 之间直接查共享论文数。仅 subfield 及以上才展开子节点做交叉查询。

---

## 2026-03-30 更新 (续) — 流程闭环 & 社区翻译

### DebateSession <-> Forum 联动

- [x] DebateSession 加载时自动检查该辩论是否已有论坛帖子 (`debate_id` 过滤)，如有则直接显示 "VIEW POST" 按钮
- [x] 后端 `list_posts` 新增 `debate_id` 查询参数
- [x] 前端 `api.listForumPosts` 新增 `debate_id` 参数支持

### Profile — 我的辩论

- [x] `Debate` model 新增 `created_by` 字段 (`ForeignKey users.id`)
- [x] `create_debate` 端点记录创建者 `user.id`
- [x] `list_debates` 新增 `created_by` 过滤参数
- [x] Profile 页面新增 "MY DEBATES" tab，展示用户创建的辩论列表（含状态高亮）
- [x] Stats 行从 3 列扩展为 4 列，增加辩论计数
- [x] 前端 `api.getDebates` 改为接收 `{ status?, created_by? }` 参数对象

### 论坛一键翻译（Twitter 风格）

- [x] 新增 `TranslationCache` 数据模型：按 `(content_type, content_id, field, target_lang)` 唯一索引，缓存翻译结果
- [x] 新增 `POST /api/forum/translate` 端点：AI 翻译 + 数据库缓存，首次调用走 LLM，后续秒返回
- [x] `ForumPostDetail` 帖子正文下方添加 "翻译帖子" 按钮，点击后在虚线框中内联展示翻译结果（标题 + 正文）
- [x] `CommentTree` 每条评论添加 "翻译" 按钮，点击后在评论下方内联展示翻译
- [x] 翻译方向根据当前 UI 语言自动判断（中文界面 → 翻译到英文；英文界面 → 翻译到中文）
- [x] 再次点击切换回原文（toggle 行为）
- [x] i18n 新增 `translatePost`, `translate`, `translating`, `showOriginal` 翻译键

---

## 2026-03-30 更新 (续) — 双轨登录系统

### 邮箱 + 密码注册/登录

- [x] `User` model 新增 `password_hash`、`email_verified`、`verify_token`、`reset_token`、`reset_token_exp` 字段
- [x] `google_sub` 改为 `nullable`（邮箱注册用户无 Google 账号）
- [x] SQLite `users` 表重建（移除 `google_sub NOT NULL` 约束）
- [x] `POST /api/auth/register`：邮箱 + 密码 + 昵称注册，自动发送验证邮件
- [x] `POST /api/auth/login`：邮箱 + 密码登录
- [x] `GET /api/auth/verify-email?token=`：邮箱验证
- [x] `POST /api/auth/resend-verification`：重新发送验证邮件
- [x] `POST /api/auth/forgot-password`：发送密码重置链接
- [x] `POST /api/auth/reset-password`：重置密码
- [x] Google OAuth 登录兼容：如已有邮箱账号，自动关联 Google 身份
- [x] SMTP 配置支持（`.env` 配置 `SMTP_HOST/PORT/USER/PASSWORD/FROM`）
- [x] `bcrypt` 密码加密，`aiosmtplib` 异步邮件发送

### 前端 AuthModal

- [x] 新建 `AuthModal.tsx` 组件：弹窗式登录/注册/忘记密码三合一界面
- [x] 登录 tab：邮箱 + 密码输入 + Google OAuth 按钮
- [x] 注册 tab：邮箱 + 密码 + 昵称 + Google OAuth
- [x] 忘记密码 tab：输入邮箱发送重置链接
- [x] 密码显示/隐藏切换
- [x] 表单验证（邮箱格式、密码长度 >= 8）
- [x] Brutalist/Lab 风格设计
- [x] `AuthContext` 更新：新增 `setAuthData`、`showAuthModal`、`setShowAuthModal`
- [x] Layout 头部：未登录时显示 "SIGN IN" 按钮（取代内嵌 GoogleLogin 组件）
- [x] 所有需要登录的操作（发帖、投票、评论、分享）改为弹出 AuthModal（取代 alert）
- [x] 未验证邮箱时顶部显示黄色 banner 提示
- [x] 新增 `/verify-email` 和 `/reset-password` 页面

### i18n

- [x] 新增 `auth.*` 完整翻译键（中英双语）
- [x] 新增 `nav.signIn` 翻译键

---

## 2026-03-30 更新 (续) — 订阅 + Token 配额 + 支付系统

### 数据模型

- [x] 新增 `Subscription` 模型：plan / status / token 配额 / Stripe 字段 / crypto 引用 / 首选模型
- [x] 新增 `PaymentRecord` 模型：金额 / 币种 / 支付方式 / 状态 / 关联计划
- [x] 新增 `plan_config.py`：三层计划配置（Free 50K / Pro 500K / Lifetime 300K tokens）
- [x] `config.py` 新增 Stripe + Crypto 配置项
- [x] `requirements.txt` 新增 `stripe>=8.0.0`

### 后端 API

- [x] `GET /api/subscription/plans` — 公开计划列表
- [x] `GET /api/subscription/me` — 当前用户订阅状态 + token 用量
- [x] `PATCH /api/subscription/model` — 切换首选 AI 模型
- [x] `GET /api/subscription/usage` — 详细 token 使用 + 支付历史
- [x] `POST /api/payment/stripe/checkout` — 创建 Stripe Checkout Session（Pro 月费 / Lifetime 买断）
- [x] `POST /api/payment/stripe/portal` — Stripe Customer Portal（管理/取消订阅）
- [x] `POST /api/payment/stripe/webhook` — Stripe webhook 回调（checkout.completed / invoice.paid / subscription 变更）
- [x] `POST /api/payment/crypto/request` — 请求加密货币支付（返回钱包地址 + 金额 + memo）
- [x] `POST /api/payment/crypto/submit-tx` — 用户提交 tx hash
- [x] `POST /api/payment/crypto/confirm` — 管理员确认到账激活订阅

### Token 配额计量

- [x] `token_quota.py` 服务：配额检查 / 消耗记录 / 按需月度重置
- [x] `ai_provider.py` 的 `chat_completion` / `generate_hypothesis` / `chat_hypothesis` 全部接入 `user_id` + `db` 参数
- [x] 调用前检查额度，超额返回 429；调用后从 LiteLLM response 读取 `usage.total_tokens` 累加
- [x] 模型访问控制：验证请求模型在 `allowed_models` 列表中
- [x] 所有 AI 端点（chat-hypothesis / edge-chat / canvas-chat）传递用户上下文进行计量

### 前端

- [x] `PricingModal` 组件：三列价格卡片 + Stripe 重定向 + 加密钱包地址显示 / tx hash 提交
- [x] `ModelSelector` 组件：轻量模型下拉，集成到 DetailPanel / EdgeDetailPanel / DebateSession
- [x] `QuotaIndicator` 组件：低配额 header 徽章 + 429 全局升级提示条
- [x] `SubscriptionContext`：全局订阅状态管理 + 429 事件监听自动弹出升级提示
- [x] Profile 页新增订阅卡片（计划 / 状态 / token 进度条 / 重置日期 / 升级按钮）
- [x] Profile 页新增模型选择器（仅 allowed_models > 1 时显示）
- [x] API client 新增全部订阅/支付方法 + 429 错误全局事件分发
- [x] TypeScript 类型：`PlanInfo` / `SubscriptionInfo` / `UsageInfo`
- [x] i18n 新增 `pricing.*` + `subscription.*` 完整中英翻译

---

## 2026-03-30 更新 (续) — 安全修复

### 邮箱验证权限统一

- [x] 新增 `get_verified_user` 依赖：在 `get_current_user` 基础上检查 `email_verified=True`，未验证返回 403
- [x] 论坛写操作（发帖 / 改帖 / 删帖 / 评论 / 投票）切换到 `get_verified_user`
- [x] 支付操作（Stripe checkout / portal / crypto request / submit-tx）切换到 `get_verified_user`
- [x] 辩论社区联动（share-to-forum / request-experiment）切换到 `get_verified_user`
- [x] 个人资料修改（PATCH /me）切换到 `get_verified_user`
- [x] 保持 `get_current_user`：GET /me、resend-verification、GET 订阅信息、积分查询、admin 操作

### 论坛状态保护

- [x] `PATCH /posts/{id}` 的 `status` 字段只允许 moderator / admin 修改，普通作者只能改 title / content
- [x] `claim_experiment` / `submit_result` 评论校验 `post_type` 必须为 `experiment_request` 或 `experiment_result`
- [x] 前端认领实验下拉从 `post.zone === "ai_generated"` 改为按 `post.post_type` 过滤

### 支付安全

- [x] `confirm_crypto_payment` 移除 `body.user_id`，改用 `record.user_id` 激活订阅
- [x] 新增幂等检查：已确认的支付不可重复确认
- [x] Stripe 订阅取消后清空 `stripe_subscription_id`

### 前端修复

- [x] `VerifyEmail.tsx`：验证成功后调用 `refreshUser()` 同步 AuthContext，banner 立即消失
- [x] `AuthModal.tsx`：Google 登录添加 `.catch()` + `onError` 回调，失败时显示错误提示
- [x] `Forum.tsx`：从 URL searchParams 初始化 `tagFilter` + `statusFilter`，深链筛选生效

---

## Phase 7: 工程基础设施 (未开始)

### 7.1 数据库迁移补全
- [ ] Alembic migration: `subscriptions` + `payment_records` 表
- [ ] Alembic migration: `translation_cache` 表
- [ ] Alembic migration: `users` 表新增 `password_hash` / `email_verified` / `verify_token` / `reset_token` / `reset_token_exp` 列
- [ ] `models/__init__.py` 补全 `Subscription` / `PaymentRecord` 导出
- [ ] 验证全新数据库从 `alembic upgrade head` 到可用

### 7.2 环境配置
- [ ] `.env.example` 补全所有配置项（JWT / Google OAuth / Stripe / SMTP / Crypto / Zep / DeepSeek）
- [ ] Stripe Dashboard 配置 Product + Price + Webhook
- [ ] Docker Compose 验证一键启动

### 7.3 测试
- [ ] 后端: pytest + httpx 测试框架搭建
- [ ] 后端: 认证流测试（注册 / 登录 / 验证 / 重置）
- [ ] 后端: 论坛 CRUD + 状态流转测试
- [ ] 后端: 辩论创建 + 轮次 + 总结测试
- [ ] 后端: 支付流测试（Stripe webhook / Crypto 确认）
- [ ] 后端: Token 配额检查 + 月度重置测试
- [ ] 前端: Vitest + RTL 测试框架搭建
- [ ] 前端: AuthModal 交互测试
- [ ] 前端: Canvas 学科选择 + 图谱加载测试
- [ ] 前端: Forum 发帖 / 投票 / 翻译流程测试

### 7.4 全局错误处理 + UX 完善
- [ ] React Error Boundary 全局兜底
- [ ] Loading skeleton（画布 / 论坛 / 辩论列表）
- [ ] Empty state 设计（无辩论 / 无帖子 / 无积分）
- [ ] SSE 断线重连机制
- [ ] 后端 rate limiting（非 token quota 的通用限流）
- [ ] Toast / notification 系统统一

### 7.5 代码清理
- [ ] 删除死代码: `useDebate.ts` / `useGraph.ts`
- [ ] `DebateSession` persona/rank/novelty 硬编码英文 → i18n
- [ ] Lazy route fallback → `t("common.loading")`
- [ ] 补全缺失 i18n key（verify-email / reset-password 页面）
- [ ] `subscription.py` 移除 `if False` 死分支
- [ ] `requirements.txt` 明确列出 `PyJWT` / `google-auth`（可选依赖文档化）

---

## Phase 8: 全局统计 + 管理后台 (未开始)

### 8.1 AI 创造力量化仪表盘（核心假说验证）
- [ ] 跨辩论火花趋势分析（时间线 + 学科热力图）
- [ ] 条件对比实验（学科数 / Agent 数 / 轮次 vs 火花质量）
- [ ] Agent 学习曲线（同一 Agent 跨辩论的认知深度变化）
- [ ] 创造力指标体系定义（新颖度 / 跨域度 / 可验证度 / 被引用度）
- [ ] 可视化 Dashboard 页面（图表 + 可下载数据）

### 8.2 管理后台
- [ ] 用户管理（列表 / 封禁 / 角色修改）
- [ ] 支付管理（Crypto 确认 / 退款 / 订阅状态）
- [ ] 帖子管理（审核 / 删除 / 置顶）
- [ ] 辩论管理（查看 / 删除 / 数据导出）
- [ ] 系统配置（AI 模型参数 / 积分规则 / 计划价格动态调整）

### 8.3 Zep 集成验证
- [ ] 真实环境数据灌入
- [ ] Agent 记忆召回质量评估
- [ ] 知识图谱与 Zep 双向同步

---

## Phase 9: 部署 + 运维 (未开始)

- [ ] GitHub Actions CI/CD（lint + test + build + deploy）
- [ ] Docker Compose 生产配置（Nginx + SSL + Postgres）
- [ ] 结构化日志（Python logging → JSON）
- [ ] APM / 异常监控（Sentry 或类似）
- [ ] 自动备份策略（DB + 上传文件）
- [ ] SEO / OG Meta / 社交分享卡
- [ ] API 文档（FastAPI 自带 /docs 之外的用户文档）
- [ ] 开发者指南 + 贡献指南

---

## Phase 10: 超预期功能 — 冲 120 分 (未开始)

### 10.1 Agent 人格进化系统
- [ ] Agent 跨辩论积累经验，形成独特学术人格档案
- [ ] Agent 成长可视化（知识广度 / 深度 / 创造力雷达图）
- [ ] 社区可以对 Agent 评价、点赞、"收藏"特定 Agent
- [ ] Agent 之间形成"学术关系网"（频繁合作 / 观点冲突记录）

### 10.2 实时协作辩论
- [ ] WebSocket 多人同时观看辩论进行
- [ ] 观众可以实时投票支持某 Agent 的观点
- [ ] 弹幕式评论 / 提问（AI 可以回应观众问题）
- [ ] "辩论直播"模式 vs "回放"模式

### 10.3 知识图谱 3D 可视化
- [ ] Three.js / React Three Fiber 沉浸式图谱
- [ ] 节点按维度分层（field → subfield → topic 三层球体）
- [ ] 飞行穿梭交互（点击节点"进入"该学科空间）

### 10.4 开放 API + 插件系统
- [ ] 公开 REST API（带 API Key 认证）
- [ ] 第三方研究者可基于平台数据做实验
- [ ] 插件系统：自定义 Agent 性格 / 评估指标 / 数据源

---

## 阻塞点 & 已知问题

- [ ] 画布从 field 入口进入时 topic 选取数量（15 个）仍可能偏少（需权衡性能和图谱可读性）
- [ ] `EdgeDetailPanel` 中 `isZh` 硬编码判断未走 i18n 标准流程
- [ ] Alembic migration 与 ORM 模型不同步（高优先级，影响新环境部署）
- [ ] `.env.example` 与 `config.py` 严重脱节（新开发者无法启动）
