# Next — 跨 agent 行动板

**这是唯一的"下一步做什么"真相源。** 所有 agent（claude-code / cursor / codex / ken）开工前必读这个文件。做完一项 → 从这里删除 → 追加到 `notes/journal/YYYY-MM.md`。新任务浮现 → 加到这里，不要藏在 research note 正文里。

**owner 标记**：`@cc` = claude-code，`@cursor` = cursor，`@codex` = codex，`@ken` = 只有 Ken 能做（决策 / 打分 / 外部判断）

**优先级**：P0 必须先做（blocker）；P1 本周内；P2 本月内；P3 记一笔以后做

**最后更新**：2026-04-15 晚 by cc（KPAX v0 任务 + pilot 状态清理）

**总导航**：先读 `PROJECT.md` 了解项目全貌，再回本文件找 owner 任务。

---

## 📌 KPAX 定位硬规则（Ken 2026-04-15 拍板，所有 agent 遵守）

1. **承诺 = "把这个问题帮你想透"**（深度/正确/全面），不是 "给你没想到的角度"。用户问 A/B 你答 C 是答非所问。
2. **5 个题型全是基础功能**，不做 MVP 裁剪。是否 / 概率 / 选择 / 策略 / 评估全覆盖。
3. **不锁 decision_domain 垂直**，通用决策工具。
4. **付费 = 代币**：消耗 token 用 / 分享赚 token / dex 或最简交互合约可买。不做法币订阅、不做传统用户注册，钱包即身份。
5. **成功判据**：10 个朋友 7 个说"有帮助"。不是 "没想到的角度"。
6. **KPAX 和 AXL Day 1 走 HTTP**，代码/DB/部署/生命周期全分开。AXL 是后端服务，KPAX 是 consumer。禁止 monorepo import。

---

## 🔥 P0 —— 阻塞态，先做这些

### `@cc` meta_01 rubric v0.1 落地三步（Ken 2026-04-16 拍板，ABC 全做）
- [ ] **A（先做）**：把 DB 里 meta_01 的完整 transcript（17 条 message）导到 `results/dry_run_20260416_165636/raw/baseline_meta_01.json`；Round 2 moderator 综合（6199 字）写成 `results/dry_run_20260416_165636/pilot_judge_rubric_v0.1.md` 正式归档；挂进 `spec.md` §4 Judge 设计章节作为 pilot rubric v0.1
- [ ] **B（之后做）**：改 runner 的 timeout：standard depth 从 2000s 拉到 4800s；meta_01 用同 prompt 重跑完整 4 rounds 拿 v0.2（对比 v0.1 看 2 rounds vs 4 rounds 精炼度差距）
- [ ] **C（并行）** `@cursor`：独立审 `pilot_judge_rubric_v0.1.md`，写出 v0.1-reviewed（识别 AXL 自偏置风险，修订维度 / 评分 anchor / 合成规则）
- [ ] 最终 pilot rubric = v0.1 + cursor 审修 + v0.2 对照优化后的版本
- 依据：`results/dry_run_20260416_165636/progress.jsonl` + Round 2 moderator 综合（DB msg id=75）

### `@cc` Checkpoint 1 pilot 启动（Checkpoint 0 已真关闭 2026-04-15 晚）
- [ ] 启动 pilot：baseline + A 组 × 20 题 × 2 run = 80 场
- [ ] 新配置下 pilot 预估：**~$73**，wall ~20 h（mean $0.91/场 × 80）
- [ ] moderator：Opus（Ken 硬要求），**不需要提 Anthropic tier**（Tier 1 自洽已验证）
- [ ] 输出 `pilot_analysis.md`：方差 / judge 自一致性 / (d) 标签效应首次量化
- 依据：`experiments/emergence_decomposition/results/dry_run_20260415_171016/mini_dry_run_report.md`

### `@ken` KPAX v0 第一步：生角色图
- [ ] 按 `notes/design/kpax-v0-deliberation-room.md` §7.2 的 7 张 prompt + §7.1 视觉锚丢给 Grok
- [ ] 每人 2–3 variant，挑稿。同时看 7 张拼一起是否像"同一个世界的人"
- [ ] 定稿后回 cc，进 Rodin/Meshy 4/Tripo 2 对比

