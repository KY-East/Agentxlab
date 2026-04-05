# 形式基础：论文索引

---

## 经典文献

### 逻辑与可计算性

| 作者 | 标题 | 年份 | 核心贡献 | 状态 |
|------|------|------|----------|------|
| Kurt Gödel | "Über formal unentscheidbare Sätze" (论形式不可判定命题) | 1931 | 证明不完备性定理(Incompleteness Theorems)：任何包含初等算术的一致形式系统必然存在不可判定命题 | ⬜ |
| Alan Turing | "On Computable Numbers, with an Application to the Entscheidungsproblem" | 1936 | 定义图灵机模型，建立可计算性理论，证明停机问题不可判定 | ⬜ |
| Alonzo Church | "An Unsolvable Problem of Elementary Number Theory" | 1936 | 发展Lambda演算，独立证明判定问题(Entscheidungsproblem)的不可解性，与Turing结果共同构成Church-Turing论题 | ⬜ |
| Alfred Tarski | "The Concept of Truth in Formalized Languages" | 1933 | 建立形式语言中语义真理的严格定义，奠定模型论语义学基础 | ⬜ |

### 信息论

| 作者 | 标题 | 年份 | 核心贡献 | 状态 |
|------|------|------|----------|------|
| Claude Shannon | "A Mathematical Theory of Communication" | 1948 | 创立信息论，定义信息熵(information entropy)、信道容量(channel capacity)，建立编码定理 | ⬜ |
| Claude Shannon & Warren Weaver | *The Mathematical Theory of Communication* | 1949 | 在Shannon信息论基础上增加Weaver对语义层(semantic level)和效果层(effectiveness level)的讨论 | ⬜ |

### 逻辑哲学

| 作者 | 标题 | 年份 | 核心贡献 | 状态 |
|------|------|------|----------|------|
| Ludwig Wittgenstein | *Tractatus Logico-Philosophicus* | 1921 | 提出逻辑图像论(picture theory of language)，主张命题是现实的逻辑图像；早期Wittgenstein立场，与后期PI形成对照 | ⬜ |
| Gottlob Frege | *Begriffsschrift* (概念文字) | 1879 | 发明现代谓词逻辑(predicate logic)的形式记法，确立形式化推理的出发点 | ⬜ |
| Saul Kripke | "Semantical Considerations on Modal Logic" | 1963 | 建立可能世界语义学(possible worlds semantics)，为模态逻辑提供标准模型论 | ⬜ |

---

## 前沿研究 (2024–2026)

### LLM推理能力的形式化评估

| 作者 | 标题 | 年份 | 来源 | 主要发现 |
|------|------|------|------|----------|
| — | "ZebraLogic: On the Scaling Limits of LLMs for Logical Reasoning" | 2025 | ICML (MLR Press) | 提出"复杂度诅咒"(curse of complexity)概念：LLM在逻辑推理任务上的准确率随问题复杂度增长而急剧下降，且扩大模型规模和推理时计算量均无法有效缓解 |
| — | (LLM逻辑推理能力综合评估) | 2025 | arXiv 2502.09100 | 系统评估LLM在演绎、归纳、溯因三类推理上的表现，指出现有基准评测多数仅关注最终答案正确率而忽略推理过程本身的合理性 |
| — | (逻辑问答与逻辑一致性分析) | 2025 | EMNLP Findings | 识别LLM推理的两类系统性缺陷：复杂逻辑问题中的答案错误，以及相关问题之间的推理自相矛盾 |
| — | (神经-符号整合方法综述) | 2025 | IJCAI | 综述Best-of-N采样、回溯机制、自验证提示、外部逻辑求解器等增强推理能力的方法，评估结果表明这些方法对根本性限制的改善有限 |

### 模型坍缩与数据生态

| 作者 | 标题 | 年份 | 来源 | 主要发现 |
|------|------|------|------|----------|
| Shumailov et al. | "AI models collapse when trained on recursively generated data" | 2024 | Nature | 严格证明递归训练于模型生成数据导致不可逆的模型坍缩(model collapse)：分布尾部率先消失，学习行为收敛至低方差点估计；现象跨越LLM、VAE、GMM等多种模型架构 |
| — | (LLM知识坍缩与认知多样性) | 2025 | arXiv 2510.04226 | 测量LLM输出的认知多样性(epistemic diversity)，发现几乎所有模型低于基础网络搜索结果的多样性水平，模型规模与多样性呈负相关，检索增强生成(RAG)可部分缓解 |
| — | "LLM Output Homogenization is Task Dependent" | 2025 | arXiv 2509.21267 | 论证输出同质化的问题严重程度因任务而异：客观数学任务的答案一致性有益，但创意写作任务要求叙事结构、视角等多维变异，仅词汇多样性不足以衡量 |

---

## 关键概念索引

- **不完备性定理** (Incompleteness Theorems) → Gödel
- **图灵机 / 可计算性** (Turing Machine / Computability) → Turing
- **Church-Turing论题** (Church-Turing Thesis) → Church, Turing
- **信息熵** (Information Entropy) → Shannon
- **逻辑图像论** (Picture Theory of Language) → 早期 Wittgenstein
- **可能世界语义学** (Possible Worlds Semantics) → Kripke
- **复杂度诅咒** (Curse of Complexity) → ZebraLogic 2025
- **模型坍缩** (Model Collapse) → Shumailov et al. 2024
- **认知多样性** (Epistemic Diversity) → 2025
- **递归训练退化** (Recursive Training Degradation) → Nature 2024
