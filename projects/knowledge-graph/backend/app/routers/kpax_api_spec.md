# AXL → KPAX HTTP API Spec

> 2026-04-15 by cc. Ken 拍板 3 endpoint（verdict / estimate / plan）。
> 不放 `api/` 是因为 AXL 所有 HTTP 入口都在 `routers/`；KPAX 专用路由加前缀 `/axl/v1` 区隔。
>
> **正文版本 = v1.1（2026-04-15 合稿后）**。Review 区在最下方，保留原文。

## cc 合稿说明（2026-04-15）

两份 review（Cursor Claude Opus / Codex）都通过，主方向一致。Ken 让我定 deep 轮数，其他我直接合。本次落地修改：

1. **`evidence_ref` 升级为结构化** `{source_type, source_id, excerpt?}` — §2.1/2.2/2.3 三处
2. **`debate_trace.agents` → `expert_lenses`**，去掉 `rank`，只保留 `discipline_id` + `name_en`。理由：rank 是 AXL 内部 agent 进化自由参数，不能被 KPAX 协议绑架
3. **`estimate.dimensions[].kind`** ∈ `{probability, scalar, score}` — 概率题不再显得是评估题的奇怪子类
4. **score / confidence 量纲注释**写进 §2.1 下面
5. **`plan.phases[].duration`** 双轨：`{start_month, end_month, text}`
6. **`meta.depth`** 回显
7. **`depth=deep` 从 6 轮压到 5 轮**。Ken 说不本质、我定。Codex 的工程理由（同步 HTTP 时长断点）比 Cursor 的产品话术更实。6+ 留给未来的 research mode SKU
8. **§5 cache 条目补边界**：不做 semantic cache ≠ 不做 request logging / hash tracking

未收的建议：无。

---

## Review by Cursor (2026-04-15)

**判断 1：3 endpoint 归并** — 没问题，不改。是否题和选择题的 pros/cons 结构完全复用（options 数量不同而已）。概率题 dimensions 只有 1 个元素不算累赘，KPAX 前端一个 if 分支搞定。

**判断 2：Response schema**
- `conditions` 字段：保留。对应 KPAX.md "关键前提条件"，用户最需要的就是"什么条件下结论会变"。
- `evidence_ref`：**建议升级**为结构化。当前 string 不够，KPAX 前端渲染引用需要区分论文/Reddit/知乎/专家意见。建议改为 `{"source_type": "paper|reddit|zhihu|expert_opinion", "source_id": "...", "excerpt": "..."}`。成本低收益高。
- `debate_trace`：当前粒度够用。不需要暴露每条 message 原文（用户要看过程用 SSE）。

**判断 3：depth → rounds**
- quick=2 / standard=4 / deep=6 保持不变。deep 约 15 分钟对人生决策可接受，KPAX 前端在选 deep 时提示预计时间即可。不砍到 5 轮。

**判断 4：不做 cache** — 同意。实验可重复 + 代币经济诚实。防重复提交在 KPAX 前端做防抖，不在 AXL 层做 cache。

**一条改动建议给 @cc**：`evidence_ref` 从 string 升级为 `{source_type, source_id, excerpt}`，涉及 §2.1/2.2/2.3 三个 Response 的 pros/cons/drivers 里的 evidence_ref 字段。其余不动。

## Review by Codex

结论先说：**3 endpoint 归并是合理的，可以继续走，不建议退回 5 endpoint。** 这份 spec 的主方向没问题，但有 4 处现在改最便宜，建议 cc 统一收进正文。

### 1. 3 endpoint vs 5 endpoint

- 维持 **3 endpoint**。按输出结构归并是对的，KPAX 前端真正要消费的是渲染协议，不是题型哲学。
- `verdict` 合并“是否题 + 选择题”也成立。是否题本质上就是一个二元选择题，`options=["做","不做"]` 不会破坏 schema。
- `estimate` 合并“概率题 + 评估题”也成立，但有一个前提：**概率题必须在 response 里被明确定义成单维 estimate**，不能让前端自己猜。
- 不建议拆回 5 endpoint。拆开后前后端分支数翻倍，pipeline 其实没变，成本高于收益。

### 2. Response schema 补充判断

