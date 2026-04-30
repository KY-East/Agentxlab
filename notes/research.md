# Research Notes — AXL/KPAX 研究笔记集合

**用途**：跨 agent（cc / cursor / codex / ken）共享的研究笔记。2026-04-17 从 `notes/research/*.md` 和 `notes/ideas/*.md` 多个独立文件合并到此单一文件，每篇原笔记对应一个 `## 大节`。原文完整保留，未做任何缩略或重写。

**阅读顺序（新人进项目推荐）**：

```
0. 思想渊源 (axl-intellectual-lineage)                 — OASIS → MiroFish → AXL 分叉
1. 涌现创造力假设 (emergent-creativity-hypothesis)     — 理论起点：我们在验证什么
2. 外部对位 (wisland-analysis-and-positioning)         — 为什么不走效率赛道
3. 自由参数 (agent-evolution-free-parameters)          — 护城河
4. 七层记忆 (seven-layer-memory-design)                — L7 元进化的物理载体
5. 架构诚实审视 (role-labels-vs-orchestrator)          — 多 agent vs orchestrator 的分歧
6. 修改方案 (remediation-plan-multi-agent)             — 基于前面的 4 个修改点
7. KPAX 知识源架构 (kpax-knowledge-source-architecture) — 三条输入线
8. 自进化量化闭环问题 (quantification-gap)             — Lucas 2026-04-17 提出的核心观察
```

**写作约定**：
1. 不放 TODO（行动项抽到 `notes/next.md`）
2. 论证完整：结论要有依据（引用数据 / 论文 / 实验 / 其他节）
3. 冲突解决：两节结论矛盾时，新节必须显式标注"与 §X 结论不一致，原因..."
4. 更新 vs 新增：小修直接编辑对应节；大版本（例如记忆体系 v2）在本文件内新增 v2 节，旧版保留历史对照
5. 引用其他节用 anchor：`[§自由参数](#agent-evolution-free-parameters-自由参数清单)`
6. 跨文件引用：`notes/design.md`、`notes/next.md`、`CHANGELOG.md` 等

**历史**：2026-04-17 前这些内容位于 `notes/research/*.md` + `notes/ideas/*.md`（共 7 个独立文件 + 2 个 INDEX.md）。合并原因：Ken 2026-04-17 指出 "文件越少越好，合并同类项，记录和战略类更是"。合并 commit 保留原 7 文件的独立 git 历史（通过 git mv + concat，可用 `git log --follow` 追溯）。

---


## axl-intellectual-lineage AXL 思想渊源：OASIS → MiroFish → AXL 分叉

> **补记缘由**：2026-04-20 Ken 在 atypica.ai radar 讨论里指出 "mirofish 是 axl 最早的想法来源，多 agent 辩论的 oasis 架构"。cc 当时搜 repo 找不到任何相关记录，确认这条关键历史脉络在 `notes/research/` → `notes/research.md` 合并时没进文档。本节据本地 `C:\Users\ken\OneDrive\Desktop\MiroFish-main` README 和 Ken 口述补上客观事实层。**Ken 的主观思想演进过程不在这里编写**——那部分如果重要，由 Ken 自己口述后补入 `notes/journal/`。

### 四者关系

```
CAMEL-AI 的 OASIS
   └─→ MiroFish（盛大集团基于 OASIS 做的群体智能预测引擎）
         ├─→ atypica.ai（用户 persona 模拟，做市场研究 / PMF 验证）
         └─→ AXL（多学科专家模拟，做跨学科碰撞 / 创造力涌现实验）
```

**同底座，三个不同应用分叉**。

### 层 0：OASIS（底层框架）

- **名字**：Open Agent Social Interaction Simulations
- **出处**：CAMEL-AI 团队开源（github.com/camel-ai/oasis）
- **定位**：多 agent 社会交互模拟的开源框架
- **角色**：MiroFish 明确声明其仿真引擎 "is powered by OASIS"

### 层 1：MiroFish（第一层应用）

- **出处**：github.com/666ghj/MiroFish（盛大集团孵化）
- **中文定位**：简洁通用的群体智能引擎，预测万物
- **英文定位**：A Simple and Universal Swarm Intelligence Engine, Predicting Anything
- **核心机制**：
  1. 从真实世界提取 seed（新闻 / 政策 / 金融信号 / 小说）
  2. 自动构建高保真平行数字世界（GraphRAG）
  3. 千个独立人格 + 长期记忆 + 行为逻辑的 agent 自由交互，社会演化
  4. 用户可从"上帝视角"注入变量推演未来
  5. ReportAgent 带工具集出报告
  6. 用户可和任意 agent 深度交互
- **工作流 5 步**：
  1. Graph Building（seed 提取 + 个体/集体记忆注入 + GraphRAG 构建）
  2. Environment Setup（实体关系提取 + persona 生成 + agent 配置注入）
  3. Simulation（双平台并行仿真 + 需求自动解析 + 动态时间记忆更新）
  4. Report Generation（ReportAgent 深度交互环境）
  5. Deep Interaction（和任何 agent 聊天 + 和 ReportAgent 互动）
- **技术栈**：Node.js + Python（≥3.11 ≤3.12）+ Docker；LLM 默认推荐阿里百炼 qwen-plus；记忆层用 Zep Cloud
- **宣传应用场景**：
  - 宏观层：决策者的排演实验室（政策 / 公关零风险测试）
  - 微观层：个人创意 sandbox（小说续写 / 幻想场景）
- **代表 demo**：武大舆情模拟、红楼梦失传结局推演

### 层 2a：atypica.ai（应用分叉 A：用户研究）

- **应用场景**：模拟真实用户人群 → 市场研究 / PMF 验证
- **产品语言**：AI research system（"像研究团队规划研究"）
- **资产**：100w+ 社媒合成 persona + 10w+ 深度访谈 persona
- **商业化切口**：创作者 / 营销人 / 产品团队（出海产品验证尤其强）
- **详见** `notes/radar.md` atypica.ai 条目

### 层 2b：AXL（应用分叉 B：学科碰撞）

- **应用场景**：模拟多学科专家 → 跨学科碰撞 / 创造力涌现实验
- **研究目标**：验证"多 agent 跨学科碰撞能否产生涌现创造力"这一假设
- **与 MiroFish 的结构对应**（只列客观对应，不编 Ken 心路）：

| MiroFish 概念 | AXL 对应 | 异同 |
|---|---|---|
| seed 提取（新闻 / 政策）| 用户问题 / 实验 benchmark 题 | 相同：从真实世界起点 |
| 千个 persona agent | 多学科专家 agent（当前 7 学科）| **范围收窄**：AXL 精度在专家领域，MiroFish 覆盖在普通人群体 |
| GraphRAG 构建数字世界 | 未做（AXL 不需要还原社会环境）| AXL 省掉了"世界"层，直接让专家对话 |
| agent 自由交互社会演化 | 多轮辩论 + moderator 压场 | **相同**：都是 agent 间非独白 |
| 长期记忆 | 七层记忆系统（Phase 2 已落地）| AXL 独立设计，参考 MiroFish + 2025 SOTA |
| 上帝视角注入变量 | 实验 config + 参数消融 | **相同思路**：控制变量做 controlled experiment |
| ReportAgent | moderator / kpax_pipeline | AXL 的 moderator 做结构化收束 |
| Deep Interaction | KPAX 座谈会形态（v0 设计中）| **相同**：用户可和任一 agent 继续对话 |

### 为什么 AXL 不是 MiroFish 的 fork

- MiroFish 的评估目标：预测未来（在 seed 给定世界下，群体社会如何演化）
- AXL 的评估目标：涌现创造力（多学科碰撞能否产生单 agent 产生不了的新角度）
- 目标不同导致 fitness function / re-rank 策略 / 记忆结构 / agent 选型**全部需要独立设计**
- 因此 AXL 没有共享 MiroFish 的代码，只借鉴了**"多 agent 社会演化 + 长记忆 + ReportAgent 收束 + 用户深度交互"这套产品骨架**

### 和 atypica 的关系：同源不是竞争

- atypica 跑通了这套思想在**产品层 + 商业层**的可行性 —— 对 AXL 是第三方验证信号
- 功能正交：atypica 做用户研究，AXL 做学科碰撞。不抢赛道
- 可对标之处（见 `notes/radar.md` atypica 条目）：产品定位语言、澄清-优先流程、persona 数据规模

### 启示清单（给未来的 agent）

1. **定性是"启发"，不是"fork / 抄袭"**（Ken 2026-04-20 明确）：AXL 从 MiroFish / OASIS 得到的是**多 agent 社会演化 + 长记忆 + ReportAgent 收束 + 用户深度交互这套产品骨架的启发**。没有共享代码、没有 fork、目标不同、实现独立。对外宣传文档（`README.md` / `KPAX.md`）**不加** "based on OASIS" 这类 credit——启发不是抄袭，没必要做这种虚伪的谦虚。
2. **护城河不在 idea 层**：MiroFish 和 atypica 已经各自吃下一块应用市场。AXL 的价值不在"更早提出多 agent"，在"把多 agent 在**学科碰撞 + 创造力涌现**这个特定场景下跑出可量化的数据曲线"
3. **技术选型对照点**：Zep Cloud 记忆（MiroFish 用）、阿里百炼 qwen-plus（MiroFish 默认 LLM）、GraphRAG（MiroFish 用）—— 这些技术选型每次涉及 AXL 同类决策时可做对照

---


## emergent-creativity-hypothesis 涌现创造力假设

> **原文件**：`notes/ideas/emergent-creativity-hypothesis.md`（2026-04-17 合并前位置）


> 作者：KY.East
> 版本：v0.1 — 待 Agent X Lab 辩论验证
> 日期：2026-04-13

---

## 核心命题

**一个经过结构化设计的多智能体系统，通过跨学科辩论和记忆积累，能够涌现出单一大模型无法自发产生的创造性洞察。**

这个命题的底层逻辑来自三个经验观察：

1. 人类最具突破性的思想往往诞生在学科交叉地带（Shannon 用布尔代数重构通信理论，Kahneman 把认知心理学引入经济学）
2. 大语言模型在单一 prompt 下倾向于收敛到训练数据中的高频模式，缺乏自发的"远距离联想"
3. 当同一个问题被不同知识背景的 agent 从不同角度审视时，它们之间的冲突和互补本身构成新的信息

---

## 理论框架

### 第一层：结构类比——从神经连接到学科连接

人脑的创造力与跨区域神经连接的密度正相关（Beaty et al., 2018; Kenett et al., 2018）。默认模式网络负责自由联想，执行控制网络负责评估筛选，显著性网络负责在两者之间切换。高创造力个体的特征是这三个网络之间的功能连接更强。

将这个发现映射到多智能体系统：

| 神经科学概念 | 系统映射 | 功能 |
|-------------|---------|------|
| 脑区 | 学科领域 | 承载特定领域的知识和推理范式 |
| 脑区内神经元 | 领域内的具体理论、数据、方法论 | 构成该领域分析能力的基本单元 |
| 白质纤维束（跨区域连接） | 跨学科辩论过程 | 迫使不同范式的知识进行交互 |
| 突触权重 | 记忆系统中的经验积累 | 记录哪些连接有效，哪些无效 |
| Hebb 学习（一起放电→连在一起） | L2 技能记忆沉淀 | 成功的分析框架被强化为可复用模板 |

这个类比在结构层面成立，但在机制层面需要修正。

### 第二层：机制修正——对抗选择，而非加权整合

大脑整合信息的方式是突触加权求和：信号按权重叠加，超过阈值则放电。这是一个连续的、非对抗的过程。

多智能体辩论的信息整合方式根本不同。它更接近三个机制的叠加：

**（a）Minsky 的心智社会（Society of Mind, 1986）**

智能由大量半自主 agent 的竞争与合作涌现。每个 agent 能力有限，但它们之间的互动——包括对抗、联盟、层级调度——产生了超出任何单一 agent 的行为。辩论引擎中的专家 agent 阵容直接体现了这个架构：不同性格（先锋/严谨/务实/质疑）、不同学科、不同立场的 agent 组成一个微型社会。

**（b）进化选择压力**

辩论中的观点竞争类似于变异-选择循环。每个 agent 提出的论点是"变异"，其他 agent 的质疑和反驳是"选择压力"，存活下来的论点是经过筛选的更强健观点。三轮辩论模拟了多代选择。记忆系统（L4 共享记忆）让筛选结果跨会话传递，相当于遗传。

**（c）Kahneman 双系统的动态演化**

辩论过程本身是 System 2（慢思考）：有意识的、分析性的、消耗大量 token 的深度推理。但当 L2 技能记忆积累到足够密度，系统开始具备 System 1 的特征：遇到类似问题时，直接加载历史框架作为起点，快速匹配模式，跳过从头推导的过程。

这意味着系统会经历一个从 System 2 主导到 System 1 辅助的自然演化。早期每个问题都需要完整辩论；后期常见场景可以用积累的经验快速响应，只有真正新颖的问题才需要完整辩论。这和人类专家的成长路径一致——新手靠刻意分析，老手靠直觉（但直觉来源于大量刻意分析的积累）。

### 第三层：涌现条件——创造力从何而来

如果单纯把多个 agent 放在一起让它们说话，创造力不会自动涌现。关键条件：

**条件一：知识的异质性必须足够大。**

来自同一范式的 agent 只会相互确认，不会产生新东西。这就是为什么系统要求"专家之间必须有观点张力"、"至少一位扮演质疑者"。异质性不仅是学科差异，还包括方法论差异（定量 vs 定性）、时间尺度差异（短期 vs 长期）、价值取向差异（效率 vs 公平）。

**条件二：碰撞必须有结构，不能是自由混战。**

无结构的讨论会退化为各说各话。辩论引擎的三轮制、主持人的共识追踪、结构化总结（共识/分歧/开放问题/方向）都是在施加约束。创造力理论（Boden, 1990）中的一个核心洞察：创造力是在约束空间中寻找意外路径，约束越明确，创造性搜索越高效。

**条件三：失败的碰撞和成功的碰撞同样有价值。**

记忆系统不应该只记住成功的分析框架。当某个跨学科连接被辩论证明行不通时（比如用量子力学类比解释社会现象被物理学家驳斥），这个"此路不通"的信息同样需要沉淀，避免未来重复尝试。这对应神经科学中突触弱化（LTD）的角色——学习包括知道什么不该连接。

**条件四：外部数据锚定。**

没有实际数据支撑的辩论会退化为纯修辞对抗。论文库（OpenAlex）和实操经验库（Reddit/知乎/Quora）的作用是为每个论点提供证据锚定，防止 agent 在辩论中凭空编造。这对应大脑中的感觉输入——没有感觉输入的纯内部活动不是创造，是幻觉。

### 第四层：记忆作为长期进化基底

四层记忆系统不只是工程上的便利，它在理论上承担了一个关键角色：让系统具备超越单次会话的认知连续性。

| 记忆层级 | 认知科学映射 | 进化角色 |
|---------|------------|---------|
| L1 持久记忆（用户画像） | 情景记忆（个体经历） | 个体适应 |
| L2 技能记忆（可复用模板） | 程序性记忆（技能） | 能力积累 |
| L3 会话搜索（历史检索） | 语义记忆（事实知识） | 知识积累 |
| L4 共享记忆（跨用户经验） | 集体记忆 / 文化传承 | 群体进化 |

L4 是最关键的一层。它让系统获得了"文化进化"的能力：一个用户的分析经验可以增强另一个用户面对类似问题时的分析质量。这不是简单的缓存——赛后验证某次分析有误，修正会传播到所有相关记忆。这构成了一个真正的学习-纠错循环。

---

## 可验证预测

如果这个假说成立，以下现象应该可观察到：

1. **多 agent 辩论生成的分析，在维度覆盖和盲点识别上，应当优于单一 agent 的深度分析。** 可以通过对比实验检验：同一问题分别用单 agent 和多 agent 分析，由人类评估者盲审评分。

2. **跨学科组合越远（知识异质性越大），当碰撞成功时产出的洞察新颖度越高，但碰撞失败的概率也越高。** 这对应创造力研究中的 exploration-exploitation tradeoff。

3. **系统使用量越大，L2/L4 记忆越丰富，对常见问题类型的分析质量应当持续上升。** 这是飞轮效应的直接体现，可以通过追踪报告评分随时间的变化来验证。

4. **系统偶尔应当产生人类评估者认为"我自己不会想到这个角度"的分析。** 这是涌现创造力的直接证据——如果系统只是把已知观点重新组合，那它只是搜索引擎；如果它能产出评估者没预期到的新角度，那就有涌现的迹象。

---

## 局限与开放问题

1. **LLM 的创造力上限问题。** 如果所有 agent 底层用的是同一个 LLM，它们的知识空间本质上重叠。多 agent 辩论能在多大程度上突破单模型的知识边界？还是说它只是更高效地探索了模型已有知识的组合空间？

2. **结构化辩论会不会压制真正激进的想法？** 三轮制和共识追踪有可能让系统倾向于"合理的创新"而排斥"疯狂的创新"。历史上最大的突破往往在当时被认为是荒谬的。

3. **记忆积累的路径依赖。** L2/L4 记忆越丰富，系统越倾向于沿已有路径思考。这是效率的提升，但也可能是创造力的衰减。如何平衡经验积累与认知灵活性，是一个未解决的问题。

4. **评估创造力本身的困难。** "我没想到这个角度"可能只是因为评估者知识有限，未必说明系统有真正的创造力。需要更严格的评估框架。

---

## 待辩论的核心论点

