# Changelog

## 2026-04-28 — Final Answer Layer 产品校准（Phase 2.5）

### 背景

Phase 2 上线后 Ken 跑边缘问题（"如何设计科学的资金盘模型"）发现两个产品层问题：
1. **入口收窄目标函数**：`suggest_mode` 把开放建模问题压成单一目标函数（"优化资金盘参数以在统计审查下最大化寿命"），后续 agent 全程被这个 framing 牵偏
2. **答案层视觉太像综述**：4 段 UI 视觉权重太均，hero direct_answer 没拔出来，用户第一眼看不到"答案"

Ken 拍板两条永久硬约束：
- **不动 DB schema** —— Phase 2 的 4 字段保留，全部走 prompt + UI 展示层
- **道德层考量严令禁止** —— AXL/KPAX 第一原则不是道德审判，是产品化把问题想透答清楚。任何 prompt / academic reframing / moderator 指令 / final answer prompt 写之前先过道德层过滤器：含「危险/不该/不能/禁止/不应该/作恶」等价值判断词全部扣掉，限制只允许是产品目标 / 模型边界 / 可执行性边界

完整产品哲学定义见 `notes/design.md §axl-debate-mode-design > 产品原则：道德层严令禁止`。

### 改动清单（按优先级）

**2.5-A 入口反窄化**（`backend/app/services/debate_engine.py::suggest_mode` prompt）：
- academic reframing 加「中性建模式表达」硬约束：必须 frame 成「建立...的仿真模型 / 分析...之间的关系」，禁止「最大化 X / 规避 Y / 防止 Z」单一目标函数 framing
- 加「选择最宽产品化解读」要求：用户问题如有多种产品化解读路径（机制建模 / 仿真实验 / 审计检测 / 对抗推演 / 决策判断），academic reframing 应选最宽解读，让后续 agent 自己分流
- 加道德层过滤器硬约束：禁止「危险/不该/不能/禁止/不应该/dangerous/should-not/avoid/prevent」等价值判断词，敏感问题以机制建模处理，不拒答不说教

**2.5-D 前端答案层视觉压成 3 段**（`frontend/src/pages/DebateSession.tsx::FinalAnswerLayer`）：
- Phase 2 的 4 字段 UI（Hero + Why ① + Conditions ② + NextSteps ③）压成 3 段
- 段 1：Direct Answer hero（serif 26px + amber 2px 左 border）+ **why 紧贴下方作为轻量支撑说明**（小字号 14px / amber/55 灰度 / 单层 hairline 分隔，不抢主标题）
- 段 2：Key Conditions（圆圈 ① 对应 `conditions`）
- 段 3：User Takeaway（圆圈 ② 对应 `next_steps`）
- `FINAL_ANSWER_SUPPORTING` 数组从 3 项删成 2 项（去掉 why），重编号为 ①②
- 数据层 4 字段（`summary_direct_answer / summary_why / summary_conditions / summary_next_steps`）完全不动，DB / schemas / types 不动

**2.5-B debate moderator 中段压力**（`backend/app/services/debate_engine.py`）：
- `MODERATOR_ROUND_OPENERS` 拆出 R2 entry：moderator R2 收尾时**软提示**「下一轮可以开始向最小可跑模型收束（状态变量 / 可观测量 / 控制变量 / 终止路径 / 失效条件）」，邀请语气，不写死字段名
- `ROUND_OPENERS[3]` debate 模式 R3 加**硬指令**：「停止扩张学科领地，把贡献压到最小可跑模型」+ 5 个具体字段（state variables / observables / control variables / termination paths / failure conditions），允许用一句话跳过本学科确实贡献不了的字段
- R1 不动以保留探索空间

**2.5-C 数值依据待验证**（`backend/app/services/final_answer_layer.py` 两份 prompt）：
- 加 conditional 规则：当 `why / conditions / next_steps` 引用具体数值（百分比 / 阈值 / AUC / 时间窗口 / 论文年份 / 样本量）作为关键依据时，必须在数值后缀「（待验证依据）」/「(pending verification)」
- 没有引用具体数值时不强制加任何标注——保持自然，让 LLM 自己识别
- 不做硬性警告条，避免产品胆小化

### 不在范围

- **不动 DB schema / alembic / model**——Phase 2 的 4 字段保留
- **不动后端 schemas / 前端 types**
- **不重做 Phase 2 主体**（Final Answer Layer / mode 分叉 / G+F 抗雷同 全部保留）

### Ken 验证清单

1. **入口校验**：跑「如何设计科学的资金盘模型」，suggest_mode 应给中性建模式 reframing（如「建立资金盘机制的仿真模型，分析参与者流入 / 兑付承诺 / 信任传播 / 数据操控 / 审计信号 / 崩盘阈值与寿命分布之间的关系」），不锁目标函数、不带价值判断词
2. **前端首屏**：进辩论详情页只看 3 段 UI（Direct Answer hero + 灰色 why 轻量补充 / Key Conditions / User Takeaway），detailed analysis 默认折叠
3. **debate R3 收束**：跑一场 debate 看 R3 是否出现「最小可跑模型」5 字段结构，同时 R1/R2 仍保持探索性
4. **数值待验证**：跑一场带数值的辩论，final answer 中数值应自动后缀「（待验证依据）」；定性辩论不应出现警告条
5. **道德层过滤器**：所有改过的 prompt grep "危险|不该|不能|禁止|不应该|作恶" → 应该 0 hits

### 回滚路径（零 schema 风险）

每一项独立可回滚：`suggest_mode` prompt / `<FinalAnswerLayer>` 视觉 / `MODERATOR_ROUND_OPENERS` R2 entry / `ROUND_OPENERS[3]` 最小模型表 / `final_answer_layer.py` 数值规则——任意一项 git revert 即可，互不依赖。

### 关联

- `notes/design.md §axl-debate-mode-design > 产品原则：道德层严令禁止` — Ken 2026-04-28 拍板硬规则永久落档
- `notes/design.md §axl-debate-mode-design > Final Answer Layer` — Phase 2 产品哲学定义（不变）
- `notes/journal/project-log-2026-04.md` 2026-04-28 — Phase 2.5 上线时间线
- Phase 2.5 plan: `c:\Users\ken\.cursor\plans\final-answer-phase-2-5_b38e82c3.plan.md`

## 2026-04-27 — Final Answer Layer 上线（Phase 2）

### 背景

Phase 1 修复 free / debate mode 分叉后，Ken 2026-04-24 跑 Debate #14 发现真问题不在 mode 污染：**两种模式都没给用户答案**。debate 给 4 段研究综述、free 给六字段 spec，用户问"X 能不能"——系统都不正面回答。违反 KPAX 第 1 条「正面回答问题是基础」。

Phase 2 在两种模式之上加 Final Answer Layer——4 段直接回答（`direct_answer / why / conditions / next_steps`），加在 4 段综述**之前**生成，不替代任何现有字段。

完整产品哲学定义见 `notes/design.md §axl-debate-mode-design > Final Answer Layer`。

### 后端改动

**新建 `app/services/final_answer_layer.py`**：
- `generate_final_answer(debate, db)` 独立 LLM 调用（用 moderator 的 `assigned_model`），返回 4 字段
- 两份 prompt：`MODERATOR_FINAL_ANSWER_PROMPT_DEBATE` + `MODERATOR_FINAL_ANSWER_PROMPT_FREE`，4 段结构相同但 moderator 指令在两种模式下不同：
  - debate 模式：`why` 段优先选 R3 仍在被使用、未被反方在 R3 内重新质疑掉的论据；`conditions` 段必须含至少一条反方硬约束
  - free 模式：`why` 段标注每条来自哪个学科组合；`conditions` 段必须含 transcript 中的 falsification_conditions 聚合
- 共有硬约束：`direct_answer` 第一句必须以「能 / 不能 / 部分能 / 暂时不能」开头 + 1 句限定，禁伪明确
- LLM 输出严格 JSON，4 段任一为空整层 fallback 为 None

**改 `app/services/debate_engine.py::generate_summary()`**：
在原 4 段 summary 生成**之前**调 `generate_final_answer()`，结果写入 4 个新 DB 字段。失败 logger.warning 不阻塞主流程（resilience）。

**改 `app/models/debate.py::Debate`**：
新增 4 个 NULLABLE TEXT 字段 `summary_direct_answer / summary_why / summary_conditions / summary_next_steps`。

**新建 `migrations/versions/013_add_final_answer_columns.py`**：4 列 ADD COLUMN，回滚 DROP COLUMN。已 `alembic upgrade head` 应用。

**改 `app/schemas.py::DebateOut`**：4 个新字段输出到前端。

### 前端改动（`pages/DebateSession.tsx`）

把原 `SummaryBlock` 拆成三个组件：
- **`<FinalAnswerLayer>`**：Hero `direct_answer` 用 serif 26px 大字 + 左侧 amber 2px 边框。三段 supporting (`why / conditions / next_steps`) 用左 rail 圆圈数字 ①②③ + mono micro-label + ReactMarkdown 渲染。沿用 4-24 PM 报告气质（amber 单色 / 1px 细线 / 衬线大标题 / mono micro-label）。
- **`<DetailedAnalysis>`**：包住原来的 4 段综述（共识/分歧/开放问题/研究方向），由父级控制 `expanded` 展开状态。
- **`<SummaryBlock>` 外壳**：Top label band「DEBATE · FINAL ANSWER」 + `<FinalAnswerLayer>` + toggle 按钮（"展开详细分析 / 收起详细分析"）+ `<DetailedAnalysis>`（默认折叠）+ Footer caption。
- 兜底：Final Answer 缺席时 `DetailedAnalysis` 默认展开（用户至少能看到 4 段综述）。

**删掉**之前 4-24 PM 的占位文案：「VERDICT SLOT (awaiting prompt upgrade)」/「答案位（待 prompt 升级填入）」全部移除——产品已从占位状态切到实装状态。

`types/index.ts::Debate` 加 4 个新字段 `summary_direct_answer / summary_why / summary_conditions / summary_next_steps`。

### 设计依据

- `notes/design.md §axl-debate-mode-design > Final Answer Layer` — 产品哲学锚点，4 段结构 / 模式适配 / 硬约束 / 前端展示规则全部定型
- `notes/journal/project-log-2026-04.md` 2026-04-27 — Phase 2 上线时间线

### Ken 验证清单

1. 同题双模式对照：选同 3 学科 + 同原问题，分别跑 mode=debate 和 mode=free——两场都应有 Final Answer Layer 4 段
2. DB 字段核实：`summary_direct_answer / why / conditions / next_steps` 都非 NULL 且内容合理
3. 前端首屏：用户进辩论详情页只看 Final Answer 4 段，detailed analysis 默认折叠
4. Direct Answer 硬约束：第一句以「能/不能/部分能/暂时不能」之一开头
5. 4 段完整性：缺一段算未完成

### 回滚路径（零 schema 风险）

1. 4 个新字段允许 NULL → `alembic downgrade -1` 自动 DROP COLUMN
2. `final_answer_layer.py` 整模块删除
3. `generate_summary()` 中的 Final Answer 调用块删除
4. 前端 `<FinalAnswerLayer>` / `<DetailedAnalysis>` 拆分回归到原 SummaryBlock