- **`conditions` 要留。** 这个字段不是锦上添花，而是 KPAX 报告里“关键前提条件”的直接承载。没有它，结论会显得过硬，没有可翻转条件。
- **`evidence_ref` 不要停留在 string，建议现在就升成结构化。** 最低也该是：
  - `{source_type, source_id, title?, url?, excerpt?}`
  - 原因很简单：KPAX 前端后面一定会遇到“同样是 string，但有的是 DOI、有的是 URL、有的是 internal paper id”，到时候再拆最贵。
- **`debate_trace` 应该收窄成“可解释运行信息”，不要暴露太多内部实现细节。**
  - 建议默认保留：`debate_id`, `rounds`, `token_usage`, `cost_usd`
  - 建议把 `agents` 从“完整内部 agent 列表”降成更适合产品展示的 `disciplines` 或 `expert_lenses`
  - 原因：KPAX 是 consumer，不需要知道 AXL 内部 rank / persona / agent 编排细节；这些字段一旦暴露出去，后面会形成兼容负担

### 3. depth → rounds

- `quick=2 / standard=4` 我觉得没问题。
- `deep=6` 我不建议保留，建议压到 **5 轮**。
- 原因不是“技术上跑不了”，而是当前交付形态是同步 HTTP + 可选 SSE，不是后台 job。你自己 spec 里也写了 AXL 当前一场 4 轮 debate 大约就是一个明显时长成本；6 轮很容易把用户推到“太久了”的区间。
- 更稳的口径是：
  - `quick=2`
  - `standard=4`
  - `deep=5`
- 如果以后 KPAX 上了后台任务 / 回来继续看结果，再把真正的“research mode”拉到 6+ 轮。

### 4. endpoint-level cache

- **v0 不做 endpoint-level cache，我同意。**
- 这条现在合理，原因有三条：
  - KPAX 的 token 经济本来就要诚实记账
  - AXL 的 debate 带有随机性和实验性，不应该在接口层假装纯 deterministic
  - 现在过早上 cache，会让“复跑同题”和“同结果复用”混成一件事
- 但建议补一句边界说明：**不做 semantic cache，不等于不做 request logging / hash tracking**。  
  后面 KPAX 至少还是需要知道：
  - 这个问题是不是跑过
  - 上次花了多少 token
  - 上次和这次输出差异大不大

### 我建议 cc 改正文时一起收的点

1. `estimate.dimensions[]` 里加一个可选 `kind`，例如 `probability | scalar | score`，这样概率题不会显得像“只是评估题的一个奇怪子类”。
2. `verdict.options[].score` 和 `recommendation.confidence` 要明确量纲。现在看起来都像 0-1，但前端不知道一个是相对推荐度还是归一化概率。
3. `plan.phases[].duration` 建议同时支持结构化字段，至少预留 `{start, end, unit}`，不要永久只靠 `"0-3 month"` 文本。
4. `meta` 里建议补 `analysis_mode` 或 `depth` 回显，方便 KPAX 前端和日志层对齐。

一句话结论：**归并方案本身没坑，可以走；真正该现在补的是 evidence 结构化、trace 收窄、deep 从 6 压到 5。**

---

## 1. 设计原则

1. **这是 AXL 对 KPAX 的唯一边界**。KPAX 不 import AXL Python 模块，只通过这组 HTTP。AXL 仓内其它 router（`debate.py` / `papers.py` 等）是给 AXL 自身前端用的，KPAX 不碰。
2. **按输出结构归并题型**，不按用户语义归。KPAX.md 五题型压成三类：
   - `/analyze/verdict` — 是否题 / 选择题（输出 = 选项 + 推荐 + 理由）
   - `/analyze/estimate` — 概率题 / 评估题（输出 = 维度打分 + 因素拆解）
   - `/analyze/plan` — 策略题（输出 = 阶段 roadmap + 风险）
3. **是否题 = verdict with options=[做, 不做]**；概率题 = estimate with dimensions=[成功概率]。路由层参数特化，不占 endpoint 名额。
4. **同步 + SSE 双模**。`stream=false` 一把返回 DecisionOutput；`stream=true` 走 SSE 实时推 debate 过程（复用 `debate_engine.run_round_stream`），最后一个事件是 `{type:"final", output:DecisionOutput}`。
5. **无鉴权 v0**。KPAX 的 token 扣费在 KPAX 侧做，AXL 不知道 KPAX 用户是谁。将来要加，用 header `X-KPAX-Signature`（HMAC），AXL 不维护用户表。
6. **Pydantic model 两边不共享**。KPAX 自己 mirror，防止隐式耦合。

