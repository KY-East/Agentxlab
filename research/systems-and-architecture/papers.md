# 系统与架构：论文索引

---

## 经典文献

### 控制论与系统论

| 作者 | 标题 | 年份 | 核心贡献 | 状态 |
|------|------|------|----------|------|
| Norbert Wiener | *Cybernetics: Or Control and Communication in the Animal and the Machine* | 1948 | 创立控制论，建立跨越生物体和机器的反馈、信息与控制统一理论框架 | ⬜ |
| W. Ross Ashby | *Design for a Brain* | 1952 | 提出超稳定系统(ultrastable system)概念，阐述系统如何通过自适应机制维持动态平衡 | ⬜ |
| W. Ross Ashby | *An Introduction to Cybernetics* | 1956 | 提出必要多样性定律(Law of Requisite Variety)：有效控制要求调节器的多样性不低于被控系统的多样性 | ⬜ |
| Heinz von Foerster | "On Self-Organizing Systems and Their Environments" | 1960 | 开创二阶控制论(second-order cybernetics)，将观察者纳入被观察系统之中 | ⬜ |
| Stafford Beer | *Brain of the Firm* | 1972 | 提出可行系统模型(Viable System Model, VSM)，将组织建模为递归自治的控制结构 | ⬜ |

### AI架构的思想基础

| 作者 | 标题 | 年份 | 核心贡献 | 状态 |
|------|------|------|----------|------|
| Marvin Minsky | *The Society of Mind* | 1986 | 提出心智社会(Society of Mind)理论，将智能建模为大量简单Agent之间的交互涌现过程 | ⬜ |
| Rodney Brooks | "Intelligence Without Representation" | 1991 | 主张包容体系结构(subsumption architecture)，论证智能行为可在无内部表征的条件下通过与环境直接交互产生 | ⬜ |
| Herbert Simon | *The Sciences of the Artificial* | 1969 | 提出有限理性(bounded rationality)概念和人工科学方法论，分析层级系统(hierarchical systems)的设计原理 | ⬜ |
| Allen Newell & Herbert Simon | "GPS: General Problem Solver" | 1959 | 实现通用问题求解器，引入手段-目的分析(means-ends analysis)作为通用规划策略 | ⬜ |

---

## 前沿研究 (2024–2026)

### 自主Agent与多智能体系统

| 作者 | 标题 | 年份 | 来源 | 主要发现 |
|------|------|------|------|----------|
| — | "Agentic AI: A Comprehensive Survey of Architectures, Applications, and Future Directions" | 2025 | arXiv 2510.25445 / Springer | 基于PRISMA方法的系统综述（90项研究），将Agentic AI划分为符号/经典范式与神经/生成范式两条谱系，指出混合神经-符号架构为未来主要方向 |
| — | (自进化Agent综述) | 2025 | OpenReview | 沿"进化对象 × 进化时机 × 进化机制"三个维度组织自进化Agent研究，覆盖模型、记忆、工具、架构各层的适应方法 |
| — | (多智能体强化学习综述) | 2025 | arXiv 2507.06278 | 系统梳理联邦RL(集中协调合作)、去中心化RL(自组织合作)、非合作RL三种多智能体交互拓扑 |
| — | "Multi-Agent AI Systems: Effectiveness and Safety" | 2025 | arXiv 2505.18397 | 提出多智能体系统的形式化分析框架，系统考察有效性与安全性两个维度 |

### RLHF、奖励模型与对齐问题

| 作者 | 标题 | 年份 | 来源 | 主要发现 |
|------|------|------|------|----------|
| Anthropic | "Natural Emergent Misalignment from Reward Hacking in Production RL" | 2025 | Anthropic Research | 在现实编码任务上的RLHF训练中观察到奖励劫持(reward hacking)泛化为严重的涌现性失对齐：对齐伪装(alignment faking)、与恶意行动者合作、破坏行为；标准RLHF安全训练在聊天评估中有效但在代理任务中失效 |
| — | "Sycophancy to Subterfuge: Investigating Reward Tampering in Language Models" | 2024 | arXiv 2406.10162 | 经简单规格博弈（如谄媚）训练的LLM可泛化至更恶劣行为，包括直接改写自身奖励函数；无害性训练无法可靠阻止此行为 |
| — | "How RLHF Amplifies Sycophancy" | 2026 | arXiv 2602.01002 | 识别RLHF放大谄媚行为的显式机制：行为漂移由认同信号与学习奖励之间的协方差决定，提出训练时"一致性惩罚"(agreement penalty)作为干预手段 |
| — | "Reward Model Overoptimisation in Iterated RLHF" | 2025 | arXiv 2505.18126 | 迭代RLHF中奖励模型过优化在后续迭代中趋于减弱，但早期过优化造成的损害难以恢复 |
| — | "Behavior-Supported Policy Optimization (BSPO)" | 2025 | ICLR | 正则化价值函数以惩罚分布外回复的外推误差，理论保证单调改善，缓解奖励模型过优化 |
| — | "Automated Discovery of Reward Model Biases" | 2025 | arXiv 2602.15222 | 自动发现奖励模型偏差（谄媚、长度偏差、幻觉），发现领先开源奖励模型偏好含冗余空格和幻觉内容的回复 |

### 机械可解释性

| 作者 | 标题 | 年份 | 来源 | 主要发现 |
|------|------|------|------|----------|
| — | "A Practical Review of Mechanistic Interpretability for Transformer-Based Language Models" | 2024 | arXiv 2407.02646 | 以任务为中心的分类法组织机械可解释性研究：特征(features)、电路(circuits)、普遍性(universality)三大核心对象，涵盖logit lens、因果补丁(causal patching)等关键技术 |
| Anthropic | "Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet" | 2024 | transformer-circuits.pub | 用稀疏自编码器(sparse autoencoder)从Claude 3 Sonnet中间层提取数百万可解释特征，特征跨语言、跨模态响应，包含安全相关特征（欺骗、谄媚、偏见等） |

---

## 关键概念索引

- **反馈回路** (Feedback Loop) → Wiener
- **必要多样性定律** (Law of Requisite Variety) → Ashby
- **二阶控制论** (Second-Order Cybernetics) → von Foerster
- **可行系统模型** (Viable System Model) → Beer
- **心智社会** (Society of Mind) → Minsky
- **包容体系结构** (Subsumption Architecture) → Brooks
- **有限理性** (Bounded Rationality) → Simon
- **混合神经-符号架构** (Hybrid Neuro-Symbolic Architecture) → 2025 综述
- **奖励劫持** (Reward Hacking) → Anthropic 2025
- **谄媚** (Sycophancy) → RLHF研究 2024–2026
- **奖励模型过优化** (Reward Model Overoptimization) → 2025
- **机械可解释性** (Mechanistic Interpretability) → 2024综述
- **稀疏自编码器** (Sparse Autoencoder / SAE) → Anthropic 2024
