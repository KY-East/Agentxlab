# 涌现来源分解实验

**设计者**：Cursor
**执行者**：Claude Code
**审阅者**：Ken
**状态**：checkpoint_0_report_ready（与 `experiments/config/experiment_registry.json` 同步；以 registry 为准）
**上游依据**：`notes/research/role-labels-vs-orchestrator.md` 第三节

---

## 1. 研究问题

AXL 多 agent 推演产出高于单 agent 的现象，收益到底来自哪里？

五个候选来源：
- **(a)** Moderator 对丰富 transcript 的综合能力
- **(b1)** 知识异质——Zep 按学科注入不同的论文和知识
- **(b2)** 模型异质——不同 agent 用不同 LLM（DeepSeek / GPT / Claude）
- **(c)** 更大的 token 预算（Anthropic 结论：80% 收益来自 token 量）
- **(d)** 学科角色标签激发了真正不同的推理模式 ← 核心假设

当前 7 agent vs 3 agent 对比无法分离这五个因素。本实验通过控制变量逐个拆开。

---

## 2. 实验组定义

| 组 | ID | agent 数 | 学科标签 | 知识注入 | 模型分配 | 控制的变量 |
|---|---|---|---|---|---|---|
| **基线** | `baseline` | 7 | 不同学科 | 按学科 Zep 检索 | 随机混合 LLM | 现状 |
| **A** | `no_labels` | 7 | 全部"通才"，无学科 | 按学科 Zep 检索 | 随机混合 LLM | 去学科标签 → 测 (d) |
| **B** | `same_knowledge` | 7 | 不同学科 | 全部用同一份混合知识包 | 随机混合 LLM | 去知识异质 → 测 (b1) |
| **C** | `same_model` | 7 | 不同学科 | 按学科 Zep 检索 | 全部用同一个模型 | 去模型异质 → 测 (b2) |
| **D** | `orchestrator` | 1 orchestrator | 无 | 7 个学科 corpus 作为工具（强制每个 corpus 至少检索 1 次） | 单模型 | 完全替代多 agent |
| **E** | `token_budget` | 1 | 无 | 按问题检索 | 单模型 | 单次调用，context 塞满到 baseline 总 token 量 |

### 组 A 详细说明
- 7 个 agent 的 system prompt 去掉所有学科描述，替换为"你是一位跨领域通才研究员"
- Zep 知识注入保留，但每个 agent 注入的知识仍按原来的学科分配（保持知识异质）
- 如果 A ≈ 基线 → 学科标签是装饰，(d) 是幻觉

### 组 B 详细说明
- 7 个 agent 保留学科标签
- 所有 agent 收到同一份知识包 = 所有学科 Zep 检索结果的合并
- 如果 B ≪ 基线 → 知识异质贡献大

### 组 C 详细说明
- 保留一切，只把所有 agent 的模型统一为 deepseek（成本最低的）
- 如果 C ≪ 基线 → 模型异质贡献大

### 组 D 详细说明
- 1 个 orchestrator agent，prompt 里描述 7 个学科视角
- 7 个学科 corpus 作为独立的 Zep 检索工具
- **强制约束**：orchestrator 必须对每个 corpus 至少检索 1 次（保证知识覆盖度和 baseline 可比）
- 跑 3 轮自我迭代（模拟 3 轮推演的 token 量）
- 如果 D ≈ 基线 → 多 agent 架构是可选的，orchestrator + tools 能平替

### 组 E 详细说明
- 1 个 agent，**单次调用**，无学科标签，无 moderator，无多次调用
- Context 尽量塞满：输入 = 问题 + 按问题检索的 Zep 知识（不分学科，全部混合）；要求长输出
- 总 token 消耗目标：和 baseline 的平均总 token 一致（通过 max_tokens 参数控制）
- 直接输出最终答案，不经过 moderator 综合
- 如果 E ≈ 基线 → 只需要更多 token，多 agent 架构是昂贵的 token 分配器
- **注意**：这是 Anthropic "80% 收益来自 token 量"的直接复现。不做"多次调用拼接"——那会引入额外自由度

---

## 3. 基准问题集

5 种问题类型 × 10 题 = 50 题。问题集冻结后不改。

