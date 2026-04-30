# Dry Run Report — emergence_decomposition Checkpoint 0

> **目录**: `experiments/emergence_decomposition/results/dry_run_20260414_173832/`  
> **wall-clock（粗）**: 2026-04-14 17:38 → 2026-04-15 04:08（约 10 小时窗口；进程随后已退出）  
> **完成度**: **5 / 10** 条 debate 产出有效 `raw/*.json`，**5 条失败或未落盘**（rate limit / 超时 / 网络 / 无限 retry）  
> **Ken 拍板（2026-04-15）**: **5 条足够做成本外推，不重跑第四次 dry run**；完整质量与方差验证交给 **Checkpoint 1 pilot**。

---

## 1. 实验目的（有效性）与本报告边界

**研究问题**（见 `spec.md` §1）是：多 agent 推演的「好处」来自哪里——**质量**（独立 LLM Judge + 可选 human）与**机制**（diversity 等指标）能否区分 **(a) moderator、(b1)(b2) 知识/模型异质、(c) token、(d) 学科标签**。这才是实验的**有效性主战场**。

**Checkpoint 0（本 dry run）不负责回答上述问题。** 它只解决三件事：

| 职责 | Checkpoint 0 做了什么 | 仍缺什么（留给 pilot / 全量） |
|------|-------------------------|-------------------------------|
| **管线有效** | 5 条 baseline 产出完整 `raw` transcript + `metrics`，证明 **runner → AXL → 落盘** 可观测、可复用 | 未跑 A/B/C/D/E 对照组，**无法**比较组间差异 |
| **数据可评** | 输出结构满足后续 **Judge 打分、diversity 计算** 的输入形态（transcript 在） | **未调用** `judge.py`、未算 diversity；**无**任何「好不好」的分数 |
| **预算可行** | 给出单次 USD / 时长数量级，判断全量是否**付得起、排得开** | 成本是**约束条件**，不是假设检验；**$500 门禁**是工程护栏，不是 p 值 |

**结论**：本报告**长篇幅写成本**，是因为 dry run 的产出**天然**是成本与稳定性；**不是**把实验目的偷换成「省钱」。**有效性结论**必须在 **Checkpoint 1 pilot**（方差、judge 校准）和 **全量**（组间对比、Wilcoxon / Cliff's delta）里出——见 `spec.md` 评估与统计章节。

---

## 2. 为何 5/10 可接受

- **5 条完整 metrics** 已覆盖题型：**comparison ×2、decision ×2、probability ×1**（均 `depth=quick`，每场 **54** 次 LLM 调用）。
- 成本外推对「单次 debate 的 USD / token」均值估计**不敏感**于是否凑满 10 条；真正需要大样本的是 **pilot 的方差与 judge 校准**。
- 第 4 次 dry run 已多次重启；继续在同一配额与网络条件下重跑，边际信息有限、工程风险高。
- **失败根因**已明确（见第 5 节），不是 AXL 业务逻辑 bug，而是 **runner 韧性 + API 配额 + 网络**。

---

## 3. 单次成本（5 条完成的 debate）

| question_id | 题型 | 内容轮次 (max) | llm_calls | prompt_tokens | completion_tokens | total_tokens | cost_usd | wall_sec |
|-------------|------|----------------|-----------|-----------------|-------------------|--------------|----------|----------|
| cmp_04 | comparison | 3 | 54 | 499706 | 55937 | 555643 | 1.8137 | 1582.66 |
| cmp_06 | comparison | 3 | 54 | 469679 | 53557 | 523236 | 1.6086 | 2069.58 |
| dec_02 | decision | 3 | 54 | 500779 | 53462 | 554241 | 2.1510 | 1606.32 |
| dec_10 | decision | 3 | 54 | 495516 | 56825 | 552341 | 1.5380 | 2360.34 |
| prob_05 | probability | 3 | 54 | 491623 | 55906 | 547529 | 1.8910 | 3142.94 |

**聚合（n=5）**