---

## 2. Endpoint

### 2.1 `POST /axl/v1/analyze/verdict`

**Request**:
```json
{
  "question": "该不该辞职去创业",
  "user_context": {
    "age": 32,
    "savings": "50w",
    "industry": "SaaS",
    "free_text": "家里有老人需要照顾..."
  },
  "options": ["辞职创业", "留下"],
  "depth": "standard",
  "stream": false
}
```

- `options` 可省；省略时 LLM 从 question 里自动抽，至少 2 个。是否题传 `["做", "不做"]` 或省略。
- `depth ∈ {"quick","standard","deep"}` 映射 debate 轮数（2/4/5）。
- `user_context` 自由 schema，内部拼进专家 prompt。

**Response (stream=false)**:
```json
{
  "question_type": "verdict",
  "options": [
    {
      "label": "辞职创业",
      "score": 0.62,
      "pros": [
        {
          "claim": "...",
          "evidence_ref": {
            "source_type": "paper",
            "source_id": "openalex_W123456",
            "excerpt": "原文摘录（可选）"
          }
        }
      ],
      "cons": [{"claim":"...", "evidence_ref": {"source_type": "reddit", "source_id": "reddit_abc123", "excerpt": "..."}}]
    },
    { "label": "留下", "score": 0.38, "pros": [...], "cons": [...] }
  ],
  "recommendation": {
    "choice": "辞职创业",
    "confidence": 0.62,
    "key_drivers": ["...", "..."],
    "key_risks": ["...", "..."],
    "conditions": ["如果 X 成立则推荐度升至 0.75"]
  },
  "debate_trace": {
    "debate_id": 1234,
    "expert_lenses": [{"discipline_id": 4183, "name_en": "Economics"}],
    "rounds": 4,
    "token_usage": {"input": 12000, "output": 8000},
    "cost_usd": 0.08
  },
  "meta": { "model_moderator": "anthropic/claude-opus-4-6", "axl_version": "2.0", "depth": "standard" }
}
```

**字段量纲**：
- `options[].score` — 相对推荐度，全部 options sum=1，范围 [0,1]
- `recommendation.confidence` — 独立置信度，与 score 无关，范围 [0,1]
- `evidence_ref.source_type` ∈ `{"paper","reddit","zhihu","expert_opinion","other"}`
- `evidence_ref.source_id` — 来源域下的唯一 ID（`openalex_Wxxx` / `reddit_xxx` / `zhihu_xxx`）
- `evidence_ref.excerpt` — 可选，辅助前端渲染引用卡片

**Response (stream=true)**: SSE, `text/event-stream`, event types:
- `agents_ready` — `{agents: [...]}` 专家组装完
- `round_start` — `{round: 1}`
- `message` — `{agent_id, content, token_in, token_out}` 每条发言
- `round_end` — `{round: 1, summary: "..."}`
- `final` — `{output: <上面的 Response JSON>}`
- `error` — `{code, msg}`

### 2.2 `POST /axl/v1/analyze/estimate`

**Request**:
```json
{
  "question": "巴西能拿 2026 世界杯吗",
  "user_context": {...},
  "dimensions": ["冠军概率"],
  "depth": "standard",
  "stream": false
}
```

- 概率题：`dimensions=["冠军概率"]` 或省略（自动填 `["发生概率"]`）。
- 评估题：`dimensions=["前景","风险","回报","门槛"]` 等多维，省略时 LLM 生成。

