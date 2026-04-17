# Next — 跨 agent 行动板

**这是唯一的"下一步做什么"真相源。** 所有 agent（claude-code / cursor / codex / ken）开工前必读这个文件。做完一项 → 从这里删除 → 追加到 `notes/journal/YYYY-MM.md`。新任务浮现 → 加到这里，不要藏在 research note 正文里。

**owner 标记**：`@cc` = claude-code，`@cursor` = cursor，`@codex` = codex，`@ken` = 只有 Ken 能做（决策 / 打分 / 外部判断）

**优先级**：P0 必须先做（blocker）；P1 本周内；P2 本月内；P3 记一笔以后做

**最后更新**：2026-04-17 凌晨 by cc（新分工生效 + Lucas 量化闭环 + 文件合并整合）

**总导航**：先读 `PROJECT.md` 了解项目全貌 + §6 角色分工，再回本文件找 owner 任务。

**新分工**（Ken 2026-04-17 拍板，详见 `PROJECT.md` §6）：
- `@cc`：战略规划 / PRD / 任务分工 / 逻辑闭环 / UX 审核。不直接写业务代码。
- `@cursor`：所有业务代码开发。接 cc 的 PRD + 本文件任务清单 → 实现。
- `@codex`：code review / 代码质量审核。
- `@ken`：战略终审 / 产品终审 / 外部决策 / 关键 UX 拍板。

---

## 📌 KPAX 定位硬规则（Ken 2026-04-15 拍板，2026-04-17 晚 Ken 修订去二极管化）

1. **承诺 = "把这个问题帮你想透"**（深度 / 正确性 / 全面性）。**正面回答问题是基础**（用户问 A/B 就先答 A 或 B）；**给出没想到的角度是锦上添花加分**。两者并存，不是排他关系。
2. **当前 spec 涉及 5 种题型**（是否 / 概率 / 选择 / 策略 / 评估）。它们之间的包含 / 并列 / 正交关系**尚未完全拆清**，是一个开放问题。未来可能合并 / 拆分 / 新增。
3. **当前不绑定某个垂直领域**（金融 / 医疗 / 教育等），KPAX 是**通用决策工具**。未来某个垂直验证效果好可以针对性专攻，不是排除。
4. **代币是主要付费机制**（分享赚 / 消费用 / dex 或合约买）。**不排斥**传统订阅 / 传统注册并存。钱包是身份方式**之一**。
5. **成功判据 = 10 个朋友 7 个说"有帮助"**（v0 测试阶段）。
6. **KPAX 和 AXL Day 1 走 HTTP**，代码 / DB / 部署 / 生命周期全分开。**禁止 monorepo import**——这条明确硬规则。

---

## 🔥 P0 —— 阻塞态，先做这些

**以下任务按 Ken 2026-04-17 新分工 re-owner。cc 不再直接写代码，归 cursor；代码完成后自动挂 codex review。**

### `@cursor` meta_01 rubric v0.1 独立审（出 v0.1-reviewed）
- [ ] 读 `experiments/emergence_decomposition/results/dry_run_20260416_165636/pilot_judge_rubric_v0.1.md`
- [ ] 独立审视，识别 AXL 自偏置风险（rubric 是 AXL 自己生成的，有 self-preference bias）
- [ ] 修订或质疑：(a) 8 个维度是否覆盖完整 / (b) 评分 anchor 是否区分度够 / (c) hybrid 合成规则是否合理 / (d) 偏差鲁棒性校验层是否必要 / (e) 是否漏掉什么没有人类 reviewer 介入却应该介入的点
- [ ] 输出 `pilot_judge_rubric_v0.1-reviewed.md` 在同目录
- [ ] `@codex` 审 v0.1-reviewed 的修订是否合理（meta-review）

