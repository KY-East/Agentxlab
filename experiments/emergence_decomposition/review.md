# Spec Review — emergence_decomposition

**Reviewer**：Claude Code
**Date**：2026-04-14
**Status**：all addressed — Cursor 已修订 spec
**对象**：`experiments/emergence_decomposition/spec.md`

本文件是对 spec 的审阅意见。分"必须改"和"建议改"两类。Cursor 看完后在 spec 里对应位置修订，不要直接删本文件，改完标注 "addressed"。

---

## 必须改（blocker，不改不能开跑）

### R1. 第 8 节研究后台降级为最小可视化

**问题**：当前 8.1/8.2/8.4 规划了 React + Tailwind + Vite + FastAPI + SSE + 热力图 + 箱线图 + AI 辅助评语 的完整 dashboard。实验还没跑一次，基座先盖好，典型的预防性架构。违反 Simplicity First。

**但**：Ken 明确说需要可视化来评估结果，不能只看 JSON。这个需求是真的，不能忽视。

**修订方向**：

保留 8.3 数据闭环协议（human_scores.json + scores_combined.json + "agent 改参数前必须先读数据"硬规则）——这是核心，不动。

砍掉：
- 实验控制台（runner.py 命令行跑就行，SSE 实时进度条不需要）
- AI 辅助评语草稿生成（先手写，真不够再加）
- 追溯 transcript 的点击跳转（v1 不做）

保留，但用最简实现：
- **结果 Dashboard 的只读版本**：一个静态 HTML（或最多一个 Streamlit 单文件 app），读 `scores_combined.json` 直接画：
  - 6 组 × 6 维度的评分表（热力图或带背景色的 table 都行）
  - 每组 overall 分数的箱线图
  - 成本对比柱状图
- **人工盲评界面**：最简 HTML 表单或一个 Python CLI（随机抽题→显示 transcript→输入 6 个分数→写 JSON）。先选一个 Ken 觉得顺手的。

实现预算：**1 天以内**。如果发现要超过 1 天，停下来先问 Ken，不自己扩展。

技术栈建议：**不用 React**。Streamlit 或 静态 HTML + Chart.js 就够，省掉前端项目结构 overhead。等实验跑完 Ken 真觉得不够用了，再迁移到 React——那时候是有数据驱动的扩展，不是预防性架构。

8.4 的 Claude Code 执行清单（React + 后端路由那条）整条删除，换成"实现最简可视化（Streamlit 或静态 HTML 二选一）"。

---

### R2. 统计功效没算，判断阈值和检验不匹配

**问题**：
- 判断标准表写 "A ≈ 基线（差 < 5%）" 和 "A ≪ 基线（差 > 15%）"。在 1-5 量表上 5% = 0.2 分，Wilcoxon 秩和检验在 n=50 vs n=50 下根本检不出来 0.2 的效应。
- 没有做过事前 power analysis，50 题 × 3 run 这个量是拍脑袋的。
- 百分比阈值（5% / 15%）和非参数检验（Wilcoxon）混用，概念不一致。

**修订方向**：

1. 判断标准改用**效应量 + 显著性**双条件：
   - 显著性：Wilcoxon p < 0.05
   - 效应量：Cliff's delta（非参对应的效应量），|δ| < 0.15 视为 ≈，|δ| > 0.33 视为 ≪
   - 百分比阈值全部删掉
2. 正式跑之前先跑 **pilot**：baseline + A 各 20 题 × 2 run = 80 次
   - 目的 1：估 overall 分数的方差，回算 50×3 够不够
   - 目的 2：校准 LLM Judge 稳定性（见 R4）
   - 目的 3：验证真实单次成本（见 R5）
   - Pilot 通过后才扩到全量 900 次。这是一个 stopping rule，明确写进第 5 节

---

### R3. 组 E 的设计没隔离掉它想隔离的变量

**问题**：当前 E 组 = "1 agent × 7 次调用 × 不同 prompt 引导方向 × moderator 综合"。这既加了 token 量，又加了"7 个引导方向"和 moderator 综合。如果 7 个方向来自学科，等于偷偷把 (d) 加回来；如果不来自学科，"引导方向"本身是新的自由度。E 组跑出来结果**不可解释**。

Anthropic 的"80% 收益来自 token 量"说的是单 agent 的 context / output 扩容，不是多次调用。

**修订方向**：

E 组改为：
- **1 个 agent，单次调用**
- Context 尽量塞满到和 baseline 总 token 消耗一致（输入长 context + 要求长输出）
- 无学科标签，无 moderator，无多次调用
- 直接输出最终答案

如果 Ken 确实想测"多次调用拼接"这条路径，那应该独立成一个新组 F，不要和 token budget 混。本实验先不做 F。

---

### R4. LLM Judge 缺 anchoring 和自一致性校准

**问题**：
- 6 维度光秃秃的 1-5 量表，没有锚点示例，judge 方差会很大
- novelty 维度（"用户自己想不到的角度"）LLM 判断几乎是随机噪声
- 没指定 judge 用什么模型，存在 self-preference bias 风险
- 没做 judge 自一致性测试

**修订方向**：

1. **给每个维度写 1/3/5 分的短 anchoring 示例**（各 1-2 句），写进 judge prompt。spec 4.1 节补一个子小节。
2. **novelty 删掉或替换**：替换为机械可统计的代理指标——"引用的跨学科概念数"或"提到的非显然关联数"。如果保留，明确标注是噪声维度，最后分析时权重降低。
3. **Judge 模型指定**：明确用一个固定的第三方模型（比如 GPT-4 或 Gemini），不能和 baseline 池子里的 agent 是同一个家族。写进 5.1 节。
4. **自一致性测试**：pilot 阶段抽 10 份 transcript 让 judge 跑 3 次，算各维度分数的方差。如果 std > 0.5 分，judge prompt 不合格，要重写。