每一项独立可回滚。

### 顺延项（Phase 2 完成后做）

- Phase 1.1: useEffect 优先级修复（Discovery 跳转 raw_question 保真）
- Phase 1.2: free Round 3 长度收紧

## 2026-04-24 下午 — free / debate 模式语义彻底分叉上线（Phase 1）

### 背景
Ken 2026-04-24 上午发现 Debate #12（mode=`free`）和 Debate #10/11（mode=`debate`）输出几乎一样。三方诊断（Ken + GPT + cursor）定位：
- 后端 `ROUND_OPENERS` / `MODERATOR_PROMPTS` / `MODERATOR_ROUND_OPENERS` 不看 mode，三套 prompt 两个模式共用
- Agent 使命段（`_build_agent_system_prompt` L381-384 zh / L446-447 en）无条件注入"参战 / 对手 / 不可或缺 / 质疑局限"，**对抗心智 80% 来自这里，两个模式都带**
- Mode 唯一硬分支是 `STANCE_PROMPTS["discipline_advocate"]`（约 80 字）——差异小到感知不到
- 前端 `Debate.tsx:153` 的 `useAcademic` 逻辑在用户**没点**"采用此改写"按钮时也会默默把 AI 改写版当 proposition 提交——`raw_question` 保真但 `proposition` 字段仍被暗中替换（Debate 12 数据库就是这个 bug 的产物）

Ken 拍板产品哲学（`notes/design.md §axl-debate-mode-design`）：`debate` 和 `free` 的区别**不是"是否有冲突"，而是冲突服务于什么**——debate 筛掉坏框架（破坏性检验 / 波普尔式），free 构建更好模型（建设性综合 / 库恩式）。`free` 不能变成"友好讨论"，必须是"建设性综合 + 保留硬分歧"，否则会产出漂亮但没骨头的综述。

完整决策过程和三方诊断保留在 `notes/journal/appendix-2026-04-24-debate-free-mode-semantic-fix-handoff.md`。

### 代码改动（5 处）

**改动 1 — agent 使命段按 mode 分叉**（`debate_engine.py::_build_agent_system_prompt`）
- 中文 L518-537 / 英文 L580+ 改成 `if mode == "debate": ... else: ...`
- `debate` 保留原文（参战 / 对手 / 不可或缺 / 质疑局限）
- `free` 改成 α 协作解题措辞：
  > 你代表 X 学科，和来自 Y Z 学科的学者**共同**把用户的问题推深。你的学科在这个问题上能贡献什么、看不到什么、在哪里会失效，都要诚实说出来。**不是要证明你的学科最重要，而是让用户拿到一份能跑的推演 spec**——能接的假设接上去，接不上去的根本分歧**必须标出来**而不是为了协作强行糊过去。

**改动 2 — 新增 `FREE_ROUND_OPENERS`**（`debate_engine.py`）
- Round 1：开场给学科视角 + 列 2-3 条假设 + 指出需要其他学科提供的假设 + 预期互补维度（不攻击）
- Round 2：**建设性挑战**（不是攻击）—— 指出变量缺失 / 假设脆弱 / 观测不可靠 / 失效条件 + **对每条挑战提出修正建议** + 防过度和谐出口（"如果另一学科假设在你学科看来从根本上不成立，不要为了协作强行接入。请标注为**根本分歧**"）
- Round 3：交付六字段**修正版 spec**（不是草案）—— `variables / assumptions / time_horizon / observables / falsification_conditions / next_steps` + 坚持标过的根本分歧

**改动 3 — 新增 `FREE_MODERATOR_PROMPTS` + `FREE_MODERATOR_ROUND_OPENERS`**
- System prompt 把身份从"导演 / 压力测试员"改成"协调者 / coordinator"：不评分、不点名"绕回舒适区"、不标"最有想象力"
- Round 2+ 收尾按**四层**组织：问题地图 / 可合成路径 / 待验证假设 / 根本分歧——**绝不把第 4 层强行合成进第 2 层**（保留冲突不强行统一）
- Round 1 结束语定调："各位是在**共建**一份可跑的 spec，不是在辩论。能接的接起来，接不上的根本分歧标出来。目标是让用户能把这份 spec 叉进实验板块去跑。"

**改动 4 — `run_round_stream` + `generate_agents` + `generate_summary` 按 mode 选 prompt 表**
- `run_round_stream` L1172-1201：读 `debate.mode`，free → `FREE_ROUND_OPENERS` + `FREE_MODERATOR_ROUND_OPENERS`；debate → 原表
- `generate_agents` L855-865：moderator system prompt 同样按 mode 分叉（free → `FREE_MODERATOR_PROMPTS`），moderator stance 从 `"moderator"` / `None` 改为 `"moderator"` / `"coordinator"` 以便后续追踪
- `generate_summary` L1349-1359：summary 阶段 moderator 心智也按 mode 分叉（保持 4 段 schema 不动，零 DB migration；coordinator 语气自然会倾向"可合成路径 + 根本分歧"语调）

**改动 5 — teammate prompt 按 mode 软化**（`_build_agent_system_prompt` L681+ zh / L720+ en）
- `debate` 保留原"同学科不同流派，不是应声筒 / 浪费一位学者的轮次"的张力措辞
- `free` 改成"同学科不同**分工**"（去"流派对抗"）+ 去"浪费轮次"的 zero-sum 措辞 + 改成"两块拼在一起就是 X 学科的完整贡献"
- 两种模式都保留 Prof 主干 / Assoc 实证边界的分化（防 G+F 修复的 P0 雷同倒退）

**改动 6 — 前端 `Debate.tsx::handleCreate` 去掉 `useAcademic`**
- 原 L153-158 的 `finalProposition = useAcademic ? academic : inputText` 改成 `finalProposition = inputText`
- 逻辑：用户点"采用此改写"按钮时 `applySuggestedProposition()` 已经把改写版同步写进输入框——此时 `inputText` 自然是改写版；用户没点 → 输入框是原话 → proposition 是原话
- 不只修 free 模式，debate 模式同样的"暗中替换 proposition"bug 一并修掉

### 验证

**Ken 手动测试路径**：
1. 前端 http://localhost:5173 新建辩论，选同样 3 学科（Complex Network Analysis / Opinion Dynamics / Complex Systems），同样问题
2. 跑一次 mode=free 跑一次 mode=debate
3. 预期输出**明显不同**：
   - debate：保留学科压力测试 / 互相攻击 / 各自磨最终答案 / 共识/分歧/开放问题/研究方向
   - free：共同推演 / 建设性挑战 / 六字段修正版 spec / moderator 分四层组织 / 根本分歧保留不合成

**DB 字段核实**（跑 `python scripts/show_debate_archive.py`）：
- `raw_question` 等于 `proposition` 当用户没点"采用此改写"（`proposition` 字段的暗中替换已消除）
- `mode=free` 的 agent `stance=None`（原有行为保留）

**产品哲学 self-check**（人工读 free 辩论 moderator 发言）：
- 不应出现：裁决 / 绕回舒适区 / 最有想象力 / 把第 4 层合成进第 2 层
- 应出现：问题地图 / 可合成路径 / 待验证假设 / 根本分歧保留 / 下一步推演

### 回滚路径（零 DB 变动，纯运行时 prompt + 前端 useState 逻辑）
1. 撤改动 4：`run_round_stream` / `generate_agents` / `generate_summary` 恢复不看 mode
2. 撤改动 1-3：删 `FREE_ROUND_OPENERS` / `FREE_MODERATOR_PROMPTS` / `FREE_MODERATOR_ROUND_OPENERS`，使命段 mode 分支恢复为无条件注入
3. 撤改动 5：teammate mode 分支恢复合并
4. 撤改动 6：前端 `finalProposition = useAcademic ? academic : inputText` 粘回

### 遗留与后续（`notes/next.md` P1 条目已更新）
- **P1 推演实验设计 v0.1 renderer**：free 模式 Round 3 六字段 output 就是这个 renderer 的雏形输入。下一步做一个独立 renderer 把 6 个 agent × 六字段合成用户可消费的 spec 卡片
- **P1 moderator 偏置多题调查**：G+F 阶段观察到 debate 模式可能有 Complex Systems 偏置——free 模式下 coordinator 心智是否缓解，需要多题跑后验证
- **P2 AI 味 pipeline 检查**：Ken 2026-04-24 明确降 P2，内容不变（引用密度 / 对称句式 / 学科边界自辩 / 数字修辞四项后处理）

## 2026-04-20 晚 — Phase 0 G+F 上线：同学科 Prof / Assoc 输出雷同的最小实验修复

### 背景
Ken 2026-04-20 给出完整总判决后点出 P0：Debate 10 实测同学科 Prof（claude-opus-4-6）和 Assoc（deepseek-chat）在 Round 2/3 产出**字数完全相同、开头一字不差**的内容（msg#82/83 = 3227 chars、msg#89/90 = 2423 chars），跨 LLM 都这样——直接破坏 AXL 多 agent 碰撞核心假设。

Ken 同步给出决策门框架（`notes/research/agent-twin-fix-decision-gate.md`）：不直接大重构，先做最小实验 G + F；`A1/A3/B1` 战略问题留 plan 模式处理。

基线数据（跑 `scripts/check_agent_twins.py 10`）：**9 个 pair-round 只有 1 个通过 D1 门槛**（len_diff ≥ 15% + ROUGE-L < 0.40 + 开头非一字不差）。学科 192 Round 2/3 ROUGE-L 高达 **0.975 / 0.990**（几乎全文相同）。

### 实现：G + F + teammate prompt 定位修正

**F：同 discipline 不同 LLM family 硬约束**（`_enforce_same_discipline_different_family`）
- 新增 `_model_family()` 把 LiteLLM slug 映射到 provider family（anthropic / openai / deepseek / google）
- `assign_models_to_agents` 结尾调用约束函数：若同学科两 agent 命中同 family，从其他学科找一个不同 family 的 agent 做**双向 swap**（保证 swap 后对方学科也不冲突）
- 若 pool 只跨 1 family（退化情况），记 warning 跳过——best-effort，不会 raise
- moderator 永不参与 swap

**G：Assoc 看同学科 Prof 的完整原文换成 3 列摘要**（`_summarize_teammate_message`）
- Assoc 发言前，触发一次**轻量 deepseek 调用**把同学科 Prof 的本轮发言压缩成三列：
  - **已覆盖点**（2-4 条，队友已明确说过——不要重复）
  - **被攻击点**（0-2 条，被其他学科质疑的地方——可辩护或换路径）
  - **待补点**（2-3 条，同学科能贡献但队友没覆盖的角度——Assoc 的主战场）
- 失败兜底：rule-based 抽 heading + bold 行（至多 8 条），永远不阻塞 round
- **只对同学科队友的发言做替换**，其他学科的发言保留完整原文（Assoc 需要engage 跨学科论点）
- 摘要在 `run_round_stream` 内有 cache（按 message_id），同一条 Prof 发言不重复抽
- `chat_completion` 显式指定 `model="deepseek/deepseek-chat"`，跳过 agent 自己的 assigned_model（摘要任务不需要 Prof 的模型）

