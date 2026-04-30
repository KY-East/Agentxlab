# Next — 跨 agent 行动板

**这是唯一的"下一步做什么"真相源。** 所有 agent（claude-code / cursor / codex / ken）开工前必读这个文件。做完一项 → 从这里删除 → 追加到 `notes/journal/project-log-YYYY-MM.md`。新任务浮现 → 加到这里，不要藏在 research note 正文里。

**owner 标记**：`@cc` = claude-code，`@cursor` = cursor，`@codex` = codex，`@ken` = 只有 Ken 能做（决策 / 打分 / 外部判断）

**优先级**：P0 必须先做（blocker）；P1 本周内；P2 本月内；P3 记一笔以后做

**最后更新**：2026-04-24 下午 by cursor（Phase 1 上线后 Debate #13 实战验证 4/6 真过 + 暴露两条遗留：P1 useEffect 优先级反转修复 + P2 free Round 3 长度触 max_tokens；详见 `notes/journal/appendix-2026-04-24-debate-free-mode-phase1-validation.md` 全文 + `project-log-2026-04.md` 2026-04-24 第二条目）

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

### ✅ 已完成：P0 同学科双 agent 雷同 G+F 修复（2026-04-24 Debate 11 实战验证通过）
- 2026-04-20 cursor 定位根因（`run_round_stream` 把前一个 agent 的完整原文直灌给下一个 agent → Debate 10 出现 msg#82/83=3227、msg#89/90=2423 跨 LLM 字数完全一致）
- 2026-04-23 Ken 拍板 "agent 模式直接开干 D+C+F+G，战略拍板留 plan 模式"——原 `notes/research/agent-twin-fix-decision-gate.md` 6 问决策门框架被绕过（文档保留作方法论参考）
- 2026-04-23 G+F 实施：`_enforce_same_discipline_different_family` + `_summarize_teammate_message` 三列摘要 + teammate prompt 改"同学科不同流派"
- 2026-04-24 Debate 11 实战验证：18 次发言零复读、三学科跨 LLM family + 流派分化稳定（详见 `notes/journal/project-log-2026-04.md` 2026-04-24 条 + 双 appendix cc/gpt 稿）
- 结论：P0 消除，debate 分工层冻结，转 P1 新排序（见下）

### ✅ 已完成：free / debate 模式语义彻底分叉（Phase 1，2026-04-24 下午）
- Ken 2026-04-24 上午发现 Debate 12（mode=free）和 Debate 10/11（mode=debate）输出几乎一样
- 三方诊断（Ken / GPT / cursor）+ cc 裁定 + Ken 产品哲学拍板全部完成
- cursor Phase 1 实施：FREE_ROUND_OPENERS + FREE_MODERATOR_PROMPTS + FREE_MODERATOR_ROUND_OPENERS + 使命段 mode 分叉 + teammate mode 软化 + 前端 useAcademic bug 修掉
- 依据：`notes/design.md §axl-debate-mode-design` 产品哲学 + `notes/journal/appendix-2026-04-24-debate-free-mode-semantic-fix-handoff.md` 工程清单
- Debate #13（"实验本身能否找到共性"）实战验证：6 条验证里 4 条真过 + 1 条 DB 核实未通过 + 1 条待 Ken 跑。详见 `notes/journal/appendix-2026-04-24-debate-free-mode-phase1-validation.md`

### `@cursor` P1 验证 4 反转：Debate.tsx useEffect 自动填充优先级 bug（Phase 1.1）
Phase 1 部署后 cursor 跑 DB 核实 Debate #13 的 proposition 字段，发现仍是 AI 改写版（"开发一个数学框架..."），不等于 raw_question（"实验本身能否找到共性..."）。根因不在中午改的 `handleCreate::finalProposition`，在 `Debate.tsx:94-104` 的 useEffect——Discovery 跳转时 `navCtx.hypothesis`（AI 改写版）优先于 `navCtx.discoveryQuestion`（用户原话）填进输入框，所以 inputText 默认值就是改写版。

这条 2026-04-17 修 raw_question 时就在 P2 挂着（"Discovery 跳转 hypothesis 进来短期可接受"），Ken 2026-04-24 产品哲学拍板把它升级为"必须修"——`proposition == raw_question` 是 Phase 1 验证 4 通过的硬条件。