### 选题原则
- 每题必须是真实可分析的问题（不是玩具例子）
- 必须涉及 2+ 个学科交叉
- 难度分布：3 简单 / 4 中等 / 3 困难
- 语言：中文
- **决策题和选择题的关系**：本质都是"多选项权衡"，区别是选择题的选项显式给出、决策题的选项需要先识别。分析引擎层面是同一类，报告渲染层面不同（选择题需要对比表）。保留两类分开实验，跑完后可以看"显式选项 vs 隐式选项"有没有质量差异

### 问题类型和示例

**预测题（Probability）** — 要求输出明确概率或数值区间：
1. 2026 世界杯巴西 vs 德国，巴西赢的概率是多少？
2. 未来 5 年内中国一线城市房价会下跌超过 20% 吗？
3. SpaceX 星舰在 2027 年前能成功载人登陆火星吗？
4. 俄乌战争在 2026 年内会达成正式停火协议吗？
5. 2030 年前会出现通过图灵测试的 AGI 吗？
6. 未来 3 年内全球会爆发一场波及 3 国以上的金融危机吗？
7. 中国人口到 2035 年会跌破 13 亿吗？
8. 特斯拉 FSD 在 2027 年前能拿到中国完全自动驾驶牌照吗？
9. 2026 年底前 BTC 会突破 20 万美元吗？
10. 下一次全球性传染病大流行（WHO 宣布 PHEIC 级别）会在 2030 年前发生吗？

**决策题（Decision）** — 本质是 yes/no 或隐式二选一，选项需要先识别：
1. 我 28 岁，在上海月薪 2 万，该不该辞职去创业做 AI 产品？
2. 家里有 200 万存款，该在杭州买房还是继续租房等降价？
3. 孩子今年高考，该选计算机还是医学？
4. 现在有一个办美国 O1 签证的机会，但我不是很想留在美国，该拿这个身份还是放弃？
5. 我的孩子 8 岁，应不应该让他大量使用 AI 工具辅助学习？
6. 我爸的房地产公司负债 30 亿，我是该回去救公司还是自己创业过自己的生活？
7. 35 岁程序员，大厂被裁，该接受降薪 40% 的中小公司 offer 还是全职做独立开发者？
8. 手里有一套北京学区房，孩子刚上完小学，现在卖掉换成现金投资还是继续持有？
9. 我在体制内干了 8 年，现在有机会跳去一家 AI 创业公司当 CTO，该不该去？
10. 父母希望我回老家发展，但我在深圳已经有稳定事业，该回去吗？

**选择题（Comparison）** — 选项显式给出，需要横向对比：
1. iPhone 17 Pro vs Samsung Galaxy S26 Ultra vs Pixel 10 Pro，哪个最值得买？
2. 留学选 MIT 还是 Stanford 还是 CMU 的 CS 硕士？
3. 创业融资选红杉、高瓴还是真格？
4. 投资配置：美股（标普 500）vs BTC vs 中国 A 股，现在 100 万该怎么分？
5. 移民选加拿大、新加坡还是日本？（考虑 AI 从业者背景）
6. 孩子学编程：Python vs Scratch vs 直接用 AI 对话式编程，哪个路线好？
7. 新能源车选比亚迪汉 vs 特斯拉 Model 3 vs 小米 SU7？（家用，预算 25 万）
8. 创业做 AI 产品，选 ToB SaaS vs ToC 消费级 vs API 平台？
9. 健身方式选力量训练 vs 跑步 vs 游泳？（30 岁久坐上班族，目标是长期健康）
10. 个人知识管理工具选 Notion vs Obsidian vs Logseq？（研究者用途）

**策略题（Strategy）** — 需要输出分步骤的执行路线：
1. 一个 3 人 AI 创业团队，0 到 1 阶段应该怎么分配精力（产品/技术/市场）？
2. 中国新能源车企如何在欧盟关税壁垒下保持市场份额？
3. 一个独立开发者如何在 6 个月内把 SaaS 产品做到 $10K MRR？
4. 我要做一个 AI 驱动的细胞重编程生物科技公司，目标 3 年内上市，路线图怎么设计？
5. 我做了一款 AI agent 对战产品，怎么 GTM，怎么一个月做到 15 万美金利润？
6. 一个二线城市的公立高中如何在 3 年内把一本率从 40% 提升到 70%？
7. 一个 50 人的传统制造业工厂，怎么分阶段引入 AI 提升产能 30%？
8. 一个海外华人自媒体，从 0 开始怎么在一年内做到 YouTube 10 万订阅？
9. 中国一个三线城市怎么通过 AI 产业吸引人才回流？
10. 一个刚拿到天使轮的 AI 教育公司，如何设计前 18 个月的产品和增长策略？