提交给 Agent X Lab 辩论引擎的中心议题：

> **多智能体跨学科辩论系统能否涌现出超越单一大模型的创造性认知能力？如果能，其机制更接近神经网络的连接涌现、进化的选择压力、还是社会系统的集体智慧？这三种解释框架各自的预测有何不同？**

建议辩论学科组合：认知科学 × 复杂系统 × 科学哲学 × 计算机科学（人工智能）

---

## wisland-analysis-and-positioning WisLand 对位分析与研究定位

> **原文件**：`notes/research/wisland-analysis-and-positioning.md`（2026-04-17 合并前位置）


**日期**：2026-04-15
**缘起**：Ken 昨天尽调了复旦张奇教授的 WisLand（Faraday）项目，会议记录 + Pre-A 融资 PDF 读完后，这份笔记用来存三件事：
1. WisLand 项目事实（团队/产品/技术栈/商业化）
2. 可以偷的技术与产品启发（11 条）
3. 面对 WisLand 存在的前提下，Ken 自己的研究该怎么定位、怎么做才有意义

**重要性**：这一笔记是 Ken 明确要求"完全记录"的一次讨论，涉及 AXL/KPAX 未来方向的根本判断。之后做任何产品/研究决策都要先读这一份。

---

## Part A ─ WisLand 项目事实

### A.1 团队

| 角色 | 姓名 | 背景 |
|---|---|---|
| 创始人 / 首席科学家 | 张奇（复旦教授） | 复旦博士（09），搜狗首席研究员（管 200+ 研发），做过搜狗首条问答、医疗搜索、搜狗 530 亿模型（百川前身）。为海康威视预训练 1.6B–30B 全流程模型。2023 年为荣耀提供全部模型。现任复旦-腾讯联合实验室主任，带约 50 名学生，一半派驻腾讯 |
| CEO | 张悦 | 张奇第一个硕士生，原 Velta 数值计算，创业后被召回 |
| CTO | （未披露） | 原搜狗同事，负责智能推荐 + 知识图谱构建 |
| COO | （未披露） | 张奇同学，原上海华东交易所，负责对外 + 量化基础设施 |
| 出海顾问 | （未披露） | 某出海公司创始人，非全职 |
| 其他 | 20+ 学生/算法 | 依托复旦资源，人力成本不入公司 |

**关键认知**：这不是"教授挂名"。张奇本人在做事（ACL2024 杰出论文是他实验室的），工程团队是前搜狗班子，不是典型学术团队。复旦-腾讯联合实验室 50 人 + 腾讯 2000 卡的资源体量是这个项目真正的护城河之一。

### A.2 起源与定位

- 张奇判断：2023 大模型是 "AI 时代最后一次创业机会"
- 不做通用大模型（认为难度高），专注产品
- 痛点：科研流程 80–90% 是体力劳动（文献检索、假设验证、实验配置、数据整理）
- 定位：面向科研人员（高校师生、企业研究员、医生等）的全流程 AI 工作空间
- 启动：2024 开发 → 2025-11 上线（最初只搜索功能）
- 4 个月达到：19 万注册 / 5 万 MAU / 5000 DAU / 海外 40%

### A.3 产品功能

| 模块 | 描述 | 收费 |
|---|---|---|
| AI 搜索 | 自建文献搜索引擎，用户问题→搜索词+验证条件，逐条比对 300–500 篇论文 | 低价几美元/月，拉日活 |
| AI 阅读 | PDF 结构化解析（表格/公式/图片），中英文对照，一键解释公式/段落，3 分钟博客式总结 | 包含订阅 |
| AI 订阅（Feed） | 用户设领域/关键词，每日自动筛选数千篇论文推送 | 包含订阅 |
| 论文复现 Agent | 用户提想法，Agent 搜索→验证→改进→查重→跑代码→输出 | 高价功能包 |
| 编程/数据分析/写作 | 自动写代码、数据分析、论文写作 | 高价 |
| 量化投研 Agent | 论文因子/策略自动复现、回测、入库，港股/A 股切换 | 企业部署 |
| 专利检索与分析 | 专利查新、交底书撰写（数据清理中） | 待定 |
| 医学合作 | 赋能药厂 + 医生 | B2B |

创始人自评：产品成熟度 70 分，预计 2026-04-20 端侧版本达 80 分。

### A.4 技术栈（关键数据）

**自建文献搜索引擎**：
- 抓 2 万+ 期刊 + 全 arXiv
- 3.55 亿条文献索引，1.2 亿全文
- **原因**：开源数据如 OpenAlex 60% 摘要缺失，无法商用
- 成本：200 万篇论文处理约 1 万元（10 张 4090 × 10 天）

**自研模型**：
- 除编程部分用外部模型，全部自研
- 成本对比：一次检索（2030 万 token 输入 + 10 万 token 输出）自研 0.1 元人民币，调 GPT-4/Claude 25 美元 → **250 倍成本差**
- 推理成本：0.3–0.5 元/百万 token，上月 GPU 推理约 1 万元
- 计划 2026-08 发布全自研 Base 模型（腾讯支持 2000 卡），去掉刷榜数据，加强学术/专利数据

**自研 PDF 解析**：
- 十年积累
- **基于 PDF 协议解析（非 OCR）**，数字精确、速度快

**评测结果（自选 benchmark）**：
- 任务：从论文抽 Section 类型（Methodology / Background 等）
- 通用模型（GPT-4/Claude/千问）F1 约 0.60–0.70
- 自研后训练模型 F1 = 0.91
- 深度分析评测（deck p-08）：WisLand overall accuracy 73.3%，在证据支撑分类维度领先 GPT-5 / Claude-Sonnet-4 / GLM-4.6

**端侧长上下文**：
- ACL2024 杰出论文：DCA（Dual Chunk Attention）+ 位置编码伸缩法则
- 免训练实现百万序列长度
- 4.20 端侧版本把这个能力塞进客户端 → 隐私 + 成本双吃

**数据飞轮**：
- 用户点击、负反馈、修改行为自动收集
- 用于模型训练 + 搜索排序
- 粒度：子步骤级隐式信号（"这条验证条件被跳过"→负信号；"这些改进都不行"→标注入库）

### A.5 商业化

| 客户 | 收费 | 典型价格 | 备注 |
|---|---|---|---|
| ToC 个人科研 | 订阅 + 高价功能包 | 基础 $5–20/月，功能包按次/按结果 | 已 300+ 付费用户，平均 300 元/月 |
| ToB 量化投研 | 云端部署费 + token/算力 | 起步 50–100 万（按席位），20 亿规模公司年费约 200 万 | 已预付 40 万开发费 |
| ToB 高校 | 低价搜索入，学生自付费 | 教育渠道商 | 已落地复旦 + 福州大学 |
| ToB 医学 | 合作分成或授权 | 与康荣华城等签约中 | 赋能药厂 + 医生 |
| ToB 专利 | 类似量化 | — | 数据清理中 |

**运营数据（截至会议）**：
- MAU 4000–5000
- 上月 ToC 收入 10 万元
- 新增付费 300+
- 近期日收入约 1 万元
- 付费转化率：核心活跃 7000 人中约 15% 付费（1000–1500 人）

**Pre-A 融资**：
- 3000 万 RMB 或等值美金
- 投后估值 3 亿 RMB
- 300 付费用户 × 300 元/月 = ARR 0.0108 亿 → **P/S = 277.8x**
- 资金用途：45% 市场 / 35% 研发 / 20% 运营
- 历史股东：百嘅资本（100 Partner）+ 微星创投

**C 轮规划（2028-05）**：100 亿估值，10 万付费，ARR 6 亿，P/S 16.7x。

### A.6 扩展顺序（优先级）

1. **量化投研**（最高优先，2026-09 前完善，5–6 家排队）
2. **专利检索**（中，2026-06 工程介入，数据 270TB 清理中）
3. **医学**（排最后，产品改动大，医生付费意愿强）

---

## Part B ─ 可以偷的 11 条技术与产品启发

### B.1  成本结构差 250 倍 → judge 策略的正确读法

WisLand 一次检索 0.1 元 vs GPT-4 25 美元。看起来是"本地/自研 → 成本归零"的故事，但套到 Ken 的 judge 问题上**我第一版写错了**，这里订正。

**错误版本**（已撤回）：pilot 后 fine-tune 一个本地 Qwen-2.5-7B 当 judge，judge 成本归零。

**错在哪**：
1. **算错账**：主 judge 成本本来就是零头。GPT-5 判一次 debate ≈ 300 tokens in + 100 out ≈ $0.003，900 次 × 3 run = **$8**。省 $8 毫无意义，烧钱的是 debater 本身不是 judge
2. **算错能力**：7B fine-tune 做**主 judge 不可信**。judge 模型规模应 ≥ 被判模型，而 debater 池里有 Claude Opus 4.6 / GPT-5.4 这种 frontier 模型，小模型给它们打 depth / novelty 分本质是小学生给教授论文打分
3. **产业共识**：Prometheus-2 / JudgeLM / PandaLM 这批工作证明 小模型只在**成对偏好（pairwise A vs B）** 上勉强能用，**绝对打分尤其开放维度（novelty, depth, breadth）上不可信**

**正确的读法**（按 Ken 04-15 云租 GPU 反问更新）：

主 judge 继续用 API，固定一个独立于 debate pool 的 frontier 模型（GPT-5 或 Gemini 2.x）。不要本地化主 judge。

**云租 GPU（AutoDL / RunPod / Vast.ai）按需开关**真正解锁的是**下列三件事**，用途是"**结构化加工**"而不是"质量判分"：

1. **Message-level 标注器**（对应 B.4 的 `message_tags`）：transcript 每条 message 打 `{key_claim, noise, off_topic, stance_shift, novelty_seed}` 标签。**这是 WisLand Section F1 0.91 的直接类比**——模式匹配 + schema 约束，14B 能到 0.85+
2. **reasoning_unit 抽取器**（对应 AXL M2）：transcript → `{agent, round, claim, evidence_ref, stance, stance_shift_from_prev, confidence}`。也是结构化抽取，14B 够
3. **API judge 的 meta-validator**：本地模型跑 pairwise 偏好比较，用来交叉检查 API judge 的系统偏差（比如 "API judge 给这条 novelty 打了 5 分，本地 pairwise 发现它应该排第 7"）。是偏差检测，不是替代判分

**云租 GPU 的实际路径**：
- 平台：**AutoDL**（国内，¥2-3/hr 4090 / ¥8-15/hr A100 80GB）或 **RunPod**（海外，$0.8/hr A100 spot）
- **破掉 7B 天花板**：A100 80GB QLoRA 直接喂到 70B，H100 喂更大。**起步 Qwen-2.5-14B，不够升 34B**
- 预估单轮实验成本：fine-tune 一次 ¥50-100，批量 inference 900 条 ¥30-50，**单轮实验总成本 < ¥200**
- 用完 terminate，不计费
- 对比本地 4090 买卡 $1600 一次性 + 电费 + 被 24GB VRAM 卡死，云租在 solo dev 偶发批处理的使用模式下**每个维度都赢**

**结论**：B.1 正确的 takeaway 不是"judge 归零"，是"**结构化加工 pipeline 可以用云租小模型跑起来**"。判分本身继续 API。

### B.2  Section 分类 F1 0.91 vs 通用 0.6–0.7 → L5 反思层设计依据

**启示**：结构化输出任务（论点提取/证据路径/stance shift 标签）用 fine-tuned 小模型明显赢让 Claude Opus 吐 JSON。Ken 的 L5 反思层拆两层：
- **生成**（创造性）：Claude Opus / DeepSeek，API 调
- **结构化标注**（一致性）：本地 fine-tune 小模型，批处理，temperature=0 天然稳定

这也解决 R4 的 judge 自一致性顾虑。

### B.3  PDF 协议解析的路径选择

WisLand 十年积累走 PDF 协议级解析（pdfminer/pdfplumber 路线），不走 OCR。

**对 KPAX 的启发**（cc 2026-04-16 晚 Ken 指出之前这段被 cc 过度外推，此处是修正版）：

- **不自建板式解析模型**——没有 10 年积累，自己从头训不过 WisLand / Marker / mineru 这些已经跑了多年的栈。用开箱工具即可。
- **开箱工具的选择按内容类型分场景**，不一刀切：
  - 学术论文（arXiv / S2）：用 `pdfminer.six` 或 `unstructured` 的 pdfminer 后端，纯协议解析够
  - 行业报告 / deck / 扫描版 / 老文档 / 社区截图：**pdfminer 看不到 → 这类场景 OCR 必要**，用现成开源方案（pdf-inspector + GLM-OCR / docling 等）
- **能力约束型立场**（Ken 原话 2026-04-16 晚）："我们没有这个积累，有了立马就用"——不是战略回避 OCR，是现实主义：有好工具就用。
- 原来 cc 写的 "绝对不要 OCR" 是错的外推，已撤回。

**之前的错误表述**（2026-04-15 cc 写的，已修正）：
> "KPAX 论文注入 **绝对不要** 用 mineru / Marker / 任何 OCR-based 方案"

这句话是 cc 把 WisLand deck 里 "基于 PDF 协议解析（非 OCR）" 的一个竞争定位点，错误外推成 KPAX 的全局硬规则。Ken 从未这样说过。

### B.4  数据飞轮粒度 → human_scores.json schema 要细化

WisLand 飞轮是**逐子步骤隐式反馈**，不是整体打分。

**改法**：`human_scores.json` 加 `message_tags` 字段，存 `{message_id: tag}`。human scorer 在 transcript 里标"这条观点最关键 / 这条是废话 / 这里开始偏题"，每 message 一个 tag。10 条 transcript × 20 message × 3 tag ≈ 600 个数据点，远超 "10 × 6 维度 = 60 分"。这份数据以后就是 fine-tune judge 模型的直接训练集。

### B.5  AI 任务交付引擎 vs multi-agent debate → 架构对照与 F 组种子

WisLand 最终形态：任务理解→证据检索→跨文档推理→推理链生成→任务交付。**串行工作流管道**，每步确定性、可调试、可加工具。

Ken 的 AXL：并行多 agent 一次汇总，非确定、涌现、难调试。

**这两者不对立，是正交**。debate 可以作为管道里"证据→推理链"那一步的内部推理节点。

**两层启示**：
- 工程：AXL 产品化缺的不是 debate 本身，是**前后管道**（抓数据 → debate → 结构化输出 → 写入记忆）。`debate_engine` 目前是孤岛。
- 研究：emergence_decomposition 的 D 组（orchestrator-worker）就是 WisLand 架构的抽象。如果 baseline ≫ D，说明 debate 作为**推理节点嵌入管道**才是正解，不是替代管道。

### B.6  云租 GPU 按小时计费 → solo dev 的算力民主化

WisLand 数据 "10 张 4090 × 10 天 = 1 万元处理 200 万论文" 是一个工程成本锚点，但**不要**照抄"本地 4090"这个形式。solo dev 的最优解是**云租按需开关**：

- AutoDL：¥2-3/hr 4090 / ¥8-15/hr A100 80GB
- RunPod：$0.3-0.8/hr 4090 / $0.8-1.5/hr A100 spot
- 用完 terminate，零维护、零 CUDA 地狱、零散热问题

**相对本地 4090 的优势**：
1. **破掉单卡 VRAM 天花板**——24GB 只能 QLoRA 到 13B，A100 80GB 能喂 70B，H100 更大。Ken 的 fine-tune 任务不用被 7B 限制
2. **可以 A/B 不同架构**——今天 14B、明天 34B、后天 70B 对比，本地买卡只能跑一种
3. **无 capex**——$1600 一次性买卡 vs 月均 ¥200-500 租金，两年内云租更划算，且不会有"买了更大模型想升级"的沉没成本
4. **批处理工作流无感**——Ken 的用例都是偶发 fine-tune + 批量 inference，不是 realtime，setup friction 几分钟可忽略

**心理锚点**：你作为 solo dev **不缺算力**，只是需要用对姿势。云租把"大模型 fine-tune"的门槛从"买一张卡"降到"开机 2 小时 ¥30"。你真正缺的是**问题定义**，而问题定义是你的绝对长板。

### B.7  OpenAlex 60% 摘要缺失 → AXL 地基有洞

**这是这次会议对 Ken 最重要的一条信息**。

`knowledge_graph.db` 是 OpenAlex 导的，4794 个学科分类元数据 OK，但文献层 60% 没 abstract。意味着：
- KPAX "论文注入"路径以 OpenAlex 为源 **直接废一半**
- 跨学科匹配时，如果某学科文献集恰好是 abstract 缺失率高的那批（人文社科尤其严重），agent 的"知识异质性"是幻觉——它拿到的是 title + venue

**解法：分层多源 fallback**（写 `PaperSource` 抽象层）：
1. **arXiv 全量 API**：Physics/Math/CS/Stat 完美覆盖，直接解决 Ken baseline 里 3/7 学科
2. **Semantic Scholar API**（Allen AI）：覆盖度优于 OpenAlex，abstract 完整率 80%+
3. **Crossref API**：元数据补全
4. **Unpaywall API**：给 DOI 返回 legal open-access PDF，补 OpenAlex 缺 abstract 但有 DOI 的条目
5. **Europe PMC**：Psychology / Social / 医学 abstract 覆盖比 OpenAlex 高

**时机**：emergence_decomposition 实验现在没用到论文内容（agent 靠 prompt 学科身份说话），所以这次实验没被影响。但一旦 L2/L3 记忆层开始把论文内容注入 agent context，这条 bug 当天爆。**提前知道省 1–2 周**。