修法两选（待 Ken 拍板）：
- a) useEffect 优先级反转：`navCtx.discoveryQuestion || navCtx.hypothesis || ...`，原话优先填输入框；hypothesis 降级为"Discovery 推荐了这个学术化版本，要采用吗"卡片，用户点采用才覆盖。**cursor 倾向 a**——保留改写版可发现性，默认尊重原话
- b) 完全去掉 hypothesis 自动填充：只用 discoveryQuestion，hypothesis 在 Discovery 页消化掉不跨页传

详见 `notes/journal/appendix-2026-04-24-debate-free-mode-phase1-validation.md` §二。

### `@cursor` P2 free 模式 Round 3 输出长度触 max_tokens 上限
Debate #13 实测 msg#154/156/157 末尾不完整（"若连片内 Lipschitz 都不满"未收尾、"ELBO ga..." 被截、"判据上"硬刹车）。professor max_tokens=4000、assoc=3000 按 debate 模式校准，free 模式六字段 + 根本分歧 + 学科贡献产出量大于 debate 的"最终答案"，standard depth 预算不够。

修法两选：
- a) free 模式专用调高 max_tokens（prof=6000 / assoc=4500）
- b) free Round 3 prompt 加"六字段每条 ≤ 80 字 / 根本分歧每条 ≤ 50 字"硬上限——纲要式而非展开式。**cursor 倾向 b**——和 distiller 方向 + KPAX 实验板块 renderer 消费纲要的方向对齐

详见 `notes/journal/appendix-2026-04-24-debate-free-mode-phase1-validation.md` §三。

### `@cc + @ken` P1 顶格优先级：AXL 产出要从"可读文本"升级为"可推演产物"（Ken 2026-04-24 拍板）

**Ken 2026-04-24 原话**：
> "我问怎么统治世界，哪怕没有答案，也要给一个模拟沙盘，或者推演实验的设计"

**这把问题拎到产品形态层**。cc 和 GPT 双稿 P1 排序里都有 distiller（三档压缩），但 distiller 只是把 3 万字综述压到 500 字——**用户仍然只能读**。Ken 要的不是压缩文本，是生成工具：

- **模拟沙盘形态**：用户输入自己的参数（资源 / 时间尺度 / 目标控制度 / 干预预算），AXL 跑一遍多 agent 推演，返回可对比的情景结果（τ 延长曲线 / 崩溃概率 / 先失控子系统 / 关键阈值触发时间）
- **推演实验设计形态**：用户给出自己想验证的假设，AXL 返回可执行的 N 步小规模试点方案（每步测哪个指标 / 看多久 / 触发哪个下一步分支 / 失败判据是什么）

两种形态都比 distiller 深一层：distiller 是**知识产品**的最后一步收束；沙盘/实验设计是从**知识产品**切换到**工具产品**。

**对照现在的 AXL 输出**（Debate 11 "如何科学的统治世界"）：
- 现在给的 = 三学科综述 + 联合诊断框架 + "拓扑-观点-系统联合预警实验"的建议研究方向
- **"建议研究方向"那段其实已经有推演实验设计的雏形**——给了 δ>20% + τ延长>40% + 桥接边<基线70% 的阈值。差的只是：这些数字被埋在 3 万字末尾用户看不到，而且没有做成可输入 / 可调参 / 可重跑的形态

**待拍板的分叉**（`@ken`）：
- a) v0 先做**推演实验设计** renderer——不引入仿真引擎，只把 agent 生成的"如果你想验证 X 该怎么做"结构化成可执行步骤清单。成本低，对现有 debate 管道改动小
- b) v0 先做**模拟沙盘**——需要 agent 框架之外的仿真能力（轻量 ABM / 系统动力学微模型 / 或多跑几次 debate 把参数做成 sweep）。成本高，产品感强
- c) **先做 a，v1 再做 b**（cursor 倾向这个，a 验证了再上 b）

**对现有 P1 排序的影响**：
- cc+GPT 双稿的 P1 "distiller 三档" **不撤销**，但地位从"顶格"降为"沙盘 / 实验设计做出来之前的过渡形态"——verdict / estimate 仍然值得做，plan 级让位给 a/b 的可执行产物
- AI 味和引用密度问题 Ken 2026-04-24 明确说 "不是最大问题"——从 P1 降为 P2（见下）

