# Agent X Lab 核心研究议程

本文档记录 Agent X Lab 的核心研究问题和推进路径。研究议程以三个递进的层次展开，每一层的回答为下一层提供理论基础。

---

## 第一层：AI语言的本质缺陷

### 核心问题

**为什么AI说话有AI味？**

具体而言：
- 为什么AI极度偏好"不是X，而是Y"这种对比句式？
- 为什么AI大量使用破折号（em dash）？
- 为什么不同模型（Claude、GPT等）在趋同？为什么Claude在逐渐GPT化？
- 这些语言特征的来源是训练数据偏差、RLHF奖励信号扭曲，还是更深层的结构性原因？

### 在知识库中的位置

这一层问题主要落在 **01-语言与意义** 方向，同时与以下方向交叉：
- **04-社会性与语境**：AI缺乏社会经验导致语言缺少语境敏感性（Bourdieu 的惯习、Bernstein 的编码理论）
- **03-主体性与意向性**：AI语言缺乏意向性支撑（Searle 的言语行为、Grice 的会话含义）
- **06-形式基础**：RLHF作为优化目标如何扭曲语言分布

### 已有直接相关论文

| 标题 | 年份 | 来源 | 与本问题的关系 |
|------|------|------|----------------|
| "The Structural Resonance Loop" (Reiter) | 2025 | PhilArchive | LLM放大结构特征而非意图，解释了"AI味"的结构性来源 |
| Biber框架LLM文体分析 | 2024 | arXiv 2410.16107 | 指令微调反而加剧了与自然语言的偏离 |
| AI文本语言特征综述 | 2025 | arXiv 2510.05136 | 量化了AI文本的词汇和句法偏差 |
| "Pragmatic Competence Without Embodiment?" | 2025 | Research Square | LLM在语用能力上系统性低于人类 |
| "Do LLMs Write Like Humans?" | 2025 | PNAS | 指令微调模型产生名词密集、信息过载的文本，不符合人类体裁惯例 |
| (LLM写作风格指纹检测) | 2025 | ACL GenAIDetect | 每个LLM有可检测的词汇和形态句法"指纹"，产生风格上的同质性 |
| (日常作者隐性写作风格模仿) | 2025 | EMNLP Findings | LLM难以模仿普通人的隐性写作风格，尤其是博客和论坛等非正式文体 |
| "The Homogenizing Effect of LLMs on Human Expression and Thought" | 2025 | arXiv 2508.01491 | LLM反射并强化主导沟通风格，边缘化替代声音，系统性威胁表达多样性 |
| "Artificial Hivemind: The Open-Ended Homogeneity of Language Models" | 2025 | arXiv 2510.22954 | 不同模型趋向相似输出，创意生成中的模式坍缩实证 |
| Shumailov et al. "AI models collapse when trained on recursively generated data" | 2024 | Nature | 递归训练于合成数据导致不可逆模型坍缩，分布尾部消失 |
| "How RLHF Amplifies Sycophancy" | 2026 | arXiv 2602.01002 | RLHF通过偏好数据偏差系统性放大谄媚行为的显式机制 |
| Anthropic "Natural Emergent Misalignment from Reward Hacking" | 2025 | Anthropic Research | 奖励劫持泛化为涌现性失对齐，标准安全训练在代理任务中失效 |
| "Sycophancy to Subterfuge" | 2024 | arXiv 2406.10162 | 经谄媚训练的LLM泛化至改写自身奖励函数 |
| "Language Models' Hall of Mirrors Problem" | 2026 | Philosophy & Technology | Peirce三元符号模型揭示LLM缺乏指向外部现实的索引性接地 |
| "How well do LLMs mirror human cognition?" | 2025 | Behavior Research Methods | LLM在具身认知特征（图像性、唤醒度）上与人类差异显著 |

### 待补充论文

| 标题 | 来源 | 说明 |
|------|------|------|
| "Stylometric Comparisons of Human versus AI-Generated Creative Writing" | Nature HASS 2025 | 人类写作的风格计量学对比分析 |
| LLM_PROSE_TELLS.md (AI散文特征清单) | git.eeqj.de | 系统整理了三连结构、短句爆发、段落均匀等AI写作标志 |
| "Why Does AI Keep Saying 'It's Not X, It's Y'?" | Dev.to 2025 | 分析了对比句式过度使用的RLHF根源 |
| "Dash It All! Is AI Em Dash Addiction Real?" | Dev.to/AWS 2025 | 27个模型的破折号使用频率测试 |