**teammate prompt 重写**（`_build_agent_system_prompt` Zh + En 双语）
- 原文："你们是一队的，共同捍卫 X 的立场。你可以补充或深化他的观点"——这是触发"把 Prof 的说一遍"的 prompt 层诱因
- 改成"**同学科队友（不同流派，不是应声筒）**"定位：
  - Prof 偏主干理论 + 路径定义
  - Assoc 偏实证 / 案例 / 边界 / 失效条件 / 反例
  - 明确"你进场时会看到 Ta 的三列摘要，你的主战场是「待补点」和「被攻击点」"
  - 明确"如果你们说的是同一件事，就浪费了一位学者的轮次"
- **零硬约束**（没有"禁止 / 必须"字样，用身份定位 + 资源浪费框架引导分化）
- 英文 teammate prompt 同步重写

### 验证工具

**`scripts/check_agent_twins.py` 升级**（从诊断临时脚本升格为正式 D1+D2 工具）
- D1 相似度：字符 3-gram Jaccard + 字符级 LCS ROUGE-L（首 200 字）+ 字数差 + 开头 100 字严格 identical 硬告警
- D2 变笨监控：每条平均字数 / heading 数 / 引用条数 / sparks 总数
- 支持 `python scripts/check_agent_twins.py <debate_id>` 查单场
- 支持 `--compare <other_id>` 跑改前 vs 改后对比，输出 Δ% 和"变笨"标记

### Ken 的测试流程

1. 打开 http://localhost:5173，新建 Debate 11：
   - 同样的 3 个学科（Complex Network Analysis / Opinion Dynamics / Complex Systems）
   - 同样的问题"怎么科学地改变世界"或"我想知道怎么统治世界"
   - 同样的 depth=standard
2. 等辩论跑完（~10-15 分钟）
3. 跑对比：
   ```
   cd projects/knowledge-graph/backend
   python scripts/check_agent_twins.py 10 --compare 11
   ```
4. 看 4 个指标是否全部达到门槛：
   - D1: pair-round 通过数 1/9 → 至少 6/9
   - D2 变短: 平均字数不应下降 > 40%
   - D2 变浅: heading 数不应下降 > 50%
   - D2 变平: sparks 总数不应下降 > 50%

### 回滚路径（如果效果不及预期或变笨）
1. 回退 `_summarize_teammate_message` 调用：改回 `body = f"[{_agent_label(nm, debate)}]: {nm.content}"`——纯运行时改动
2. F 约束回退：`_enforce_same_discipline_different_family` 调用注释掉
3. teammate prompt 回退：把原"补充或深化"版本粘回
4. 全程无 DB / schema 改动，回滚成本极低

### 遗留（进 `notes/next.md` P2）
- G 新增一次 deepseek 摘要 LLM call，每个 Assoc 发言前多 ~10-20s 延迟。如果 D2 变笨没问题但 context token 爆炸的 P2 问题要合并处理，下次考虑把摘要改成"摘要函数复用 moderator 每轮末尾的缺口维护"（避免重复 LLM call）
- D1 的 `prefix_100_identical` 硬告警对 Debate 10 Round 2/3 未触发（因中文 vs 英文引号差），但 ROUGE-L 0.97+ 触发了软告警。下次可调成 ROUGE > 0.95 或 Jaccard > 0.80 当硬告警

## 2026-04-18 凌晨 — Moderator 凭空编了 5 个用户没选的学科（根因：它看不到在场学科）

### 现象
Ken 创建 Debate 9，选的学科是 niche 子学科：
- Complex Network Analysis Techniques
- Opinion Dynamics and Social Influence
- Complex Systems and Dynamics

但 Moderator 开场吐出来的方向菜单是 5 个通用大学科：**物理学、计算机科学、政治学、哲学、经济学**——**一个都对不上**用户选的。

Ken 的怒点："我都说了多少遍不要交叉了，那是实验的选择！"——辩论阶段必须严格用用户选的学科，不能再由 AI 自由发挥"猜哪些学科相关"。

### 根因
诊断脚本读 Debate 9 的 `debate_agents.system_prompt` 原文，发现 Moderator 的 prompt 从头到尾**没有任何地方写了"在场是哪几个学科"**。只有：
- 用户原话
- 学术化改写
- 一句"（没有预先准备的方向菜单；第 1 轮开场请自行简述每个在场学科可能关心的角度，但不要指派。）"——**但从未告诉它"在场学科是什么"**

学者的 system_prompt 里有 `all_discipline_names`（通过 `topic = " x ".join(...)` 注入），所以学者知道队友是谁。**Moderator 完全漏掉了这块**——我 2026-04-17 写 `generate_agents` 拼 moderator prompt 时的疏漏。

LLM 在没有学科列表的情况下，从"怎么科学的统治世界"这种大问题反推"可能相关的学科"，自然拉出物理/计算机/政治/哲学/经济这 5 个通用大学科。和 Ken 选的 3 个 niche 子学科毫无关系。

另一个同类风险点：`suggest_mode` 的 prompt 里虽然写了 `"discipline": "<exact name from the list>"`，但约束语气太软，LLM 在某些情况下也会自由发挥。虽然 Debate 9 没踩到（Ken 没点 AI 推荐，`suggested_dimensions` 是 None），但是个定时炸弹。

### 代码改动

**`app/services/debate_engine.py::generate_agents` — Moderator prompt 注入硬约束**：
- 新增 `## 本场在场学科（硬约束）` 段落，把 `names_display`（中文时）或 `names_en`（英文时）逐行列出
- 附上 3 条硬性规则：
  1. 方向菜单每项必须且只能对应上述学科之一，**严禁引入其他学科名**（用户没选的"物理学""哲学"等**一律不准出现**）
  2. 方向菜单 ≠ "这问题可能相关的学科"，而是 "**在场这几位学者各自能切什么角度**"
  3. niche 子学科就用子学科名，不准擅自泛化成一级学科
- 英文版同步

**`MODERATOR_ROUND_OPENERS[1]` 同步**：
- 原文"列出每个学科可能的 2-3 个切入角度"改成"**且只能列 system prompt 里「本场在场学科」那一节中的学科**，严禁引入列表外"
- "不准出现的学科"举例：物理学 / 哲学 / 经济学（用户没选就不准提）

**`elif proposition:` 分支（没有 raw_question 的老路径）也补上**：
- 在旧 proposition-only 的 mod_prompt 里加了"围绕上面「本场在场学科」那几位展开——不准引入列表以外的学科"
- 不让旧流程重蹈覆辙

**`suggest_mode` prompt 硬化约束**：
- 学科列表改成逐行展示（每行 `- <name>`），强调 "use these EXACT names, do not paraphrase, do not substitute with parent-umbrella names"
- 新增 `HARD RULES` 段落，4 条：
  1. `discipline` 字段必须字符级匹配传入列表
  2. 禁止引入列表外学科（举例 Physics / Economics / Philosophy）
  3. niche sub-field 用 niche 名，不准泛化（举例 "Opinion Dynamics and Social Influence" 别写成 "Sociology"）
  4. `suggested_dimensions` 条目数必须等于传入学科数，一一对应

**`suggest_mode` 后端兜底校验**：
- 即便 LLM 依然乱来，Python 层会在合并结果前对每个 dim 做 `if disc_str not in allowed: continue` 过滤
- 被过滤的条目记 `logger.warning` 输出，方便事后 debug LLM 守规情况
- 过滤后如果 cleaned 为空则 `suggested_dimensions = None`（不给前端半吊子菜单）

### 影响
- Debate 9 及之前的老辩论数据不动（moderator 的 system_prompt 已经写进去了，是错的，但数据保留作为"修复前样本"）
- 新创建的辩论：Moderator 一定能看到在场学科列表，硬约束下无法再编造学科名
- suggest_mode 多了一层 Python 兜底，即使 LLM 偶发漂移也不会污染 debate 数据

### 验证步骤（给 Ken）
重新建一次辩论，选同样的 3 个 niche 学科：
- Complex Network Analysis Techniques
- Opinion Dynamics and Social Influence
- Complex Systems and Dynamics

Moderator 开场的方向菜单**只能**是这 3 个子学科名（原文），不准出现物理/计算机/政治/哲学/经济这种大学科。如果又出现了，说明硬约束失败，需要更猛的 prompt。

## 2026-04-18 凌晨 — Ken 实测打出两个追加 bug，根因各自清晰

### 背景
Ken 按前面的"根因修复"流程走了一遍，从 Discovery 输入"怎么科学地改变世界"→ 跳转辩论页 → 点开始辩论。结果两个新问题：
1. Moderator 开场念的"用户原话"根本不是"怎么科学地改变世界"，而是 Discovery AI 生成的那段长改写"创建政策、技术或文化规范在国家间扩散的预测模型..."
2. Moderator 发完开场后，学者一个都没发言，前端卡在"[Agent 们正在思考...]"

数据库查 Debate 8：
- `raw_question` = Discovery 改写版，**和 proposition 完全一样**
- `messages` 表只有 1 条（moderator 的开场），6 个学者 0 条

所以两个都是实打实的 bug，不是感觉问题。

### 问题 1：Discovery → Debate 跳转时用户原话被 AI 改写覆盖

**根因**：`frontend/src/pages/Debate.tsx::useEffect`（L94-104）的优先级：
```tsx
const candidate = navCtx.hypothesis || navCtx.coreTension || navCtx.direction || navCtx.discoveryQuestion || "";
```
`hypothesis` 是 Discovery 阶段 AI 把用户原话深化出的研究方向（长句），`discoveryQuestion` 才是 Ken 实际敲的那句话。优先级倒置 → proposition 输入框里永远是改写版 → `handleCreate` 里 `raw_question = proposition.trim()` → **Ken 的原话从来没进过任何后端字段**。

昨晚 CHANGELOG 里写"长期建议加提示"的那一条遗留，Ken 实际体验下来一点都不可接受，必须当下修。

**修复**（`Debate.tsx`）：
- `handleCreate` 里：`rawUser = (navCtx.discoveryQuestion || "").trim() || proposition.trim()`。Discovery 原话优先作为 `raw_question` 发给后端，**不管用户有没有编辑过输入框**。
- `proposition`（学术版）用于展示给学者作为"学术化改写"，`raw_question`（用户原话）用于 Moderator 开场和每个学者 system prompt 的"必须紧咬"段落
- 在输入框**上方**新增 amber 色提示条：「你的原话："怎么科学地改变世界" — 会原样传给学者；下面输入框里是 Discovery 的学术化改写，可编辑」
- 让 Ken 从进页面第一眼就看到「原话 vs 改写」的区别，不会再混淆

### 问题 2：辩论卡在 moderator — free plan quota 把学者挡在门外