### `@cc` P1 Distiller 三档输出（cc + GPT 双稿共识，地位调整为过渡形态）
详见 `notes/journal/project-log-2026-04.md` 2026-04-24 条目的"后续动作"1-3 项。verdict / estimate 两档仍做，plan 级让位给上面"沙盘 / 实验设计" renderer。

### `@cc` P1 Moderator 可能有 Complex Systems 偏置（GPT 抓的系统信号）
Debate 11 moderator 判断和最终共识偏向 CS 框架（反身性 / 硬边界 / 适应性规避占大头），Network 被压成"工程层"、Opinion 被压成"校准层"。单次不能下结论，需要多题验证：连跑 3-5 题不同主题，看 CS 是否每次都被 moderator 标为"最有想象力"。如果是系统偏置，需要调 moderator prompt 里对"元层次叙述"的隐性偏爱。

### `@cc` P2 AI 味 pipeline 检查（Ken 2026-04-24 明确降级）
Ken 原话："AI 味的问题，引用的问题，这不是最大的问题"。原 cc+GPT 双稿把这条排 P1，按 Ken 拍板降 P2。内容不变：引用密度上限 / 对称句式检测 / 学科边界自辩 / 数字修辞（模式 17）四项后处理检查。

### `@ken` 上线前必做：关闭 `AUTH_BYPASS_DEV_MODE`
2026-04-17 晚 cursor 加的 dev 旁路开关，当前 `.env` 里 `AUTH_BYPASS_DEV_MODE=true` → 所有 auth 检查被短路成 id=1 的 Ken 账户。**任何 deployment 前**必须改成 `false` 或删除该行，否则 AXL 会完全裸奔。代码层面不需要改动，只改 `.env`。启动 log 会打 70 字符包围的 WARNING 提醒，但仍建议部署脚本里加断言 `AUTH_BYPASS_DEV_MODE != true`。详见 CHANGELOG 2026-04-17 "Dev-only 认证旁路开关"条目。

### `@ken` P2 depth 选项的 UI 承诺 vs 实际耗时完全脱节（Debate 10 实证，2026-04-20 发现）
Ken 选 `standard`（UI 写"~3 分钟"），Debate 10 实际跑了 ~15 分钟还没结束。UI 文案是前端代码硬编码字符串（`Debate.tsx:558`），**与后端实际耗时没有任何约束关系**——当时写的时候拍脑袋编的。

**当前 UI 承诺 vs 数学下限**：

| depth | UI 标签 | max_tokens (prof/assoc) | 21 turns × 平均耗时下限 |
|---|---|---|---|
| quick | ~1 分钟 | 800/600 | 21×5s = ~2 分钟（UI 误差 2x） |
| standard | ~3 分钟 | 4000/3000 | 21×40s = ~14 分钟（UI 误差 **5x**） |
| deep | ~8 分钟 | 8000/6000 | 21×80s = ~28 分钟（UI 误差 3.5x） |
| max | ~15 分钟 | 12000/10000 | 21×120s = ~42 分钟（UI 误差 3x） |

外加：spark_extractor 每条发言后跑 1 次独立 LLM call（21 次额外 +3-10s/次）、_resolve_weights 创建辩论时 1 次、generate_summary 1 次大调用。

**Ken 2026-04-20 决定**：「记录，然后一会儿想解决方案」。候选方案待 Ken 拍板：
- **A. UI 诚实化**：不改后端，只把文案改成真实耗时（~2 / ~12-15 / ~25-30 / ~40-45 分钟）。代价：劝退用户。
- **B. 降 max_tokens 兑现承诺**：standard 改成 800/600（等于现在的 quick），让 "3 分钟" 真成立。代价：单条发言短得像群聊，"深度辩论"感觉消失。
- **C. 同 round 内并行发言**：打破"每人看前人"因果，全部 professors 同时看 round 1 状态并行 generate，只有 moderator 串行。代价：失去交锋感，变成并行独白 + moderator 收束。
- **D. spark_extractor 真异步**：`asyncio.create_task` fire-and-forget。省 21×5s ≈ 2 分钟。不改辩论本质。
- **E. 学科数 / team_size 硬上限**：3 学科 × 每队 1 人 + 1 moderator = 4 turns × 3 round = 12 turns，耗时腰斩。代价：失去"大团圆"感。
- **F. 组合**：A+D+E（UI 真话 + spark 异步 + 软上限学科数），最现实。