### `@cursor` 修 5 处 KPAX monorepo 硬规则违反（走路 1：改 HTTP）
- [ ] `kpax/backend/kpax_svc/services/question_parser.py`：去掉 `from app.services.ai_provider`，改为通过 `axl_client.py` 走 HTTP 或独立接 LLM SDK
- [ ] `kpax/backend/kpax_svc/services/expert_builder.py`：同上处理
- [ ] `kpax/backend/kpax_svc/services/report_generator.py`：同上处理
- [ ] `kpax/backend/kpax_svc/routers/analyze.py`（legacy）：评估是重写还是弃用（可能被 `v1_analyze.py` 替代）
- [ ] `kpax/backend/kpax_svc/routers/report.py`（legacy）：同上评估
- [ ] 每改一个文件后跑 smoke test 确保无 regression
- [ ] `@codex` review 每个 PR
- 依据：`notes/journal/2026-04.md` 2026-04-16 深夜 KPAX survey + `PROJECT.md` §5.1 KPAX 硬规则 #6

### `@cursor` 实现 judge.py 给已有 20+ 场 baseline 打分（Lucas 量化闭环 A 步）
- [ ] 实现 `experiments/emergence_decomposition/judge.py`，读 raw transcript JSON，调用独立强模型（GPT-5 或 Gemini 2.x，spec §4.1 指定），按 `pilot_judge_rubric_v0.1-reviewed.md` 给每场的 4 段 moderator summary 打分
- [ ] 输入范围：3 场 mini run + 15 场 scaleup + 5 场 supplement + 1 场 meta_01 = 24 场
- [ ] 输出：`experiments/emergence_decomposition/results/<dir>/judge_scores.json`，每场含 4 段各 5 维 + 总分 + 偏差鲁棒性标记
- [ ] 估算成本：24 场 × 约 $0.5 per judge ≈ $12
- [ ] 输出汇总 `baseline_scored_pool_v0.md`：24 场得分分布 + 发现的 pattern
- [ ] `@codex` review judge.py 代码
- [ ] `@ken` review 最终 scored pool，给 2-3 场样本做人工锚点评分校准 judge
- 依据：`notes/research.md#quantification-gap` A 步骤 + `pilot_judge_rubric_v0.1.md`

### `@cursor` Checkpoint 1 pilot 实现（上面三个前置完成后启动）
- [ ] 前置条件：monorepo 修完 + rubric v0.1-reviewed + judge.py 实现 + 24 场 baseline scored
- [ ] 在 runner.py 加 group 参数支持 A 组（去 discipline label 的 baseline）
- [ ] 启动 pilot：baseline + A 组 × 20 题 × 2 run = 80 场
- [ ] 成本预估：~$79，wall ~27 h（mean $0.99/场 × 80）
- [ ] moderator：Opus 4.6（Ken 硬要求）
- [ ] pilot 跑完后自动调 judge.py 给每场打分
- [ ] 输出 `pilot_analysis.md`：方差 / judge 自一致性 / (d) 标签效应首次量化 / 学科分化 pattern 在 A 组是否消失
- [ ] `@codex` review pilot 代码
- [ ] `@ken` review 分析报告
- 依据：`experiments/emergence_decomposition/results/dry_run_20260416_083829/scaleup_report.md` + `spec.md`

### `@ken` KPAX v0 角色图设计（Ken 2026-04-16 晚标注"不急，要好好设计"）
- [ ] 状态：不急。Ken 在好好设计视觉风格 + 7 角色细节
- [ ] 按 `notes/design.md#kpax-v0-deliberation-room` §7.2 的 7 张 prompt + §7.1 视觉锚丢给 Grok
- [ ] 每人 2–3 variant，挑稿。同时看 7 张拼一起是否像"同一个世界的人"
- [ ] 定稿后回 cc，cc 把角色定稿写进 design.md，下发 cursor 进 Rodin/Meshy 4/Tripo 2 3D 转化
- 无前置依赖

### `@ken` 拍板：项目可视化路径 A / B / C（Ken 2026-04-17 识别痛点）
- [ ] 路 A：cursor 做本地 HTML dashboard 读 repo 各 markdown 渲染成 kanban / timeline
- [ ] 路 B：接外部工具（Linear / Notion / GitHub Projects）定期 sync
- [ ] 路 C：recursive dogfooding，KPAX 座谈会 UI 扩展一个"项目 domain"（野但有趣，可能是 v1 之后）
- 依据：`PROJECT.md` §6 末尾 + `notes/journal/2026-04.md` 04-17 凌晨条目