**根因**：Ken 的 subscription 是 free plan，`allowed_models=["deepseek/deepseek-chat"]`（见 `plan_config.py`）。但 `.env` 里配了：
```
DEBATE_MODEL_PRO=gpt-5.4
DEBATE_MODEL_CON=deepseek/deepseek-chat
DEBATE_MODEL_MODERATOR=anthropic/claude-opus-4-6
```
`assign_models_to_agents` 给 7 个 agent 随机分配这三种之一。每个学者 `chat_completion` 进入时，`token_quota.py::validate_model(sub, "gpt-5.4")` 看到 gpt-5.4 不在 allowed_models 里，**直接抛 `HTTPException(403)`**。

关键陷阱：这个 403 是在 `chat_completion` 的 retry 循环**外面**抛的（`validate_model` 在 try 块之前），不走 retry，直接上抛到 SSE 的 `event_generator.except`，yield `error` 给前端，`run_round_stream` 彻底中断。

Round 1 moderator 恰好拿到 deepseek-chat 跑通（日志里看到 719 tokens 成功），下一个学者分到 gpt-5.4 就 403 → 整个 SSE 挂了。前端看到的是"Agent 们正在思考..."，实际上后端已经把 round 1 判定结束了。

这是 `auth_bypass_dev_mode` 和 token_quota 没有对齐的设计漏洞：auth 层面 Ken 是"绕过登录的 dev 账户"，但 subscription 层面他仍然是 free plan。Ken 自己用自己的 .env 里的模型做本地测试，却被自己订阅 plan 卡死。

**修复**（`app/services/token_quota.py`）：
- `check_quota(user_id, db)` 首行：`if settings.auth_bypass_dev_mode: return sub` — dev 模式跳过 monthly_token 上限和 status 检查，但仍确保 sub 存在
- `validate_model(sub, requested_model)` 首行：`if settings.auth_bypass_dev_mode: return requested_model or sub.preferred_model or "deepseek/deepseek-chat"` — dev 模式下任何 `.env` 配的模型都放行，不检查 allowed_models
- `record_usage` 不动 — token 计数仍正常累加，方便 Ken 观察实际消耗；只是不再作为 throttle 依据

**`app/main.py` 启动 warning 同步升级**：原文"ALL AUTH CHECKS ARE DISABLED" 改成 "ALL AUTH + QUOTA CHECKS ARE DISABLED"，多一行明确"Token limits and allowed_models are bypassed"，部署前漏关的提醒更醒目。

### 设计权衡
为什么是"dev bypass 短路 quota"而不是"把 Ken 升级到 pro plan"或"改 .env 回全 deepseek"：
- **升级 Ken 到 pro**：治标不治本。任何新 dev 账户都会重新踩坑，而且产品层面"pro"是付费用户概念，不应和 dev 环境绑定
- **改 .env 回全 deepseek**：Ken 明确要求 `DEBATE_MODEL_PRO=gpt-5.4`、`MODERATOR=claude-opus-4-6`，测试的就是多模型差异。改回 deepseek 等于放弃测试目标
- **dev bypass 统一短路**：和之前 auth bypass 同一个哲学——dev 模式下产品层约束全部解除，一个 env flag 进出。生产部署关了就自动恢复

### 遗留
- **SSE 快速重连**：日志显示 `rounds/stream` 被前端 3 秒内发了 3 次，可能是 React StrictMode 双挂载或 `DebateSession` useEffect cleanup 节奏问题。每次断开导致 `assign_models_to_agents` 的 `db.flush()` 未 commit 被 rollback，下次重 shuffle。不是阻塞点但会让 model 分配非确定。记到 `notes/next.md`，后续低优跟进。

## 2026-04-17 — 根因修复：用户原问题从创建辩论那一刻起就丢失了

### 现象（Ken 发现）
Ken 在前端输入"怎么科学地统治世界"→ 点"✨ AI 推荐"→ 看到 Moderator 在辩论里用的是"研究全球治理模型：比较中央集权、联邦制、多层级治理…"——**完全不是他问的那句话**。一开始我以为是 Moderator 的 prompt 问题（把它从"综述员"升级为"导演"），但 Ken 追问之后定位到更底层：

> "你得说啊！得结合的看啊：用户 XX 登录，问了个问题，这个问题用学科视角看包含了 XXX——你懂吗？"

### 根因（不是 prompt，是数据流）
翻 `debate_engine.py::suggest_mode`：

```python
# 修复前
prompt = (
    f"Given these academic disciplines: {', '.join(discipline_names)}\n\n"
    "Which format would be more productive for their interdisciplinary exchange?\n"
    ...
)
```

**`suggest_mode` 从头到尾只看学科名，根本没传用户的问题进去**。所以它返回的 `suggested_proposition` 是 LLM 凭学科组合**瞎编**的。

然后前端 `Debate.tsx:126`：
```tsx
if (s.suggested_proposition) setProposition(s.suggested_proposition);
```

**把输入框里 Ken 的原话直接覆盖掉**。从这一刻起，Ken 敲的"怎么科学地统治世界"在系统里**不再存在任何地方**——Moderator、每个学者、所有日志、所有数据库字段里都只剩 AI 瞎编的那句。Moderator 行为本身其实是对的，它在忠实处理一个被污染的 proposition。

这是 AXL 自设计之初就埋的坑，不是我今天引入的回归。但它直接让"Ken 用自己话发起研究"这个核心产品体验失效，必须根治。

### 设计目标
- **原问题永不丢失**：用户输入一旦提交，必须在数据库里有一份不可覆写的 `raw_question`
- **学术改写 = 可选辅助**：前端的"AI 推荐"当然还有价值，但只能作为**可选采用**的学术化建议展示，**不允许静默替换用户输入**
- **Moderator 职责从"派活"转"介绍人"**：Round 1 原话引用 + 展示方向菜单，**不再强制分派"恰好 1 个角度"**（Ken 明确反对：「不应该规定切入的入口，这样就会变得非常窄」）
- **方向菜单由 AXL 自己生成，不让 Moderator 即兴造**：前端 `suggest_mode` 阶段就把"每个学科可能切入的 2-3 个角度"连同学术改写一起返回，存进 `Debate.suggested_dimensions`

### 代码改动

**数据库层**（迁移 `012_add_debate_raw_question.py`）：
- `debates.raw_question TEXT NULL`：存用户输入的原话，不被任何后续流程覆盖
- `debates.suggested_dimensions TEXT NULL`：存 `suggest_mode` 返回的维度菜单（JSON 字符串）

**`app/services/debate_engine.py::suggest_mode`**：
- 签名加 `user_question: str | None = None`
- Prompt 首段直接把用户原话三引号展示给 LLM，并强调 "keep this EXACTLY — do not rewrite it away"
- 返回字段新增 `suggested_dimensions: [{"discipline": ..., "angles": [...]}]`，2-3 个角度/学科
- 明确告诉 LLM：这是"MENU, not an assignment"
- 若没有 `user_question`，LLM 被硬约束不得编造 `suggested_proposition`（设为 null）

**`app/services/debate_engine.py::_build_agent_system_prompt`**：
- 新增参数 `raw_question`
- 学者 system prompt 现在同时展示两份：
  - `## 用户的原问题（必须紧咬）`：引号原话 + "即便有学术化改写，每一轮都必须回到这句原话本身"
  - `## 学术化改写（辅助理解，不替代原问题）`：仅当 raw_question 与 proposition 不同才展示
- 中英文双语同步

**`app/services/debate_engine.py::generate_agents` → Moderator 注入块**：
- 新增参数 `raw_question` / `suggested_dimensions`
- Moderator system prompt 拼上：
  - 用户原话（三引号包裹，强调"必须原话引用，不要改写掉"）
  - 学术化改写（仅当与原话不同）
  - 已经准备好的**方向菜单**（学科 → 角度列表），明确标注"仅供参考，学者自选"

**`MODERATOR_PROMPTS` + `MODERATOR_ROUND_OPENERS[1]`**：
- 彻底重写 Round 1 指令：从"改写问题 + 分派 1 个角度"改为"原话引用 + 展示学术改写 + 展示方向菜单 + 保护自由"
- 明确"这是选项，不是任务派单——各位挑自己想切的"
- 删除原先"给每个学科分派恰好 1 个切入角度"的表述（Ken 反对："不应该规定切入的入口"）

**`app/routers/debate.py`**：
- `DebateCreate` 接受 `raw_question` + `suggested_dimensions`
- 若 mode=debate 且前端没传 raw_question，用 proposition 回填（向后兼容）
- `suggested_dimensions` 序列化为 JSON 字符串落库
- 把原话和维度菜单同时透传给 `generate_agents`
- `SuggestModeRequest` 新增 `user_question`，路由透传到 `suggest_mode`

**`app/schemas.py`**：
- 新增 `DimensionSuggestion` Pydantic 模型
- `DebateOut.suggested_dimensions` 用 `field_validator` 做字符串 → list 反序列化
- `ModeSuggestion` + `DebateCreate` 都暴露维度字段

**前端 `frontend/src/pages/Debate.tsx`**：
- `handleSuggestMode` 现在传 `proposition`（Ken 的输入）过去；**不再调用 `setProposition(s.suggested_proposition)` 覆盖输入框**
- 新增建议卡片 UI：展示学术改写（带"采用此改写替换输入框"按钮，非自动）+ 方向菜单（按学科 · 角度 列出）
- `handleCreate` 传 `raw_question`（用户原话）、`proposition`（采用则是改写版，否则等于原话）、`suggested_dimensions`（若 AI 推荐已运行）

**前端 `client.ts` + `types/index.ts`**：
- `suggestMode(disciplineNames, userQuestion?)` 签名扩展
- `createDebate` 扩展接受 `raw_question` + `suggested_dimensions`
- 新增 `DimensionSuggestion` type，`Debate` / `ModeSuggestion` 暴露新字段

### 验证
启动后端（auth bypass 下），直接 `POST /api/debates/suggest-mode`，body：
```json
{"discipline_names": ["Political Science","Sociology","Economics"],
 "user_question":"怎么科学地统治世界"}
```
返回：
- `reason_zh` 明确提到"用户的问题是一个具体（尽管极端）的问题"——证明原话进入了 LLM
- `suggested_proposition`: `"What are the most effective mechanisms for establishing and maintaining global hegemony?"`——是原话的学术化改写，**不是**瞎编
- `suggested_dimensions` 三个学科各 2-3 个具体角度，比如政治学拿到"权力与合法性理论 / 地缘战略 / 历史霸权对比"

### 产品影响
- Ken 下次再输入"怎么科学地统治世界"→ 点 AI 推荐 → **原话还在输入框里**，下方卡片展示学术改写（可选采用）+ 每学科维度菜单（仅展示）
- 创建辩论后，Moderator 第 1 轮第一句就是「用户 Ken 问的是："怎么科学地统治世界"」——**原话直接摆在学者面前**
- 学者 system prompt 里永远同时看得到原问题和学术改写，任何一轮都必须"紧咬原话"
- Moderator 不再派活，只介绍方向菜单。「**这是选项，不是任务**」