关联：下面 P2 `context token 指数增长` 条目是同一系统性问题的另一面（深层因）；本条是 UI/承诺层的浅层症状。解决方案拍板时一起考虑。

### `@cursor` P2 辩论越到后面越慢（context token 指数增长，Debate 10 实证）
2026-04-20 Ken 实测：Debate 10 7 agent × 3 round，越到后面每条发言越慢，round 2 中段某条 deepseek 调用单次耗时 **2 分 09 秒**。根因是 multi-agent 辩论的经典 token 爆炸：

Debate 10 token 增长实测（从 ai_provider "User 1 used X tokens" 日志摘）：
- Round 1 前段：1,209 / 2,785 / 1,623 / 2,495 / 1,688 tokens
- Round 1 后段：4,668 / 4,896 / 7,700 / 9,534 tokens
- Round 2 开头：15,799 tokens
- Round 2 中段：10,926 tokens（单次 2 分 09 秒）

每轮每个 agent 的 prompt = 系统指令 + 前面**所有人**发言。7 agent × N round，context 近乎平方级增长。预估 round 3 单条 30-40k tokens，deepseek/claude 处理长 context 本身就慢。

代码里有个 `app/services/session_memory.py::build_compressed_context` 本是为此而写，但从实际 token 数看**压缩效果有限甚至没生效**。调查顺序：
1. `build_compressed_context` 在 round ≥ 2 是否真的压缩历史，还是 passthrough
2. `spark_extractor.extract_sparks_from_message` 每条发言后跑独立 LLM call（日志里 "Extracted N spark(s)"）， 阻塞下一个 agent。改成 `asyncio.create_task` fire-and-forget 不等返回
3. `depth=standard` 默认 `max_tokens=4000/3000`，agent 倾向写满。可以降到 2000-2500 压缩单条发言长度
4. 深层方案：改 agent-centric context（每个 agent 只看自己历史 + 对手关键点摘要，不看全量），但这会动 agent system prompt 结构，工作量大

当前影响：功能可用但体感差。**Ken 明确说"记一下"不是让立刻 debug**，等 v0 KPAX 实装完后和其他 P2 一起做。

### `@cursor` P3 SSE 连接在 Round 1 快速重连 3 次（Debate 8 日志实证）
2026-04-18 凌晨 Ken 创建 Debate 8，日志显示前端在 3 秒内发了 3 次 `POST /api/debates/8/rounds/stream`。每次建立→断开，导致后端 `assign_models_to_agents` 的 `db.flush()` 未 commit 被 rollback，下次重新 shuffle 分配。不阻塞功能（第 3 次稳定下来后跑通了 moderator），但会让每次辩论的 model 分配非确定，debug 时混淆视听。怀疑是 `DebateSession.tsx` 的 `useEffect` 依赖 / cleanup 节奏问题，或 React StrictMode 双挂载。本地 dev 复现步骤：创建辩论 → navigate → 看后端日志 `rounds/stream` 调用次数。修复方向可能是：(a) `assign_models_to_agents` 改为 commit 而不是仅 flush；(b) 前端 `AbortController` 正确处理 SSE 取消而非快速重连。

### `@cursor` P2 补齐 `raw_question` 相关收尾（2026-04-17 根因修复后的遗留）
CHANGELOG 2026-04-17 "根因修复：用户原问题从创建辩论那一刻起就丢失了" 已落地主修复（迁移 012 + `Debate.raw_question` + `suggest_mode(user_question=...)` + 前端不再覆盖输入框）。遗留三项：
- 老 debates 的 `raw_question` 字段是 `NULL`，无法回填。**新辩论起才干净**。不需要 migration data，只需要在 Debate 详情页兜底显示 proposition 而不是 raw_question。
- `Discovery` / 跳转带 `hypothesis` 进来的辩论，`Debate.tsx:95` 的 useEffect 会自动填 proposition。这种情况下"Ken 的原话"其实是来自 Discovery 阶段的 AI 改写，不是本次他敲入的。短期可接受，长期建议在输入框上方加一个 hint "这是你刚才在 Discovery 里问的那个问题吗？可以编辑"。
- `generate_summary` 里用的是 `MODERATOR_PROMPTS` 裸模板，没注入 raw_question。长期建议从 `Debate.raw_question` 读回来拼进总结 prompt，保持"紧咬原问题"的一致性。