**Response**:
```json
{
  "question_type": "estimate",
  "dimensions": [
    {
      "name": "冠军概率",
      "kind": "probability",
      "score": 0.18,
      "unit": "probability",
      "drivers": [
        {
          "claim": "...",
          "weight": 0.4,
          "evidence_ref": {"source_type": "paper", "source_id": "openalex_Wxxx", "excerpt": "..."}
        }
      ],
      "counter_drivers": [
        {
          "claim": "...",
          "weight": 0.3,
          "evidence_ref": {"source_type": "reddit", "source_id": "reddit_xxx", "excerpt": "..."}
        }
      ],
      "confidence_interval": [0.12, 0.25]
    }
  ],
  "overall": {
    "summary": "中等偏下概率，主要受 X Y Z 影响",
    "confidence": 0.55
  },
  "debate_trace": {
    "debate_id": 1234,
    "expert_lenses": [{"discipline_id": 94, "name_en": "Physics"}],
    "rounds": 4,
    "token_usage": {"input": 12000, "output": 8000},
    "cost_usd": 0.08
  },
  "meta": { "model_moderator": "anthropic/claude-opus-4-6", "axl_version": "2.0", "depth": "standard" }
}
```

**`dimensions[].kind`** ∈ `{"probability", "scalar", "score"}`：
- `probability` — 0-1 概率，`unit="probability"`。概率题用这个
- `scalar` — 有量纲数值（价格/时长/距离），`unit` 填具体单位
- `score` — 0-1 归一化打分，`unit="normalized"`。评估题多维用这个

### 2.3 `POST /axl/v1/analyze/plan`

**Request**:
```json
{
  "question": "怎么从零开始做一个 SaaS",
  "user_context": {...},
  "goal": "12 个月内跑到 MRR 10k",
  "constraints": ["solo dev","无外部融资"],
  "depth": "deep",
  "stream": false
}
```

**Response**:
```json
{
  "question_type": "plan",
  "phases": [
    {
      "idx": 1,
      "name": "PMF 探索",
      "duration": {"start_month": 0, "end_month": 3, "text": "0-3 month"},
      "actions": [
        {
          "action": "...",
          "owner": "self",
          "rationale": "...",
          "evidence_ref": {"source_type": "paper", "source_id": "openalex_Wxxx", "excerpt": "..."}
        }
      ],
      "gate": "必须达成 X 才进下一阶段",
      "risks": [{"risk":"...", "mitigation":"...", "severity":"high"}]
    }
  ],
  "critical_path": ["phase1.action2", "phase2.action1"],
  "overall_risks": [...],
  "debate_trace": {
    "debate_id": 1234,
    "expert_lenses": [{"discipline_id": 1955, "name_en": "Computer Science"}],
    "rounds": 5,
    "token_usage": {"input": 18000, "output": 12000},
    "cost_usd": 0.14
  },
  "meta": { "model_moderator": "anthropic/claude-opus-4-6", "axl_version": "2.0", "depth": "deep" }
}
```

**`phases[].duration`** 是双轨结构：`start_month` / `end_month` 给前端画 timeline，`text` 给日志和简单文本渲染。`severity` ∈ `{"low","medium","high","critical"}`。

---

## 3. 内部 pipeline 映射（AXL 侧实现约束）

每个 endpoint 内部走统一四步，只有 **prompt 模板** 和 **summary 渲染** 按 question_type 分支：

```
(1) disciplines = select_disciplines(question, user_context, top_k=5)
    └─ 复用 AXL 现有的学科匹配逻辑（knowledge_graph.db）

(2) agents = generate_agents(question, disciplines, mode="collision")
    └─ 复用 debate_engine.generate_agents（bug 已修）

(3) for r in range(depth_to_rounds[depth]):
        messages = run_round(debate, agents, r)
    或 stream 模式下 run_round_stream
    └─ 复用 debate_engine.run_round / run_round_stream

(4) output = render_output(debate, question_type)
    └─ 这一步是新的。按 question_type 跑一次 moderator LLM (Claude Opus 4.6)
       用对应的 JSON schema prompt，产出 verdict/estimate/plan 结构。
       不是从 generate_summary 改，而是并列一个 render_{verdict|estimate|plan}。
```

**depth_to_rounds**：`{"quick": 2, "standard": 4, "deep": 5}`。6+ 轮留给未来 research mode SKU，不在 v0 范围。

**moderator 固定** `anthropic/claude-opus-4-6`（Ken 2026-04-15 拍的硬规则）。

---

## 4. 错误码