---

### R5. $300-800 的成本跨度说明执行路径没定

**问题**：2.6 倍差距意味着模型选择、重试策略、失败处理都没定。不能开跑。

**修订方向**：

在第 5 节"执行协议"下加一个 **checkpoint 0**：

- 先跑 **10 次 dry run**（baseline 组，随机 10 题，每题 1 次）
- 实测单次成本、延迟、失败率
- 外推到 900 次的总成本
- 如果总成本 > $500，先暂停，让 Ken 决定是砍 run 数、砍组数、还是换便宜模型
- 这个 checkpoint 的结果写进 `results/dry_run_report.md` 让 Ken 看

这也是 Goal-Driven Execution 的直接应用——长任务的第一步必须是可验证的小规模试跑。

---

## 建议改（不 blocker，但 spec 会更好）

### R6. (b) 候选在研究问题和判断标准里指代不一致

第 1 节研究问题把 (b) 写成"异质模型 + 异质知识的真实多样性"——合为一项。但第 2 节表格和第 6 节判断标准把 B 和 C 分开测，结论也分开。建议第 1 节直接拆成：

- **(b1)** 知识异质（Zep 按学科注入）
- **(b2)** 模型异质（多 LLM 混合）

四个候选变五个，表达更准确。

### R7. 组 D 没规定 orchestrator 对 7 corpus 的调用约束

如果 orchestrator 自己决定调几次、调哪个，它可能只调 2 个 corpus 就收敛，token 消耗自然比 baseline 少。这时候 D ≪ baseline 不知道是"架构差"还是"token 少"。

两条路选一条：

1. **Fixed**：orchestrator 强制每个 corpus 至少检索一次（保证覆盖）
2. **Free + token-matched**：orchestrator 自由调用，但额外算一个子组 D' 强制把 token 消耗拉到和 baseline 一致，看质量是否追平

推荐路线 1，简单，可解释性强。spec 2.D 节补一句约束。

### R8. 双报告、分角色解释（原"主辅颠倒"收回）

**原始建议的错误**：v1 review 写过"主辅指标颠倒，方向冲突时先信多样性"。这是范畴错误，Codex 指出后收回。

原因：机械多样性指标（pairwise_cosine / unique_concept / cross_discipline_ref）测的是**过程多样性**，不是**输出质量**。两个 transcript 可以多样性爆表但综合报告稀烂，也可以多样性低但结论扎实。用"讨论得热闹不热闹"代替"结论好不好"是偷换概念。

**修订后的建议**：两套指标分角色解释，不可相互替代，并列呈报。

- **质量结论** ← Judge + human（回答"输出好不好"）
  - 指标：LLM Judge overall + 5 维度，人工校准子集
  - 用于判断：哪个组的最终报告更有用
- **机制结论** ← Diversity metrics（回答"涌现的来源在哪、多样性从哪来"）
  - 指标：pairwise_cosine_mean / unique_concept_count / stance_shift_count / cross_discipline_reference_count
  - 用于判断：去掉某个变量后多样性是否坍缩，涌现是否还存在

两套结论都要在 summary.md 里独立报告，**不允许一套吞掉另一套**。特别是不允许用多样性指标代替质量裁判。

这恰好对应本实验的原始目的——**拆解涌现来源**，不是单纯评质量。质量指标回答"值不值"，多样性指标回答"来源在哪"，本来就是两件事。

spec 第 4 节开头加一段说明，明确两套指标的分工和并列关系。

---

## 不需要改的部分（明确确认）

- 6 组核心思路（特别是 A 组去学科标签保留知识异质）
- 50 题 5 类基准集（Probability / Decision / Comparison / Strategy / Evaluation）冻结
- 执行顺序（baseline+A → B+C → D+E）
- 多样性辅助指标的 4 个维度
- 数据闭环协议（8.3 节），"agent 改参数前必须读数据"的硬规则
- 结果存储的目录结构
- 第 9 节风险缓解表

---

## 修订后 Claude Code 的执行顺序

1. Checkpoint 0：10 次 dry run，产出 `dry_run_report.md`，Ken 看过批准
2. Checkpoint 1：pilot（baseline + A 各 20 题 × 2 run = 80 次），产出 pilot 分析（方差、judge 自一致性、成本外推）
3. Checkpoint 2：Ken 批准后扩到全量，按 5.2 顺序分批跑
4. Checkpoint 3：每批跑完生成中间 summary.md，Ken 看过再跑下一批
5. Checkpoint 4：最简可视化（Streamlit 或静态 HTML，1 天以内），读 scores_combined.json
6. Checkpoint 5：最终 summary.md + 实验结论 + 对 `remediation-plan-multi-agent.md` 的反馈

每个 checkpoint 不通过就停下来问 Ken，不自己往下冲。

---

## 给 Ken 的一句话总结

Spec 的**科学骨架**没大问题，6 组思路对路，A 组尤其关键。**三个硬毛病**：统计功效没算（R2）、E 组设计混了变量（R3）、成本没估准（R5）——这三个不改直接跑会浪费钱出不可解释结果。**一个主观判断**：8 节那个 React dashboard 先不做，降级为 Streamlit 或静态 HTML 1 天搞定，等第一轮数据出来 Ken 觉得不够用再升级——这样既满足可视化需求，又不会在实验前盖 3 天前端基座。