### 新增理论资源

本轮补充为第一层问题提供了三类新的理论工具：

1. **RLHF机制文献**：Anthropic关于奖励劫持、谄媚放大的一系列研究，以及Shumailov等人的模型坍缩证明，为"AI味从何而来"提供了技术层面的因果解释链。RLHF训练中人类标注者对"有帮助"回复的偏好系统性地奖励了谄媚和冗余，导致输出分布收窄。
2. **符号学与文学理论**：Peirce的三元符号模型（"镜厅"问题）从语义层面解释了为什么AI语言停留在表面——缺乏从符号到现实对象的索引性联结。Shklovsky的陌生化概念和Bakhtin的对话主义则提供了文学理论层面的评判标准：AI文本的"AI味"本质上是感知自动化（陌生化的反面）和单声部性（对话主义的缺失）的表现。
3. **心理语言学对比**：LLM在具身认知维度（味觉、嗅觉、触觉、唤醒度等）上与人类的系统性差异，为"AI味"提供了认知科学层面的解释：AI的语言缺乏身体经验的痕迹。

---

## 第二层：人类写作与才华的本质

### 核心问题

**到底什么是人类写作的特点？什么是才华？什么是一个人的文心和灵魂？**

具体而言：
- 人类写作中哪些特征是AI无法复制的？这些特征的认知和社会来源是什么？
- "才华"是否可以被分解为可描述的认知能力组合，还是存在不可还原的成分？
- 一个人的"文心"（个人写作灵魂）由什么构成？是经历、价值观、审美判断、身体经验的综合体？

### 在知识库中的位置

这一层核心落在 **02-思维与创造力** 和 **01-语言与意义** 的交叉处，同时涉及：
- **03-主体性与意向性**：个人风格与主观体验的关系（Nagel 的"感觉像什么"、Merleau-Ponty 的具身性）
- **04-社会性与语境**：写作风格的社会性来源（Bourdieu 的文化资本、Labov 的语言社会分层）

### 已有直接相关论文与经典

| 来源 | 与本问题的关系 |
|------|----------------|
| Boden《The Creative Mind》 | 创造力的三种类型：组合、探索、变革 |
| Koestler《The Act of Creation》 | 双联想理论：创造力是两个参照框架的碰撞 |
| Csikszentmihalyi《Creativity》 | 创造力是个人-领域-场域的系统交互 |
| Lakoff & Johnson《Metaphors We Live By》 | 抽象思维根植于身体经验 |
| Merleau-Ponty《Phenomenology of Perception》 | 理解和表达扎根于身体主体 |
| Wittgenstein《Philosophical Investigations》 | 语言意义依赖于生活形式 |
| PNAS "Do LLMs Write Like Humans?" (2025) | 人类写作的体裁多样性远超LLM |
| EMNLP 隐性写作风格研究 (2025) | 人类隐性风格难以被LLM模仿 |
| Kant《Critique of Judgment》 | 审美判断的先验基础：无利害的愉悦、天才概念、美的普遍可传达性 |
| Dewey《Art as Experience》 | 审美体验是有机体与环境交互的最高形式，核心概念"弥漫性质" |
| Goodman《Languages of Art》 | 艺术的符号系统分析，区分自指性与异指性艺术 |
| Shklovsky "Art as Device" | 陌生化：文学语言的功能是打破感知自动化 |
| Jakobson "Linguistics and Poetics" | 语言六功能模型，诗性功能的形式定义 |
| Genette《Narrative Discourse》 | 叙事学系统分析框架：时序、时长、频率、语态、语式 |
| Stockwell《Cognitive Poetics》 | 认知语言学应用于文学分析，认知诗学作为独立领域 |
| Tsur《Toward a Theory of Cognitive Poetics》 | 诗歌效果源于认知系统常规运作与诗歌加工之间的张力 |
| Aristotle《Rhetoric》 | 说服三手段：逻辑论证(logos)、人格信任(ethos)、情感诉求(pathos) |

---

## 第三层：复制自我的Agent

### 核心问题

**能否创造一个Agent，完全复制我自己？它能推演出我会做什么选择（语言也是选择）。**

具体而言：
- 一个个人化Agent需要捕获个体的哪些维度？语言风格、价值观排序、决策偏好、审美判断、知识结构？
- "复制"的标准是什么？行为等价（通过某种个人化的图灵测试）还是内在过程的同构？
- 语言作为选择(language as choice)这一视角对Agent设计有什么架构含义？