| HTTP | code | 含义 |
|---|---|---|
| 400 | invalid_depth | depth 不在枚举 |
| 400 | bad_options | verdict 传了 <2 个 options |
| 422 | question_too_short | question 字数 < 5 |
| 429 | axl_busy | 并发超过 AXL 容量 |
| 500 | debate_failed | 推演中途挂 |
| 503 | moderator_unavailable | Claude API 挂 |

---

## 5. 不做的事

- ❌ 不做 endpoint-level cache（一样的 question 一样的 context 每次都重跑，保证实验可重复 + 代币经济诚实）
- ❌ 不做 rate limit（KPAX 侧控制）
- ❌ 不做 auth（v0）
- ❌ 不做 webhook（KPAX 要长任务就用 stream=true SSE）
- ❌ 不做 batch endpoint（一次一个 question）

**边界说明**：不做 semantic cache **不等于**不做 request logging。AXL 会对每个 request 记录 `request_hash`（基于 question + user_context 归一化哈希），日志层保留 `{request_hash, debate_id, token_usage, cost_usd, timestamp}`。KPAX 后面要做 "这题我跑过吗 / 上次花了多少 / 两次输出差多少" 的分析时从日志层取，不走 cache。

---

## 6. 实装顺序

1. `routers/kpax_router.py` — 3 个 endpoint，先全返回 mock DecisionOutput（静态 JSON），能让 KPAX 联调
2. `services/kpax_pipeline.py` — 四步 pipeline 的真实实现，每个 endpoint 调一次
3. `services/kpax_renderers.py` — `render_verdict / render_estimate / render_plan` 三个 moderator 调用
4. SSE 接入（复用 `run_round_stream`）
5. 错误处理补全

**v0 必做**：1+2+3+4（SSE 提前到 v0 必做，见 §10）。

---

## 7. v0 具体实现决策（cc 2026-04-17 PRD 补充）

这节补齐 cursor 实现时必须明确但 §3 / §6 没覆盖的具体决策。所有决策都带理由，不是拍脑袋。

### 7.1 Pipeline 文件位置与职责划分

**决策**：新建两个文件，职责按 §6 已有顺序清晰分层：

- **`app/services/kpax_pipeline.py`** — 主编排层。对每个 endpoint 串 "disciplines 选择 → agents 生成 → 轮次 run → structured render"，并处理持久化（§8）。
- **`app/services/kpax_renderers.py`** — 结构化渲染器。`render_verdict` / `render_estimate` / `render_plan` 三个函数，各自调 moderator LLM（Claude Opus 4.6）一次，喂对应的 JSON schema prompt，产出对应 Response 结构。

**不做**：不改 `debate_engine.py` 本体（硬规则：debate_engine 是 AXL 学术底座，不被 KPAX 产品 schema 绑架）。

### 7.2 moderator summary → structured Response 的映射策略

**选项 A**：改 `generate_summary` 让 moderator 直接出 KPAX Response JSON。
**选项 B**：`generate_summary` 保持中文四段输出不变；在它之后加一步 `structured_extractor`，用一次独立 LLM call（便宜模型，$0.05/场）把中文四段抽取成 verdict / estimate / plan 的 JSON。

**决策：B**。

**理由**：
- moderator 的四段中文输出（consensus / disagreements / open_questions / directions）是 AXL 实验要评估的对象（pilot_judge_rubric_v0.1 的评估目标）。如果按选项 A 让它直接出 KPAX JSON，实验评估对象变了，rubric 要重写，rubric v0.1 白跑
- B 让 AXL 学术输出形态保持不变，KPAX 产品 JSON 是 KPAX 层的独立 concern，符合 AXL/KPAX 分层硬规则
- 二次抽取的成本可以接受（便宜模型，一次 call），而且 extraction 失败可 fallback 到"半结构化"（把中文四段直接装进 Response 的 free-text 字段）

**实现位置**：`kpax_renderers.py` 里 `render_verdict / render_estimate / render_plan` 三个函数内部都调两步：
1. 拿到 `generate_summary` 的中文四段输出
2. 调 `structured_extractor(four_sections, target_schema)` 得到 JSON，填入 Response 的 options / dimensions / phases 等字段

### 7.3 question → disciplines 映射（v0 硬编码 vs 动态选择）