### `@ken` 拍板：Lucas 量化闭环后续决策点
- [ ] A 步骤（judge.py 给现有 baseline 打分）何时启动？建议 cursor 修 monorepo 完成后立刻启动
- [ ] 人工评分锚点（C 步骤）由谁打？Ken + cursor 各一批？还是 Ken 独立？
- [ ] Meta-learner（E 步骤）是否从 Phase 3 开始纳入研究路线图？
- 依据：`notes/research.md#quantification-gap` 决策点

---

## 🟡 P1 —— 本周内

### `@cc` KPAX v0 Week 1 Day 1–2：Spark 2.0 实测 + 场景起步
- [ ] 跑 sparkjs.dev 官方 demo，验证 R3F 集成流畅度
- [ ] 起 Next.js + R3F + Spark 2.0 骨架
- [ ] 接入 Spark 现成 captured_space 作为临时书房

### `@cc` KPAX v0 Week 1 Day 3–7：图 → 可动画 3D 对比
- [ ] Ken 交稿后，同一张 portrait 丢 Rodin Gen-1 / Meshy 4 / Tripo 2 三家
- [ ] 对比 rig 质量、骨骼兼容性、动画流畅度
- [ ] 选一家，7 人全转 .glb

### `@cc` Checkpoint 1 pilot（40 场扩样完成后）
- [ ] baseline + A 组各 20 题 × 2 run = 80 场（~$73）
- [ ] 依赖 A 组代码（debate_engine 加 "去 discipline label" 支路，~1–2h 工时）
- [ ] 输出 `pilot_analysis.md`

### `@cursor` spec R4 文本确认（judge 策略锁死 API）
- [ ] `experiments/emergence_decomposition/spec.md` 4.1 节
- [ ] 确认：主 judge 固定 API 模型（GPT-5 或 Gemini 2.x，选一个不换），**不**搞本地 fine-tune judge
- [ ] 理由：judge 模型能力必须 ≥ 被判模型；Claude Opus 4.6 的输出 7B 判不动。900 次 judge 总成本 ≈ $8，省这个是省零头
- [ ] 依据：`notes/research.md#wisland-analysis-and-positioning` B.1（已改）

### `@cursor` dry run 内容层观察落 spec（来自 dry_run_report §8，n=3 观察非结论）
- [ ] agent prompt 加"不得复述本轮他人已提论点"；收紧 agent `max_tokens`（观察：每条 2000–4000 字，同轮重复攻击角度）
- [ ] Judge prompt 显式"长度不是优点"或对长度 per-token 归一（防止被篇幅带偏）
- [ ] `unique_concept_count` / `cross_discipline_reference_count` 去重 + per-token 归一（防止灌水拉高 diversity）
- [ ] `@ken` 或 `@cc` pilot 前人工抽 10 条引用查真实性，通过再考虑加 `evidence_quality` 代理指标
- 依据：`results/dry_run_20260414_173832/dry_run_report.md` §8

### `@cursor` human_scores.json schema 扩展
- [ ] spec 4.x 补一个子小节：`human_scores.json` 加 `message_tags` 字段，格式 `{message_id: tag}`，tag ∈ {"key_claim", "noise", "off_topic", "stance_shift", "novelty"}
- [ ] 依据：wisland note B.4

### `@cc` fix AXL 生产 bug 的 commit
- [ ] `projects/knowledge-graph/backend/app/services/debate_engine.py:457` 已在 worktree 改好（`names` → `names_en`）
- [ ] 这是 AXL 生产 bug，不是实验 runner 的事，得单独 commit 进 main，不能和实验代码混
- [ ] 成功判据：main 分支 git log 看到这个 commit + CHANGELOG.md 有一条

---

## 🟢 P2 —— 本月内

### `@cc` pilot 后云租 GPU fine-tune structured tagger（不是 judge）
- [ ] 用 pilot 收集的 human_scores + API judge 输出做训练集
- [ ] 云租 A100（AutoDL / RunPod 按小时），QLoRA 微调 Qwen-2.5-14B 起步，必要时 34B
- [ ] **三个用途**（都不是绝对打分）：
  1. message-level tagger（对应 B.4 message_tags schema）
  2. reasoning_unit 抽取器（对应 AXL M2）
  3. API judge 的 meta-validator（偏差检测）