### 遗留与下一步（见 `notes/next.md`）
1. 历史 debates 没有 `raw_question`（新增字段默认 `NULL`），无法回填——只能从数据起新辩论开始干净
2. AXL 还有另一个入口（`Discovery` / 跳转进来带 `hypothesis`）——`Debate.tsx:95` 的 `useEffect` 自动填充 proposition 也属于"用户没主动输入"情况；这类入口下 `raw_question` 会等于 navCtx 里的改写版，短期可接受，但长期最好有明显的"这是你刚才在 Discovery 里问的原话吗？可以编辑"提示
3. `generate_summary` 用的是 `MODERATOR_PROMPTS` 裸模板，不带 raw_question——目前总结不会 drift 太多，但长期建议同步注入，保持一致性

### Ken review 后补的两个收尾（主修复的连带遗漏）

**中优：Zep 共享上下文还在按"学科名拼接标题"检索，和问题脱节**（`debate_engine.py::_retrieve_zep_contexts`）
- 症状：我把主逻辑改成"围绕用户原问题"，但 shared context 的 `topic = debate.title` 仍然只拿到 `"政治学 × 社会学 × 经济学"` 这种拼接标题去 Zep 查，打掉了"问题中心化"改动的一截
- 修复：改成 `raw_question > proposition > title` 三级回退。Zep 现在会用用户原话去检索共享知识
- per-agent 检索仍按学科名（`agent.discipline.name_en`）——这个合理，学科特定知识确实应该按学科查

**低优：Round 1 流式进度条 `total_speakers` 少算 1 个**（`routers/debate.py::next_round_stream`）
- 症状：之前 moderator 在 Round 1 不发言，`total_speakers` 特意排除它；这次根因修复把 moderator 改成 Round 1 第一个发言（见 `_order_agents_for_round`），但 SSE 路由里那段排除条件忘删。结果 Round 1 前端进度显示 `1/N` 到 `N/N` 时最后会冒出第 `N+1` 条
- 修复：直接 `total_speakers = len(debate.agents)`，所有轮次所有发言者都算上

## 2026-04-17 — Dev-only 认证旁路开关（`AUTH_BYPASS_DEV_MODE`）

### 背景
Ken 要在前端测改完 prompt 后的辩论效果（问题："我想统治世界，怎么做"），但前端点"开始辩论" → `POST /api/debates` → **401 Not authenticated**。DB 里只有 1 个账号 `ken@klesa.com`（已验证），Ken 无活跃 session，登录流程卡住了产品验证。

Ken 明确指示："直接把登录的先断开，后面再加上登录的逻辑"——v0 个人测试阶段，auth 暂时不是重点。

### 设计目标
- **不改路由、不改业务代码**：所有受保护 endpoint 继续写 `Depends(get_verified_user)`，一行不动
- **一个 env 开关搞定开关**：`AUTH_BYPASS_DEV_MODE=true` 开，`false` 或删除该行即恢复
- **生产安全默认**：`Settings` 里默认 `False`，不会因为代码误合并到生产而裸奔
- **足够大声**：启动时打 70 字符 `=` 包围的 WARNING，防止忘关

### 代码改动

**`app/config.py`**：`Settings` 新增字段
```python
auth_bypass_dev_mode: bool = False
```

**`app/services/auth.py`**：新增私有 helper + 三个 dependency 首行短路
- 新增 `_dev_bypass_user(db)`：开关开启时返回 DB 里 `id` 最小的 user；关闭时返回 `None`
- `get_current_user / get_verified_user / get_optional_user` 三个函数首行都调 `_dev_bypass_user(db)`，非 `None` 就直接 `return`，不再 decode JWT 也不查 `email_verified`

**`app/main.py`**：启动时若开关为 `True`，打 7 行 WARNING 包围框，明确警告"不要部署"+"如何恢复"

**`.env`**：写入 `AUTH_BYPASS_DEV_MODE=true`，带 5 行注释说明"MUST set back to False before deployment"

### 恢复登录的单步操作
```
# .env 里改一行 或 删一行：
AUTH_BYPASS_DEV_MODE=false
# 然后重启 uvicorn
```
不需要回滚任何代码。

### Windows 踩坑
1. **uvicorn `--reload` 在 Windows 不可靠**：改 `config.py + .env` 后 WatchFiles 说 reload 了，但 worker subprocess 实际仍用旧 settings（新 python 进程 `print(settings.auth_bypass_dev_mode)` 返回 `True`，但 HTTP 请求仍被 401）。
   **解法**：硬重启——`taskkill /PID <reloader_pid> /T /F`（/T 杀进程树），然后重启 uvicorn。
2. **之前踩的坑**：`Stop-Process -Force` 只杀父进程，子 worker 继续 listen 端口。这次用 `taskkill /T /F` 杀进程树才彻底。

### 验证
- ✅ `AUTH_BYPASS_DEV_MODE=True` 的启动 WARNING 出现在日志里（70 字符包围框）
- ✅ 无 token `GET /api/subscription/me` 返回 200，内容是 `ken@klesa.com` 账号的订阅状态（以前应该 401）
- ✅ `python -m py_compile` + basedpyright 0 errors
- ⏳ Ken 在网页端重跑辩论效果待验证（现在可以直接点"开始辩论"）

### 未改动
- KPAX 新 endpoint（`/axl/v1/analyze/*`）本来就没挂 auth dependency，本次不受影响
- JWT 签发 / 登录 API / Google OAuth 代码**原样保留**，只是被短路了。恢复就是关 env 变量。
- 不改 `get_verified_user` 的 403（verified 检查）逻辑——bypass 在其之前，所以无 email 验证也能用

### 相关 handoff
承接 [AXL 辩论没回答问题](6e9c3252-4fa5-485e-aedd-377bc707ea97)；绑定 `notes/next.md` 的"Ken 待办"栏需要一条：**上线前记得关 `AUTH_BYPASS_DEV_MODE`**。

---

## 2026-04-17 — Debate prompt 中文词准确性修正（紧跟上一条）

### 背景
Ken 审查上一条（Moderator 导演化）时直接打回两处明显的翻译腔：
- "下一轮**该追什么**" —— "追"在中文里是打猎/追债的动作，不是讨论
- "不奖励**合规**" —— "合规"在中文=法务/监管术语（regulatory compliance），和 prompt 想表达的"照本宣科"完全无关

Ken 的原话："这些词的准确性你完全不在乎吗？"——指的是我把英文原词（chase / compliance）机械搬运过来，没做中文语感校对。

### 根因
我写中文 prompt 的惯性是"先用英文想一遍，再往中文套"。句法对上了就没再朗读一遍检查搭配是否中文本来有这种用法。这是 AI 生成中文的典型失真模式，也是 KPAX/AXL 产品输出的直接威胁——prompt 里每个词都在"调教 LLM 看见什么世界"。

### 代码改动（`projects/knowledge-graph/backend/app/services/debate_engine.py`）

Moderator 系统 prompt + Moderator Round 1 opener + Moderator 收尾 opener + Round 2/3 agent opener 全部通读重校，改了 14 处词：

| 原词（翻译腔） | 改后 |
|---|---|
| 下一轮该追什么 / 必须追什么 | 下一轮应该聚焦什么 / 下一轮聚焦什么 |
| 不奖励合规 | 不奖励循规蹈矩 |
| 改写成可操作的形态（×2 处） | 改写成具体能回答的形式 |
| 漂进「学科综述」模式 | 滑进「学科综述」的套路 |
| 谁滑进了学科自嗨 | 谁绕回了本学科的舒适区 |
| 攻击角度 | 切入角度 |
| 可以跨线 | 可以跨学科 |
| 谁在漂 | 谁偏了题 |
| 最意外 | 最出人意料 |
| 最有承诺的版本（committed 直译） | 最坚定的版本 |
| 把问题改写、给了你的学科一个角度 | 改写了问题，给你的学科指派了一个切入角度 |
| 你的领域**会**怎么说 | 你的领域会怎么看、怎么做、怎么预测（去掉不自然的 bold 强调） |
| 具体能回答的形式——具体到可以想象怎么回答它 | 具体能回答的形式——要具体到让人能想象怎么回答它（消重复） |

英文 prompt 不改（`reward imagination, not compliance` 在英文里是通顺的固定搭配）。

### 自我约束
后续写中文 prompt 强制加一步：**写完后自己中文朗读一遍**，听到任何"这不是人话"的搭配立即改。不等 Ken 挑出来。

### 验证
- `python -m py_compile app/services/debate_engine.py` ✓
- basedpyright 0 errors ✓
- 运行时行为未变，只是词层面的修正，不影响上一条 A+B+C 的结构改动

### 相关 handoff
承接 [AXL 辩论没回答问题](6e9c3252-4fa5-485e-aedd-377bc707ea97) 同一轮次。

---

## 2026-04-17 — AXL 辩论把 Moderator 从"综述员"升级为"导演"（A+B+C 三改）

### 背景
Ken 测试 KPAX/AXL 时问"怎么统治世界"，三位教授全部进入学科综述模式（Opinion Dynamics 教授花 2000 token 背 Social Impact Theory / Hegselmann-Krause / Bakshy 2015），**没人直接回答用户的实际问题**。Ken 诊断根因："moderator 得先控制节奏、引导方向"——完全命中。

扫完 `debate_engine.py` 后发现三层叠加导致离题：
1. Round 1 moderator 被硬编码**跳过**（`if agent.persona == "moderator" and current_round == 1: continue`）——话题跑偏时他根本不在场
2. Moderator prompt 只要求"综合观点 / 识别共识 / 中立"——**缺"对齐用户问题"的硬约束**
3. `ROUND_OPENERS[1]` 第一条就让 agent "陈述学科核心论点 / 引用理论方法 / 指出学科盲区"——**prompt 本身诱导综述**

Ken 的产品约束："不要限制 AI 的想象力，但也不能完全驴唇不对马嘴"——所以本次改动**只锁一根线（回答用户问题），其他全放开**，不堆"必须/严禁"。

### 代码改动（`projects/knowledge-graph/backend/app/services/debate_engine.py`）

**A. `ROUND_OPENERS[1/2/3]` 三轮开场白重写**：每轮第一条强制"先直接回答用户问题"，然后再展开学科论据。保留其他所有想象力条款（挑战盲区、跨学科提问、互补点、最终方案、未解分歧）。

**B. `MODERATOR_PROMPTS` 重写 + 新增 `MODERATOR_ROUND_OPENERS`**：moderator 定位从"被动总结员"改为"**导演**"。Round 1 他**第一个**发言（`_order_agents_for_round` Round 1 从 `professors+juniors+moderators` 改成 `moderators+professors+juniors`；`run_round_stream` 去掉 Round 1 跳过逻辑），任务是：**把用户问题改写成可操作形态 + 给每个学科分派 1 个攻击角度**（~200 字，不替学者回答问题）。

**C. Moderator Round 2+ 末尾发言职责扩展**：专用 opener 要求 3-5 条——谁答了题谁偏了题 / 最出人意料的想象力一步 / 下一轮应该聚焦什么。下一轮 agent 看得见这条总结（经 `build_compressed_context` 进入 history），实现"导演→学者→导演拉回→学者"闭环。