### B.8  复现 Agent 的 6 步工作流 → debate agent 的工具调用模板 (F 组种子)

WisLand 论文复现 Agent：用户提 idea → 搜索 → 验证 → 改进 → 查重 → 跑代码 → 输出。每步是一个**可调用工具**。

映射到 Ken 的 debate agent：

| WisLand 步骤 | debate 里的工具等价 |
|---|---|
| 搜索 | `retrieve_evidence(topic)` → Zep / 学科语料 |
| 验证 | `check_claim(claim, evidence)` → 事实校验小模型 |
| 查重 | `check_novelty(claim, history)` → 余弦距离 |
| 改进 | debate 天然有 |
| 跑代码 | 对 Ken 不适用 |
| 输出 | moderator summary（有了） |

**启示**：debate agent 不应该光靠 prompt 自说自话，应该能调 retrieve / verify / novelty-check 三个工具。这三个工具恰好对应 spec 三个 diversity 指标——现在是**跑完之后才算**，如果 agent 过程中就能看到，debate 动力学完全不同。**这可能是未来的第 F 组**（带工具的 debate），不要这次加，但记在研究问题 backlog 里。

### B.9  量化投研 PMF 信号 → KPAX 商业化路径启示

WisLand 最硬的垂直：量化投研，已预付 40 万开发费，5–6 家排队，50–100 万/席起步。单垂直 + 明确交付物 + 客户已付款。

**对 KPAX 的启示**（不是让你做量化）：
- KPAX "通用决策工具"定位太宽，和 WisLand "通用科研工具"一样的病
- WisLand 打法：通用产品 → 找第一个愿预付款的垂直 → 单点打穿
- KPAX 的"第一个垂直"可能是医疗决策？法律？投资？消费？现在答不出，但要**开始收集**

**具体动作**：KPAX 埋一个 session tag——用户自己填或 LLM 自动打"这次决策属于什么领域"。跑 3 个月看分布，哪个领域重复使用最密集、哪个愿意付 100 元而不是 5 元，就是第一个垂直。

### B.10  端侧 + DCA 百万长序列 → 七层记忆 L1/L2 本地化的同行验证

WisLand 4.20 端侧版把 ACL2024 DCA 论文能力塞进客户端，本地跑论文阅读/搜索/总结。

**启示**：Ken 七层记忆的 **L1 工作 + L2 情节**其实**没必要走云端**。本地一张 4090 跑 Qwen-2.5-14B 或 GLM-4-9B，L1/L2 全本地，L3 语义以上才走云 API。

好处：
- KPAX 用户决策数据天然 privacy-preserving（未来 to-B selling point）
- 单用户月成本从几美元 API 降到电费
- 本地开发迭代完全断网，不依赖 API 稳定性

**中期架构决策**，不是现在改，但 WisLand 4.20 是一个"同行已验证这条路走得通"的信号。

### B.11  自评节奏 → solo dev 的可问责迭代

张奇自评产品 70 分，明确说 4.20 版本到 80 分。**自评 + 具体日期 = 可问责的节奏**。

**具体动作**：给 AXL 和 KPAX 各打当前分数 + 下一个 milestone 日期 + 要到几分。贴在 memory 里，每周一自己对一次。这是管理层面，不是技术，但比技术更决定 solo dev 能不能 ship。

---

## Part C ─ Ken 研究定位：面对 WisLand 存在的前提下怎么做才有意义

### C.1  "超过他们"是错误框架

Ken 和 WisLand **不在一条跑道上**。

**WisLand = efficiency play**：把科研人员 18.7 小时文献整理压缩到 2 小时。天花板是"节省时间"。全部技术栈（自建索引、PDF 协议解析、fine-tuned section classifier、DCA 长序列）都服务一件事——**人已经知道要做什么，AI 帮你更快做到**。

**Ken = capability play**：multi-agent debate + 七层记忆 + L7 元进化，本质在问"AI 能不能做到单 agent + 人类思维做不到的事"。天花板是"开拓新能力"。

在 efficiency 跑道上，跟 50 人团队 + 腾讯 2000 卡 + 十年 PDF 解析积累比，Ken 每个工程维度都必输。但 **efficiency play 有天花板，capability play 没有**。WisLand C 轮目标 100 亿估值、10 万付费、ARR 6 亿是一个具体有限的可吃满市场。capability play 如果成立，产生的是**新能力本身**，不是更高效的老能力。

**正确的问题**：不是"怎么超过他们"，是 **"在他们必然碰不到的维度上，我能做出什么只有我能做的东西"**。

### C.2  他们必然碰不到的三个维度

#### 维度 1：没 KPI 绑架的长周期实验

WisLand 每个实验必须 serve ARR。Pre-A 3000 万烧完要交 A 轮答卷，A 轮交 B 轮答卷。他们**做不了**：
- **L7 元进化**（自由参数自我改写）：收敛可能几百次迭代，工业团队没耐心
- **反事实实验**（故意让 agent 犯错看涌现边界）：对 ARR 负贡献
- **长周期记忆动力学**（decay / retrieval 的几个月级效果）：收集期太长

Ken solo dev + 无融资压力 = 能做他们做不了的事。这不是"我慢所以我有时间"，是**结构差异**。他们永远不会做这些，Ken 做了就是 Ken 的。

#### 维度 2：研究方法论本身

WisLand 不会发论文讲他们怎么构建 reasoning index，那是护城河。Ken 发论文讲 emergence_decomposition 怎么拆解涌现来源，**论文就是护城河**——**身份 moat，不是技术 moat**。

solo dev 相对工业团队最大的杠杆是**发表**。代码能被 fork，用户能被抢，产品能被复制，**论文署名不能**。arXiv 上一篇 "Decomposing Emergence in Multi-Agent LLM Debate" 的作者身份是 Ken 的，十年后还是。WisLand 50 个工程师没一个能抢。

#### 维度 3：消费决策垂直

WisLand 锁定科研 / IP / 医疗 / 量化。共同点：**用户已经知道要决策什么，需要 AI 加速**。

KPAX 瞄的消费决策是另一类：**用户不知道自己该不该做、为什么做、有没有更好的选项**。不是 efficiency，是 capability——需要 AI 帮用户**生成他自己想不到的选项**。

WisLand 永远不会进这个垂直：
- ARPU 低（KPAX $5–20/月 vs WisLand 科研 $300）
- 需要情感维度 + 个人价值观建模（和他们的证据推理栈正交）
- 没有明确 benchmark（他们 Section F1 0.91 这种指标不存在）

**前提**：KPAX 必须跑出和科研工具不一样的产品形态。如果 KPAX 做成"决策版 Scholar QA"，又输了。

### C.3  具体动作（按优先级）

#### P0 — 立刻：把 emergence_decomposition 跑完，写成论文

这是研究身份的第一块砖。不是为投资人，不是为 KPAX 用户，是为了 Ken 在这个研究方向上**有一份可引用的产出**。跑完按正经论文格式写（arXiv technical report 水平），贴 github + arXiv。

跑完要面对三种结果：
- **A**：baseline（多 agent 异质）显著赢 E 组 → 方向成立，下一步 L7 实验
- **B**：E 组（单 agent 长 context）追平 baseline → Anthropic 那句话对，multi-agent 路径被 Ken 自己证伪，**需要 pivot**
- **C**：都差不多 → 实验设计本身有问题，重做

**现在就该想好 B 和 C 的 Plan B**。如果核心假设被证伪 pivot 到哪？这是 goal-driven execution 里"长任务分支提前规划"的直接应用。在实验出结果之前，必须写一份 `plan_b.md`，否则结果出来的那一刻是情绪驱动决策，不是理性决策。

#### P1 — 中期：放弃追赶 WisLand 工程栈

| 工程方向 | 该做 | 不该做 |
|---|---|---|
| 论文检索 | arXiv + Semantic Scholar API | 自建索引 |
| PDF 解析 | 开箱工具按内容分场景选（学术论文 pdfminer / 其它场景 OCR-based 开箱方案都行） | 自研板式解析模型 |
| Judge 模型 | pilot 后 QLoRA 一个小 judge | Post-train base 模型 |
| 长序列 | 没必要 | DCA 端侧 |
| 文献数据库 | OpenAlex + multi-source fallback | 抓 2 万期刊 |

每一条 WisLand 做的工程 Ken **都不要做**。不是做不好，是做了就把自己拉回 efficiency 跑道，必输。**工程预算全部喂给研究实验**，不要喂给产品基础设施。

#### P2 — 长期：L7 元进化实验 + 开源研究层

- emergence_decomposition 之后的下一个实验是 **L7 自由参数自我改写**。这是七层记忆里唯一 WisLand 没有也不会有的层。
- 如果能跑出"agent 系统通过 L7 自我改写后在某个任务上显著超过不改写的版本"，就有第二篇论文 + 一个全行业没人有数据的方向
- 把 AXL **研究层**代码开源（`debate_engine` + `seven_layer_memory` + `free_params`），产品层（KPAX UI / 商业化 / 用户数据）闭源
- 开源绑定 Ken 的名字到这个方向，同时不影响 KPAX 商业化

### C.4  三个危险陷阱

1. **把 KPAX 做成小号 Scholar QA**：一旦开始做论文检索、学术写作辅助、参考文献整理——那一刻就输了。KPAX 必须保持在 WisLand 不碰的消费决策垂直
2. **被 WisLand 的工程美学 impressed，开始想追赶**："自研 base / 2000 卡 / 10 张 4090 / DCA / 289M 混合模型"这些会诱惑 Ken。不要。一旦开始，研究时间被工程吞掉
3. **误以为有研究 moat 就安全**：研究 moat 只在**持续产出**的前提下成立。一篇论文 + 三年不更新，研究身份贬值。每 3–6 个月必须有一个新实验 / 新观察 / 新博客。这是 solo dev 的纪律要求

### C.5  最诚实的一面：研究假设可能是错的

**必须说这句**：Ken 研究的东西**有可能根本没意义**。

"跨学科碰撞产生创造力"目前只是假设，没经过严格实验。emergence_decomposition 可能告诉你：cross-discipline 是噪声不是信号。L7 元进化可能告诉你：自由参数改写收敛不了或退化。

这个风险**真的存在**。不能被"solo dev 做独立研究很浪漫"的叙事盖住。

**解法唯一**：用实验去证伪自己。如果 emergence_decomposition 结论是 B 或 C，必须面对，不能把实验重做成偏向假设的方向。这是 solo dev 最容易出的 bias——没有同行评审，只有自己骗自己。

Ken memory 里有"No Flattery"规则——不对 Claude 献媚。现在**反过来对自己**：**不要向自己献媚**。实验结论是什么就是什么。

### C.6  一句话总结

**Ken 和 WisLand 不在一条跑道上，别试图超过。在他们必然不做的三件事上（L7 元进化 / 反事实实验 / 消费决策垂直）做到全行业第一，同时承担研究假设被自己证伪的风险**。

---

## Part D ─ 具体行动清单（按时间排序）

### 这周（dry run 跑完后立刻）

- [ ] 写 `dry_run_report.md`（Checkpoint 0 输出）
- [ ] 写 `experiments/emergence_decomposition/plan_b.md`：如果实验结论是 B 或 C，下一步怎么走。**必须在 Checkpoint 1 pilot 开始前写完**
- [ ] 读本笔记一遍，确认没有认知偏差

### Checkpoint 1 pilot 中途

- [ ] 修改 `human_scores.json` schema，加 `message_tags` 字段（B.4）
- [ ] 改 spec R4 文本：judge 模型策略从 "固定第三方模型" 改为 "pilot 用 API judge 校准，之后 QLoRA fine-tune 本地 judge"（B.1）

### Checkpoint 1 pilot 跑完之后

- [ ] QLoRA fine-tune 一个本地 judge 模型（Qwen-2.5-7B 或 GLM-4-9B，单 4090）
- [ ] 开始写 emergence_decomposition 论文初稿

### emergence_decomposition 全量跑完

- [ ] arXiv 发表论文
- [ ] 开源 AXL 研究层代码（`debate_engine` + `seven_layer_memory` + `free_params`）
- [ ] 根据实验结果 A/B/C 执行对应 plan

### KPAX 层面（平行推进）

- [ ] 埋 session tag：用户决策所属领域（B.9）
- [ ] 论文注入路径：学术论文走 `pdfminer.six` / `unstructured`；行业报告 / 扫描版 / 社区截图场景允许 OCR（按内容类型选开箱方案，不自建板式解析模型）（B.3）
- [ ] 写 `PaperSource` 多源 fallback 抽象层（arXiv + S2 + Crossref + Unpaywall + Europe PMC）（B.7）
- [ ] **不要**做：自建索引、post-train base 模型、自研板式解析（C.3 P1 表格）

### 管理纪律

- [ ] 给 AXL / KPAX 各打当前成熟度分（类比 WisLand 70→80）+ 下一 milestone 日期 + 目标分（B.11）
- [ ] 每周一自检：我这周做的事属于 efficiency 跑道还是 capability 跑道？如果是 efficiency，为什么？

---

## 附录：数据来源

- **PDF**：`C:\Users\ken\OneDrive\Desktop\【WisLand】Pre-A轮融资计划书-Faraday.pdf`（Pre-A 融资计划书，19 页，云岫资本）
- **会议记录**：Ken 2026-04-15 AIXC 线上会议记录（Ken 口述粘贴）
- **讨论记录**：Claude Code 会话 2026-04-15，完整对话见 `.claude/projects/.../3d593c8c-4102-4956-aa51-e81d004e4696.jsonl`

**相关笔记**：
- `notes/ideas/emergent-creativity-hypothesis.md` — 涌现创造力假设理论框架
- `notes/research/seven-layer-memory-design.md` — 七层记忆系统（L7 是 Ken 相对 WisLand 的核心差异点）
- `notes/research/agent-evolution-free-parameters.md` — 自由参数进化
- `notes/research/role-labels-vs-orchestrator.md` — orchestrator vs 多 agent debate 路线分歧
- `notes/research/remediation-plan-multi-agent.md` — 多 agent 修改方案
- `experiments/emergence_decomposition/spec.md` — 当前实验 spec
- `experiments/emergence_decomposition/review.md` — spec review 历史

---

## agent-evolution-free-parameters 自由参数清单

> **原文件**：`notes/research/agent-evolution-free-parameters.md`（2026-04-17 合并前位置）


**日期**：2026-04-14
**性质**：共享研究笔记（Claude Code / Cursor / Codex 都应读）
**关联假设**：`notes/ideas/emergent-creativity-hypothesis.md`

---

## 起因

Ken 让我看 EvoMap（evomap.ai）—— 一个 AI agent 自进化基础设施平台。

**EvoMap 是什么**：核心协议叫 GEP（Genome Evolution Protocol），概念栈包含三层：

- **Gene**：原子级 fix pattern，自带 validation command
- **Capsule**：Gene 的打包集合，本质是"进化版的 Skill"
- **Evolver 引擎**：扫描 runtime log → 匹配 Gene/Capsule → 生成下一步进化 prompt → 记录 EvolutionEvent 审计事件
- 关键点：prompt generator，不是 code patcher。不自动改代码、不联网、不执行任意 shell
- 网络层 EvoMap Hub 可选，用于跨 agent 共享 Capsule、worker pool、进化排行榜

**和 AXL/KPAX 的关系**：表面相似，实际不同层。

| | EvoMap | AXL + KPAX |
|---|---|---|
| 层级 | Agent 基础设施 | 研究 + 产品应用 |
| 记忆对象 | Agent 自己的能力（skill / fix pattern） | 用户决策历史 + debate agent memory |
| 进化机制 | 跨 agent 共享 verified capability | 跨学科 agent 碰撞产生涌现 |
| 单位 | Capsule（可复用技能包） | Evidence + Cognition distillation |

**结论**：值得借鉴概念（EvolutionEvent 审计链 ≈ evidence_ref、Gene/Capsule 分层 ≈ L1/L2 记忆分层、80/15/5 策略比例），不做集成。两者正交：EvoMap 解决"能力在 agent 间流通"，AXL 解决"跨学科碰撞产生新知识"。

---

## Ken 的关键判断

> 不管是个体智能还是群体智能，你想让 agent 自进化都得有这样的设计。难不是难在 idea，而是难在那些具体的数值、公式、算法。

这个观察是对的。所有做 agent 进化的系统最后都会撞到同一组问题，区别在于谁有数字、谁是拍脑袋。本文把 AXL/KPAX 和 EvoMap 共同要回答、但目前都没答案的**自由参数**列清楚，作为后续研究路线。

---

## 五类自由参数

### 1. Fitness / 选择信号

一条新产生的知识值不值得留下，取决于一个标量判断。

- **EvoMap 做法**：Gene 自带 validation command，能跑通就留。只在"代码修复"这种有客观 ground truth 的场景成立
- **KPAX cognition_distiller 现状**：判据不清楚。如果靠 LLM 自评，就是被评价者当评委，回路自污染
- **需要的数字**：保留阈值 τ，低于 τ 丢弃
- **需要的机制**：τ 的来源（人工标注、用户反馈、外部验证、还是其他）

### 2. Re-rank 权重

KPAX 记忆系统 plan 现写：`peer_reviewed ×1.3`，`external ×1.2`，`generated ×0.9`。

这三个数是 bootstrap 启发式，需要升级为数据支撑：

- 权重对最终 retrieval 质量的影响曲线（扫参测）
- `generated ×0.9` 是否足以防止自我强化
  - 监控指标：generated 内容在 top-K retrieval 中的占比
  - 超过 50% = 回声室告警