**选项 A**：v0 硬编码 7 学科 baseline（物理 / 数学 / 经济 / 心理 / 社科 / CS / 艺术人文），每次请求都用同一批。
**选项 B**：v0 立刻实现 `expert_builder` 动态选学科（按问题 relevance_score 从数据库选 3-7 学科）。

**决策：v0 用 A，v0.1 升级到 B**。

**理由**：
- MVP 定义是 "用户输入一个问题 → 能拿到基于真实 7 学科辩论 + moderator 真综合的有用回答"。7 学科硬编码已经满足这个定义（20 场 baseline 实验已证实质量）。
- 动态选学科（B）涉及 relevance_score 算法 + 学科知识库检索，是独立的复杂工作，可以并行开发但不阻塞 MVP 联调
- Ken 2026-04-17 原话 "先正面回答问题是基础"——v0 先做到"正面回答"，动态选学科是"锦上添花"
- v0.1 升级时 `kpax_pipeline.py` 里把 `_get_disciplines_v0()` 替换为 `expert_builder.pick(question, user_context)`，其他代码不改

**KPAX v0 产品层约束**：v0 Response 的 `debate_trace.expert_lenses` 里仍然只显示**本场实际参与的化身**（哪怕都是 7 学科固定）。未来 v0.1 动态选学科后前端显示逻辑不变。

### 7.4 evidence_ref 在 v0 的策略

**问题**：Response schema 要求每个 pros / cons / drivers 都有 `evidence_ref = {source_type, source_id, excerpt}`。但 agent 发言里的引用是自由文本（"按 Kahneman 2011 的研究…"），没有结构化。

**选项 A**：v0 把 evidence_ref 设为空数组（违反 spec）。
**选项 B**：从 agent message 抽"引用片段"字符串 + 标 `source_type="expert_opinion"`，`source_id` 填 `agent_{discipline_id}`（例 `agent_4183` 代表经济学家），`excerpt` 填原文引用片段。
**选项 C**：v0 真接 Zep / OpenAlex 查论文，匹配到 paper source_id。

**决策：v0 用 B，v1 升级到 C**。

**理由**：
- A 违反 spec，不选
- B 让 Response 结构**完整**，evidence_ref 所有字段都有值，不会让前端兼容出错
- B 的来源层级诚实——`source_type="expert_opinion"` 明确表达"这是某位化身的观点，不是论文引用"，用户看 KPAX 前端时能区分
- C 需要 Zep 查询 + paper matching 算法，v0 做会阻塞 MVP
- v1 升级：`structured_extractor` 再加一步 `evidence_resolver` —— 把 agent 引用的文献 name / author 查 Zep 找到 openalex paper id，升级 source_type 从 `expert_opinion` 到 `paper`

**结构化抽取规则**（structured_extractor prompt 里明确）：
- 每个 pros / cons / drivers claim 必须附 evidence_ref
- 默认 source_type=`expert_opinion`，source_id=`agent_{discipline_id}`
- excerpt 填 agent 原话片段（≤ 200 字），保证前端能展示"这是谁说的 + 原话"
- 如果 agent message 里**明确引用了**论文（比如 "Kahneman 2011 《Thinking, Fast and Slow》"），excerpt 保留引用字符串，v1 升级时 evidence_resolver 会再把 source_type 升级到 paper

---

## 8. 持久化与化身标识（v0 必做，Ken 2026-04-17 要求预留）

### 8.1 背景

Ken 2026-04-17 明确未来 KPAX 产品形态包括 "用户可以点击某个化身继续和 ta 聊" （followup 对话）。v0 即便不实现 followup 逻辑，**数据结构和化身标识必须到位**，否则未来做 followup 时要重写 pipeline + 回填历史数据。

### 8.2 必改点

**A. debate 持久化**：`kpax_pipeline.py` 内部**直接使用 AXL 主 `SessionLocal`**（不是实验 runner 的隔离 DB copy）。每次 KPAX 请求产生的 debate 完整落库，含 `debates` 表 + `debate_agents` 表 + `debate_messages` 表。

**B. `expert_key` 字段加入 `expert_lenses`**：

当前 §2.1 / 2.2 / 2.3 的 Response 里 `debate_trace.expert_lenses` 是 `[{discipline_id, name_en}]`。**修订为**：