| 指标 | mean | median | p95* | min | max |
|------|------|--------|------|-----|-----|
| prompt_tokens | 491461 | 495516 | 500564 | 469679 | 500779 |
| completion_tokens | 55137 | 55906 | 56647 | 53462 | 56825 |
| total_tokens | 546598 | 552341 | 555363 | 523236 | 555643 |
| cost_usd | **1.800** | **1.814** | **2.099** | 1.538 | 2.151 |
| wall_sec | **2153** | **2069.6** | **2986** | 1582.7 | 3142.9 |

\* p95 用线性插值（n=5 的小样本近似）。

**模型费用拆分（示例：cmp_04）**：`deepseek-chat` 约 $0.04；`gpt-5.4` 约 $1.04；`claude-opus-4-6` 约 $0.73（每场因调用分布不同，prob_05 上 Opus 占比更高）。

---

## 4. 全量外推（900 debates，顺序跑）

以 **mean cost_usd ≈ 1.800** 计：

- **900 × 1.800 ≈ $1,620**（点估计）
- **900 × median 1.814 ≈ $1,633**

以 **mean wall_sec ≈ 2153 s** 计：

- **900 × 2153 s ≈ 1,937,700 s ≈ 538 h ≈ 22.4 天**（单 worker 顺序、无并行）

### Checkpoint 0 成本门禁（spec：全量约 $500 量级需审视）

| 判据 | 结果 |
|------|------|
| 900 次点估计 vs $500 | **未通过**（约 **3.2×**） |
| 解读 | 当前 **quick 深度 + 7 agent + 混合模型 + Opus moderator** 下单场成本偏高；需在 **pilot 前**从「减组 / 减 run / 换 moderator / 提配额」中选组合，或接受分阶段预算 |

**若需压成本（方向性，具体数字在 pilot 用实测校正）**

- **砍重复 run 数**（spec 原定每题 3 run）：线性降总成本。
- **砍实验组数或先做 baseline+A**：线性降样本量。
- **dry run / pilot 换非 Opus moderator**：分钟级 input token 压力下降，但需在 report 记 **校正系数**（正式实验仍可按 Ken 规则固定 Opus）。

---

## 5. 失败与卡死原因（5 条未完成）

归纳（与 Claude Code 现场诊断一致）：

1. **Anthropic 组织级 rate limit**（约 30k input tokens/min）：moderator 单次调用可 **15–25k+ input tokens**，易触顶。
2. **DeepSeek 单次请求长时间阻塞**（如 **600s** 级 timeout 打满）。
3. **本地网络 DNS / 断连**（`getaddrinfo failed` 等）。
4. **runner 无 max retry 上限**：失败即重试，易在 **rate limit + 抖动** 下长时间空转。

**结论**：属 **基础设施与 runner 策略** 问题，不是「辩论引擎逻辑错误」；但 **pilot 前必须改 runner**（见第 6 节）。

---

## 6. Runner 必改三项（pilot 开跑前，@cc P0）

1. **`max_retries=3`（或等价 hard cap）**：超限将该 debate 标 **failed**，记原因，**进入下一条**。
2. **debate 之间强制 `sleep(65)`**（或按 provider 文档对齐到 **分钟级窗口**），缓和 **Anthropic 分钟配额**。
3. **`progress.jsonl` heartbeat**：每完成一场 append 一行 `{question_id, status, ts, cost_usd?}`，可脚本监控「是否还活着」。

---

## 7. Moderator 选型（pilot 前拍板，建议写入 pilot 配置而非口头）

| 选项 | 做法 | 成本/时长 | 质量与可解释性 |
|------|------|-----------|----------------|
| **A** | dry run / pilot 用 **GPT-5 或 Gemini 2.x** 做 moderator；**正式全量**再固定 **Opus** | 分钟配额压力显著下降；成本通常低于 Opus | 需在 pilot 报告里记 **模型校正系数**（相对 Opus） |
| **B** | **全程 Opus** + **debate 间 sleep 65s** | 时长上升（粗估 10 debate 可 +~10 min 量级 sleep，但总时长仍受单次调用 token 影响） | 与「正式实验」一致，无跨模型校正 |
| **C** | **提升 Anthropic 档位**（tier 2/3，更高 input tok/min） | 费用上升 | 最少改实验设计，依赖商务/配额 |