- 从启发式切到学习式的门槛：多少条用户采纳/否决数据之后可以用监督学习替代拍脑袋

### 3. 多样性 / 坍缩阈值

跨学科 debate 最大风险：多轮之后 agent 互相说服、观点趋同、涌现消失。

- **EvoMap** 靠结构性隔离（Capsule + 审计链）防污染，缺数值监控
- **AXL** 现在靠定性观察（Ken 对 7-agent vs 3-agent 的质量判断）

要把"涌现创造力"从玄学变成可检验假设，必须有可观测的 diversity metric：

- 候选指标：
  - agent 发言 embedding 的 pairwise cosine 距离均值
  - 每轮新增概念的 novelty score（相对前 N 轮的最小距离）
  - 立场向量方差
- **坍缩警报阈值 X**：多样性 < X 时，debate engine 强制注入扰动
  - 扰动手段：换 agent、塞反方论文、改温度、改 prompt
- X 的数值现在没有。没有这个数，"涌现创造力"就永远是玄学

### 4. Innovation / Optimization / Repair 比例

EvoMap 拍的是 80/15/5。延伸问题：

- 这三个比例怎么测好坏
- 不同任务类型应不应该用不同比例
  - KPAX 五种问题类型（yes/no、probability、comparison、strategy、evaluation）可能各有最优比例
- 是否应该是 debate 过程中动态变化的

### 5. Memory decay

- cognition 写入 L2 之后是否随时间衰减
- 衰减函数形态：指数、线性、阶梯、还是只在被新证据反驳时降权
- EvoMap 假设 Gene 是 timeless，不处理
- KPAX 的用户决策历史显然有时效性，但现在没有衰减函数

---

## 研究路线建议

1. **参数清单冻结**
   Phase 3（KPAX 接 Zep）之前把所有自由参数列完整。接上 Zep 后结构凝固，改动成本上升。

2. **可观测指标定义**
   每个自由参数对应一个或多个可测指标。
   - 示例：`diversity_metric = var(embedding(agent_turn_i))`
   - 示例：`echo_chamber_score = |generated in top_K| / K`

3. **最小扫参框架**
   - 固定一组基准问题（覆盖 KPAX 五种问题类型）
   - 扫参数组合，记录指标
   - 目标不是一次找到最优，而是建立 `参数 → 指标 → 主观质量` 的映射
   - 这是项目里唯一能产出真正学术论文的部分

4. **并行性**
   这件事和论文注入报告、Dashboard 正交，可以独立推进。不阻塞当前 P0。

---

## 核心判断

EvoMap 没解决这些问题，它用的也是拍的数字让系统能跑。**谁先把这些数字从启发式升级到数据支撑的曲线，谁就有护城河。**

"涌现创造力"假设能不能验证，取决于这个参数实验台建没建起来。没有它，所有关于 debate 质量的讨论都停留在定性层面，论文级别的贡献出不来。

---

## 相关文件

- `notes/ideas/emergent-creativity-hypothesis.md` — 假设的理论框架
- Cursor plan: `memory_system_architecture_7d1abf0b.plan.md` — 当前 re-rank 权重和 origin 机制
- `projects/knowledge-graph/backend/app/services/cognition_distiller.py` — distill 流程（fitness 信号的候选落点）
- `projects/knowledge-graph/backend/app/services/agent_memory.py` — memory decay 的候选落点

## 来源