**评估题（Evaluation）** — 需要多维度打分和综合判断：
1. 评估 OpenAI 的 AGI 路线图可行性
2. 评估远程办公对团队创造力的长期影响
3. 评估中国高铁出海战略的成功概率和关键风险
4. 评估未来 10 年对 AI 创业者来说，最适宜创业的 3 个国家/地区
5. 评估中美未来 20 年的经济体量走势，中国 GDP 超过美国的概率
6. 评估 Anthropic 的"宪法 AI"路线能否成为 AI 安全的主流范式
7. 评估 2026 年全球 AI 监管格局对创业公司的影响（欧盟 AI Act vs 美国 vs 中国）
8. 评估"数字游民"生活方式的长期可持续性（经济、健康、社交三维度）
9. 评估 Web3 / 区块链技术在 2030 年前的实际落地前景（去掉投机泡沫后）
10. 评估中国民营航天（蓝箭、星际荣耀等）在 2030 年前追上 SpaceX 的可能性

**基准集状态：50 题已冻结。不再修改。**

---

## 4. 评估指标

**两套指标分角色解释，不可相互替代，并列呈报：**
- **质量结论** ← LLM Judge + 人工评分（回答"输出好不好"）→ 判断哪个组的最终报告更有用
- **机制结论** ← 多样性机械指标（回答"涌现来源在哪、多样性从哪来"）→ 判断去掉某个变量后多样性是否坍缩

两套结论在 summary.md 里独立报告，不允许一套吞掉另一套。质量指标回答"值不值"，多样性指标回答"来源在哪"，这是两件事。

### 4.1 LLM Judge 质量评分

盲评——judge 不知道结果来自哪个组。Judge 用一个**独立于 baseline agent 池家族的强模型**（如 GPT-5 / Gemini 2.x 等，整个实验期间固定一个不换，避免 self-preference bias 和跨批次漂移）。

**Rubric**：采用 **Pilot Judge Rubric v0.1**（Ken 2026-04-16 拍板）。完整 rubric 文档：
`results/dry_run_20260416_165636/pilot_judge_rubric_v0.1.md`

**来源与版本路径**：
- v0.1：AXL 自己跑 meta_01 元任务产出（递归 dogfooding，recursive validation of the engine on a real academic question）
- v0.1-reviewed：`@cursor` 独立审修订版（识别 AXL 自偏置，见 `notes/agenda/next.md` P0 Rubric C 任务）
- v0.2：meta_01 跑完整 4 轮 standard depth 产出的精炼版（需 runner timeout 调整到 4800s）
- v1.0：pilot 校准数据 + A/B 回归测试后的稳定版

**rubric 核心结构（100 分制，每段 25 分）**：
- 通用维度 15 分（实质性 / 可证伪性 / 诠释框架显化 / 跨学科碰撞 / 可解释性）
- 段落特异维度 10 分（每段的 A/B/C/D 两个专属指标）
- 偏差鲁棒性校验层（标签遮蔽 / 风格改写 / 顺序扰动 / 伪深刻 / 伪具体 5 项对抗测试）
- 强制人工复核触发条件（6 项）
- Hybrid 总分合成（段均 × 0.85 + 最低段 × 0.15，带底线拦截）

**适用范围**：评估 moderator 每场 `consensus / disagreements / open_questions / directions` 四段输出。

详细评分 anchor 和评估方法见 `pilot_judge_rubric_v0.1.md`，此处不重复。

**5 维度评分**（删掉 novelty，替换为机械可统计的跨学科引用数，移到 4.2）：

```json
{
  "question_id": "prob_01",
  "group_id": "baseline",
  "run_id": 1,
  "scores": {
    "relevance": 1-5,
    "depth": 1-5,
    "evidence_quality": 1-5,
    "balance": 1-5,
    "actionability": 1-5
  },
  "overall": 1-5,
  "judge_reasoning": "..."
}
```