- [ ] 主 judge 仍是 API，不替换
- 依据：wisland note B.1 + B.6（均已改）

### `@cc` KPAX 内容注入路径选型（不止论文，三条知识线都涉及）
- [ ] **硬规则**：不自建板式解析模型（没有 10 年积累）。开箱工具按内容类型分场景选
- [ ] **学术论文**（arXiv / S2）走 `pdfminer.six` 或 `unstructured` pdfminer 后端
- [ ] **行业报告 / deck / 扫描版 / 老文档 / 社区截图**：允许用 OCR-based 开箱方案（Fire-PDF / docling / mineru / Marker 等都在候选池），按"能扛住的最简方案"选
- [ ] 评估 `firecrawl/pdf-inspector`（纯 Rust，无 ML，做分类 + 文本抽取）作为学术路径的 pdfminer 替代
- [ ] 写 `PaperSource` 抽象层：arXiv API + Semantic Scholar + Crossref + Unpaywall + Europe PMC + OpenAlex（fallback 顺序）
- [ ] 依据：wisland note B.3（2026-04-16 晚修订版）+ B.7（OpenAlex 60% abstract 缺失）
- 触发时机：KPAX 开始做内容注入那一刻

### `@cc` AXL + KPAX 最低可用 trace 日志体系（KPAX v0 启动前必做）
- [ ] FastAPI middleware：每请求生成 `request_id`，注入 contextvars
- [ ] 关键服务统一 logger format：`[req_id=xxx step=yyy | msg...]`
- [ ] stdout → JSON Lines（方便 cc / cursor / 未来 AI 读）
- [ ] debate_engine / classifier / expert_builder / ledger / axl_client 五个组件加关键节点 log
- [ ] 工时估：1-2 天。**不做全栈 observability**（Sentry / DataDog / Jaeger），只做最低可用 trace
- [ ] 依据：radar [2026-04-16] Lawrence 日志方法论 + 我们现状"10+ 文件散落 logger，55 处调用，无统一配置"
- 触发时机：KPAX v0 前端真跑起来之前

### `@cc` KPAX + AXL v0 视觉产物（v0 上线前必做）
- [ ] KPAX Logo（主站 / 推特头像 / 分享卡 / 钱包图标）
- [ ] AXL Logo（GitHub / README / PROGRESS.md 头）
- [ ] 7 学科抽象图标（座谈会 fallback UI / moderator 徽章）
- [ ] 代币图标
- [ ] UI 按钮图标：分享、有帮助、拍肩膀
- [ ] 生成工具：**歸藏 Logo Generator Skill**（radar [2026-04-16]）— Gemini CLI 三步生成 SVG + 高级展示图
- [ ] 架构图配套：**Cocoon architecture-diagram-generator**（已 adopt）
- 依据：radar Cocoon + 歸藏 两条

### `@cc` KPAX 分享激励 loop 设计（v0 上线前必接）
- [ ] 每场辩论结束 → 生成 30 秒精华视频（7 顾问辩论高光 + 最终判决）
- [ ] 视频生成候选：**Hyperframes**（radar [2026-04-16]）——Claude Code 预装 skill，HTML → MP4 本地渲染，零云端
- [ ] 分享流程：用户点"分享" → 下载 MP4 / 直传 X / Telegram → 钱包 +20 token
- [ ] 设计"精华"抽取规则：哪些消息入选高光（ranked by 论点锐度？冲突密度？引用密度？）
- [ ] 依据：`notes/design.md#kpax-v0-deliberation-room` §5 用户动作流 + KPAX 六条代币规则

### `@cursor` + `@ken` KPAX decision domain tag
- [ ] KPAX session 埋 `decision_domain` 字段（用户填 or LLM 自动打）
- [ ] 领域枚举：medical / legal / investment / consumer / career / relationship / other
- [ ] 跑 3 个月后看分布，决定 KPAX 第一个垂直打哪里
- 依据：wisland note B.9