**建议**：**A** 适合 **校准成本与防卡死**；**B** 适合 **强一致性、可接受更长 wall-clock**；**C** 适合 **少改代码、预算换配额**。正式实验的「Opus moderator」规则建议在 **spec 中区分 calibration 阶段 vs production 阶段**。

---

## 8. 内容层观察（n=3 transcript，observations only，**非结论**）

> **边界**：人工读过 3/5 场完整 transcript（`cmp_04`、`dec_02`、`prob_05`）。**未跑对照组、未跑 Judge、未算 diversity**。本节只记**可观测现象**，不充当 spec (a)~(d) 的假设检验答案。

**观察**

1. **baseline 下存在可观测的交互信号**。七学科不是轮流独白：Round 2 出现互相点名（数学 ↔ 物理、心理 ↔ 数学、艺术人文 ↔ 经济）、立场在对手压力下位移（`dec_02` 数学从"单模型最优阈值"转向"分布鲁棒优化"、部分承认物理学批评）。这给 A 组（去标签）对照提供了**差异可测的基础**——**能不能说"机制生效"要等 A 组对比**。
2. **每条消息篇幅明显偏长**（2000–4000 字/条），同一轮内对同一对手的攻击角度有重复。怀疑是 **token limit 过宽** 或 prompt 未强制去重。对 pilot 的影响：**Judge 打分可能被长度干扰**、`unique_concept_count` / `cross_discipline_reference_count` 需**去重/per-token 归一**，否则灌水会拉高 diversity 指标。
3. **文献引用密度高**（每条约 3–5 篇，涉及 Kahneman/Tversky、Poterba、Mandelbrot、Bourdieu、Heidegger、Foucault 等），用法在论证链里有功能位、不是堆关键词。**但未验证引用真实性**——pilot 前人工抽 10 条查是否真存在，真实后再考虑加入 `evidence_quality` 代理指标。
4. **moderator 最终综合段未读到**（本节只读了 agent 消息流），因此"最终输出质量"仍未评估。

**对 pilot 的可落地影响**

| 观察 | 动作 | 归属 |
|------|------|------|
| 消息过长 / 重复 | 收紧 agent max_tokens；prompt 加"不得复述本轮他人已提论点" | `@cursor` spec prompt 调整 |
| Judge 长度偏好 | Judge prompt 显式"长度不是优点"；或 per-token 归一 | `@cursor` spec §4 judge |
| diversity 灌水 | `unique_concept_count` 去重 + per-token 归一 | `@cursor` spec §metrics |
| 引用真实性 | pilot 前人工抽 10 条 | `@ken` 或 `@cc` 工具脚本 |

---

## 9. Checkpoint 0 结论与下一步

- [x] **5/10 样本足够**做本次 **成本与时长数量级**外推（Ken 已确认不重跑）。
- [x] **runner 三项**列入 **agenda P0**（pilot 前落地）。
- [ ] **有效性**：**未测量**；pilot 起才进入 **Judge + diversity + 方差**，再谈「多 agent 是否更好、好在哪里」。
- [ ] **moderator 策略**在 **pilot 启动会**上定 A/B/C（或混合）。
- [ ] **Ken 审批**本 report 后：`experiment_registry` 进入 **「report 已就绪 → 待 pilot」**；**Checkpoint 1 pilot** 见 `spec.md` 与 `notes/agenda/next.md`。

**原始数据文件**

- `raw/baseline_cmp_04.json`
- `raw/baseline_cmp_06.json`
- `raw/baseline_dec_02.json`
- `raw/baseline_dec_10.json`
- `raw/baseline_prob_05.json`

---

*生成：Cursor，metrics 自 raw JSON `metrics` 字段汇总。*