### `@ken` KPAX v0 本地端到端 curl 验证（§13.6 step 10 收尾 + final_verify）
cursor 2026-04-18 凌晨把 §13.6 十步代码完成了，但 cursor 没本地 Postgres + 真 LLM key，端到端 curl 验证需 Ken 亲手跑。详细清单 `CHANGELOG.md` 2026-04-17 凌晨条目最后一段（7 步）。关键点：(1) sync 路径 JSON 完整性 + options score 加起来 ≈ 1；(2) SSE 事件序列 `agents_ready → round_* → final` 能正常打出；(3) BYOM `llm_provider_override` 非 null → 501；(4) 两个 followup endpoint 必 501；(5) 真实问题 3 道抽检 evidence_ref.excerpt 是否真从 agent 原话截、recommendation 是否和 summary 呼应。异常报给 @cursor / @cc 分别回退 prompt / fallback 策略。

### `@cursor` 等 v0 KPAX 实装完后处理：Codex review 里 Ken 筛过的 3 条（其余忽略）
2026-04-18 凌晨 Codex 给了一份多维 review，Ken 评 70% 有用 / 30% 凑数。**Ken 已经逐条筛过**，这里只记**真要做的**和**反指令**：

**真要做（v0 KPAX 实装完后一起，估计 10-15 分钟）**：
1. **emoji 冲突验证**：`PROJECT.md §8` 写作规则禁 emoji，需要 `rg "[\u{1F300}-\u{1F9FF}]" -t md` 扫描所有 .md 文件，找出实际带 emoji 的（包括状态面板、CHANGELOG、next.md 等）。如果有，要么清掉，要么改 §8 把"禁 emoji"改成"特定区域允许"。Codex 提的状态面板漂移属于这条。
2. **KPAX.md / design.md / research.md 三文件职责边界**：`research.md` 有 `§kpax-platform-philosophy`、`design.md` 有 KPAX v0 deliberation room 设计、PRD 又散落在 `backend/routers/kpax_api_spec.md`——三个地方都能写 KPAX，未来必然冲突。要写一条 3 行规则塞进 `PROJECT.md §11`：哪种内容去哪个文件，违反时优先 trust 哪个。
3. **raw_question 跨两端口径对齐**（cursor 自补，Codex 没看到）：昨晚救起来的 `Debate.raw_question` 字段目前只有 AXL Moderator prompt 在用。KPAX v0 的 `kpax_renderers.py` / `kpax_pipeline.py` 还在按老逻辑从 `debate.proposition` 取问题。`/api/kpax/sessions/{id}/render` 出来的 evidence_ref 引用的"用户问题"会和 AXL Moderator 念的不一致。两套消费同一份 DB 但口径不一致，比 emoji 冲突更值得 P1。

**反指令（Codex 提了但 Ken 明确不要做）**：
- ❌ **不要拆分 PROJECT.md**：Codex 因为 PROJECT.md 塞了 13 节就提"拆分"，但这是 Ken 明确"文件越少越好"原则的结果。任何 reviewer 看到大文件都会本能提拆分，要抵制这个默认趋势。如果未来 cursor / codex / cc 自己也想拆 PROJECT.md，先回这条。
- ❌ **last-updated 字段漂移**（Codex 提的 metadata 洁癖）：5 分钟能做但不影响决策，归 P3 或干脆不做。

**Ken 没在 review 里说但 cursor 想补的更深的 4 条 risk**（暂不入待办，仅留底）：(a) 平台 vs 产品执行风险：KPAX 定位摇摆；(b) BYOM UX 没定，朋友测试时不知怎么用；(c) token 经济没设计：定价/换算/充值；(d) raw_question 跨两端口径（已在上面 P1 列出）。

**触发时机**：cursor v0 KPAX 实装完成（@ken 验收 §13.6 step 10 通过）后立刻做。不要在 v0 验证之前打断。