**Anchoring 示例（必须写进 judge prompt）：**

| 维度 | 1 分 | 3 分 | 5 分 |
|---|---|---|---|
| relevance | 完全没回答用户问的问题，跑题 | 回答了主要问题但遗漏了关键约束条件 | 精准回应用户问题的每一个具体方面 |
| depth | 只有表面常识，任何人都能说出来 | 有一些专业分析但停在第一层因果 | 揭示了非显然的深层机制或二阶效应 |
| evidence_quality | 没有任何具体依据，全是观点 | 引用了一些数据/论文但不够具体 | 每个论点都有具体来源、数据或案例支撑 |
| balance | 只看一面，明显偏向某个结论 | 提到了多个角度但有的角度明显敷衍 | 各角度都得到了认真分析，包括不利证据 |
| actionability | 结论模糊到无法执行 | 给了方向但缺少具体步骤或条件 | 给出了可直接执行的具体行动+判断条件 |

Judge prompt 要求：只看最终输出质量，不看过程。不知道有几个 agent、什么模型。

**Judge 自一致性校准**（在 pilot 阶段执行）：
- 抽 10 份 transcript 让 judge 跑 3 次
- 各维度分数 std > 0.5 则 judge prompt 不合格，需要重写 anchoring
- 校准通过后才启动正式评分

### 4.2 多样性指标（机械统计，可重复）

这些指标比 LLM Judge 噪声低、可重复。最终分析时**质量和多样性双报告，分角色解释**：质量结论看 Judge+human，机制结论看 diversity，各管各的，不相互替代。

```json
{
  "question_id": "prob_01",
  "group_id": "baseline",
  "run_id": 1,
  "diversity": {
    "pairwise_cosine_mean": 0.42,               // agent 发言两两 embedding 余弦距离均值
    "unique_concept_count": 23,                  // 去重后的独立概念数
    "stance_shift_count": 5,                     // agent 在推演中改变立场的次数
    "cross_discipline_reference_count": 8,       // 跨学科引用次数
    "cross_discipline_concept_count": 12         // 引用的非本学科概念数（替代原 novelty 维度）
  }
}
```

### 4.3 成本指标

```json
{
  "question_id": "prob_01",
  "group_id": "baseline",
  "run_id": 1,
  "cost": {
    "total_tokens": 45000,
    "total_cost_usd": 0.12,
    "latency_seconds": 45,
    "llm_calls": 21
  }
}
```

### 4.4 人工评分（验证子集）

每组随机抽 10 个结果，Ken 自己盲评。打分维度和 LLM Judge 一样。用来校准 LLM Judge 的可靠性。

---

## 5. 执行协议

### 5.1 运行参数

- **每组每题跑 3 次**，取中位数
- **推演深度**：`quick`（控制成本）
- **推演轮数**：3 轮（标准）
- **语言**：中文
- **Judge 模型**：独立于 baseline 池家族的强模型（GPT-5 / Gemini 2.x 等，固定不换）
- **总运行量**：6 组 × 50 题 × 3 次 = 900 次推演（全量，需通过 pilot 后才启动）
- **预估成本**：通过 checkpoint 0 dry run 实测后确定（不再拍脑袋）

### 5.1.1 Checkpoint 0：Dry Run（成本估算）

正式跑之前必须先做：
- 跑 **10 次**（baseline 组，随机 10 题，每题 1 次）
- 实测：单次成本、延迟、失败率
- 外推到 900 次的总成本
- 输出 `results/dry_run_report.md`，Ken 看过批准后才继续
- **如果总成本 > $500，暂停，让 Ken 决定砍 run 数 / 砍组数 / 换便宜模型**

### 5.1.2 Checkpoint 1：Pilot（统计功效验证）

Dry run 通过后：
- 跑 **baseline + A 组各 20 题 × 2 run = 80 次**
- 目的 1：估 overall 分数的方差，回算 50×3 的样本量是否足够
- 目的 2：LLM Judge 自一致性测试——抽 10 份 transcript 让 judge 跑 3 次，各维度 std > 0.5 则 judge prompt 不合格要重写
- 目的 3：校准成本外推
- 输出 `results/pilot_report.md`，Ken 批准后才扩到全量

### 5.2 执行顺序