**语气约束**："你信任这些学者，不替他们写作业"——避免 moderator 越权。Moderator 输出 cap 在 1200 token（深度模式下也不泛滥）。

### 对 KPAX v0 的顺带好处
KPAX `kpax_pipeline.stream_kpax_debate_events` 调的就是同一个 `run_round_stream` + `generate_summary`。**AXL prompt 修好 → KPAX verdict/estimate/plan 的 evidence_ref 质量跟着变好**，一个补丁两边收益。

### 成本代价（Ken 已拍板接受）
- Round 1 新增一次 moderator 调用 → 总 token 估算 +15~25%
- 单次辩论总耗时 +5~15s（Round 1 moderator 是串行前置步骤，学者要等他说完才能开始）
- 按 emergence_decomposition 基线 $0.035/agent-round 推算，3 学科 3 轮辩论从约 $0.32 涨到约 $0.39

### 未动 / 留白
- `generate_summary` 四段总结 prompt 未改——它已经围绕命题写，能吃到新的"有方向"的 agent 发言
- 没有新增"是否偏题"的自动评分机制——Ken 确认"moderator 一句话点名就够"，不做结构化评分，保持轻量
- `STANCE_PROMPTS` 不动——那是 pro/con 辩论专用，本次改动针对 `mode != debate` 的 interdisciplinary 讨论路径（命题 mode）

### 验证状态
- **语法 / lint**：`python -m py_compile app/services/debate_engine.py` 通过，basedpyright 0 errors
- **端到端**：待 Ken 本地用"怎么统治世界"再跑一次，肉眼对比：(a) Round 1 第一发言是 moderator 且分派了具体角度；(b) 学者们开头 1-3 句是直接答用户问题不是学科综述；(c) Round 2 开场 moderator 点名了谁飘

### 相关 handoff
- Ken 的问题诊断和 A+B+C 方案确认：[AXL 辩论没回答问题](6e9c3252-4fa5-485e-aedd-377bc707ea97)

---

## 2026-04-17 (凌晨) — KPAX v0 从 mock 到真 debate：§13.6 十步全部代码完成

### 背景
Ken 2026-04-17 晚依据 `notes/research.md §kpax-platform-philosophy` 和 `kpax_api_spec.md §13 (v1.3)` 下放 handoff，要求 cursor 按 §13.6 的 10 步实施清单把 KPAX v0 从 mock 推到真实 debate 能跑通的状态。"execution over experimentation，useful result 先出，wallet 最后"。

本次变更为**代码为主 + 文档同步**：新建 3 个 service + 重写 1 个 router + 2 个 KPAX 侧文件字段改名 + token_ledger 事件分层。

### 代码新增 / 重写

**AXL 侧（`projects/knowledge-graph/backend/`）**：
- **[新建]** `app/services/kpax_discipline_selector.py`：LLM 动态选择 3/5/7 个学科（奇数，最少 3），从 7 学科候选池，含 fallback
- **[新建]** `app/services/kpax_pipeline.py`：主编排 + 持久化到 AXL 主 DB 的 `debate / debate_agent / debate_message` 表；含同步 `run_kpax_debate` 和流式 `stream_kpax_debate_events` 两个变体；强制每学科 1 化身（weight=30 绕 `_decide_team_sizes` 的 size=2 分支），保证席位 == 学科数 == 3/5/7
- **[新建]** `app/services/kpax_renderers.py`：verdict / estimate / plan 三个 renderer + 内联 structured_extractor，把 AXL 四段中文总结投影成 KPAX 结构化 JSON；带 fallback（抽取失败时用四段 free-text 填 semi-structured，不 500）；evidence_ref 强制回填，options 分数强制 normalize 成 sum==1
- **[重写]** `app/routers/kpax_router.py`：三个 analyze endpoint 从 mock 改真（`run_kpax_debate` → renderer → Response）+ `stream=true` 分支返 SSE（`text/event-stream`，事件 `agents_ready / round_start / message / round_end / final / error`）+ 两个 followup endpoint 占位 501 + 校验 `llm_provider_override != null → 501` + `expert_lenses[]` 扩展 `expert_key / name_zh / skill_source` 三个字段
- **[+1 行]** `app/main.py`：挂 `kpax_router.followup_router`

**KPAX 侧（`kpax/backend/kpax_svc/`）**：
- **[重写]** `services/token_ledger.py`：`wallet_id → wallet_address` 全量改名（不保留别名，避免回流）；`LedgerEntry` 加 `event_type ∈ {kpax_token_delta, llm_cost_usd}`；新增 `record_llm_cost(wallet, cost_usd, request_hash)` 审计 API，v0 主产品免费 → 不扣 balance 但独立落账；顺手把 `threading.Lock` 升成 `RLock` 修掉一个历史 deadlock（charge / refund 嵌套获取同一 Lock 的改写前就存在的 bug，被新加的 `record_llm_cost` 调用路径暴露）
- **[重写]** `routers/v1_analyze.py`：`wallet_id → wallet_address`（Request / Response / URL path 全部）；AXL 返回后调 `record_llm_cost(cost_usd=debate_trace.cost_usd)` 做 platform 审计
- **[改 2 处]** `tests/smoke_v1_analyze.py`：body 里 `wallet_id → wallet_address`

### 架构决策（cursor 自裁，待 @cc / @codex PR review 复核）
1. **stream 字段分发：同 endpoint 分支**（不开独立 `/verdict/stream` URL）—— `if req.stream: return StreamingResponse(...)` 在同一 endpoint 内分叉。保 KPAX 前端未来调用连续性，OpenAPI response_model 会因 StreamingResponse 被 FastAPI 自动跳过 validation，可接受。
2. **`user_id → wallet_address` 窄解读** —— KPAX 边界字段 / 新 pipeline / token_ledger 全部用 `wallet_address`；AXL 内部 `chat_completion(user_id)` / `token_quota` / `users` FK 保留 `user_id`（绑 AXL `users` 表，改名波及 20+ 文件且风险大）。v0 KPAX 请求 `user_id=None` 穿透下传，v1 再加 wallet→user 映射。
3. **席位数口径**：传 `user_weights={d.id: 30}` 给 `generate_agents`，强制每学科 1 位化身（weight<40 走 team_size=1 分支），保 KPAX 产品约定"席位 = 3/5/7"。否则 default weight=50 会让每学科出 2 agent，席位翻倍。
4. **Cost 估算粗糙版**：v0 因 AXL `chat_completion` 不返 LiteLLM `response.usage`，改用 depth × agent × round 常量估算（$0.035/agent-round 基于 emergence_decomposition 实测校准）。v0.1 改 `chat_completion` 返 usage 后重算。

### 未改动 / 延后
- **BYOM（LLM provider override 实际生效逻辑）**：PRD §13.3 §9 划归 v1，v0 只接字段 + null 校验。
- **Skill marketplace / persistent skill avatars（`skill_*` expert_key）**：v1+。
- **前端 SSE UI**：Ken handoff 明确不是 cursor 责任，等 KPAX 前端实装。
- **Solana / Base 链 adapter**：`token_ledger.ChainAdapter` 只留抽象类，v2+ 实装。
- **Followup endpoints**：URL 形状已锁（`/axl/v1/debate/{id}/agent/{expert_key}/ask` + `/axl/v1/skill/{skill_id}/ask`），v0 永远返 501。

### 验证状态
- **静态 / import 级**：`python -c "from app.routers import kpax_router; from app.services import kpax_pipeline, kpax_renderers, kpax_discipline_selector"` 全通过；5 个 KPAX 路由注册正确
- **token_ledger 单元**：`seed 50 → charge standard 25 → balance=25 → record_llm_cost $0.99 → balance 不变 + 独立 llm_cost_usd 审计行` 链路通过
- **端到端（待 Ken 本地做）**：需要 Postgres + 真 LLM API key，见下方"Ken 本地验证清单"。`kpax/backend/tests/smoke_v1_analyze.py` 因 router 改真后不能再走 mock 路径，语义从 "单元冒烟" 变成 "集成冒烟"，PostgreSQL 未起时会在 t1 就 fail（预期行为，不是回归）。

### Ken 本地验证清单（按顺序做）
1. 启动 Postgres（`docker-compose up -d db`）+ 跑 migrations
2. 启动 AXL backend（`uvicorn app.main:app --port 8000`）
3. **Sync 路径**：`curl POST http://localhost:8000/axl/v1/analyze/verdict -H "Content-Type: application/json" -d '{"question":"应不应该现在辞职去全职做 KPAX","user_context":{"age":32,"runway_months":8},"depth":"quick","options":["辞","不辞"]}'` 应返回完整 VerdictResponse JSON，`options[].score` 加起来 ≈ 1.0
4. **SSE 路径**：上面同 body 加 `"stream":true`，`curl -N`，看到 `agents_ready → round_start → message × N → round_end → ... → final` 事件序列
5. **BYOM 拒绝**：加 `"llm_provider_override":{"provider":"custom"}` 应返 501 `not_implemented_in_v0`
6. **Followup 占位**：`curl -X POST http://localhost:8000/axl/v1/debate/1/agent/debate_1_agent_1/ask` 应返 501 `followup_not_implemented_in_v0`
7. **质量抽检**：随便挑 3 道真实问题（1 verdict / 1 estimate / 1 plan），看 evidence_ref.excerpt 是否真从 agent 原话截出、recommendation 是否和 debate summary 实质呼应

如 step 3-4 产出劣质 / 乱编，报给 cc，要么 prompt 调，要么回退到"把 AXL 四段直接塞进 free-text 字段"的更保守 fallback。

### 风险
- **端到端未亲手跑过**：cursor 无本地 Postgres + API key，所有上面"通过"只是 import / unit 级。若 Ken 验证时发现 pipeline 断在某个具体环节（e.g. `run_round` async 里 Session 状态不对），报过来。
- **token usage = 估算值**：`debate_trace.token_usage` 是粗略估计不是真值，对外界看是"看起来合理"但实际不可用于计费对账。v0.1 必须改真。

---

## 2026-04-17 (深夜) — 化身人数口径纠正（2-7 → 3/5/7） + 7 椅固定承诺恢复

### 背景
Ken 指出前一条日志 (d) 写的"化身人数 2-7（moderator 不计入）"是 cursor 对 `notes/design.md §2` 产品侧 UI 策略的误读。原设计里"**7 椅永驻**（学科完整性视觉承诺）"和"**出席化身 3 / 5 / 7 位**（奇数便于决断，最少 3，尤其 KPAX）"是**两个独立量**，cursor 合并成 "2-7 张按召唤数调" 把两件事都写错（(i) 椅子数不随人动 (ii) 起步是 3 不是 2）。详见 `notes/journal/project-log-2026-04.md` 2026-04-17 深夜条目。

本次变更为**纯文档**：无代码改动、无功能变化、无运行时影响。

### 文档修订（8 处）