### ✅ `@cc` KPAX 后端 survey（2026-04-16 晚完成）
发现 5 处 monorepo import 违反硬规则 #6。见 `notes/journal/2026-04.md` 2026-04-16 深夜 cc 条目。

### `@cc` KPAX v0 最短可跑路径（路 2：绕开违规 services）
- [ ] `question_classifier._chat_fn` 接真 LLM（DeepSeek 或 Anthropic SDK 直调，不走 AXL），~30 min
- [ ] AXL `kpax_router.py` mock 改真调 `debate_engine.py`（产出真 debate + moderator summary），~2-3h
- [ ] 前端 v0 从零（按 Claw3D 架构模板 + Spark 2.0 + R3F + Rodin/Meshy/Tripo 人物生成），三周节奏见 `notes/design/kpax-v0-deliberation-room.md`
- [ ] **三个违规 services（question_parser / expert_builder / report_generator）暂不动**，留到 v1 决定重写成 HTTP-only 还是弃用

### `@cursor` KPAX v1 清账：decide 三个违规 services 命运
- [ ] 等 v0 上线、真实使用数据反馈后再评估
- [ ] 每个文件评估：重写成 HTTP-only（拆掉 `from app.services.ai_provider`，改用 KPAX 自己的 LLM client 或通过 axl_client）/ 弃用（功能被 v0 简化链替代）
- [ ] 依据：`notes/journal/2026-04.md` 2026-04-16 深夜 survey + KPAX 硬规则 #6

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
- [ ] 依据：`notes/research/wisland-analysis-and-positioning.md` B.1（已改）

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
- [ ] 依据：`notes/design/kpax-v0-deliberation-room.md` §5 用户动作流 + KPAX 六条代币规则

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
- [ ] 输出一段话更新 `notes/research/seven-layer-memory-design.md` 的 backend 部分
- 依据：`notes/external-references-radar.md` [2026-04-16] witcheer Two-Camps 第 1 条连接

### `@cc` OpenClaw 6 加权信号做 agent-evolution-free-parameters 默认值
- [ ] 读 OpenClaw 的 dreaming process 源码（light sleep / REM / deep sleep 三阶段）
- [ ] 把 6 个信号（relevance 0.30 / frequency 0.24 / query diversity 0.15 / recency 0.15 / consolidation 0.10 / conceptual richness 0.06）作为 AXL 自由参数 L7 元进化的 prior，写进 `notes/research/agent-evolution-free-parameters.md`
- [ ] AXL 差异化写明：别人 hard-code，我们让它 per-user 可学习
- 依据：同上，第 2 条连接

### `@cursor` emergence_decomposition 续集：compounding_gain_benchmark（下一个实验）
- [ ] emergence_decomposition 全量跑完后，下个实验设计：测 "session N 是不是比 session 1 更聪明"（compounding gain）
- [ ] witcheer 指出这是现有所有 memory benchmark 的空白——AXL 护城河的天然论文立足点
- [ ] 提前写 spec 草稿，等 emergence 全量结果 + 自由参数初版 validate 后启动
- 依据：radar [2026-04-16] 第 3 条连接 + `notes/research/agent-evolution-free-parameters.md` + `seven-layer-memory-design.md` L7

### `@cc` 深读 Thoth（145⭐ 小项目）
- [ ] Thoth 4 阶段 dream cycle：duplicate merging 0.93 sim / enrichment / relationship inference / confidence decay 90 天
- [ ] 10 entity types + 67 typed relations 的 schema 设计值得抄
- [ ] 评估能否作为 AXL Phase 3（L3 语义 + L4 程序记忆）的参考实现
- 依据：radar [2026-04-16] 第 4 条连接

### ✅ `@cc` 建 KPAX 知识源架构笔记（2026-04-16 深夜完成）
落地：`notes/research/kpax-knowledge-source-architecture.md`。v0/v1/v2 phasing 已给出，等 Ken 拍板第 8 节 4 个决策点。

### `@cc` 建 KPAX 知识源架构笔记（archived above）
- [ ] 新建 `notes/research/kpax-knowledge-source-architecture.md`
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
- 依据：`notes/research/seven-layer-memory-design.md` + `wisland-analysis-and-positioning.md` C.2 维度 1

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