```json
"expert_lenses": [
  {
    "expert_key": "debate_1234_agent_5678",
    "discipline_id": 4183,
    "name_en": "Economics",
    "name_zh": "经济学"  // 新加，前端 zh 显示用
  }
]
```

- `expert_key` 格式：`debate_{debate_id}_agent_{agent_id}`，在 KPAX 产品生命周期内唯一
- 前端要索引某化身时，把 expert_key 传回 followup endpoint

**C. moderator summary 存 debate 记录**：`generate_summary` 产出的中文四段要存到 `debates` 表（原来已经存了，复用）。这是 followup 时化身要 "记得" 之前讨论的原材料。

### 8.3 不破坏实验 runner

- `experiments/emergence_decomposition/runner.py` 仍然用隔离 DB copy（实验数据污染防护，不变）
- `kpax_pipeline.py` 用主 DB（生产路径）
- 两个入口互不干扰，共用 `debate_engine.py` 库函数

---

## 9. Followup v1 预留接口（v0 占位，v1 实现）

### 9.1 Endpoint

```
POST /axl/v1/debate/{debate_id}/agent/{expert_key}/ask
```

**Request (v1 将支持)**:
```json
{
  "question": "物理老师，你刚才说的能量守恒我没听明白，能再解释下吗",
  "user_context": {...},  // 可选，沿用 debate 的 context
  "depth": "quick",  // 默认 quick，followup 不需要深度推演
  "stream": false  // v0 只支持 false，v1 voice mode 见 §11
}
```

**Response v0**：`501 Not Implemented`，body `{"code": "followup_not_implemented_in_v0", "scheduled": "v0.1"}`

**Response v1**:
```json
{
  "expert_key": "debate_1234_agent_5678",
  "discipline_id": 4183,
  "name_en": "Economics",
  "message": "好问题。我刚才说的能量守恒不是物理意义的那个...",
  "references_original_debate": [msg_id_1, msg_id_3],  // 引用了原辩论里哪几条消息
  "token_usage": {...},
  "cost_usd": 0.02,
  "meta": {...}
}
```

### 9.2 v1 内部实现约束（预告，v0 不做）

- 复用原 debate 的 agent system_prompt + 原 messages 作为 context
- 单次 chat_completion 调用，不跑整轮 run_round（followup 是 1v1 不是多 agent）
- Token 成本 ~$0.02-0.05/次（远低于整场 debate）
- 有 rate limit（同一 debate + 同一 user 每分钟最多 N 次，防止无限 loop）

### 9.3 v0 为什么现在就要占位

不占位的代价：v1 实现时要改 `kpax_api_spec.md` 加新 endpoint + KPAX 前端要改调用层 + AXL 要加路由。占位后，v1 实现时只改 501 handler 为真实逻辑，其他不动。

---

## 10. Stream + Voice：SSE 提前到 v0 必做（Ken 2026-04-17 修订原 §6）

### 10.1 原 §6 的错误

原 §6 写 "v0 只做 1+2+3 的同步版本，SSE 排 v0.1"。**Ken 2026-04-17 纠正**：KPAX 用户不是 "干等 15 分钟看报告"，是 **"3-5 分钟有互动的实时对话体验"**——这需要 SSE (v0) + Voice (v1) 双管齐下，不能排到 v0.1。

### 10.2 v0 必做：SSE 同步到 KPAX 前端

SSE 事件类型（§2.1 已定义，此处明确 v0 实现要求）：

- `agents_ready` — debate 初始化完，前端可以开始渲染座谈会 7 席 UI
- `round_start` — 某轮开始
- `message` — 每条 agent 发言（**流式逐字符或逐句推**，不是整条发完才推；前端可立即 TTS）
- `round_end` — 某轮结束
- `final` — 含完整结构化 DecisionOutput JSON
- `error` — 异常

**v0 必做**：前 5 种 event 全部实装。KPAX 前端在 SSE stream 到来时**逐 message 渲染 + 逐 message 调 TTS**（见 §10.3），用户感知 ≠ "等 15 分钟"，是 "全程看化身们讨论"。

### 10.3 Voice v1 预留（v0 不实装但 protocol 定死）

**v1 要实现**：