### `@codex` KPAX v0 §13.6 十步代码 PR review
重点审两项 cursor 自裁决策的合理性：(a) **stream 同 endpoint 分支** vs 独立 URL——评估 FastAPI OpenAPI 与 response_model 被自动跳过是否真 acceptable；(b) **wallet_address 窄解读**——评估 AXL 内部保留 `user_id` 是否会让 v1 wallet→user 映射层变脏。其次审 `kpax_pipeline.py` 的 DB 事务边界（`db.commit()` 只在结尾一次，中途 exception 依靠 Session context 回滚是否安全）、`kpax_renderers.py` 的 fallback 分支是否会掩盖真实 bug（semi-structured fallback 对用户是"降级"但对 QA 是"信号丢失"）、`token_ledger.py` RLock 修复是否足够（还是应该重构成"无锁嵌套"）。

### `@cursor` v0.1 把 `chat_completion` 真实 token usage 暴露出来（替换当前估算）
§13.6 step 3 的 `_estimate_cost` 是 $0.035/agent-round × 粗估 token 常量，不是真值。v0.1 必须：(1) patch `app/services/ai_provider.chat_completion` 返回 `(content, usage_dict)` tuple（或挂到 `chat_completion.last_usage` ContextVar）；(2) `kpax_pipeline` 累加真 usage；(3) `debate_trace.cost_usd` + `token_usage` 改真值；(4) `token_ledger.record_llm_cost` 传真值。风险：`chat_completion` 有 20+ 调用点，返回签名变动要全链路改。先做 ContextVar 方案（不改签名）。

### ✅ `@cursor` meta_01 rubric v0.1 独立审（出 v0.1-reviewed）—— 2026-04-17 完成（含 P0-3 量化代理补完）
落地：`experiments/emergence_decomposition/results/dry_run_20260416_165636/pilot_judge_rubric_v0.1-reviewed.md`。核心发现：维度 4"跨学科碰撞"对 A 组构成循环论证（P0-1）；维度 1 名"实质性 vs 套话"触犯写作规则反模式 1（P0-2）；0-3 级 anchor 区分度不足（P0-3，**5 维量化代理已补全 2026-04-17 下午**）；合成公式性质未显式声明（P0-4）；judge 一致性未校准（P1-3）。5 项 P0 建议 + 3 项 P1 + 3 项 P2。下一步 @codex meta-review（**重点审 P0-1 把维度 4 移出总分会不会让假设 (d) 测不到**），再 @ken 采纳。

### ✅ `@cursor` 修 5 处 KPAX monorepo 硬规则违反 —— 2026-04-17 完成（含 Ken 拍板路径 D 落地）
3 services + v1_analyze._chat_fn 4 处已修（新建 `kpax_svc/clients/llm_client.py` + 4 个 import 切换，smoke test 通过）。legacy 2 router Ken 2026-04-17 拍板**路径 D：冻结 + 例外登记**——新增 `PROJECT.md` §5.1 规则 #6 例外段 + 2 个 router + `kpax_svc/__init__.py` 全部加显式 deprecation 注释声明"新功能禁止进"。

- [x] `services/question_parser.py` → `kpax_svc.clients.llm_client`
- [x] `services/expert_builder.py` → 同上
- [x] `services/report_generator.py` → 同上
- [x] `v1_analyze.py::_chat_fn` 接入 llm_client（原 stub `NotImplementedError`）
- [x] **Ken 拍板路径 D**：legacy 冻结，`PROJECT.md` §5.1 例外段落地，3 个文件注释到位
- [ ] `@codex` review：`llm_client.py` + 4 处 import 切换 + `legacy_routers_assessment.md` + 路径 D 落地文件（analyze.py / report.py / `__init__.py` 注释 + PROJECT.md §5.1 例外段）

### `@cursor` legacy 路径 B 迁移复查触发器（KPAX v0 PRD 完成日启动）
路径 D 不是终点。触发条件到位后 @cursor 立即启动路径 B 迁移，同步删 legacy + 清 sys.path hack + 清例外登记。