1. 先跑基线 + A 组（最关键的对比：学科标签有没有用）
2. 再跑 B + C 组（分离知识和模型异质性）
3. 最后跑 D + E 组（架构级替代方案）

每批跑完可以先看初步结果，不用等 900 次全跑完。

### 5.3 结果存储

```
emergence_decomposition/results/
├── run_20260415_100000/
│   ├── raw/
│   │   ├── baseline_prob_01_run1.json
│   │   ├── baseline_prob_01_run2.json
│   │   └── ...
│   ├── scores.json          ← 全部评分汇总
│   ├── diversity.json       ← 全部多样性指标汇总
│   ├── cost.json            ← 全部成本汇总
│   └── summary.md           ← 自动生成的分析
```

---

## 6. 判断标准

使用**效应量 + 显著性**双条件判断，不用百分比阈值：

- **显著性**：Wilcoxon 秩和检验 p < 0.05
- **效应量**：Cliff's delta（非参数效应量），|delta| < 0.15 视为"≈"（可忽略差异），|delta| > 0.33 视为"≪"（中等以上差异）
- 两套指标并列报告：质量结论看 LLM Judge overall + 人工校准，机制结论看多样性机械指标。各管各的，不相互替代

所有对比的"≈"条件统一为 `p > 0.05 或 |delta| < 0.15`，"≪"条件统一为 `p < 0.05 且 |delta| > 0.33`。

| 对比 | ≈ 的含义和动作 | ≪ 的含义和动作 |
|---|---|---|
| A vs 基线 | 学科标签是装饰，(d) 是幻觉 → 改写研究假设，弱化角色标签，强化知识注入 | 学科标签有真实效果，(d) 成立 → 继续强化，探索为什么有效 |
| B vs 基线 | 知识异质 (b1) 贡献可忽略 → Zep 按学科注入不是壁垒，可简化 | 知识异质 (b1) 贡献大 → Zep 按学科注入是核心壁垒，优先加强质量 |
| C vs 基线 | 模型异质 (b2) 贡献可忽略 → 可统一用一个模型省成本 | 模型异质 (b2) 贡献大 → 多 LLM 混合是核心壁垒，增加模型种类 |
| D vs 基线 | orchestrator + tools 能平替多 agent → KPAX 可大幅简化架构 | 多 agent 架构不可替代 → 架构本身有贡献，保留多 agent |
| E vs 基线 | token 是主因，多 agent 是昂贵的 token 分配器 → 把钱花在 token 预算上 | token 不是主因，多 agent 架构有架构级贡献 → 架构投资合理 |

---

## 7. Claude Code 执行清单

**按 checkpoint 顺序执行，每个 checkpoint 不通过就停下来问 Ken，不自己往下冲。**

0. **读本文件**确认理解实验设计，特别是第 5.1.1 / 5.1.2 节的 checkpoint 定义
1. **Checkpoint 0 — Dry Run**：
   - 实现 `runner.py` 最小可跑版本（只支持 baseline 组）
   - 跑 10 次（baseline 组，随机 10 题，每题 1 次）
   - 实测单次成本、延迟、失败率，外推到 900 次总成本
   - 产出 `results/dry_run_report.md`
   - **停下来等 Ken 批准**。总成本 > $500 必须让 Ken 决定砍 run 数 / 砍组数 / 换模型
2. **Checkpoint 1 — Pilot**：
   - 扩展 `runner.py` 支持 A 组配置
   - 实现 `judge.py`（含 4.1 节的 anchoring prompt 和 GPT-4 调用）
   - 跑 baseline + A 各 20 题 × 2 run = 80 次
   - 做 judge 自一致性测试：抽 10 份 transcript 让 judge 跑 3 次，各维度 std > 0.5 则重写 anchoring prompt
   - 回算 50×3 样本量是否够，校准成本外推
   - 产出 `results/pilot_report.md`
   - **停下来等 Ken 批准**
3. **Checkpoint 2 — 全量实现**：
   - 扩展 `runner.py` 支持 B / C / D / E 全部组
   - 实现多样性计算（4.2 节指标，输出 diversity.json）
   - 实现成本统计（4.3 节，输出 cost.json）