- **`notes/design.md` §1** "KPAX 真实价值" 括号：`15 分钟 / 2-7 化身按问题组合 / 碰撞` → `15 分钟 / 每场 3/5/7 位化身按问题组合发言（奇数便于决断，最少 3） / 碰撞`
- **`notes/design.md` §1** "KPAX 要做的是智囊团" 段：`我按这个问题召集了 2-7 位化身` → `我按这个问题召集了 3/5/7 位化身（最少 3 位）` + 补"场景 7 座永驻 + 动态前景规则见 §2"的引用
- **`notes/design.md` §3 书房基础布局**：座椅数从 cursor 错写的 `2-7 张按召唤化身数量调` 恢复为 `7 张风格化座椅（固定，不因出席人数变化，本场出席的化身 3/5/7 位落座发言，其余椅子空着或由未召唤化身占位在边上）`
- **`KPAX.md` §一 化身体系段**：`每场 2-7 位化身` → `每场 3/5/7 位化身发言（奇数便于形成判断，最少 3 位避免对话太薄）` + 补"7 张椅子固定是学科完整性承诺"的场景说明
- **`notes/research.md` §kpax-knowledge-source-architecture** 3 处：`生产化身 2-7 人` / `化身团（2-7 人按问题组合）` / `化身团 v0（2-7 人）` → 都改为 `3/5/7 位` 表述（保留"最少 3"的约束文字）
- **`notes/research.md` §human-skill-distillation-layer** 2 处：`编排机制：按问题动态组 2-7 位化身` / `召唤 2-7 位` → `组 3/5/7 位化身（奇数，最少 3）` / `每场召唤 3/5/7 位`
- **`notes/next.md` 化身视频条目**：`化身数按本场实际 2-7 位` → `化身数按本场实际 3/5/7 位`
- **`notes/journal/project-log-2026-04.md`** 顶部追加 `[04-17 深夜]` 条目记录此次纠正

### 未改动
- **`README.md` AXL `2-7 disciplines / 2-7 个学科`** 暂不动——AXL 是学术工具场景，Ken 2026-04-17 深夜的纠正原话"**尤其是 KPAX**"暗示 AXL 可以宽一点，未明示要改。等 Ken 确认是否同步收紧到 3/5/7。
- **`CHANGELOG.md` 2026-04-17 (晚) 条目里列出的 `2-7` 描述** 保留原文不擦除——历史痕迹留作审计（那是当时写错的事实），由本条新增条目覆盖最新口径。
- **`notes/journal/project-log-2026-04.md` 2026-04-17 晚条目 (d)** 保留原文不擦除——同上，由本条新增日志条目覆盖。

### 教训
cursor 读过 `design.md §2`（"7 把椅子是永远在的" + "3 / 5 / 7 怎么决定" 两小节都在）但总结时把两个量合并成连续区间并把起步从 3 写成 2。下次凡涉及数字约束（人数、轮数、token 上限、奇偶规则）必须逐字核对原文而非压缩复述。

---

## 2026-04-17 (晚) — 化身（Avatar）体系文档化 + 时间博物馆场景 + 9 处术语修订

### 背景
Ken 2026-04-17 晚敲定 KPAX 本质是 "AXL 多 agent 机制 + 个体记忆工程层"，化身概念从原 `顾问/专家` 命名升级为产品战略层术语。同时视觉方向选 E "时间博物馆"，允许跨时代化身（柏拉图 / 希特勒 / Musk / 野生专家）同台辩论。`notes/journal/project-log-2026-04.md` 2026-04-17 晚条目有完整背景。

本次变更为**纯文档**：无代码改动、无功能变化、无运行时影响。

### 文档变更

**术语修订（9 处 + 附带 2 处）**：

- **`PROJECT.md` §2.1 AXL 状态表**：辩论引擎 "7 学科碰撞" → "多 agent 碰撞，数量 / 身份 / 模型可配置"
- **`notes/design.md` §4.5**：AXL 描述 "debate_engine + 7 学科 agent + ..." → "debate_engine + 多 agent 编排层（当前 emergence_decomposition 默认 7 学科配置，待验证） + ..."
- **`notes/design.md` §1**：KPAX 真实价值 "15 分钟 / 7 专家 / 碰撞" → "15 分钟 / 2-7 化身按问题组合 / 碰撞"
- **`notes/design.md` §1 "KPAX 要做的是智囊团"** 段：改为化身语义（2-7 位化身按需混编 / 引用 research.md §human-skill-distillation-layer）
- **`notes/design.md` §3 书房基础布局**：座椅数从 "7 张" 改 "2-7 张按召唤化身数量调"
- **`notes/research.md` §kpax-knowledge-source-architecture**：5 处术语更新——"7 学科 agent" → "多学科 agent"（AXL 底座）；4 处 "7 顾问" → "化身团（2-7 人按问题组合）" / "化身各自" / "化身团中相关学科角色（+ 可选实践型 skill）"

**新增章节 / 段落**：

- **`notes/research.md` 新增 §human-skill-distillation-layer**（~250 行）—— 完整定义 KPAX 化身层：两层技术构成（专业知识层 + 个人记忆层）/ 三类化身对比（学科 / 真人 / 野生）/ 技术栈候选并列表（Hermes / EvoMap / alchaincyf / Nuwa / Zep / 反蒸馏 信号）/ 四线输入视角（化身是 Line D 个体视角，区别于 A 学术 / B 行业 / C 社区三条群体视角线）/ IP 与肖像合法化边界（分级处理 + 通用工程约束 + 合法化底线）/ v0/v1/v2 phasing / AXL 硬规则 #6 再申 / 开放问题挂 next.md
- **`notes/design.md` 新增 §3.1 时间博物馆（Hall of Time）** —— 场景的上位容器定义 / 4 厅候选（书房 / 现代会议厅 / 东方庭院 / 广场竞技场）/ 场景推荐规则 / 跨时代化身的视觉处理（每人穿自己时代服饰，不强行统一）/ 争议化身分级访问机制 / v0 范围声明（实装仍只做书房厅）
- **`KPAX.md` §一 新增"化身体系：时间博物馆里的跨时代智囊团"段** —— 三类化身来源 + 场景叙事 + 和市面人格化 skill 对话工具（alchaincyf / 女娲 / LuBtc888 汇总 26 skill / 反蒸馏）的差异化（KPAX 做跨化身编排，不做单 skill 品质军备赛）
- **`KPAX.md` §附录 技术来源表** 扩 3 行：EvoMap/Evolver（化身自进化参考）+ alchaincyf 13 名人 skill + 女娲（v1 货架候选，需 license 预审）+ 技术栈不绑定声明

**`notes/radar.md` 新增 4 条**（按时间倒序，加在最上面）：

1. **[2026-04-17] EvoMap / Evolver — 自进化 agent 框架（GEP + 10 步循环）** — 动作 adopt（化身层候选技术栈，和 Hermes 并列）
2. **[2026-04-17] alchaincyf 开源名人 skill 生态（13 名人 + 女娲蒸馏工具）** — 动作 track（license 预审通过后 adopt）
3. **[2026-04-17] 反蒸馏.skill** — 动作 track（不采纳工具本身，作为生态信号读：skill 单品已被商品化，KPAX 差异化在跨化身编排层）
4. **[2026-04-17] @LuBtc888 26 skill 汇总推文** — 动作 track（市场扫描 + 产出 v1 化身 shopping list 输入）

**`notes/next.md` 同步**：
- P1 增 `@ken` 任务："视觉冲突 + 化身分级访问机制拍板"（E-A vs E-B 范围 + 争议化身闸门 + 在世名人免责条款）
- P2 增 `@cursor` 任务："alchaincyf 13 名人 skill + 女娲 license 预审"
- P2 增 `@cursor+@ken` 任务："v1 真人化身 shopping list（5 领域 5-7 位）"
- P2 增 `@cc` 任务："时间博物馆 v1 多厅切换实装设计"
- P2 增 `@ken` 任务："KPAX.md slogan 3 选 1"（cursor 起草 3 候选）
- 原"7 学科抽象图标" / "7 顾问辩论高光" 更新为 "化身图标系统" / "化身辩论高光"

### 验证

- 无代码变更，无需 smoke test
- `notes/next.md` 最后更新时间戳已更新
- `notes/journal/project-log-2026-04.md` 2026-04-17 条目已追加完整背景

### 后续

- @codex meta-review：重点审 (a) §human-skill-distillation-layer 的 IP / 肖像 / 合法化边界是否漏项 (b) 化身三层分类（学科 / 真人 / 野生）是否存在类别模糊 (c) AXL 硬规则 #6 在化身层是否有新的隐性破口
- @ken 拍板：next.md P1 视觉冲突 + 分级机制 + P2 slogan 3 选 1

---

## 2026-04-17 (傍晚) — KPAX legacy routers 路径 D 落地（冻结 + 例外登记）

### 背景
Ken 2026-04-17 傍晚拍板：legacy `routers/analyze.py` + `report.py` 采用**路径 D（冻结 + 例外登记）**，不弃用（A 会让前端 7 文件挂）、不条件门（C 会稀释硬规则）、不立即走 HTTP（B 前置依赖 cc PRD 和 AXL 端点改真，时机未到）。

### 文档变更

- **`PROJECT.md` §5.1 规则 #6**：加**例外登记段**——点名 `analyze.py` + `report.py` 为例外文件，明示新功能禁止进，替换触发点锚定 "KPAX v0 前端协议 PRD 完成日"，复查负责人 @cursor / @ken
- **`PROJECT.md` §2.2 KPAX 状态表**：3 services + llm_client + v1_analyze 从"待改"改为 ✅ 合规；legacy 2 router 从 ❌ 改为 ⚠️ "例外登记"；前端行描述改为"基于 legacy 5 步的 7 文件骨架，v0 座谈会形态未起"
- **`kpax/backend/kpax_svc/legacy_routers_assessment.md`**：2026-04-17 下午重写——加"前端依赖面"节纠正原 "前端未起" 事实错误（实测 grep 发现 7 文件真依赖）；新增路径 D；cursor 非约束性建议从 A 翻转为 D 作短期 + B 作中期

### 代码变更（注释 only，无逻辑改动）

- **`kpax/backend/kpax_svc/routers/analyze.py`**：文件头加 36 行 deprecation 注释（违规点列表 + 路径 D 原因 + 3 条存在期间规则：新功能禁止进 / bug 修可以但最小化 / 替换日随路径 B 删除 + 替换触发点 + 指向评估文档）
- **`kpax/backend/kpax_svc/routers/report.py`**：文件头加 16 行简版 deprecation 注释
- **`kpax/backend/kpax_svc/__init__.py`**：sys.path hack 上加 15 行注释（明示仅为 legacy 保留、其他 KPAX 代码不依赖、与 legacy 一同删除、禁止新增 `from app.*`）

### 验证

- smoke test：`python -c "from kpax_svc.main import app"` → 13 routes 全部就位（legacy 5 步 `/api/analyze/*` + v1 `/api/v1/analyze*` + report `/api/report/*` + health）
- 路径 D 不改任何运行时逻辑，零功能回归风险

### 后续 — 路径 B 迁移触发器（已挂 `notes/next.md`）