- [ ] **前置 1**：`@cc` 出 KPAX v0 前端协议 PRD（含 SSE event schema + session state 模型）
- [ ] **前置 2**：`@cc` 触发 AXL `kpax_router.py` 从 mock 改真，含 `/axl/v1/debate/stream` (SSE) + `/axl/v1/debate/{id}/messages` (GET)
- [ ] 两前置就绪后：cursor 在 `kpax_svc/routers/v1_session.py` 重建 session state 流程走 HTTP
- [ ] 同步删 `routers/analyze.py` + `routers/report.py` + `services/context_collector.py` + `kpax_svc/__init__.py` sys.path hack
- [ ] 清 `PROJECT.md` §5.1 规则 #6 下的例外登记段
- [ ] 估算工期：前置就绪后约 1-1.5 工作日

### `@cursor` judge 一致性校准（pilot 前置，P1-3 升级到 P0）
rubric v0.1-reviewed 由 Claude Opus 设计，judge 按 spec §4.1 用 GPT-5 / Gemini 2.x。两者在 rubric anchor 执行上的一致性未验证。pilot 启动前先做小型校准。

- [ ] 取 3 场已有 baseline transcript（建议从 15 场 scaleup 里挑"低争议 / 中 / 高争议"各 1 场）
- [ ] 用 GPT-5 和 Gemini 2.x 各跑一遍 rubric v0.1-reviewed 打分（4 段 × 5 通用维度 × 0-3 + 2 段落特异维度 × 0-5）
- [ ] 计算两家 judge 的 Pearson 相关 + 段级 RMSE + 单维分歧点
- [ ] 判据：相关 > 0.85 → 单选主 judge 锁定（spec §4.1 要求）；相关 < 0.85 → rubric anchor 改写更通用化
- [ ] 输出 `experiments/emergence_decomposition/results/<dir>/judge_consistency_check_v0.1r.md`
- [ ] 估算成本：3 场 × 2 模型 ≈ $5
- [ ] `@codex` review 校准方法
- [ ] 依赖：需 Ken 先采纳 rubric v0.1-reviewed（否则校准对象不稳定）

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
- 依据：`PROJECT.md` §6 末尾 + `notes/journal/project-log-2026-04.md` 04-17 凌晨条目

### `@ken` 拍板：Lucas 量化闭环后续决策点
- [ ] A 步骤（judge.py 给现有 baseline 打分）何时启动？建议 cursor 修 monorepo 完成后立刻启动
- [ ] 人工评分锚点（C 步骤）由谁打？Ken + cursor 各一批？还是 Ken 独立？
- [ ] Meta-learner（E 步骤）是否从 Phase 3 开始纳入研究路线图？
- 依据：`notes/research.md#quantification-gap` 决策点

---

## 🟡 P1 —— 本周内

### `@ken` 视觉冲突 + 化身分级访问机制拍板（2026-04-17 化身体系落地遗留）
- [ ] **视觉方向 E 时间博物馆已拍板**（`notes/design.md §3.1`）但 v0 实装范围是什么？
  - 候选 E-A：v0 先做书房厅一个场景（现有 §3 内容），时间博物馆作为产品叙事写进 KPAX.md 但前端不实装多厅
  - 候选 E-B：v0 做书房 + 现代会议厅两个，支持基本切换
- [ ] 化身分级访问机制：争议化身（希特勒 / 毛泽东 / 敏感人物）出现前的闸门如何设计？
  - 候选：默认推荐池不含 → 用户主动搜索召唤 → 出场前学术声明
  - 具体 UI 和声明文案由 v1 前端 PRD 决定
- [ ] 在世名人化身用户免责条款：v1 前端上线前签不签？
- [ ] 依据：`notes/research.md §human-skill-distillation-layer` #7 IP/肖像边界 + `notes/design.md §3.1`
- [ ] 触发时机：v0 前端起步前必须闸 E-A vs E-B

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

### `@cursor` alchaincyf 13 名人 skill + 女娲工具 license 预审
- [ ] 逐一读 alchaincyf 仓库里每个 skill 的 LICENSE / README
- [ ] 对每个 skill 生成三列表：(a) 软件 license 是否允许二次使用/商用 (b) 所蒸馏名人是否在世 (c) skill 引用的源材料版权状态
- [ ] 输出 `notes/research/alchaincyf_skill_license_audit.md`
- [ ] 通过预审的 skill 入 v1 真人化身 shopping list
- [ ] 成本预估：半天
- [ ] 依据：`notes/radar.md` [2026-04-17] alchaincyf 条目 + `notes/research.md §human-skill-distillation-layer` #7.3

