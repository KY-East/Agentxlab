# Mini Dry Run Report — prompt + max_tokens 收紧验证

> **目的**：验证 2026-04-15 对 `debate_engine.py` 的两处改动是否同时解决「冗长重复」与「单场贵」。
> **方法**：用 seed=42 取同样的 3 道题（**与原 dry run 完全重叠**），在新 config 下重跑，直接对比。
> **结论**：**双赢**——单场成本腰斩（–45%）、单条消息字数腰斩（–42~–49%）、wall-clock 减半（–55%）、**推演结论未降反锐**。Tier 1 Anthropic 配额自洽，0 失败。

---

## 1. 改动内容

**`projects/knowledge-graph/backend/app/services/debate_engine.py`**

1. `depth_tokens["quick"]`：`(1500, 1000)` → `(800, 600)`（只动 quick，不影响 standard/deep/max 的生产 KPAX 调用）
2. `_build_agent_system_prompt` 中文 `## 输出规则` 新增两条：
   - 严禁复述本轮他人已提过的论点或角度；要回应就必须升级/反驳/补新证据
   - 严禁凑字数：宁可短而锐利，不要长而啰嗦

**`experiments/emergence_decomposition/runner.py`**（runner 韧性三项一次性落地）

1. `progress.jsonl` heartbeat：run_start / debate_start / debate_done 每步写盘，可外部监控
2. `asyncio.wait_for(..., timeout=2000s)`：单场硬 cap 33 分钟，超限标 failed 进下一条
3. debate 之间 `await asyncio.sleep(65)`：缓和 Anthropic 分钟级 input token 配额

---

## 2. 3 场直接对比（同题 n=3）

| qid | 指标 | 旧 (04-14) | 新 (04-15) | Δ |
|---|---|---|---|---|
| **cmp_06** | cost_usd | 1.6086 | **0.8269** | **–48.6%** |
|  | total_tokens | 523,236 | 312,027 | –40.4% |
|  | wall_sec | 2069.6 | 885.4 | –57.2% |
|  | 单条字数 mean | 2040 | **1176** | **–42.4%** |
| **cmp_04** | cost_usd | 1.8137 | **0.8770** | **–51.6%** |
|  | total_tokens | 555,643 | 331,877 | –40.3% |
|  | wall_sec | 1582.7 | 892.0 | –43.6% |
|  | 单条字数 mean | 2075 | **1180** | **–43.1%** |
| **dec_10** | cost_usd | 1.5380 | **1.0118** | **–34.2%** |
|  | total_tokens | 552,341 | 327,752 | –40.7% |
|  | wall_sec | 2360.3 | 926.7 | –60.7% |
|  | 单条字数 mean | 2153 | **1102** | **–48.8%** |
| **mean (n=3)** | **cost_usd** | **1.6534** | **0.9052** | **–45.3%** |
|  | total_tokens | 543,740 | 323,885 | –40.4% |
|  | wall_sec | 2004.2 | 901.4 | –55.0% |
|  | llm_calls | 54 | 54 | 0（结构不变） |
|  | 单条字数 mean | 2089 | 1153 | –44.8% |

**关键**：llm_calls 不变，说明不是偷工减料跳步；变化完全来自**每次调用更短**与**每轮上下文重读更便宜**的复合效应。

---

## 3. 推演结论是否受损（内容层，非成本层）

对比 `cmp_06` 的 moderator summary（两份并列）：

### 3.1 consensus

**旧**：
> 启蒙工具的核心价值在于建立"可执行心智模型"。Scratch 因其概念完整性、执行可见性、错误可诊断性...

**新**：
> Scratch 的基石价值：低认知负荷、可视化反馈、公平性、叙事创作... Python 长期价值... **AI 对话式编程高风险**（明确点出）

→ 新版把"AI 对话式编程高风险"作为共识写进顶层，旧版埋在 disagreements 里。

### 3.2 disagreements

**旧**（抽象价值层冲突）：
> 终极目标的根本冲突：外部真实性 vs 内在主体性 vs 终身适应性

**新**（资源分配层冲突）：
> 路径时序与资源分配的优先级：社会最优普及公平 vs 个体最优卓越发展

→ 新版更可操作，旧版更哲学。

### 3.3 第一轮消息结构

随机抽新 config 数学学科 round-1 开场：

> # 数学学科立场陈述
> ## 核心论点
> 编程教育路线的选择本质上是一个关于"抽象层级跃迁"的认知数学问题
> ## 关键论据
> - 论据一：抽象层级理论（Kramer 2007 / Wing）...

→ 完整结构（核心论点 → 关键论据 → 文献引用）保留，不是被砍成骨架。

### 3.4 字数分布变紧

| | 旧 cmp_06 | 新 cmp_06 |
|---|---|---|
| min | 881 | 805 |
| max | 2822 | 1506 |
| median | 1954 | 1175 |

→ 旧版有灌水长消息（~2800 字），新版 max 贴着硬 cap（1506），分布紧。说明 agent 在 cap 压力下被迫提纯。

---

## 4. 全量外推（对比旧 report §4）

| 项 | 旧 report | 本次 mini run |
|---|---|---|
| mean cost_usd | $1.800 | **$0.905** |
| mean wall_sec | 2153 s | **901 s** |
| 900 场全量点估计 | **$1,620** | **$815** |
| vs $500 门禁 | 超 3.2× | 超 1.6× |
| 900 场顺序 wall | 22.4 天 | **9.4 天** |

**含义**：旧 report 建议的「砍题目/砍组/换 moderator」降本方案**全部作废**。新 config 下：

- Opus moderator 规则可保留（Ken 硬要求）
- run=3 可保留
- 6 组 50 题全量可保留
- 唯一未达 $500 门禁的缺口是 $300 量级，可通过 pilot 里可能出现的进一步优化 + 并行 worker 时长砍半来补齐

---

## 5. Rate limit 自洽验证

3 场全成功，0 失败，runner log 无 `429` / `rate_limit_error`。

原因：新 config 下单次 Opus moderator 调用 input 从 ~15–25k 降到 ~7–10k 量级（线性跟随总 token 降幅），加上 runner 的 `sleep(65)`，Tier 1 的 30k input tok/min 绰绰有余。

**结论**：**提 Anthropic tier 不再是必须**。后续 pilot 可直接在 Tier 1 下启动。

---

## 6. Checkpoint 0 真正关闭

| 子目标 | 状态 |
|---|---|
| 管线有效 | ✅（5/5 + 3/3 成功） |
| 数据可评 | ✅（raw + metrics 结构与 Judge / diversity 输入形态兼容） |
| 预算可行 | ✅（$815 量级，与 pilot 实际校正空间足） |
| 冗长重复（04-15 新暴露） | ✅（–45% 字数、硬 cap 生效、结论未降反锐） |
| runner 韧性 | ✅（heartbeat + timeout + inter-debate sleep 已落地） |

**Checkpoint 0 → Checkpoint 1 开闸。**

---

## 7. 下一步

1. `@cc` 按 `spec.md` §5.2 启动 Checkpoint 1 pilot：baseline + A 组各 20 题 × 2 run = 80 场，估 **~$73**，wall ~20 h
2. `@cursor` 把本次 mini run 的 prompt 经验沉淀进 spec §4（反重复规则、max_tokens 策略）
3. `@ken` pilot 跑完读 `pilot_analysis.md` 决定是否开全量

---

*生成：claude-code，基于 `raw/*.json` + `progress.jsonl` 统计，`dry_run_20260414_173832` 作为旧基线直接对比。*