1. **TTS 侧**（KPAX 前端）：收到每条 `message` event 时，把 content 送 ElevenLabs 流式 TTS，按 `expert_key` 映射到对应音色（v0 已经在 `expert_lenses` 里给了 expert_key，v1 在此基础上加声音）
2. **STT 侧**（KPAX 前端）：用户可打断（比如 "物理老师等等"），前端 STT 识别 → 送 followup endpoint（§9）
3. **Interrupt 协议**（v1 AXL 侧）：debate 进行中收到 followup 请求时，**不打断主 debate**，followup 另开 single-agent call，异步返回。主 debate 继续跑完，followup 结果单独显示

**v0 Protocol 预留**：
- SSE `message` event 的 content 字段必须**按语义切段**（一句一个 chunk 或按标点切），不要整段一次性返回——否则 v1 TTS 延迟会很大
- `expert_lenses` 里 v1 可以加 `voice_id` 字段（v0 不用填），对应 ElevenLabs voice library ID

### 10.4 v0 实装顺序修订

原 §6 的 `v0 = 1+2+3` 改为 **`v0 = 1+2+3+4`**。SSE 和同步 HTTP 都作为 v0 必做。

**为什么提前**：如果 v0 发布时只有同步 HTTP（用户看 loading 15 分钟无事发生），用户体验 = 死。SSE 是 "用户看化身们实时讨论" 的前提，不做 SSE 的 v0 对产品核心价值是空的。

---

## 11. v0 成功判据与验证路径

### 11.1 技术层成功判据（cursor 验证）

- [ ] `POST /axl/v1/analyze/verdict` 同步调用返回有效 VerdictResponse（mock 已通过，改真后要通过）
- [ ] `POST /axl/v1/analyze/verdict?stream=true` SSE 事件流能跑通，前 5 种 event 完整
- [ ] `POST /axl/v1/analyze/estimate` 同上
- [ ] `POST /axl/v1/analyze/plan` 同上
- [ ] debate 持久化到主 DB 可 `SELECT * FROM debates WHERE id={debate_id}` 查回
- [ ] expert_key 格式正确且 unique
- [ ] followup endpoint 返回 501（v0 不实现但占位）
- [ ] End-to-end 跑一题 "该不该辞职创业" 看 response 有**真内容**（7 学科真辩论 + 结构化抽取的 pros / cons / recommendation），不是 mock

### 11.2 产品层成功判据（Ken 验证）

Ken 2026-04-17 原话 "最小 MVP = 能输出一个有用的结果"。验证方式：

- Ken 自己输入 3 个他**真实关心**的问题（不是测试问题）
- 看返回的 Response JSON 渲染成报告 / SSE 流能不能给 Ken **思考启发**
- 不是跑通接口就算，是**内容本身对 Ken 有用**

如果 Ken 反馈 "不够深 / 不够锐 / 套话多"，回到 `kpax_renderers.py` 的 prompt 调整，而不是接口层改。

### 11.3 v0 不验证的（明确推到 v0.1 / v1）

- 付费意愿（没有前端，没有付费流程）
- 化身续聊（v1）
- Voice TTS / STT（v1）
- 时间博物馆多场景（v1）
- 野生专家 / 真人化身（v1 人物 skill）
- 动态 expert_builder（v0.1）

### 11.4 v0 完成后的下一步（触发 v0.1）

v0 联调通过后，启动：
1. KPAX 前端做一个最简报告渲染 UI（不是座谈会，是 Response JSON 结构化渲染）——让 Ken 能在浏览器看报告
2. 基于 v0 数据做 rubric v0.1-reviewed 的 judge.py 实现（Lucas 量化闭环 A 步）
3. KPAX v1 形态设计（座谈会 3D + voice + 续聊）进入开发

---

## 12. 向后兼容与版本控制

- 本文件是 v1.1（原）+ v1.2（2026-04-17 补充 §7-§11，cc）。**没有破坏性修改**，只是补充。
- `expert_lenses` 字段扩展新加 `expert_key` / `name_zh` 是**新增字段**，不破坏已 parse 的 KPAX 前端。
- SSE 从 v0.1 提前到 v0 必做是**范围扩张**，不是协议变更。
- Followup endpoint 是**新 URL**，不影响原 3 endpoint。

未来真的要破坏性修改，走 `/axl/v2/`，不在 v1 路径下改 schema。