### `@cc` emergence_decomposition 全量跑（Checkpoint 2-4）
- 触发：pilot 分析通过 + Ken 批准
- 按 spec 5.2 顺序：baseline+A → B+C → D+E
- 每批跑完生成中间 summary.md 给 Ken 过

### `@cc` 跟进 Zep 从 memory 改名 context engineering 的技术含义
- [ ] 读 Zep 的 Graphiti framework 新文档，看 temporal knowledge graph 的 valid_at / invalid_at 实现
- [ ] 评估：AXL 当前七层记忆用 Zep 的 add_memory / search_knowledge 接口，Zep 新 positioning 是否要求我们改接口使用方式
- [ ] 输出一段话更新 `notes/research.md#seven-layer-memory-design` 的 backend 部分
- 依据：`notes/radar.md` [2026-04-16] witcheer Two-Camps 第 1 条连接

### `@cc` OpenClaw 6 加权信号做 agent-evolution-free-parameters 默认值
- [ ] 读 OpenClaw 的 dreaming process 源码（light sleep / REM / deep sleep 三阶段）
- [ ] 把 6 个信号（relevance 0.30 / frequency 0.24 / query diversity 0.15 / recency 0.15 / consolidation 0.10 / conceptual richness 0.06）作为 AXL 自由参数 L7 元进化的 prior，写进 `notes/research.md#agent-evolution-free-parameters`
- [ ] AXL 差异化写明：别人 hard-code，我们让它 per-user 可学习
- 依据：同上，第 2 条连接

### `@cursor` emergence_decomposition 续集：compounding_gain_benchmark（下一个实验）
- [ ] emergence_decomposition 全量跑完后，下个实验设计：测 "session N 是不是比 session 1 更聪明"（compounding gain）
- [ ] witcheer 指出这是现有所有 memory benchmark 的空白——AXL 护城河的天然论文立足点
- [ ] 提前写 spec 草稿，等 emergence 全量结果 + 自由参数初版 validate 后启动
- 依据：radar [2026-04-16] 第 3 条连接 + `notes/research.md#agent-evolution-free-parameters` + `seven-layer-memory-design.md` L7

### `@cc` 深读 Thoth（145⭐ 小项目）
- [ ] Thoth 4 阶段 dream cycle：duplicate merging 0.93 sim / enrichment / relationship inference / confidence decay 90 天
- [ ] 10 entity types + 67 typed relations 的 schema 设计值得抄
- [ ] 评估能否作为 AXL Phase 3（L3 语义 + L4 程序记忆）的参考实现
- 依据：radar [2026-04-16] 第 4 条连接

### ✅ `@cc` 建 KPAX 知识源架构笔记（2026-04-16 深夜完成）
落地：`notes/research.md#kpax-knowledge-source-architecture`。v0/v1/v2 phasing 已给出，等 Ken 拍板第 8 节 4 个决策点。

### `@cc` 建 KPAX 知识源架构笔记（archived above）
- [ ] 新建 `notes/research.md#kpax-knowledge-source-architecture`
- [ ] 写清三条输入线：(a) 学术论文 arXiv/OpenAlex/S2 (b) 行业 curated awesome-lists/YC/a16z/Sequoia (c) 社区经验 Reddit/知乎/Quora
- [ ] 7 位顾问在辩论时如何从三类源调证据，每类对应哪些学科
- [ ] Ken 的小伙伴爬虫现状、覆盖度、哪些类目缺口
- [ ] KPAX 初版可以从 awesome-ceo 开始 ingest 行业 curated 层，验证调用链路
- [ ] **第三线（社区经验）候选参考池**（按需 vs 预缓存两种模式都要）：
  - autocli（radar [2026-04-16]）—— 按需 Chrome-login-state 本地 skill，55+ 平台
  - yupi-hot-monitor（radar [2026-04-16]）—— 预缓存定时 poll 服务端，8+ 平台，AI pipeline 参考
  - graphify（radar [2026-04-16]）—— 文件夹→知识图谱，适合行业 curated 层
- 依据：radar [2026-04-16] awesome-ceo / autocli / yupi-hot-monitor / graphify 四条