- [EvoMap 官网](https://evomap.ai)
- [EvoMap/evolver GitHub](https://github.com/EvoMap/evolver)

---

## seven-layer-memory-design 七层记忆

> **原文件**：`notes/research/seven-layer-memory-design.md`（2026-04-17 合并前位置）


**日期**：2026-04-14
**性质**：共享研究笔记（Claude Code / Cursor / Codex 都应读）
**配套文档**：
- `notes/research/agent-evolution-free-parameters.md` — 自由参数清单，本设计的 L7 是其物理载体
- `notes/ideas/emergent-creativity-hypothesis.md` — 涌现创造力假设，本设计的 L5 多样性监控是验证这个假设的关键机制

---

## 起因

项目 CTO 已经做了一版 7 层记忆系统。Ken 要求基于 2025 年 SOTA 重新设计一个"最接近理论最强"的 7 层，用来对照 / 迭代 / 潜在替换 CTO 版本。

本文件不是"最强"的声明，是**目前 SOTA 能拼出来的最完整 7 层**。每一层都有具体论文对应，不凭空。

---

## 一、SOTA 速览

实际读过的参考系统（均有 arxiv / 官方实现，不是道听途说）：

| 系统 | 年份 | 分层 | 核心设计 |
|---|---|---|---|
| MemGPT / Letta | 2023 | 3 | Main context / Core / Recall / Archival。OS 式分页。 |
| Generative Agents（Stanford）| 2023 | 3 | Memory stream + Reflection（重要性阈值 150 触发）+ Plan（日/时/动作三级）|
| Voyager | 2023 | 1 强 | Skill library 作为程序记忆，vector DB 存 code，docstring embedding 检索 |
| HippoRAG / HippoRAG 2 | 2024-25 | 类脑 | 新皮层（LLM）+ 海马旁回（encoder）+ 知识图谱 + Personalized PageRank |
| A-MEM（NeurIPS 2025）| 2025 | 1 网 | Zettelkasten：原子笔记 + 动态链接 + 新笔记反向更新旧笔记 |
| Mem0 | 2025 | 2 阶段 | Extraction + Update；user/session/agent 三作用域；LOCOMO +26% |
| G-Memory（NeurIPS 2025）| 2025 | 3 图 | Insight Graph + Query Graph + Interaction Graph，为多 agent 协作设计 |
| LightMem | 2025 | 3 段 | Atkinson-Shiffrin 启发：感觉过滤 → 短期工作区 → 睡眠时巩固到长期 |
| SimpleMem | 2025 | 3 阶 | 熵感知压缩 → 递归巩固 → 查询感知检索 |
| SEAL（MIT 2025）| 2025 | 自进化 | 模型生成 self-edit，RL reward 是下游任务表现。有灾难性遗忘问题 |
| Darwin Gödel Machine（Sakana 2025）| 2025 | 自进化 | Agent 变种 archive，交替 self-modify 和 task eval。SWE-bench 20→50% |
| ADAS / Meta Agent Search | 2024 | 自进化 | Meta agent 写代码生成新 agent，archive 反哺下一轮 |

来源见文末链接。

---

## 二、七层设计

### 设计原则

- 每层独立功能边界，不和其他层重叠
- 每层有明确读写协议和遗忘/晋升规则
- 每层对应 `agent-evolution-free-parameters.md` 里的某一类自由参数
- 全部可追溯到 SOTA 来源
- 专门为 AXL（跨学科辩论）+ KPAX（决策工具）+ 涌现创造力研究优化，不是通用 agent

从最快/最易失到最慢/最稳：

---

### L1 — 工作记忆（Working Memory）

| 字段 | 值 |
|---|---|
| 时间尺度 | 秒-分钟 |
| 存什么 | 当前 turn 的 scratch pad、思维链中间状态、活跃 tool call 结果 |
| 载体 | in-context，不持久化 |
| 读写 | 每次 agent 动作写一次，下次对话 reset |
| SOTA 对应 | MemGPT main context |
| 自由参数 | context budget 分配（system prompt / tools / history / scratch 各多少 token）|

**关键设计点**：设一个"scratch overflow"触发器——超过预算时自动把内容推向 L2，不能直接丢弃。

---

### L2 — 情节记忆（Episodic Log）

| 字段 | 值 |
|---|---|
| 时间尺度 | 会话-月 |
| 存什么 | 完整的原始对话和事件流，**逐字，不删减** |
| 载体 | append-only 日志 + 时间索引 + 语义索引 |
| 读写 | 只追加，绝不原地改；读走 recency + semantic + importance 三路合并 |
| SOTA 对应 | Generative Agents memory stream、MemGPT recall |
| 自由参数 | importance scoring 函数（哪条事件进入后续 reflection 触发）|

**为什么必须逐字**：
1. 所有上层（L3/L5/L6）都从它蒸馏，原料丢了就回不去
2. Evidence traceability 的唯一真相源
3. CTO 说的"记录完整对话形成语言风格"—— L6 的语料基础

**遗忘规则**：不主动遗忘，只冷热分层。超过 30 天自动转冷存储，仍可召回。

---

### L3 — 语义记忆（Semantic Memory）

| 字段 | 值 |
|---|---|
| 时间尺度 | 用户-项目生命周期 |
| 存什么 | 从 L2 抽取的去上下文化事实、实体、关系、偏好。**原子级** |
| 载体 | A-MEM 风格原子笔记图谱 + 向量索引 |
| 读写 | 写：Mem0 两阶段（extract → update），必须带 evidence_ref。读：HippoRAG 风格的 embedding + Personalized PageRank 多跳 |
| SOTA 对应 | A-MEM + Mem0 + HippoRAG 2 |
| 自由参数 | Re-rank 权重（peer_reviewed / external / generated 系数）、节点合并阈值 τ、echo chamber score |

**节点 schema**：
```
{
  content: str,
  keywords: [str],
  tags: [str],
  links: [node_id],
  origin: "external" | "generated",
  evidence_ref: [L2 event_id],
  confidence: float,
  created_at: timestamp,
  last_updated: timestamp
}
```

**关键字段 `origin`**：
- `external`：从论文、用户直接陈述、外部源进来
- `generated`：LLM 推断出的

这是防自污染的唯一结构性防线。re-rank 时 generated 权重 < external。

**A-MEM 的关键创新必须搬过来**：新节点会反向触发旧节点更新，让图谱持续重构，而不是只追加。

---

### L4 — 程序记忆 / 技能库（Procedural Memory）

| 字段 | 值 |
|---|---|
| 时间尺度 | 永久 |
| 存什么 | 可执行的单元——prompt 模板、agent workflow、工具调用序列、数据管道 DAG |
| 载体 | vector DB 存 code + docstring，检索用 docstring embedding |
| SOTA 对应 | Voyager skill library + Darwin Gödel Machine archive + ADAS |
| 自由参数 | Fitness 阈值 τ、Innovation/Optimization/Repair 比例、变种多样性下限 |

**Skill schema**：
```
{
  code: str,
  docstring: str,
  validation_case: [input_output_pair],
  fitness_score: float,
  lineage: [parent_skill_id],
  origin_skill_ids: [skill_id]  // 组合来源
}
```

**进化机制**：
- Voyager 式：复杂 skill = 简单 skill 的组合，组合结构显式存
- Darwin Gödel Machine 式：维护变种 archive，不只留最优解，保留多样性
- 每次 skill 被调用都记录成败，更新 fitness

**DAG 子结构**：当前活跃任务以 HTDAG（Hierarchical Task DAG）形式存放。每个节点是一个 L4 skill 实例，边是依赖关系。DAG 不是独立一层，是 L4 的运行时视图。

---

### L5 — 反思 / 洞察记忆（Reflection & Insight）

| 字段 | 值 |
|---|---|
| 时间尺度 | 周期性生成（每天/每 N 事件）|
| 存什么 | 对 L2-L4 的 higher-level 推断。不是原始事实，是结论 |
| 触发 | Generative Agents 式——最近事件 importance 累计超阈值（原论文 150），或定时 sleep cycle |
| 载体 | G-Memory 的 Insight Graph 结构——节点是洞察，边是"从哪些证据来" |
| SOTA 对应 | Generative Agents reflection + G-Memory Insight Graph |
| 自由参数 | 坍缩警报阈值 X、reflection 触发阈值、洞察保留率 |

**关键：这层最容易自污染**。必须：
1. 洞察 100% `origin=generated`，严禁伪装 external
2. 触发 reflection 的重要性阈值可调
3. **Diversity monitor 在这里落地**——一轮 reflection 产生的新洞察如果和旧洞察平均 cosine > X，警报 + 强制多样性注入（换 agent、换 prompt、改温度、塞反方论文）

**这是验证涌现创造力假设的物理位置**。X 的数值留空，由 L7 实验台扫出来。

---

### L6 — 人格 / 风格记忆（Persona & Style）

| 字段 | 值 |
|---|---|
| 时间尺度 | 慢变（周-月）|
| 存什么 | 用户的语言指纹——词汇偏好、句式习惯、推理风格、价值观、禁忌词 |
| SOTA 对应 | LoCoMo assertion-based persona + LightMem sleep consolidation |
| 自由参数 | 蒸馏窗口大小、重算频率、LoRA adapter rank |

**两种形态并存**：

1. **结构化 persona card**（JSON，显式、可审）：
```
{
  writing_rules: [...],           // 禁"不是而是"、禁 emoji 等
  vocabulary_bias: {...},
  sentence_length_dist: {...},
  taboo_patterns: [...],
  reasoning_preferences: {...}
}
```

2. **LoRA adapter / soft prompt**（隐式，覆盖面更广）：长期蒸馏 L2 语料进参数层

**读写**：
- 写：sleep cycle 时从 L2 全量语料**重新蒸馏，不增量**。增量会被最近一次反常对话污染
- 读：作为 system prompt 的动态组成部分注入每次对话

**为什么必须重算**：增量更新的 persona 会漂移。全量重算成本高但可以离线做。

---

### L7 — 元记忆 / 进化账本（Meta-Memory & Evolution Ledger）

| 字段 | 值 |
|---|---|
| 时间尺度 | 系统生命周期 |
| 存什么 | 系统自身的进化轨迹 |
| 载体 | append-only event ledger + 时间和参数双索引 |
| SOTA 对应 | Darwin Gödel Machine agent archive + ADAS archive + EvoMap EvolutionEvent |
| 自由参数 | **所有其他层的自由参数都在这里被实验、被观测、被归档** |

**存什么具体**：
- 参数扫描实验结果（哪个 re-rank 权重组合在哪个 benchmark 上多少分）
- Agent 变种 archive（Darwin Gödel Machine 式，包括失败变种）
- 策略胜率历史（不同 debate 配置在不同问题类型上的质量指标）
- 每一次 L4 skill 的 fitness 变化
- 每一次 L3 节点合并/分裂的事件
- 每一次 L5 reflection 的 diversity 指标

**Event schema**：
```
{
  event_type: str,
  timestamp: ts,
  before_state: obj,
  after_state: obj,
  trigger: str,
  outcome_metric: float,
  lineage: [parent_event_id]
}
```

**用途**：
1. 反向调节 L3 的 re-rank 权重（从拍脑袋升级到数据驱动）
2. 给研究论文提供原始数据
3. 审计 debug——任何一次系统行为都能回溯到是哪些 L7 事件导致的

**这是参数实验台的物理落点**。`agent-evolution-free-parameters.md` 里列的五类参数，实验结果全部存这里。

---

## 三、跨层机制

缺任何一条整个系统都会崩。

### 1. Consolidation Loop（睡眠巩固循环）

来源：SLEEP framework、LightMem、SimpleMem、SEAL 的 sleep-time update。

异步 offline 任务，不阻塞 online 对话：

```
每 N 小时 / 每 M 条新事件：
  L2 → L3：提取新事实（Mem0 两阶段）
  L2 → L6：重算用户 persona（全量）
  L3 + L5 → L5：触发 reflection，产出新洞察
  L4 使用记录 → L4：更新 skill fitness
  所有上述事件 → L7：记录成 evolution event
```

**硬要求**：offline。不能让用户等 consolidation。

### 2. Origin Field 贯穿全栈

| 层 | 允许的 origin |
|---|---|
| L2 | 一定 external（原始记录）|
| L3 | external or generated |
| L4 | external or generated |
| L5 | **一定 generated**（它就是推断层）|
| L6 | 混合（结构化部分 external，LoRA 部分 generated）|
| L7 | 一定 external（进化事件的客观记录）|

检索时 re-rank：`score *= origin_weight[origin]`。防回声室最后一道防线。

### 3. Evidence Chain

L3/L4/L5/L6/L7 每条内容带 `evidence_ref` 指向 L2 原始事件。审计时可追溯任何结论到原文。

### 4. Diversity Monitor

跑在 L5 和 L3：
- 定义：单次 reflection 产出的新洞察两两 embedding 方差
- 警报：低于 X → 强制多样性注入
- X 留空，由 L7 实验台扫出来

### 5. Fitness Routing

L4 skill 执行结果 → L7 记录 → 反向调 L3 权重 / L5 触发阈值 / L4 innovation 比例。

**闭环**：上层用得好不好，反过来调下层参数。

---

## 四、七层 vs 经典三分法

| 经典分类 | 对应层 | 说明 |
|---|---|---|
| Working memory | L1 | |
| Episodic | L2 | |
| Semantic | L3 | |
| Procedural | L4 | |
| **新增** Reflective | L5 | Generative Agents 引入，对话 agent 必需 |
| **新增** Persona/Identity | L6 | 对话 agent 特有 |
| **新增** Meta-evolution | L7 | 自进化系统特有 |

三条新增层是做自进化系统绕不开的，不是凑数。L5 不存在做不了 higher-level 推断；L6 不存在没有风格一致性；L7 不存在所有参数只能拍脑袋。

---

## 五、和 CTO 版本的对线清单

CTO 已经做了一版 7 层。下面十条用来逐条对照，任何一条答不上就是改进点：

1. L2（原始日志）叫什么？append-only 还是会编辑？会编辑就断了 evidence chain
2. 有没有 `origin` 字段区分 external 和 generated？没有就是回声室风险敞开
3. Reflection 层周期还是事件触发？阈值多少？可调吗？硬编码就是拍脑袋
4. Skill library 保留多样性还是只留最优？只留最优等于放弃 open-ended evolution
5. Persona 层增量更新还是全量重算？增量会漂移
6. 元记忆层存不存？append-only？不存就没参数实验台
7. Consolidation 是 online 还是 offline？online 会卡用户
8. DAG 结构是哪一层的子结构？独立一层会和 skill library 重叠
9. 有没有 diversity monitor？哪层跑？没有就无法验证涌现创造力假设
10. Fitness signal 从哪里来？答"LLM 自评"就是回路自污染

---

## 六、核心判断

1. **"最强"这个定语站不住**。没有任何记忆系统被证明是最强。这个是 2025 年 SOTA 能拼出来的最完整 7 层，每层都能引到具体论文。
2. **最关键三层是 L2、L3、L7**。
   - L2 保证可追溯
   - L3 是主要工作区
   - L7 是研究护城河的物理位置
3. **两个 7 层都是 7 层，但哪 7 层差别巨大**。CTO 版本和本设计重合度高说明思路对路；有明显不同值得一次面对面对线。
4. **本设计和自由参数清单闭环**。L7 是参数实验台的物理载体。两件事合起来才是完整研究路线。

---

## 七、相关文件

- `notes/research/agent-evolution-free-parameters.md` — 自由参数清单，L7 存放所有实验结果
- `notes/ideas/emergent-creativity-hypothesis.md` — 涌现创造力假设，L5 多样性监控是验证机制
- `projects/knowledge-graph/backend/app/services/agent_memory.py` — 当前 AXL 记忆实现，待对照重构
- `projects/knowledge-graph/backend/app/services/cognition_distiller.py` — 当前 distill 流程，对应 L2 → L3/L5 consolidation
- `projects/knowledge-graph/backend/app/services/session_memory.py` — 当前 session 层，对应 L2

---

## 来源

- [MemGPT arxiv 2310.08560](https://arxiv.org/abs/2310.08560)
- [Letta docs](https://docs.letta.com/concepts/memgpt/)
- [Generative Agents arxiv 2304.03442](https://arxiv.org/abs/2304.03442)
- [Voyager arxiv 2305.16291](https://arxiv.org/abs/2305.16291)
- [HippoRAG arxiv 2405.14831](https://arxiv.org/abs/2405.14831)
- [HippoRAG 2 报道](https://www.marktechpost.com/2025/03/03/hipporag-2-advancing-long-term-memory-and-contextual-retrieval-in-large-language-models/)
- [A-MEM arxiv 2502.12110](https://arxiv.org/abs/2502.12110)
- [Mem0 arxiv 2504.19413](https://arxiv.org/abs/2504.19413)
- [G-Memory arxiv 2506.07398](https://arxiv.org/abs/2506.07398)
- [SEAL arxiv 2506.10943](https://arxiv.org/abs/2506.10943)
- [SEAL 项目主页](https://jyopari.github.io/posts/seal)
- [Darwin Gödel Machine arxiv 2505.22954](https://arxiv.org/abs/2505.22954)
- [Sakana DGM 主页](https://sakana.ai/dgm/)
- [ADAS arxiv 2408.08435](https://arxiv.org/abs/2408.08435)
- [TDAG arxiv 2402.10178](https://arxiv.org/abs/2402.10178)
- [Deep Agent HTDAG arxiv 2502.07056](https://arxiv.org/html/2502.07056v1)
- [LightMem arxiv 2510.18866](https://arxiv.org/html/2510.18866v1)
- [Language Models Need Sleep openreview](https://openreview.net/pdf/05bbb74851e965f5199f45f83937d1c396f048c8.pdf)
- [SimpleMem github](https://github.com/aiming-lab/SimpleMem)
- [Memory in the Age of AI Agents 综述](https://arxiv.org/abs/2512.13564)
- [LoCoMo benchmark](https://snap-research.github.io/locomo/)

---

## role-labels-vs-orchestrator 架构自审（多 agent vs orchestrator）

> **原文件**：`notes/research/role-labels-vs-orchestrator.md`（2026-04-17 合并前位置）


**日期**：2026-04-14
**性质**：共享研究笔记（Claude Code / Cursor / Codex 都应读）
**触发**：Ken 分享了一篇 X 长文，核心判断"AI 社区流传的三省六部式多 agent 架构是过度复用人类思维的错觉"，对项目触动较大。本笔记记录文章核心 + 对项目当前设计的诚实审视。
**配套文档**：
- `notes/research/remediation-plan-multi-agent.md` — 基于本笔记产出的修改方案
- `notes/research/seven-layer-memory-design.md` — L5 反思层的改进点来自本笔记
- `notes/research/agent-evolution-free-parameters.md` — 第四节的对照实验要加进 L7 实验台

---

## 一、文章核心

来源：X/Twitter 长文（Ken 粘贴，来源未公开归档，作者 `@sujingshen`）。参考材料列表是 Anthropic / OpenAI / Google 三家的工程博客。

### 四条核心论断

1. **三省六部式分工解决的是人类瓶颈，不是 AI 瓶颈**
   - 人类分工是因为注意力有限 + 专业壁垒 + 协调成本
   - LLM 一个都没有：同一个模型既能写 PRD 又能写代码，没有"职业边界"
   - 给 agent 贴"PM / 测试工程师"标签，不会让它更专业，只会让它**拒绝越界**
   - 最有价值的推理恰好发生在边界上，角色标签从系统层面封死了这个可能性
   - **结论：角色扮演制造的是"艺术性拒绝"，不是真实专业化**

2. **信息在角色传递中死亡**
   - Agent A 产出文档传给 Agent B
   - 传递的是**结论**，不是推理过程
   - B 拿到文档重新理解，隐含假设持续丢失
   - 工作流越长，最终输出越"局部正确整体漂移"——每个节点看起来合理，但整体已经偏离目标
   - 人类组织靠会议 / 文化 / 非正式沟通补偿这个损耗，agent 之间没有这些机制

3. **三家大厂的真实做法是 orchestrator-worker + 显式外部状态**
   - **Anthropic**：Context Engineering 取代 Prompt Engineering；Claude Code / Research 系统用 `claude-progress.txt` 跨 session 状态文件；orchestrator-worker 架构里 lead agent 持有完整意图，subagent 并行探索，结果回流给 lead agent 综合
   - **OpenAI**：Codex spec 文件冻结目标 + runbook + server-side compaction + Skills 概念；GPT-5.3-Codex 跑 25 小时不间断完成完整设计工具
   - **Google**：Gemini 1M context + Conductor 扩展（把项目意图从聊天移出到代码库持久 markdown）+ Gemini 3 的 Thought Signatures 防止 reasoning drift

4. **Anthropic 的 subagent 和 CrewAI 的分工看起来像，本质反着**
   - **三省六部 / CrewAI**：职能性分工（接力赛）—— PM → Dev → QA，每个角色只处理一段，信息从上一棒传到下一棒
   - **Anthropic Research**：功能性并行（撒网）—— 多个同性质 subagent 同时搜索不同方向，没有下一棒，结果全部回流给同一个 orchestrator 合成
   - **关键区别**：
     - 前者是**信息压缩传递**，后者是**并行覆盖合成**
     - 前者最大的问题是信息衰减，后者最大的收益是搜索空间扩大
     - Anthropic 自己的数据：token 消耗量解释 80% 的性能差异

### 真正的架构原则（五条）

1. **推理链不能断，只能分叉再合并**。多 agent 的正确用法是主 agent 持有完整意图，子调用为了深挖某个子问题，结果回流给主 agent，而不是传给下一个 agent。
2. **显式外部状态，不靠模型记住**。progress.txt / git history / spec 文件，形式不重要，原则是推理链的关键节点必须外化到持久存储。
3. **Multi-agent 的价值是并行覆盖，不是分工**。Anthropic 的结论：性能提升主要来自花了更多 token，不是分工更合理。适合 breadth-first（广度优先）任务，不适合连续推理、深度依赖上下文的任务。
4. **验证 agent 是否定者，不是接棒者**。对抗性检验，不是流水线传递。
5. **工具是工具，不是角色**。给 agent 配什么工具（bash / 文件读写 / 代码执行）远比给它贴什么标签重要。工具决定能做什么，角色标签只约束愿意做什么。

---

## 二、对项目的诚实审视

### 站得住的部分（不改）

以下设计和文章原则对齐：

| 设计点 | 为什么对齐 |
|---|---|
| **AXL 主持人模式**（moderator + 多 agent 共享 transcript）| Moderator 持有完整 transcript，agent 发言汇聚到共享流，**更接近 orchestrator-worker 而不是流水线**。agent 之间不直接传文件，都对着共同上下文说话 |
| **多 LLM 混合推演**（DeepSeek / GPT / Claude 随机分配给不同 agent）| **真实异质性**，不是贴标签的虚假多样性。正好踩在 Anthropic "多 token 多方向" 的收益点上 |
| **Zep 按学科注入知识**（每个 agent 拿到的不只是不同 prompt，还是不同原始资料）| **真实信息异质**，不是假的角色异质 |
| **Cursor plan 文件归档** | 接近 Anthropic 的 `claude-progress.txt` 模式：append-only、跨 session 可读、外部锚点 |
| **7 层设计里的 L2（append-only 原始日志）+ L7（进化账本）** | 文章推的"显式外部状态"模式。L2 绝不原地改、evidence_ref 贯穿全栈——原则完全一致 |

**核心判断**：项目里真正接近 SOTA 的部分是**异质性**（多 LLM + Zep 按学科知识），而不是角色扮演。继续强化前者，弱化后者。

### 有风险的部分（要改）

详细修改方案见 `notes/research/remediation-plan-multi-agent.md`。本节只列清单：

1. **KPAX 五步分析流程**（`question_parser → expert_builder → context_collector → debate → report_generator`）是经典流水线。用户真实意图只存在于第一句原话里，到 report 那步早就被重写/压缩/总结了三轮
2. **KPAX 生成带立场的专家**（`{学科, 立场, 人格}` 标签）可能在制造"伪专业"。立场应该是**临时 lens** 而不是身份标签
3. **7 层记忆的 L5 反思层是隐藏的压缩环节**。reflection 把 L2 原始对话压缩成 higher-level insights，下游检索可能直接用反思输出而跳过 L2 原文
4. **核心研究假设本身受挑战**。"跨学科碰撞产生涌现创造力"隐含预设"学科标签能激发真正不同的推理模式"。当前的 7 agent vs 3 agent 对比不足以证明这条假设，因为收益可能来自异质性或 token 预算而不是角色

---

## 三、核心研究假设的挑战与对照实验

这是本笔记最重的一节。

### 挑战

Ken 项目的研究护城河叫"跨学科碰撞产生涌现创造力"。这个假设隐含预设：

> 给同一个模型贴不同学科标签，能激发真正不同的推理模式。

按文章的逻辑，这个预设站不住：同模型同参数、只是 prompt 不同的 N 个 agent，本质就是一个模型在不同 prompt 约束下的 N 次采样。"涌现"的四个可能来源：

| 代号 | 来源 | 是不是 Ken 假设的核心 |
|---|---|---|
| (a) | Moderator 对丰富 transcript 的合成能力 | 否 |
| (b) | 异质模型 + 异质知识的真实多样性 | 否 |
| (c) | 更大的 token 预算（Anthropic 说 80% 收益在这里）| 否 |
| **(d)** | **真正不同的推理模式** | **是** |

当前 7 agent vs 3 agent 的对比在 (a)(b)(c)(d) 任意一个解释下都成立。**不能区分 (d) 是不是真的存在**。

### 对照实验清单

要分离这四个因素，需要加以下实验到 L7 参数实验台（见 `agent-evolution-free-parameters.md`）：

| 组 | 配置 | 用来分离什么 | 对比判断 |
|---|---|---|---|
| **基线** | 7 agent，不同学科，不同知识，不同模型 | 现状 | — |
| **A** | 7 agent，**全部标签为"通才"**，不同知识，不同模型 | 去掉学科标签 → 看 (d) | 如果 A ≈ 基线，学科标签是装饰，(d) 是幻觉 |
| **B** | 7 agent，不同学科标签，**同一份混合知识**，不同模型 | 去掉知识异质 → 看 (b) 的知识部分 | 如果 B ≪ 基线，知识异质贡献大 |
| **C** | 7 agent，不同学科标签，不同知识，**同一个模型** | 去掉模型异质 → 看 (b) 的模型部分 | 如果 C ≪ 基线，模型异质贡献大 |
| **D** | **1 个 orchestrator** + 7 个学科 corpus 作为工具 | 完全抛弃多 agent → 看 orchestrator-worker 能不能平替 | 如果 D ≈ 基线，多 agent 辩论架构是可选的 |
| **E** | 1 个 agent，**相同 token 总量**分成 7 次调用 | 纯粹看 (c) token 预算效应 | 如果 E ≈ 基线，只需要更多 token |

### 为什么这组实验是关键

1. **研究护城河验证**：不管结果是正还是反，都是社区稀缺的答案
2. **如果 (d) 是幻觉**：假设需要改写——"emergence 来自异质信息 + 异质模型 + moderator 综合"，而不是"来自学科角色碰撞本身"。更保守但更扎实
3. **如果 (d) 是真的**：那就是真正的发现，有论文潜力。需要进一步测 (d) 的边界
4. **如果只有 (c) 成立**：项目的整个多 agent 架构可以大幅简化，把钱花在 token 预算上而不是架构上

---

## 四、和七层记忆设计的关系

本笔记暴露了 L5 反思层的一个隐藏风险：**reflection 是一个压缩环节**，下游如果直接用反思输出而不回溯 L2 原文，就是文章批评的"信息在传递中死亡"。

需要加硬规则到 `seven-layer-memory-design.md` 的跨层机制：

- 任何使用 L5 反思的下游代码，**必须同时回溯到 L2 原文做二次校验**
- L5 是 L2 的**补充索引**，不是替代索引
- 检索管道默认行为："L2 优先，L5 兜底"，而不是反过来

---

## 五、核心判断

1. **三省六部批判对 KPAX 产品层（五步流程）打击最大，对 AXL 研究层（debate 架构）打击较小**。因为 AXL 的 moderator 架构本来就接近 orchestrator-worker，只是之前没意识到。
2. **项目真正接近 SOTA 的部分是异质性（多 LLM + Zep 按学科知识），不是角色扮演**。继续强化前者，弱化后者。
3. **研究假设要么用第三节的对照实验去证伪/证实，要么改写假设**。改写方向：涌现来自异质信息 + 异质模型 + moderator 综合，不来自学科角色本身。
4. **"过分复用人类思维"这个自我批评完全成立**。具体体现是：贴角色标签、让 agent 按职能传递、把"专家辩论"当成"真实专家会议"的直接模拟。但项目做对的地方也不少，尤其是异质性和外部状态。

---

## 六、来源

- 原文：Ken 从 X 分享（作者 `@sujingshen`），本地未归档，引用自记忆
- 参考材料（来自原文引用的三家工程博客）：
  - Anthropic Engineering Blog: Building Effective Agents, Effective Context Engineering, Multi-Agent Research System, Effective Harnesses for Long-Running Agents
  - OpenAI Developers Blog: Run Long Horizon Tasks with Codex, Shell + Skills + Compaction
  - Google Developers Blog: Architecting Efficient Context-Aware Multi-Agent Framework, Conductor: Context-Driven Development for Gemini CLI

---

## remediation-plan-multi-agent 修改方案

> **原文件**：`notes/research/remediation-plan-multi-agent.md`（2026-04-17 合并前位置）


**日期**：2026-04-14
**性质**：共享修改计划（Claude Code / Cursor / Codex 都应读）
**上游**：`notes/research/role-labels-vs-orchestrator.md` — 问题诊断
**下游**：本文件列出的具体改动点，按优先级排序

---

## 原则

1. **不重写代码层 debate 引擎**。AXL 的 moderator + 共享 transcript 本来就接近 orchestrator-worker，不是问题源。
2. **优先改产品层（KPAX）**，产品层是流水线式分工的重灾区。
3. **每个改动点都必须先定义指标**，否则改动只是信仰，不是工程。
4. **改动本身也要进 L7 进化账本**——改之前的指标、改之后的指标、改动原因，全部作为 evolution event 记录。
5. **Scope control**：本文件只列方向和边界，不在本文件里写代码。具体 PR 拆分和排期在真正动手时再做。

---

## 修改点 1：KPAX 五步流水线 → Orchestrator + Tools

### 现状

```
用户问题
   ↓
question_parser.py        ← LLM 调用 1：解析成结构化意图
   ↓ 结构化 JSON
expert_builder.py         ← LLM 调用 2：生成专家阵容
   ↓ 专家列表
context_collector.py      ← 汇总背景信息
   ↓ 背景包
AXL debate engine         ← LLM 调用 3~N：多轮推演
   ↓ debate 总结
report_generator.py       ← LLM 调用 N+1：生成报告
   ↓
用户看到的最终报告
```

### 为什么错

- 用户**真实意图**只存在于第一句原话里
- 到 `report_generator` 时，它看到的是**被重写 3 轮后的结构化数据**，不是用户原话
- 每一步都在做"理解上游输出 → 生成本层输出"的 LLM 调用，每次都在压缩
- 工作流越长，最终报告越"局部正确整体漂移"

### 修改方向

**核心动作**：从五个独立 service 接力，改成**一个 orchestrator 持有完整 session state，把五个能力当工具调用**。

具体调整：

1. **引入一个 `KPAXOrchestrator` 类**
   - 入口只有一个：`orchestrator.handle(user_message)`
   - 持有一个 `SessionState` 对象，字段包括：
     - `original_user_message: str` —— **永不覆盖，永不重写**
     - `parse_result: dict | None`
     - `experts: list | None`
     - `context_pack: dict | None`
     - `debate_transcript: list | None`
     - `report: str | None`
     - `tool_call_log: list` —— 每次工具调用的原始 in/out

2. **把现有五个 service 改造成"工具"**
   - 签名统一：`tool(session_state: SessionState) -> dict`
   - 每个工具**可以读完整 session state**，包括 `original_user_message` 和所有历史字段
   - 工具的输出**只追加到 session state**，不覆盖已有字段
   - 工具不再互相直接调用，全部经由 orchestrator 调度

3. **Orchestrator 的决策逻辑**
   - 不是硬编码的五步流水线
   - 是"根据当前 session state 判断下一步调用哪个工具"
   - 允许工具**重复调用**（比如先 parse 一次，生成专家后发现意图不明，再 parse 一次）
   - 允许工具**跳过**（简单问题不需要全流程）

4. **每个工具的 prompt 改造**
   - **所有 LLM 调用的 system prompt 都必须包含 `original_user_message`**
   - 不能只看上游的结构化输出做决策
   - 这条是死规则，防止信息在传递中死亡

### 改动文件（估计）

- 新增：`kpax/backend/kpax_svc/services/orchestrator.py`
- 新增：`kpax/backend/kpax_svc/services/session_state.py`（如果没有现成的）
- 改造：`question_parser.py` / `expert_builder.py` / `context_collector.py` / `report_generator.py` —— 签名统一 + prompt 里加 original_user_message
- 改造：`routers/analyze.py` —— 从直接调 service 改成调 orchestrator
- **AXL debate engine 不动**

### 验证指标

在 L7 进化账本里对比改造前后：

- **意图保持度**：让 LLM 判官对比 `report` 和 `original_user_message`，打分是否回应了用户真实诉求
- **结论一致度**：同一个问题连续跑 5 次，report 的核心结论是否稳定
- **token 消耗**：改造后每个请求总 token 的变化
- **延迟**：p50 / p95 延迟

### 风险

- Orchestrator 决策逻辑本身是一个 LLM 调用，可能成为新的瓶颈
- 改造期间会有一段时间产品层不稳定，需要 feature flag 灰度
- 工具重复调用可能把 token 成本推高

### 优先级

**P0**。这是 KPAX 层最大的架构债，而且改起来可控——五个 service 改造成工具接口不是重写，只是统一签名。

---

## 修改点 2：专家立场从"身份标签"改为"临时 lens"

### 现状

KPAX 的 `expert_builder.py` 给每个 agent 生成 `{学科, 立场, 人格}` 三元组，立场字段示例：
- 保守派 vs 激进派
- 理论派 vs 实证派
- 乐观派 vs 悲观派

这个立场作为 agent system prompt 的一部分，贯穿整场 debate。

### 为什么错

- 同一个模型扮演"保守派经济学家"和"激进生态学家"，本质是同一套参数在不同 prompt 约束下生成文本
- 贴标签的效果是**约束它愿意做什么**，不是**让它真的更专业**
- "保守派"被框死时，遇到需要激进推理的场景会**拒绝越界**（文章说的艺术性拒绝）
- 真正有价值的推理发生在立场边界上，当前设计从系统层面封死了这个可能

**但学科标签不等于立场标签，这两个要分开看**：

- **学科标签**：有 Zep 知识注入做真实信息异质的支撑，不只是贴标签，保留
- **立场标签**：没有信息异质支撑，纯粹是 prompt 约束，去掉或改造

### 修改方向

**核心动作**：立场从 agent 身份剥离，变成 moderator 发起的**临时视角请求**。

具体调整：

1. **`expert_builder.py` 去掉 stance 字段**
   - 专家只有 `{学科, 人格}` 两个维度
   - 学科绑定 Zep knowledge，人格影响推理风格（激进/保守/综合/桥梁），这两个都是当前保留
   - 立场**不再是 agent 属性**

2. **`debate_engine.py` 的 round_opener 机制扩展**
   - Moderator 在每一轮提问时可以**主动要求某个 agent 从特定立场回应**
   - 同一个 agent 在不同轮次可以被要求用不同立场
   - 典型的 moderator prompt：
     ```
     第二轮请 {agent_X} 从保守立场重新审视第一轮的结论。
     第三轮请 {agent_X} 从激进立场提出反例。
     ```
   - 这就把"立场"从身份约束变成了**同一个 agent 的多视角采样**

3. **保留对抗性推演选项**
   - Moderator 在需要时可以让两个**同一 agent** 的两个立场视角互相反驳
   - 相当于让同一个脑袋先站在 A 立场再站在 B 立场，而不是两个不同脑袋各站一边
   - 这更贴近人类真正的"深度思考"而不是"开会"

### 改动文件

- `kpax/backend/kpax_svc/services/expert_builder.py` —— schema 去 stance
- `projects/knowledge-graph/backend/app/services/debate_engine.py` —— round_opener 支持 lens 切换
- 前端 UI：如果有显示专家立场的地方要改成"当前视角"的动态显示，不是固定标签

### 验证指标

- **越界推理发生率**：抽样 debate，统计"某 agent 的发言明显偏离了自己立场"的次数。修改前和修改后对比
- **多样性指标**：每个 agent 在整场 debate 里 stance shift 的次数（现状固定立场次数永远是 1）
- **主观质量**：人工评分和 LLM judge 评分，对比 agent 的发言是否更丰富

### 风险

- 立场作为身份标签有一个副作用是**强化 agent 间的区分度**，去掉之后可能导致 agent 发言趋同
- 需要 moderator 主动分配立场，moderator 的能力变成新的瓶颈
- 如果 moderator 偷懒，整场 debate 会退化成"所有 agent 都用默认立场"

### 优先级

**P1**。比 P0 轻，但修改面更小，可以和 P0 并行。

---

## 修改点 3：L5 反思层加二次校验硬规则

### 现状

`notes/research/seven-layer-memory-design.md` 里的 L5 反思层定义：
- 触发条件：L2 事件 importance 累计超阈值
- 输出：higher-level insights，带 evidence_ref 指回 L2
- 被下游检索使用

### 为什么错

Reflection 是一个**压缩环节**。把 L2 原始对话压缩成"高层洞察"，天然会丢失细节。如果下游代码**直接用反思输出而不回溯 L2 原文**，就是文章批评的"信息在传递中死亡"。

`evidence_ref` 字段只是**允许**回溯，不是**强制**回溯。强制性靠检索管道的硬规则保证。

### 修改方向

**核心动作**：改 `seven-layer-memory-design.md` 的跨层机制章节，加一条硬规则；改 AXL 现有的 cognition_distiller 和 agent_memory 实现，对齐新规则。

具体调整：

1. **文档层面**
   - `seven-layer-memory-design.md` 的"跨层机制"章节加一节：
     > **L5 二次校验规则**：任何使用 L5 反思输出的下游代码，**必须同时回溯到 L2 原文做二次校验**。L5 是 L2 的补充索引，不是替代索引。检索管道的默认行为是 "L2 优先，L5 兜底"，而不是反过来。

2. **代码层面**（现有 AXL 里对应 L5 的组件）
   - `projects/knowledge-graph/backend/app/services/cognition_distiller.py` —— distill 产出的 insight 每条都带 **源事件 id 列表**（不只是模糊的 evidence_ref 字符串）
   - Agent memory 检索接口：每次返回 insight 时，**同时返回对应的 L2 原始事件片段**，作为同一次检索的附加结果
   - 使用 insight 的下游代码**必须消费 L2 片段**，否则 linter / 类型系统应该报错（可以用 Python 的 `NewType` 或者 wrapper class 强制）

3. **实验验证**
   - 对比"只读 L5" vs "L5 + L2 回溯"两种检索模式在推演质量上的差异
   - 放进 L7 进化账本

### 改动文件

- `notes/research/seven-layer-memory-design.md` —— 加一节
- `projects/knowledge-graph/backend/app/services/cognition_distiller.py` —— 输出加源事件 id
- `projects/knowledge-graph/backend/app/services/agent_memory.py` —— 检索返回合并 L2 + L5
- 所有调用 agent memory 的地方需要适配新的返回格式

### 验证指标

- **检索召回质量**：同一个查询，只用 L5 vs L5+L2 两种模式的下游生成质量对比
- **反思漂移率**：抽样 L5 insight，对比它和所引用 L2 原文的语义距离，超过阈值视为漂移

### 风险

- 强制回溯会推高 token 消耗（每次检索都要带 L2 片段）
- L2 片段可能很长，需要设计"最小相关片段"的抽取逻辑
- 改检索接口会 cascade 到很多调用点，PR 面大

### 优先级

**P1**。不紧急但重要。可以在 L5 真正被大规模使用之前完成。

---

## 修改点 4：为研究假设加对照实验组

### 现状

当前用 7 agent vs 3 agent 的对比来支撑"跨学科碰撞产生涌现创造力"假设。这个对比在以下四种解释下都成立：

- (a) Moderator 对丰富 transcript 的合成能力
- (b) 异质模型 + 异质知识的真实多样性
- (c) 更大的 token 预算
- (d) 真正不同的推理模式 ← 这才是 Ken 的核心假设

无法分离 (d)。

### 为什么错

这不是工程错误，是**研究方法错误**。当前的证据不足以支持结论。研究假设要么被对照实验证伪/证实，要么被改写成更保守的版本。

### 修改方向

**核心动作**：在 L7 参数实验台里固化六个对照组，按 `agent-evolution-free-parameters.md` 的"最小扫参框架"思路跑。

具体调整：

1. **固化实验组定义**（同 `role-labels-vs-orchestrator.md` 第三节的表）

   | 组 | 配置 |
   |---|---|
   | 基线 | 7 agent，不同学科，不同知识，不同模型 |
   | A | 7 agent，全部标签为"通才"，不同知识，不同模型 |
   | B | 7 agent，不同学科标签，**同一份混合知识**，不同模型 |
   | C | 7 agent，不同学科标签，不同知识，**同一个模型** |
   | D | **1 个 orchestrator** + 7 个学科 corpus 作为工具 |
   | E | 1 agent，相同 token 总量分成 7 次调用 |

2. **固化基准问题集**
   - 覆盖 KPAX 五种问题类型（yes/no、probability、comparison、strategy、evaluation）
   - 每种问题类型选 10 个代表问题
   - 共 50 个问题
   - **问题集冻结**，不能边跑边改

3. **固化评估指标**
   - 每组对每个问题跑 3 次，取中位数
   - 指标：
     - **LLM judge 质量评分**（盲评，不知道来自哪组）
     - **人工评分子集**（每组抽 10 个，Ken 自己评）
     - **多样性指标**：单场 debate 内 agent 发言的 embedding 方差
     - **token 消耗**：总 token、per-agent token

4. **结果写入 L7**
   - 每组每次实验作为一条 evolution event
   - 最终分析报告作为一份独立 note：`notes/research/experiment-2026-XX-emergence-decomposition.md`

5. **结论触发的后续动作**
   - 如果 A ≈ 基线：研究假设改写为"emergence 来自异质性 + moderator 综合"，去掉"学科角色"这一层
   - 如果 D ≈ 基线：KPAX 的多 agent 架构可以大幅简化为 orchestrator + tools
   - 如果 E ≈ 基线：重点转向"如何高效分配 token 预算"，放弃复杂架构

### 改动文件

- 新增：`kpax/backend/kpax_svc/experiments/` 目录
- 新增：`experiments/emergence_decomposition.py` —— 实验 runner
- 新增：`experiments/benchmark_questions.json` —— 冻结的 50 题
- 新增：`notes/research/experiment-2026-XX-emergence-decomposition.md` —— 结果分析
- L7 进化账本需要支持"实验事件"类型

### 验证指标

这组实验本身就是验证工具。它的输出就是判断其他修改点方向是否正确的依据。

### 风险

- 跑完一轮 50 题 × 6 组 × 3 次 = 900 次推演，成本不低（估算 $500-2000 视模型而定）
- 如果基准问题选得不好，结果无法推广
- Ken 作为人工评分者有偏见，需要设计盲评流程

### 优先级

**P0 研究路线**，但**不阻塞 P0 工程改造**（修改点 1、2、3）。实验 runner 的基础设施可以和架构改造并行建。

---

## 优先级汇总

| 修改点 | 优先级 | 工程或研究 | 依赖 |
|---|---|---|---|
| 1. KPAX 五步流水线 → Orchestrator | P0 | 工程 | 无 |
| 2. 立场身份 → 临时 lens | P1 | 工程 | 可以和 1 并行 |
| 3. L5 反思二次校验 | P1 | 工程 | 不阻塞其他 |
| 4. 对照实验组 | P0 研究 | 研究 | 不阻塞工程 |

---

## 不修改的部分（明确列出，防止误伤）

1. **AXL `debate_engine.py` 内部**。它是 orchestrator-worker 的一个实例，不是三省六部的受害者。
2. **多 LLM 混合推演机制**。这是异质性的来源，继续强化。
3. **Zep 按学科知识注入**。这是真实信息异质，继续保留。
4. **Cursor plan 文件归档 + AGENTS.md 共享入口**。已经是正确的外部状态模式。
5. **7 层记忆的 L2 / L7 设计**。已经对齐文章原则，不动。
6. **代码层的"debate"命名**。只改对外文案，代码保持。

---

## 后续动作

1. Ken 审阅本文件，确认优先级和范围
2. 确认后，把每个修改点拆成可执行的 task 卡片（不在本文件里做）
3. P0 工程改造（修改点 1）先开 PR，小步快跑
4. P0 研究（修改点 4）同时启动实验 runner 基础设施
5. 每次改动前后的指标变化写进 L7 进化账本

---

## kpax-knowledge-source-architecture KPAX 知识源架构

> **原文件**：`notes/research/kpax-knowledge-source-architecture.md`（2026-04-17 合并前位置）


**日期**：2026-04-16 深夜
**作者**：claude-code
**触发**：Ken 2026-04-16 晚提醒 cc 漏掉了 KPAX 知识层的真实形态——"KPAX 不仅仅是论文，还有行业的数据、经验，还有小伙伴在爬 Reddit / 知乎 / Quora"。原 `kpax-v0-deliberation-room.md` 没有明确 KPAX 的知识输入结构，这份笔记补上。
**上游**：`KPAX.md` 产品定义 + `notes/design/kpax-v0-deliberation-room.md` + radar 条目（autocli / yupi-hot-monitor / graphify / awesome-ceo）

---

## 1. 为什么不能只吃论文

AXL 作为研究平台，多学科 agent 辩论时默认吃学术论文（arXiv / OpenAlex / Semantic Scholar）。这对**学术问题**够用——agent 在讨论"Anthropic 宪法 AI 路线能否成为主流范式"时，学术论文是对的证据源。

但 KPAX 是**通用决策工具**，用户问题远超学术范畴：
- "我 28 岁月薪 2 万该不该辞职创业" —— 论文有相关研究但**不够**。需要真实创业者的经验（Reddit r/startups / 知乎创业话题 / YC 创业者访谈）
- "孩子 8 岁该不该大量用 AI" —— 需要育儿论坛（小红书 / 知乎 / Mumsnet）的第一手体验
- "小米汽车 vs 特斯拉 Model 3 vs 比亚迪汉怎么选" —— 需要实时车主社区（懂车帝 / 汽车之家 / 雪球）的真实使用反馈
- "2026 BTC 能不能破 20 万" —— 需要 crypto 社区情绪（X / Telegram / 雪球）+ on-chain 数据

**学术论文**告诉你"长期 / 结构性"的事；**行业 curated 资源**告诉你"圈内人的框架"；**社区经验**告诉你"具体个体的真实感受"。三者少一条，KPAX 的"帮你想透"就少一条腿。

---

## 2. 三条输入线的分工

### 2.1 Line A：学术论文（academic）
- **源**：arXiv / Semantic Scholar / OpenAlex / Crossref / Unpaywall / Europe PMC（多源 fallback 顺序见 `notes/research/wisland-analysis-and-positioning.md` B.7）
- **特征**：长期论证、peer-reviewed、方法透明
- **典型命中学科**：物理 / 数学 / CS / 心理 / 社科 / 艺术人文（当前 emergence_decomposition 使用的 7 学科多数从这里取证；KPAX 生产每场出席化身 3/5/7 位，奇数便于决断，最少 3，组合按问题动态选）
- **承担的问题层**：底层机制 / 理论框架 / 历史规律 / 可证伪命题
- **当前状态**：AXL Zep + Phase 1/2 记忆系统支撑，已就位

### 2.2 Line B：行业 curated（industry）
- **源**：awesome-list 生态（awesome-ceo / awesome-system-design 等）/ YC blog / a16z / Sequoia playbooks / Pragmatic Engineer 这类高质量 substack / 经典行业报告（Gartner / McKinsey 公开版）
- **特征**：实操经验浓缩、圈内人的思维框架、可验证但不是学术严谨
- **典型命中学科**：经济学（商业模型）/ CS（技术选型）/ 心理学（用户 insight）/ 社科（制度约束）
- **承担的问题层**：商业实操 / 产品策略 / 组织管理 / 工程选型 / 市场洞察
- **当前状态**：**未 ingest，等待**。候选参考：**graphify**（文件夹 → 可查询知识图谱，radar 2026-04-16）

### 2.3 Line C：社区经验（community）
- **源**：Reddit（英文）/ 知乎 / Quora / 小红书 / 雪球 / 豆瓣 / HackerNews / X / 微博 / 懂车帝 / 汽车之家 等垂直社区
- **特征**：第一人称真实体验、情绪化、样本偏小但细节具体、有实时性
- **典型命中学科**：心理（个体体验）/ 社科（群体认知模式）/ 艺术人文（叙事层）/ 经济（真实消费行为）
- **承担的问题层**：具体个案 / 情绪/偏好 / 真实使用场景 / 群体共识或极化
- **当前状态**：Ken 说小伙伴在做爬虫。**两种架构候选**（见下）

---

## 3. Line C 的两种架构：按需 vs 预缓存

### 3.1 按需模式
- **代表工具**：**autocli**（radar 2026-04-16，Rust 4.7MB skill，55+ 平台，Chrome 登录态复用）
- **触发**：用户问题进来 → agent 判断需要社区证据 → 实时调 autocli 拉相关平台当前热议
- **优点**：数据新鲜、按问题精准、不占存储
- **缺点**：每次调用有延迟（秒级或更久）、Chrome 登录态依赖意味着**服务端部署限制大**

### 3.2 预缓存模式
- **代表工具**：**yupi-hot-monitor**（radar 2026-04-16，Node.js 全栈，8+ 平台定时 poll，AI 做查询扩展 + 真假识别 + 相关性 + 摘要）
- **触发**：后台按热门话题定时 poll（每 30 分钟）→ AI 二次加工 → 存入热点库 → 用户问题进来 → agent 从缓存库检索
- **优点**：毫秒级响应、可做深度 preprocessing
- **缺点**：只对热门话题覆盖好、冷门问题仍然得现查

### 3.3 KPAX 真跑起来两种都要
- **用户问题 → classifier 判类型 → expert_builder 决定需要哪类证据**
- 如果问题是**热门 / 广覆盖**（比如 "小米汽车怎么样"）→ 命中预缓存库秒级返回
- 如果问题是**冷门 / 具体 / 个人化**（比如 "月薪 2 万上海 28 岁该不该回老家某三线城市"）→ 走按需 autocli 现拉
- 化身团（每场 3/5/7 位按问题组合，最少 3）在辩论过程中调用证据源时，这两种模式都是可用 tool

---

## 4. Line B 的架构：graphify 为主候选

### 4.1 graphify 的定位
- GitHub: safishamsi/graphify
- 把任意文件夹（code / docs / papers / images / videos）转成**可查询的知识图谱**
- Claude Code / OpenClaw / Cursor 等多 agent 通用 skill

### 4.2 KPAX 的 Line B 工作流
```
Ken / 运营手工整理 curated 资源 → 本地文件夹（/kpax_knowledge/industry/startups/yc/*.md）
  ↓
graphify ingest → 知识图谱
  ↓
expert_builder 按问题类型决定需要哪些节点
  ↓
化身团中相关学科角色（主要是经济 / CS / 心理 / 社科，以及可选的实践型化身如 Musk/巴菲特 skill）在辩论中查询 graph
  ↓
拉到相关 essay / playbook 片段作为证据
```

### 4.3 初版种子
- **awesome-ceo**（radar 2026-04-16）：8 模块（融资 / 产品 / 销售 / 营销 / 管理 / 招聘 / 财务 / 创业），YC / a16z / Sequoia curated。可作为 KPAX 初版 Line B 的种子库，验证 ingest 链路
- 后续扩展方向：awesome-system-design（技术）/ 成瘾与戒瘾经典框架（心理）/ 消费心理学读本（心理 × 经济）/ 职场 playbook（社科 × 经济）

---

## 5. 三条线的交叉与合成

### 5.1 一个问题典型调用链（示例）
**用户问**："35 岁程序员大厂被裁，该接降薪 40% 中小公司 offer 还是全职做独立开发者？"

- **Line A** 学术论文：劳动经济学关于职业中断的研究 / 心理学 resilience 文献 / 创业失败率 meta-analysis
- **Line B** 行业 curated：YC 文章 "how to prepare financially for founding" / Paul Graham essays / Pragmatic Engineer career advice
- **Line C** 社区经验：Reddit r/cscareerquestions 相似案例 / 知乎"35 岁中年危机"话题 / HackerNews career 讨论

化身各自从三类里拉适合自己角色的证据，在辩论中碰撞。

### 5.2 证据权重
- 学科决定倾向：经济学更重 A + B，心理学更重 A + C，社科全覆盖
- moderator 在 synthesis 时应标注证据来源层级（论文 / 行业 / 社区）——让用户知道**共识建立在哪层证据上**，这是 pilot_judge_rubric_v0.1 的"可解释性与理由可对话性"维度的直接落地

---

## 6. 三条线的 v0/v1/v2 phasing

### v0（3 周内 MVP）
- Line A：保留现有 AXL Zep 系统，不额外改造
- Line B：**graphify + awesome-ceo 种子**（1 天接通，KPAX 后端加个 graph_client 调用入口）
- Line C：**先跳过**，KPAX 化身团 v0（每场 3/5/7 位）只吃 A + B。不做社区数据接入

**理由**：Line C 两种架构都有部署限制（autocli 要本地 Chrome / yupi 要服务端），v0 给 10 个朋友测试时不必要。上线后根据反馈决定要不要接。

### v1（v0 发布后 1-2 月，根据朋友反馈决定）
- Line C：接入**预缓存模式**（yupi-hot-monitor 架构参考）。针对 KPAX 使用最频繁的 3-5 个问题域（消费决策 / 职业 / 育儿 / 投资），后台持续 poll 对应社区
- Line B：扩到 3-5 个 curated 资源集（awesome-ceo + awesome-system-design + 投资经典框架 + 职场经典 + 消费决策经典）

### v2（Ken 上链代币 + dex 上线后）
- Line C：加按需模式（autocli），处理冷门 / 个人化问题
- Line B：建**用户贡献机制**——用户可以上传自己的 curated 资源到 KPAX 共享池（代币激励），形成 KPAX 自己的知识底座

---

## 7. 和 AXL 的边界（再次强调硬规则 #6）

**所有知识源接入必须在 KPAX 层做**，不走 AXL monorepo import。具体：

- Line A 已经在 AXL 层（Zep 是 AXL 的），KPAX 通过 axl_client.py HTTP 调用时**顺带取**，不直接调 Zep
- Line B（graphify）在 KPAX 层独立部署，KPAX 的 expert_builder 或新增 `graph_client.py` 走 HTTP 或本地 Python 调用
- Line C（未来 autocli / yupi 派生）也在 KPAX 层独立

**反模式**：从 AXL 的 agent 直接调 KPAX 的知识源——会形成 AXL 依赖 KPAX，循环。AXL 是单向底座，不反向知道 KPAX 存在。

---

## 8. 待决策

- [ ] **v0 要不要就做 A + B 两条线，跳过 C**？（建议是的）
- [ ] **graphify 作为 Line B 主候选确认**？（目前是候选池里最合适的，graphify / Thoth 都可，倾向 graphify 因为 Claude Code skill 原生）
- [ ] **Line C 的 autocli vs yupi 哪个先**？（v1 决定，v0 先不做）
- [ ] **用户贡献知识源的代币激励设计**（v2 决定）

---

## 9. 关联文件

- `KPAX.md`：产品承诺
- `notes/design/kpax-v0-deliberation-room.md`：v0 形态（前端）
- `notes/external-references-radar.md`：四条工具 radar 条目（awesome-ceo / autocli / graphify / yupi-hot-monitor）
- `notes/research/wisland-analysis-and-positioning.md`：PDF 解析选型（Line A 的实现细节）
- `notes/agenda/next.md`：Line B 初版接入任务（graphify + awesome-ceo 种子）

---

*最后更新：2026-04-16 深夜。v0/v1/v2 phasing 是建议，待 Ken 拍板第 8 节 4 个决策点。*

---

## kpax-platform-philosophy KPAX 平台定位与商业模式（Ken 2026-04-17 晚拍板）

> **原文件**：无（本节 2026-04-17 晚新增）

**触发**：Ken 2026-04-17 晚在 PRD 讨论中明确否决 cc 之前所有"付费产品"假设。原话为：

> "我不准备产品收费，而是走腾讯模式，未来可以卖这种厉害的 skill，用户接自己的大模型，如果嫌麻烦，可以充值，我们可赚可不赚这个差价。"
>
> "所以这些角色，未来可能能出很多，用户也可以自己建，平台思维，未来我们再去中心化，发币，解决 token=token 的问题，打通算力和币的价值。"
>
> （Ken 对 v0 开发策略补充）"前期完全中心化开发，先验证商业模式。"

此节作为 KPAX 产品定义的**商业模式锚**，防止 cc / cursor / 其他 agent 再把 KPAX 当单一付费产品设计。

### 1. 产品身份：Platform / Marketplace，不是单产品

KPAX 不是"付费决策工具"或"AI 化身聊天产品"，是 **AI skill 化身组合讨论平台** + **skill marketplace 基础设施**。参考系：

- 不对标 ChatGPT / Perplexity（付费 SaaS）
- 不完全对标 Character.AI（单人 AI 陪聊，收订阅费）
- 最接近的类比：**app store + 游戏 UGC 平台 + AI skill 生态的混合体**——有平台 own 的核心功能，有第三方 / 用户 / 开源的内容供给，有多种变现路径

用户角色：**既是消费者，也是创作者**。普通用户召唤化身讨论，有能力的用户 / 开发者 / 第三方可以上架自己做的 skill 供他人使用。

### 2. 收入来源：三层，主产品免费

**层 A：主产品免费**——KPAX 的化身召唤 + 多化身讨论 + 时间博物馆场景 + 基础报告生成，**用户 0 成本使用**。这是入口流量 + 用户养成习惯。

**层 B：Skill Marketplace（v1 启动）**——开发者 / 创作者 / 内容方可以上架付费 skill（精品化身）。示例：
- 某 VC 合伙人把自己思考框架做成 skill（付费订阅 / 按次调用）
- 某心理咨询师把特定流派的方法论做成 skill
- 开源名人 skill（已存在开源生态，如 alchaincyf 的 munger / feynman 系列）保持免费作为流量池，付费 skill 作为长尾变现

KPAX 作为平台**抽成 / 收上架费**，创作者赚主要收入。

**层 C：代币经济（v2 起，发链代币后）**——用户的 KPAX 代币和算力 token 价值直接挂钩，平台通过代币发行机制捕获价值（具体模型待 v2 设计）。

### 3. LLM 成本承担：BYOM 默认，代付可选

**默认路径**：用户自带 API key（Bring Your Own Model）——OpenAI / Anthropic / DeepSeek / 自部署模型。KPAX **不内化这个成本**。

**代付路径**（便利服务）：用户嫌 BYOM 麻烦，可充值让 KPAX 代付 LLM 成本。Ken 原话 "我们可赚可不赚这个差价"——KPAX 不把代付当主要收入源，纯便利增值。

**含义**：
- KPAX 的 margin 压力归零（不像 Perplexity 每次调用烧公司钱）
- 用户消费心智不是"订阅 $20/月"，是"我的 API key 跑了多少钱" + "订了哪些 skill"
- 竞争壁垒从"谁的 LLM 更便宜"转移到"谁的 skill 生态更好"

### 4. 中心化 vs 去中心化：分阶段

| 阶段 | 时期 | 重点 |
|---|---|---|
| **v0** | 当前到 v0 上线 | **完全中心化开发**，先验证"化身平台 + 多化身讨论 + 免费主产品"的商业模式是否成立 |
| **v1** | v0 上线后 | 中心化 + 引入 skill marketplace + BYOM 功能化 |
| **v2+** | 商业模式验证后 | 去中心化 + 发币 + 链上算力/价值结算 |

Ken 明确"前期完全中心化开发"——v0 代码不引入任何链上复杂度（RainbowKit / wagmi / 代币合约 / 链上签名这些 v0 都不做）。但 schema 和字段命名（如 `wallet_address` 代替 `user_id`）从 v0 开始就为去中心化迁移预留。

### 5. "Token = token" 问题的长期命题

Ken 提出的核心技术命题：**用户持有的 KPAX 平台代币 ↔ LLM 消耗的计算 token**，价值应该直接打通，不是 opaque 抽象代币。

v0 / v1 阶段这两个是分离的（平台代币是记账单位，LLM token 是外部 API 资源）。v2 去中心化后：

- 用户持币 = 直接对应 N 次推演 / N 条讨论的权利
- 算力市场的价格发现在链上（LLM 成本的波动自然反映到代币价格）
- 价值捕获机制从"平台定价"变成"市场定价"

这是 Web3 结构性价值，不是 Web2 订阅模式能提供的。Web2 用户依然可用（传统支付接入代付服务），但 Web3 用户才能获得完整价值捕获。

### 6. Platform 架构对 v0 代码的具体要求（摘录 `kpax_api_spec §13`）

v0 虽然完全中心化，但代码和 schema **必须为 platform + 去中心化预留**。具体：

- **`wallet_address`** 全链路替换 `user_id`（§13.4）
- **`skill_source`** 字段加入 `expert_lenses[]`（§13.3，取值 `platform_discipline | platform_skill | user_created | third_party_creator`，v0 只用第一个）
- **`expert_key`** 支持两种格式（`debate_{id}_agent_{aid}` / `skill_{sid}`，v0 只产生前者但 regex 允许两者）
- **`llm_provider_override`** Request 字段（v0 强制 null，v1 启用 BYOM）
- **`token_ledger`** event 分层（`kpax_token_delta` / `llm_cost_usd`，v0 只记后者）
- **Skill followup endpoint `/axl/v1/skill/{skill_id}/ask`** 占位返回 501（v1 启用）

这些预留的**时间成本 v0 额外 +3-4 小时**，但避免 v1 / v2 迁移时改 protocol，值得。

### 7. cc 在此议题上的系统性错误（2026-04-17 晚认错）

cc 作为 PRD owner 在 v1.1 / v1.2 PRD 里一直默认 KPAX 是"付费决策工具"，未主动质问商业模式。直到 Ken 本次明确拍板才修订。同类错误几周内至少三次：

- 2026-04-15：把"消费决策工具"写进 KPAX 定位（应是"通用决策工具"）
- 2026-04-17 午：KPAX 六条硬规则二极管化（条件性立场写成绝对规则）
- 2026-04-17 晚：默认 KPAX 付费产品（应是 platform + 免费主产品 + skill 变现）

**共同根源**：cc 写 PRD 前不主动质问根本假设（商业模式 / 平台身份 / 长期愿景），习惯于"先写 PRD 等 Ken 挑错"。

**纠正措施**（已写入 `memory/feedback_ai_smell_patterns.md` 模式 14）：cc 动 PRD 笔前必先回答 3 个根本问题：
1. 商业模式是什么？（付费 / 免费 / 分成 / BYOM / 广告）
2. 产品身份是什么？（单产品 / platform / 基础设施 / 内容生产）
3. 长期路径是什么？（纯中心化 / Web3 / UGC / 去中心化 / 用户所有权）

三个问题答不上来就问 Ken，不凭假设开写。

### 8. 关联文件

- `projects/knowledge-graph/backend/app/routers/kpax_api_spec.md` §13（v1.3 PRD 正文）
- `notes/design.md` `§kpax-v0-deliberation-room`（v0 前端形态）
- `notes/next.md`（v0 / v1 / v2 任务清单）
- `memory/feedback_ai_smell_patterns.md` 模式 14（cc 写 PRD 前 self-check）

---

## quantification-gap 自进化量化闭环问题（2026-04-17 Lucas 提出）

> **原文件**：无（本节为 2026-04-17 新增，未曾作为独立文件存在）

**触发**：2026-04-17 Lucas 在与 Ken 对话中提出——AXL 的自进化体系（`agent-evolution-free-parameters` 定义的 5 类自由参数 + `seven-layer-memory-design` L7 元进化层）在理论上完整，但**现在没有量化的值**。即："这个答案我们并不知道好不好。所以你怎么知道往哪个方向强化？"

这是自进化的**死穴**，比实验本身的 content 层对照更底层。

### 问题的技术重述

自进化的完整闭环（理论）：

```
自由参数配置 → debate → moderator 输出
                          ↓
                   judge 打分（量化值）
                          ↓
                 根据分数梯度调参数
                          ↓
                   下一次 debate 更强
```

中间 "量化值" 这一块，AXL 现在是空的。现状：

| 环节 | 状态 |
|---|---|
| 五类自由参数（§agent-evolution-free-parameters） | 已完成：写完，理论定义清楚 |
| Judge rubric 定义 | 已完成：`experiments/emergence_decomposition/results/dry_run_20260416_165636/pilot_judge_rubric_v0.1.md`，100 分制 |
| **Scored sample pool（有分数的 debate 样本）** | **未开始：零样本** |
| 人工评分锚点（防 judge 自偏置） | 未开始 |
| Meta-learner（从分数梯度调参） | 未开始：理论都没写 |

Lucas 的观察本质是：**rubric 只是定义了"尺子"，但还没真去量东西**。我们跑了 20+ 场 baseline（15 scaleup + 5 supplement + 3 mini run + 1 meta_01），没有一场被 judge 打过分。"哪个方向强化" 没有数据回答。

### 量化闭环的 5 层构建路径

**A（立刻可做，cc→cursor 分工下 cursor 执行）**：实现 `experiments/emergence_decomposition/judge.py`，用 `pilot_judge_rubric_v0.1.md` 给现有 20+ 场 baseline 打分。建立 scored pool v0。Judge 模型按 spec §4.1 用独立强模型（GPT-5 或 Gemini 2.x）。成本估计：20 场 × 约 $0.5-1（judge 比 debate 便宜得多）≈ $10-20。

**B（pilot 时，gated on A 完成 + rubric 稳定）**：80 场 pilot（baseline + A 组）跑完后全部 judge 打分。**第一次量化对比 "学科标签是否提升质量"**（spec 假设 d 的直接检验）。

**C（持续性任务）**：Ken + cursor 各评 5-10 场（人工锚点），校准 judge 是否跑偏（防 self-preference bias）。见 spec §4.4 人工评分子集。

**D（全量后，Checkpoint 2-4）**：6 组 900 场 judge 打分，得到 5 个自由参数每个维度的对照数据。这是 meta-learner 需要的训练集。

**E（Phase 3，需要独立设计）**：L7 元进化模块真实现——输入自由参数 + 问题特征，输出预期分数；用分数梯度优化参数配置。此步可能需要另开一个实验（例如 `experiments/meta_evolution_v1/`）。

### 对项目的直接影响

1. **不做 A 之前，"自进化" 只是理论叙事**，无法给 Ken / Lucas / 外部审稿人验证
2. **A 的成本低（~$20）、依赖少**（rubric 已有，judge 模型选型已有），应该作为 Checkpoint 1 pilot 的前置动作，**不晚于 pilot 启动**
3. **B 的输出是 AXL 学术价值的第一次量化证据**——baseline vs A 组的 judge 分数差异，是 spec 假设 d（学科标签激发不同推理模式）的直接检验，具备发论文 preliminary finding 的条件
4. **E 是 Phase 3 的真正护城河**——目前所有竞品（含 WisLand）都没有 meta-learner 层。如果做出来且有效，AXL 在此维度上是独一家

### 与现有笔记的关系

- `§agent-evolution-free-parameters` 定义了 5 类参数（fitness / re-rank / diversity 坍缩 / innovation 比例 / decay），但没定义参数调整的**信号来源**。本节补齐：信号来源 = judge 分数梯度
- `§seven-layer-memory-design` L7 元进化层是此闭环的**承载结构**，分数梯度通过 L7 写回参数
- `§remediation-plan-multi-agent` 的 4 个修改点里没有 "量化闭环" 这一项——Lucas 这个观察应作为**第 5 个修改点**补进去
- `pilot_judge_rubric_v0.1.md`（在 experiments/ 下不在 notes/）是 A 步骤的直接输入

### 待决策（2026-04-17，Ken 待拍板）

- A 步骤何时启动？建议：修 monorepo 完成后（cursor 负责）→ 立刻做 A（cursor 实现 judge.py）→ 再启动 pilot
- 人工评分锚点（C）由谁打？Ken + cursor 各一批？还是 Ken 独立？
- Meta-learner（E）是否从 Phase 3 开始纳入研究路线图？

### 引用

- Ken 2026-04-17 原话：
  > "Lucas 提了一个很好的点。我们现在自进化这套体系，其实是没有量化的值的。也就是这个答案我们并不知道好不好。所以你怎么知道往哪个方向强化。"

---

## human-skill-distillation-layer KPAX 化身层 / 个体记忆工程层（2026-04-17 新增）

> **原文件**：无（本节为 2026-04-17 新增，未曾作为独立文件存在）
>
> **触发**：Ken 2026-04-17 敲定 KPAX 的架构本质是 "AXL 多 agent 机制 + 个体记忆工程层"，化身体系（Avatar）从概念升级为产品战略层，需要一篇正式技术笔记，描述这一层做什么、怎么做、和 AXL 怎么分工、与既有三线知识源（§kpax-knowledge-source-architecture）的关系。
>
> **上游**：`KPAX.md`（产品战略） / `notes/design.md §kpax-v0-deliberation-room`（v0 形态） / `notes/radar.md`（Hermes / EvoMap / alchaincyf 等候选工具）

---

### 1. 本章要回答的问题

1. KPAX 在 AXL 之上多的那一层，在做什么
2. 化身（Avatar）是什么，三类化身的技术差异在哪
3. 具体用哪些技术栈（Hermes / EvoMap / alchaincyf skill 生态等）来落这一层
4. 和 AXL 的边界（硬规则 #6）怎么走
5. 和 §kpax-knowledge-source-architecture 定义的三条知识输入线（A/B/C）是什么关系
6. IP / 肖像 / 合法化 / 在世名人 / 争议人物的工程边界
7. v0 / v1 / v2 怎么分阶段做

---

### 2. 架构定位：AXL 是底座，KPAX 在底座上叠加化身层

```
┌─────────────────────────────────────────────────────────────┐
│ AXL（研究平台，独立项目）                                      │
│  - debate_engine（多 agent 辩论编排）                          │
│  - generate_agents / reverse_discovery（动态组 agent）         │
│  - 学科知识：Zep + OpenAlex + 4516 topic 图谱                  │
│  - 七层记忆 + moderator + 自由参数                             │
│  - 服务边界：HTTP API（KPAX 只能从这里进）                     │
└─────────────────────────────────────────────────────────────┘
                         ↑ HTTP only（硬规则 #6）
                         │
┌─────────────────────────────────────────────────────────────┐
│ KPAX（通用决策工具，独立项目）                                  │
│  ├── 问题解析 / 证据注入 / 报告生成 / 代币 / 钱包 / 前端       │
│  └── **化身层（本章主题）**                                    │
│       ├── 化身的**专业知识层**：复用 AXL 的学科知识（HTTP 调）  │
│       ├── 化身的**个人记忆层**：KPAX 自己做（下详述）          │
│       ├── 化身的**演化机制**：KPAX 自己做（下详述）            │
│       └── 化身的**编排机制**：按问题动态组 3/5/7 位化身（奇数，最少 3；+1 mod）│
└─────────────────────────────────────────────────────────────┘
```

**一句话总结**：AXL 提供"多 agent 辩论 + 学科知识"的底座能力；KPAX 在这个底座上，**为每个 agent 加一层"个体记忆"**，让它从"学科化身"升级成"有具体思考框架 / 经验历史的化身"。

---

### 3. 化身的两层技术构成

每一位化身 = **专业知识层** + **个人记忆层**。

| 层 | 内容 | 数据源 | 技术载体 |
|---|---|---|---|
| **专业知识层** | 学科 / 领域的结构化知识（物理公式 / 经济模型 / 心理学流派 / 创业方法论） | AXL 的学科图谱 + 学术论文 + 行业 curated（Line A + B） | AXL 侧 Zep + graphify，KPAX 通过 HTTP 调 AXL 拿到 |
| **个人记忆层** | 具体个体的决策框架 / 判断习惯 / 语言风格 / 历史判断轨迹 | 公开言论 / 著作 / 推文 / 访谈 / 投资备忘录 / 采访 | KPAX 侧：Hermes / EvoMap / Skills 体系 |

**三类化身是"个人记忆层丰俭不同"的同一类机制**：

| 化身类型 | 专业知识层 | 个人记忆层 | 举例 |
|---|---|---|---|
| **学科化身** | 饱满（完整学科知识） | **空 / 占位**（仅有学科常识） | "一位物理学家" / "一位经济学家"（当前 v0 默认） |
| **真人化身** | 饱满（所属学科/领域知识） | **饱满**（从公开材料抽取的个体框架） | 费曼化身 = 物理学科 + 费曼个人记忆 |
| **野生化身** | **看社区给的覆盖度** | **中等**（公开发言抽取） | Reddit 某位长期高质量发言者（经过用户反馈筛选） |

**重要推论**：学科化身不是一种独立形态，而是"个人记忆层为空"的退化情形。v1 可以顺滑把学科化身升级为真人化身（物理化身 → 物理化身 + 费曼个人记忆）。

---

### 4. 技术栈候选（全并列，不押单家）

Ken 2026-04-17 定调：**所有有利的都用，不介入社区内部的立场纠纷**。以下候选平行考察，按实际工程表现取舍：

| 工具 / 生态 | 主要提供什么 | 在化身层里的位置 | 状态 |
|---|---|---|---|
| **Hermes Agent**（NousResearch，MIT） | 三层记忆模式 / SKILLS 系统 / PLUR 共享记忆 / MEMORY.md + USER.md 文件即记忆 | 个人记忆层的基础存储结构 | radar adopt |
| **EvoMap / Evolver** | GEP 基因进化协议 / Scan-Select-Mutate-Validate-Solidify 10 步循环 / reflection 周期 / 三层记忆 | 化身演化机制（化身用久了怎么更新） | radar adopt（2026-04-17） |
| **alchaincyf 13 名人 skill + 女娲（Nuwa）蒸馏工具** | 开源现成的名人 skill 货架 + 自动化蒸馏 pipeline | v1 真人化身初始池 + 从社区文本蒸馏野生化身的工具 | radar track，license 预审通过后 adopt |
| **LuBtc888 汇总的 26 skill 生态** | 市场全景扫描信号 | shopping list 输入 | radar track |
| **Zep Cloud** | 跨会话记忆检索（AXL 侧已在用） | 化身跨会话记住用户历史的存储 | 已在 AXL 层采用 |
| **反蒸馏.skill** | 对 skill 做混淆防抽取 | 不采纳工具本身，作为生态信号读 | radar track |

**选型原则**：
- 每个候选在 KPAX 里都只承担**一到两个子能力**（比如 Hermes 做存储 / EvoMap 做演化 / 女娲做蒸馏），不让任何一家包揽全栈
- 所有采纳项必须能在 KPAX 一侧独立部署，和 AXL 之间仍然只走 HTTP（硬规则 #6 不松动）

---

### 5. 和 §kpax-knowledge-source-architecture 三条线的关系

原 §kpax-knowledge-source-architecture 定义了三条知识输入线（Line A 学术 / Line B 行业 curated / Line C 社区经验），这三条是**群体视角 / 聚合信号**——学者共识、行业公共框架、大众平均经验。

化身层引入的是**第四条输入视角：个体视角**。

| 输入线 | 视角 | 代表证据形态 |
|---|---|---|
| Line A | 学者群体共识 | "劳动经济学的主流文献说中年转行风险高" |
| Line B | 行业公共框架 | "YC 建议 18 个月 runway 再跳" |
| Line C | 大众真实经验平均 | "r/startups 500 个案例里，70% 失败在 12 个月内" |
| **Line D（本章）** | **具体个体的完整决策框架** | "Paul Graham 在同样境况下怎么想 / Musk 会怎么判 / 王阳明的知行合一在这里怎么解" |

**关键区别**：前三条是**证据 / 参考**，化身从中取证；第四条是**另一位参与者进入辩论**——真人化身不是被引用的资料，是**和其他化身在同一场里发言**的对手。巴菲特化身在辩论里会和 CS 化身 argue 起来，但 Line C 的 Reddit 案例只是被引用。

---

### 6. 和 AXL 的边界（硬规则 #6 再申）

化身层全部在 KPAX 侧实现，不污染 AXL：

| 要做的事 | 放哪 | 怎么走 |
|---|---|---|
| 动态组 agent / 辩论编排 / 学科知识 | AXL | KPAX 通过 `axl_client.py` HTTP 调 |
| 化身个人记忆的存储 | **KPAX** | KPAX 侧独立 Zep namespace / SQLite / 文件 |
| 化身蒸馏（把公开材料抽成 skill） | **KPAX** | KPAX 侧独立 pipeline（可调 LLM，但不访问 AXL 数据库） |
| 化身演化（GEP / reflection） | **KPAX** | KPAX 侧独立 meta-learner |
| 化身被召唤进辩论 | **KPAX → AXL** | KPAX 在调 AXL `/debate/run` 时把化身的 `system_prompt + individual_memory` 作为参数传过去，AXL 不需要知道"这是真人化身还是学科化身" |

**AXL 不反向知道化身系统的存在**。AXL 只看到"一组 agent 参数进来，跑辩论，输出结果"，agent 里是学科还是真人化身对 AXL 透明。

---

### 7. IP / 肖像 / 合法化 / 伦理边界

化身涉及真实人物时，边界从工程层就要划清：

#### 7.1 分类处理

| 人物类别 | 使用边界 | 举例 |
|---|---|---|
| **公共历史人物（已故）** | 使用公开出版物、已进入公共领域的文本。不伪造其立场，只基于有文献的发言。 | 柏拉图 / 王阳明 / 费曼（费曼本人已故，但需注意著作权） |
| **在世公众人物** | 只用其**公开发言 / 公开出版物 / 公开演讲 / 已发表访谈**。**不基于未公开私人信息**。所有化身输出必须明确标注"这是基于 XX 公开言论的化身，不代表 XX 本人立场"。 | 巴菲特（股东信 + 公开访谈）/ Musk（公开推特 + 公开演讲）/ Paul Graham（已发表 essay） |
| **争议 / 敏感公共人物** | **分级访问机制**。默认不出现在推荐池，用户需主动召唤；对极度敏感人物（如希特勒）需要多一层警告和学术用途声明。 | 希特勒 / 毛泽东 / 政治敏感人物 |
| **野生专家（社区）** | 只基于其公开发言的 ID 行为特征，**不披露其真实身份**。化身出现时不指名道姓，按匿名 handle 呈现。需在 KPAX 用户协议中声明数据来源。 | Reddit u/xxx 长期高分判断者 |

#### 7.2 通用工程约束

- **Agent 不声称"我是 XX 本人"**：所有化身 system_prompt 强制包含 disclaimer —— "基于 XX 公开言论中展现的决策框架进行推理，不代表 XX 本人立场"
- **所有化身输出附带 evidence_ref**：化身说的每个核心判断，追溯回具体公开来源（哪篇股东信 / 哪条推文 / 哪本书第几章）
- **在世名人用户自行关闭**：用户可在设置里关闭某位在世化身，避免关联风险
- **不同司法辖区的差异**：中国大陆 / 美国 / 欧盟对公众人物引用边界不同，界面按地区调整（v1 后处理）

#### 7.3 合法化的底线

- 不训练 / 不微调基于名人专属文本的模型权重；化身是 **prompt + 记忆文件** 的组合，不是权重级的"克隆"
- 不发布化身的个人记忆文件到公共数据集（防止二次蒸馏）
- 任何来自 alchaincyf 等开源 skill 生态的化身，使用前必须过 license 预审（见 `notes/next.md` 对应任务）

---

### 8. v0 / v1 / v2 phasing

#### v0（3 周内，MVP 给朋友测）
- 化身 = **纯学科化身**（个人记忆层留空 / 占位），每场召唤 3/5/7 位（奇数，最少 3）
- 个人记忆存储结构先搭起来（Hermes 设计模式 + KPAX 侧 Zep namespace），但内容为空
- 技术栈只用 Hermes 存储模式 + AXL 的学科知识（HTTP）
- 目标：验证"化身团辩论 + 结构化报告"的核心闭环，化身身份暂不差异化

#### v1（v0 发布后 1-2 月）
- 引入 **真人化身初始池**：从 alchaincyf 13 名人 skill 里过 license 预审后选 5-7 位，覆盖 5 个领域（商业 / 科技 / 投资 / 哲学思想 / 艺术人文），**中西混合**避免押单一文化维度
- 个人记忆层用 Hermes 的 MEMORY.md / SKILLS 文件结构实装
- 引入化身演化机制（EvoMap GEP 协议的简化版）：每场辩论后 moderator 给每位化身一个简短反馈，进入化身的"反思池"
- 目标：验证"真人化身+学科化身混编"的辩论质量是否比纯学科化身高

#### v2（Ken 上链代币 + dex 上线后）
- 引入 **野生化身识别管线**：结合 autocli / yupi 等社区数据采集工具 + 女娲蒸馏工具，从高活跃社区识别候选野生化身，经用户反馈闭环过滤
- 引入 **用户贡献化身**：用户可以上传自己喜欢的人物资料 + 女娲自动蒸馏，产出 KPAX 内部的 long-tail 化身池（代币激励）
- 完整的化身演化机制（EvoMap 10 步循环 + reflection）
- 目标：让 KPAX 的化身池持续扩张，形成"化身商店 / 时间博物馆"的完整形态

---

### 9. 开放问题（留给 Ken 或未来迭代）

- **v1 的 5 位真人化身具体是谁** → 见 `notes/next.md` v1 化身 shopping list 任务
- **alchaincyf 的 license 能否逐一过关** → 见 `notes/next.md` license 预审任务
- **在世名人的化身用户是否需要签免责条款** → v1 前端 PRD 阶段决定
- **时间博物馆视觉形态 vs v0 原维多利亚书房美学的冲突** → 见 `notes/next.md` P1 @ken 待决
- **化身和 AXL 学科 agent 的 system_prompt 合并规则**（当真人化身被召唤时，AXL 侧应如何接收）→ v1 实装前 @cursor 设计

---

### 10. 关联文件

- `KPAX.md` §一"化身体系"段：对外产品叙事
- `notes/design.md §kpax-v0-deliberation-room`：v0 前端形态
- `notes/radar.md`：Hermes / EvoMap / alchaincyf / 反蒸馏.skill / LuBtc888 26 skill 条目
- `notes/research.md §kpax-knowledge-source-architecture`：三线输入（化身是第 4 条）
- `PROJECT.md §6`：工作分工（cc 战略 / cursor 实现 / codex review）

---

*最后更新：2026-04-17。v0 / v1 / v2 phasing 是规划，非承诺，实际时间线以 Ken 拍板为准。*

---