4. **Checkpoint 3 — 分批全量运行**：
   - 按 5.2 节顺序分批：baseline+A → B+C → D+E
   - 每批跑完生成中间 `summary.md`，Ken 看过再跑下一批
5. **Checkpoint 4 — 可视化 + 盲评工具**（1 天以内，超时停下问 Ken）：
   - Streamlit 或静态 HTML 看板读 `scores_combined.json`
   - CLI 盲评工具写 `human_scores.json`
   - 自动合并输出 `scores_combined.json`
6. **Checkpoint 5 — 最终分析**：
   - 最终 `summary.md`：组间对比表 + Wilcoxon p 值 + Cliff's delta + 质量/机制双报告
   - 对 `notes/research/remediation-plan-multi-agent.md` 的反馈
   - 更新 `experiment_registry.json` 状态

不需要：
- 不需要改 AXL debate_engine 代码
- 不需要改前端
- 不需要改 Zep manager

---

## 8. 可视化 + 评分工具（最小版）

第一轮用最简实现。Ken 觉得不够用了再升级到 React dashboard。

### 8.1 技术栈

**Streamlit 单文件 app**（或静态 HTML + Chart.js）。不用 React，不建前端项目结构。
实现预算：**1 天以内**。超过 1 天停下来问 Ken。

### 8.2 功能（v1 只做这些）

**结果看板**（只读）：
- 6 组 × 5 维度的评分表（带背景色的热力图 table）
- 每组 overall 分数的箱线图
- 成本对比柱状图（token / 美元 / 延迟）
- 多样性指标对比图

**人工盲评**：
- CLI 或最简 HTML 表单（随机抽题 → 显示 transcript → 输入 5 个分数 + 评语 → 写 JSON）
- 不显示来自哪个组（盲评）
- 提交后自动写入 `results/run_xxx/human_scores.json`

**v1 不做**：
- 实验控制台（runner.py 命令行跑）
- AI 辅助评语草稿（先手写，真不够再加）
- 点击追溯到 transcript（v1 不做）
- SSE 实时进度条

### 8.3 数据闭环（核心）

这是整个后台最重要的设计——**打分结果是 agent 的训练数据，不只是人看的报告**。

```
人工打分
   ↓ 自动写入
experiments/results/run_xxx/human_scores.json    ← 结构化 JSON
   ↓ 自动聚合
experiments/results/run_xxx/scores_combined.json  ← LLM judge + 人工合并
   ↓ agent 可读
下次 Claude Code / Cursor 改代码时：
  - 读 scores_combined.json
  - 知道哪个组好、哪个差、差在什么维度
  - 直接引用具体分数作为改动依据
  - 不需要 Ken 手动传话
```

**写入协议**：

```json
{
  "question_id": "prob_01",
  "group_id": "baseline",
  "run_id": 1,
  "evaluator": "ken",
  "timestamp": "2026-04-15T10:30:00Z",
  "scores": {
    "relevance": 4,
    "depth": 3,
    "evidence_quality": 5,
    "balance": 4,
    "actionability": 3
  },
  "overall": 4,
  "comment": "深度不够，没有考虑到汇率因素"
}
```

**Agent 读取约定**：

任何 agent 改 re-rank 权重、debate prompt、推演参数前，如果 `experiments/results/` 里有相关实验数据，**必须先读数据再做决策**。这条写进 `.cursor/rules/research-context.md` 和 `AGENTS.md`。

### 8.4 Claude Code 执行清单（追加）

在第 7 节基础上追加：

7. **实现最简可视化**（Streamlit 或静态 HTML，1 天以内）：
   - 读 `scores_combined.json` 画看板
   - 实现 CLI 盲评工具，输出 `human_scores.json`
   - 合并 LLM + 人工评分输出 `scores_combined.json`

---

## 9. 风险和缓解

| 风险 | 缓解 |
|---|---|
| 900 次推演成本过高 | Checkpoint 0 dry run 估真实成本 → pilot 80 次验证 → Ken 批准后才全量 |
| LLM Judge 不可靠 | Pilot 阶段做 judge 自一致性测试（std > 0.5 重写 prompt），人工评分子集校准 |
| 基准问题选偏 | 5 类 × 10 题分散风险 |
| Zep 检索不稳定 | quick depth + retry + 降级 |
| 组间 token 消耗不一致 | E 组专门控制总 token 量一致 |