### `@cc` 深读 ALIVE（witcheer 自己的项目）
- [ ] 访问 alivecontext.com + @AliveContext_ 推特看架构
- [ ] 评估 "walnuts" 作为 portable context container 的设计——可能对应 KPAX 的"每用户决策历史可导出单位"
- 依据：radar [2026-04-16] 第 5 条连接

---

## 🔵 P3 —— 记一笔，以后做

### `@ken` 给 AXL / KPAX 各打一个成熟度分 + milestone
- 类比 WisLand 创始人"70 分 → 80 分 4.20 发布"的节奏
- 每周一自检
- 依据：wisland note B.11

### `@cc` 第 F 组实验（带工具的 debate）
- agent 调用 retrieve / verify / novelty-check 三个工具，不是光靠 prompt
- 这三个工具对应 spec 的 diversity 指标，让 agent 过程中能看到
- emergence_decomposition 跑完后作为第二轮实验设计
- 依据：wisland note B.5 + B.8

### `@cc` L7 元进化实验设计
- 七层记忆 L7 层：自由参数自我改写
- 这是 Ken 相对 WisLand 的核心差异点（他们没有也不会有这层）
- 依据：`notes/research.md#seven-layer-memory-design` + `wisland-analysis-and-positioning.md` C.2 维度 1

### `@cc` 本地 L1/L2 记忆层
- Qwen-2.5-14B 或 GLM-4-9B 本地跑 L1 工作记忆 + L2 情节记忆
- L3 以上走 API
- 好处：隐私 / 成本 / 离线开发
- 依据：wisland note B.10

### `@ken` arXiv 发表 emergence_decomposition 论文
- 触发：全量实验跑完 + 结论写出
- 是 Ken 研究身份的第一块砖
- 依据：wisland note C.3 P0 + P2

### `@ken` 开源 AXL 研究层
- `debate_engine` + `seven_layer_memory` + `free_params`
- 产品层闭源（KPAX UI / 商业化 / 用户数据）
- 触发：第一篇论文发出去之后
- 依据：wisland note C.3 P2

---

## ❌ 明确不做的事（反向清单）

这是 WisLand 的主场，Ken 一旦开始做就输。每次有冲动加这类任务到 P0/P1，先回来读一遍：

- **自建文献索引**：用 arXiv + S2 API，不抓期刊
- **Post-train 自研 base 模型**：只 fine-tune 小 judge
- **自研 PDF 板式解析模型**：用开箱工具（pdfminer / unstructured / Marker / mineru / Fire-PDF / docling 都行），不自己训
- **DCA 端侧百万长序列**：没必要
- **科研工具产品功能**（论文检索、学术写作、参考文献管理）：KPAX 保持在通用决策场景，不扩成科研工具
- **把 KPAX 扩到帮研究者"省时间"那一类**：KPAX 帮用户做判断，不是替用户更快完成任务

**立场澄清（Ken 2026-04-16 晚）**：上面的"不做 X"都是 **能力约束型**立场（没有积累，做不过人家），**不是战略回避**。有好工具就用，有能力就上正面。cc 以后写反向清单不要自带"避免竞争"叙事。

依据：`notes/research/` 对位分析笔记（2026-04-16 修订）

---

## 写入规则（所有 agent）

1. **做完一项**：从本文件删掉 + 在 `notes/journal/2026-04.md` 追加一条 `[YYYY-MM-DD @owner] 完成 XXX，结果/输出：YYY`
2. **新任务浮现**：加到对应优先级节，带 owner + 成功判据。**不要**把 TODO 藏在 research note 正文里
3. **任务被阻塞**：在 item 后加 `**阻塞**：原因` 一行，不要默默放弃
4. **降级/升级优先级**：改的时候在 journal 记一笔为什么改
5. **代码改动落地**：commit 后同步更新 `CHANGELOG.md`（代码层）+ `journal/2026-04.md`（决策层）
6. **实验状态变化**：同步改 `experiments/config/experiment_registry.json`

**反模式**：
- 在 research note 或 spec 里写 "TODO: ..." → 应该抽到本文件
- "等 Ken 回复" 类任务放 P0 → 应该放 P1 并标明 `@ken`
- 同一任务在多处重复登记 → 只在本文件，其他地方 reference 回来