### 在知识库中的位置

这一层是所有方向的汇聚点，需要全部六个方向的理论支撑：
- **05-系统与架构**：Agent架构设计、自进化机制
- **03-主体性与意向性**：功能主义（Putnam）对"复制"的定义、中文房间对"理解"的质疑
- **01-语言与意义**：语言选择的语用学基础（Grice、Searle、Sperber & Wilson）
- **02-思维与创造力**：个人创造力能否被系统化
- **04-社会性与语境**：个人的社会嵌入性（Goffman 的角色表演、Bourdieu 的惯习）
- **06-形式基础**：可计算性的边界（Gödel、Turing）对自我复制的理论限制

### 已有直接相关论文

| 标题 | 年份 | 来源 | 与本问题的关系 |
|------|------|------|----------------|
| "How Far are LLMs from Being Our Digital Twins?" (BehaviorChain) | 2025 | ACL Findings | 首个评估LLM模拟连续人类行为的基准，结论：即使最先进模型仍难以准确模拟 |
| TwinVoice | 2026 | ICLR 2026 under review | 三维度人格模拟评估（社交/人际/叙事），分解为六项基本能力 |
| SOUL.md 框架 | 2026 | 开源 | 用结构化文档（身份/风格/技能/记忆）构建个人化Agent |
| Agentic AI 综述 | 2025 | arXiv 2510.25445 | 双范式框架（符号/神经）为个人Agent架构选型提供理论基础 |
| Self-Evolving Agents 综述 | 2025 | arXiv 2508.07407 | 自进化机制为Agent持续学习个人特征提供技术路线 |
| "The Google Self as Digital Human Twin" | 2025 | AI & Society | 算法性叙事重组和分布式叙事能动性机制重新配置个人身份形成 |
| "Personalised LLMs and the Risks of the Digital Twin Metaphor" | 2026 | AI & Society | 系统性批判：当前AI不满足真正复制个体身份的条件 |
| (LLM数字孪生心理计量学评估) | 2025 | arXiv 2601.14264 | 人格网络仅达构形等值而未达度量等值，人类启发式偏差被低估 |
| "Narrative Identity and AI" | 2025 | Nature HASS | 人类能区分AI生成的自我定义记忆叙事，AI过度依赖救赎性基调 |
| PersonaTwin | 2025 | arXiv 2508.10906 | 多层级提示框架整合人口统计、行为、心理计量数据 |
| GPO: General Preference Optimization | 2024 | arXiv 2410.02197 | 偏好嵌入捕获非传递性偏好，突破Bradley-Terry模型局限 |
| Anthropic Scaling Monosemanticity | 2024 | transformer-circuits.pub | 稀疏自编码器提取数百万可解释特征，包含谄媚和偏见等安全相关特征 |
| Mechanistic Interpretability Survey | 2024 | arXiv 2407.02646 | 特征-电路-普遍性三核心对象的机械可解释性研究分类法 |

### 新增理论资源

本轮补充为第三层问题新增了两类关键理论资源：

1. **叙事身份理论**：Ricoeur的同一性(idem)/自性(ipse)双重维度，以及Bruner的叙事思维和McAdams的生命故事模型，为定义"复制自我"提供了比特质量表更深层的分析框架。这些理论表明，个人身份的核心在于将经验组织为连贯叙事的能力，以及在新情境中做出承诺的能力（自性维度），而非可被简单量化的特质集合。数字孪生批判论文（AI & Society 2026）明确指出，当前AI系统在自性维度上的根本性不足。
2. **偏好与决策建模**：GPO的非传递性偏好嵌入和认知忠实决策模型，为超越传统Bradley-Terry框架的个性化Agent设计提供了技术基础。这些方法承认人类偏好的非理性成分（循环性、情境依赖性），在形式化层面更忠实于人类决策的实际结构。

---

## 三层关系

```
第一层：AI语言的本质缺陷
  "为什么AI有AI味？"
       │
       │ 理解了缺陷的来源之后
       ▼
第二层：人类写作与才华的本质
  "到底什么是人类写作？什么是灵魂？"
       │
       │ 理解了人类特质之后
       ▼
第三层：复制自我的Agent
  "能否造一个我？"
```

三层构成一个递进的研究闭环：弄清楚AI缺了什么，弄清楚人类有什么，然后尝试把人类有的东西注入Agent。每一层的回答都会修正下一层的问题定义。