前置 1：@cc 出 KPAX v0 前端协议 PRD  
前置 2：AXL `kpax_router.py` mock 改真 + 新增流式端点  
两者就绪 → @cursor 在 `kpax_svc/routers/v1_session.py` 重建 session 流程走 HTTP → 同步删 legacy 2 router + `context_collector.py` + sys.path hack + 例外登记段

---

## 2026-04-17 — KPAX monorepo 违规修复（4/5 点落地，legacy 2 router 待 Ken 拍板）

### 代码变更

新建：
- **`kpax/backend/kpax_svc/clients/llm_client.py`**：KPAX 独立 LLM 客户端。litellm 薄封装，签名兼容原 `app.services.ai_provider.chat_completion`，去掉了 `user_id` / `db` token_quota 耦合（KPAX 的 quota 是钱包代币，不是 LLM token）。默认模型 `deepseek/deepseek-chat`，env `KPAX_LLM_MODEL` 可覆盖。log 遵守 `PROJECT.md` §9 规范（`extra={step, model, tokens_*}`）。

import 切换（每个文件 1 行改动）：
- **`kpax_svc/services/question_parser.py`**：`from app.services.ai_provider` → `from kpax_svc.clients.llm_client`
- **`kpax_svc/services/expert_builder.py`**：同上
- **`kpax_svc/services/report_generator.py`**：同上

`v1_analyze._chat_fn` 接入：
- **`kpax_svc/routers/v1_analyze.py`**：`_chat_fn` 原 stub `raise NotImplementedError` → 调 `llm_client.chat_completion`。classifier 现在可真实分类题型，fallback 保留。

### 验证
- `grep "from app\."` 在 `kpax_svc/services/` 零匹配，`kpax_svc/routers/` 仅剩 legacy `analyze.py` / `report.py` 4 处
- smoke test：`python -c "from kpax_svc.clients.llm_client import chat_completion; from kpax_svc.services.* import *; from kpax_svc.main import app"` OK，routes 列表正常

### 待 Ken 拍板（评估文档）
- **`kpax/backend/kpax_svc/legacy_routers_assessment.md`**：legacy `analyze.py` + `report.py` 的 3 路径对比（A 弃用 / B 走 HTTP / C 条件门保留）+ cursor 非约束性建议（倾向 A）+ `__init__.py` sys.path hack 清理选项

## 2026-04-15 (晚) — 冗长重复修复 + runner 韧性落地 + Checkpoint 0 真关闭

### 代码变更
- **`projects/knowledge-graph/backend/app/services/debate_engine.py`**：
  - `depth_tokens["quick"]`：`(1500, 1000)` → `(800, 600)`（只动 quick，不影响 standard/deep/max 的生产 KPAX 调用）
  - `_build_agent_system_prompt` 中文输出规则新增两条硬约束：严禁复述本轮他人已提论点（要回应必须升级/反驳/补新证据）、严禁凑字数
- **`experiments/emergence_decomposition/runner.py`**（runner 韧性三项一次性落地）：
  - `progress.jsonl` heartbeat（run_start / debate_start / debate_done）
  - `asyncio.wait_for(..., timeout=2000s)` 单场 33 min 硬 cap
  - debate 间 `await asyncio.sleep(65)` 缓和 Anthropic 分钟配额

### 验证
- **mini dry run（seed=42, n=3, 同题 cmp_06/cmp_04/dec_10）**：
  - **cost**：$1.65 → **$0.91**（–45%）
  - **total_tokens**：543k → **324k**（–40%）
  - **wall_sec**：2004s → **901s**（–55%）
  - **单条消息字数**：2089 → **1153**（–45%，跨 3 题一致）
  - 0 失败，0 rate limit（Tier 1 自洽，不需要提 Anthropic tier）
- **推演结论质量**：moderator summary 未降反锐（"AI 对话式编程高风险"从 disagreements 升为 consensus；冲突点从"终极价值"抽象层变为"资源分配优先级"可操作层）
- 完整对比：`experiments/emergence_decomposition/results/dry_run_20260415_171016/mini_dry_run_report.md`

### 全量外推调整
- 900 场：$1,620 → **$815**（旧 report §4 的"砍题目/砍组/换 moderator"降本方案全部作废）
- Opus moderator + run=3 + 6 组 50 题原设计可全保留

## 2026-04-15 — 实验 Checkpoint 0 文档与 dry run 报告

### 文档与注册表
- **`experiments/emergence_decomposition/results/dry_run_20260414_173832/dry_run_report.md`**：基于 5 条成功 `raw/*.json` 汇总单次 token/USD/时长，外推 900 次成本与 runner 必改项；`experiment_registry.json` 状态更新为 `checkpoint_0_report_ready`，增加 `dry_run_report` 路径字段
- **`experiments/emergence_decomposition/spec.md`**：文首状态与 registry 对齐
- **`experiments/README.md`**：说明 `status` 允许 `checkpoint_*` 粒度
- **`AGENTS.md`**：当前快照更新（runner 已存在、KPAX HTTP-only、Checkpoint 0 待 Ken 批）
- **`notes/agenda/next.md`**：P0 改为 runner 三项 + Ken 审批；**`PROGRESS.md`**：修正「零测试」表述为后端已有 pytest、E2E 仍薄
- **KPAX**：`kpax_svc/main.py` 注册 **`v1_analyze`** 路由（`/api/v1/analyze`），与 legacy `analyze` 并存直至退役

## 2026-04-14 — Memory System Phase 1 实施

### 代码变更
- **zep_manager.py 重写**：所有 `graph.add` 写入附带结构化 metadata（origin, evidence_ref, memory_type, source, confidence, verification, created_at, source_id）
- **检索升级**：`search_knowledge` 支持 metadata filter（origin / memory_type）+ origin 权重 re-rank（external x1.2, generated x0.9）
- **`retrieve_context` 增强**：返回的上下文标注 [external] / [generated] 来源
- **agent_memory.py 重写**：`push_agent_cognition` 写入附带 metadata + debate_id 证据锚点
- **cognition_distiller.py**：传入 debate_id 到 agent memory，完成证据链
- **debate_engine.py**：`push_debate_summary` 调用传入 debate_id
- **zep.py 路由**：`push_discipline_knowledge` / `push_scholar_knowledge` 传入 openalex_id

### Phase 2: 会话记忆压缩
- **session_memory.py 新建**：Round 3+ 自动压缩历史为三层结构（压缩摘要 + 上轮原文 + 未解决问题清单）
- **debate_engine.py**：`run_round_stream` 的 `_build_history` 替换为 `build_compressed_context`，按 depth 动态决定压缩时机
- 压缩阈值：quick=R2, standard/deep=R3, max=R4
- 压缩失败自动降级到全文模式，不中断辩论

### 新增测试（项目第一批测试，31 条全通过）
- `tests/test_memory_metadata.py`：17 条——metadata schema、origin re-ranking、filter 构建、writer 验证、evidence anchor
- `tests/test_session_memory.py`：14 条——压缩阈值、消息分轮、三层 context 结构、降级回退、depth 适配、压缩效率

### 架构改进（plan 更新）
- **知识 vs 模型产物分层**：metadata schema 新增 `origin = external | generated` 字段，检索排序时 external 权重 x1.2、generated 权重 x0.9，从结构上防止 AI 自我强化
- **证据锚点（evidence anchor）**：metadata schema 新增 `evidence_ref` 字段，每条长期记忆追溯到原始来源（debate_message_id / paper_id / content hash），让 verification 不只是标签而是可追溯的信任链
- **Write Ownership Policy 扩展**：表中新增 origin 列和 evidence_ref 示例列，每种数据类型的来源分类和证据要求明确
- **验收断言扩展**：新增 origin 优先级断言（external 排在 generated 之前）和 evidence_ref 非空断言

### 第一性原理 Review 记录
- 4 条洞察完整存档至 plan 文档末尾
- 2 条已采纳（origin 分层 + evidence anchor），2 条记录待后期实施（task-specific retrieval + 效用验证）
- 战略级提醒：当前用 metadata 分层是最小方案，数据量增长后可能需要拆检索管道

### 文档同步
- KPAX.md Brain Rot 防御思路新增"知识 vs 模型产物分层"和"证据锚点"两条
- PROGRESS.md 更新记忆系统进度

## 2026-04-13 — 项目体检 & 辩论引擎大改

### 重大变更
- **辩论模型：正反方 → 学科碰撞**：废弃旧的 advocate/challenger 正反方机制，改为每个学科代表自己参战、跨学科碰撞。同一学科的教授+副教授是队友，不同学科之间互相质疑。重写了 STANCE_PROMPTS、ROUND_OPENERS 和 `_build_agent_system_prompt`
- **辩论深度可选**：新增 Debate.depth 字段（quick/standard/deep/max），用户可选辩论深度，token 上限从 1500~12000 动态调整
- **多 LLM 混合辩论**：每场辩论随机分配 DeepSeek / GPT-5.4 / Claude Opus 4.6 给不同 agent，assignment 持久化到 DebateAgent.assigned_model，重启不丢
- **辩论流程连续性保护**：sessionStorage 保存 autoRun 任务状态，刷新后自动恢复续跑；beforeunload 防误关；autoRunRef 防重入

### 新增
- **社区论坛系统**：ForumPost / ForumComment / ForumVote 全套，帖子类型（用户/AI生成/辩论总结/实验请求）、实验认领流程、积分系统、一键翻译
- **用户系统**：注册/登录/Google OAuth/邮箱验证/密码重置，JWT 认证链路
- **订阅与支付**：Subscription 模型、Stripe 集成、加密货币支付、token 配额管理、模型选择
- **Profile 页**：个人资料编辑、头像、发帖/辩论/积分历史、订阅管理
- **Pricing 页**：套餐对比、支付入口
- **翻译缓存**：TranslationCache 模型，论坛内容一键翻译

### 安全修复
- 辩论 next_round / summarize 加 owner 校验，防止他人控制辩论
- SSE 每条消息即时 commit，刷新不丢数据
- 论坛帖子状态流转加 post_type 校验，普通帖不能进入实验状态
- 加密支付确认改用 record.user_id，不再信任前端传入
- Stripe 降级时清空 stripe_subscription_id 等字段
- 邮箱验证接入 get_verified_user 权限链

### i18n & 文案
- suggest_mode() 推荐逻辑从"正反辩论"改为"学科碰撞"
- en.json / zh.json 辩论相关文案全面更新（Structured Debate → Focused Debate / 学科碰撞）
- 中文 prompt 用中文学科名，消除中英混排
- 前端 AgentRow / MessageBlock 移除 advocate/challenger 标签，改显示 assigned_model

### UI 改进
- DebateSession 左侧 Agent 侧边栏可拖拽调整宽度（160px-480px）
- Agent 名字从 truncate 改为 break-words 自动换行
- 学科分组标题中文模式显示中文名
- 辩论创建页新增 4 格深度选择器（快速/标准/深度/极限）

### 项目体检
- 完成三维度评估：功能 87 / 产品 72 / 生产就绪 48
- 发现 3 张表 + 15 字段缺 migration
- .env.example 仅覆盖 5/26 个变量
- 输出 6 阶段优化路线图 + 27 项可执行任务列表

---

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