### `@cursor` + `@ken` v1 真人化身 shopping list（5 领域 5-7 位）
- [ ] 基于 alchaincyf license 预审结果 + LuBtc888 26 skill 扫描 + Ken 手动补充
- [ ] 按 5 领域分布各 1-2 位：**商业**（巴菲特 / Musk）/ **科技创业**（乔布斯 / PG）/ **投资 / 金融**（芒格）/ **哲学 / 思想**（柏拉图 / 王阳明）/ **科学**（费曼）—— 以上为候选，Ken 最终拍板
- [ ] 中西混合，避免押单一文化
- [ ] 每位化身产出一份简明档案：生卒年 / 代表性公开材料 / 典型适用问题类型 / 不适用问题类型 / 争议度评级（绿 / 黄 / 红）
- [ ] 输出 `notes/research/kpax_v1_avatar_shopping_list.md`
- [ ] 触发时机：alchaincyf license 预审完成后
- [ ] 依据：`notes/research.md §human-skill-distillation-layer` #8 v1

### `@cc` 时间博物馆 v1 多厅切换实装设计
- [ ] v0 只做书房厅，v1 候选增加：现代会议厅 / 东方庭院 / 广场-竞技场
- [ ] 场景推荐规则：看问题领域自动推荐厅，用户可手动切换
- [ ] 跨时代化身同台的视觉处理：每人穿自己时代服饰，不强行统一
- [ ] 触发时机：v0 发布后，根据朋友反馈决定
- [ ] 依据：`notes/design.md §3.1 时间博物馆`

### `@ken` KPAX.md slogan 候选 3 选 1
- [ ] cursor 2026-04-17 化身体系落地时起草 3 个 slogan 候选，Ken 拍板或自拟：
  - 候选 A：**"时间博物馆里的你的智囊团 —— 让柏拉图和 Musk 一起帮你拿主意。"**（形象 / 叙事感强）
  - 候选 B：**"不是跟一个 AI 聊天，是召集一个跨时代智囊团替你辩论。"**（差异化对比强）
  - 候选 C：**"把你问的这件事，帮你想透。"**（承袭 KPAX.md 原有承诺，低调克制）
- [ ] 拍板后 cursor 更新到 KPAX.md 头部
- [ ] 依据：`KPAX.md §一"化身体系"` 段

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
- [ ] 化身图标系统（座谈会 fallback UI / moderator 徽章 / 学科化身 / 真人化身 / 野生化身 三类视觉区分）
- [ ] 代币图标
- [ ] UI 按钮图标：分享、有帮助、拍肩膀
- [ ] 生成工具：**歸藏 Logo Generator Skill**（radar [2026-04-16]）— Gemini CLI 三步生成 SVG + 高级展示图
- [ ] 架构图配套：**Cocoon architecture-diagram-generator**（已 adopt）
- 依据：radar Cocoon + 歸藏 两条

### `@cc` KPAX 分享激励 loop 设计（v0 上线前必接）
- [ ] 每场辩论结束 → 生成 30 秒精华视频（化身辩论高光 + 最终判决，化身数按本场实际 3/5/7 位）
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

1. **做完一项**：从本文件删掉 + 在 `notes/journal/project-log-2026-04.md` 追加一条 `[YYYY-MM-DD @owner] 完成 XXX，结果/输出：YYY`
2. **新任务浮现**：加到对应优先级节，带 owner + 成功判据。**不要**把 TODO 藏在 research note 正文里
3. **任务被阻塞**：在 item 后加 `**阻塞**：原因` 一行，不要默默放弃
4. **降级/升级优先级**：改的时候在 journal 记一笔为什么改
5. **代码改动落地**：commit 后同步更新 `CHANGELOG.md`（代码层）+ `journal/project-log-2026-04.md`（决策层）
6. **实验状态变化**：同步改 `experiments/config/experiment_registry.json`

**反模式**：
- 在 research note 或 spec 里写 "TODO: ..." → 应该抽到本文件
- "等 Ken 回复" 类任务放 P0 → 应该放 P1 并标明 `@ken`
- 同一任务在多处重复登记 → 只在本文件，其他地方 reference 回来
