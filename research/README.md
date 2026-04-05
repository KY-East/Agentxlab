# Agent X Lab

跨学科研究实验室。研究人工智能、语言哲学、认知科学、社会学、控制论、逻辑学、美学、修辞学、叙事理论及其交叉领域。基础理论研究为根基，工程实践为产出路径，在人文社科与计算科学之间建立系统性对话。

## 定位

个人独立研究机构，采用贝尔实验室的运作理念：基础研究与应用开发并行，理论洞见直接指导技术实现。

研究工作从阅读、梳理和批判性分析各学科的核心文献开始，逐步形成独立的研究问题，最终落地为可运行的系统或可发表的研究成果。

## 研究方向

当前设有六个方向，每个方向维护独立的论文索引、经典笔记、前沿笔记和开放问题。未来将根据研究进展新增或拆分方向。

| 方向 | 涉及学科 | 覆盖规模 |
|------|----------|----------|
| [语言与意义](research/language-and-meaning/) | **哲学**: Philosophy of Language · **语言学**: Pragmatics, Semantics, Semiotics · **文学研究**: Narratology, Cognitive Poetics, Russian Formalism · **修辞学**: Rhetoric, Argumentation Theory · **计算机科学**: Natural Language Processing | 经典 20+，前沿 24+ |
| [思维与创造力](research/thinking-and-creativity/) | **心理学**: Cognitive Psychology, Psychology of Creativity · **哲学**: Aesthetics (Kant, Dewey) · **计算机科学**: Computational Creativity · **认知科学**: Embodied Cognition, Dual Process Theory | 经典 10+，前沿 5+ |
| [主体性与意向性](research/subjectivity-and-intentionality/) | **哲学**: Philosophy of Mind, Phenomenology (Husserl, Heidegger, Merleau-Ponty) · **心理学**: Personality Psychology (Big Five), Narrative Identity · **计算机科学**: AI Alignment | 经典 16+，前沿 12+ |
| [社会性与语境](research/sociality-and-context/) | **社会学**: Microsociology (Goffman), Sociology of Knowledge (Berger & Luckmann), Ethnomethodology (Garfinkel) · **语言学**: Sociolinguistics (Labov, Bernstein) · **STS**: Actor-Network Theory (Latour), SCOT | 经典 9+，前沿 6+ |
| [系统与架构](research/systems-and-architecture/) | **控制论**: Cybernetics (Wiener, Ashby, Beer), Second-Order Cybernetics (von Foerster) · **计算机科学**: Multi-Agent Systems, RLHF / Reward Modeling, Mechanistic Interpretability · **认知科学**: Society of Mind (Minsky) | 经典 9+，前沿 14+ |
| [形式基础](research/formal-foundations/) | **数学**: Mathematical Logic (Gödel, Tarski), Computability Theory (Turing, Church) · **电气工程**: Information Theory (Shannon) · **计算机科学**: LLM Reasoning Evaluation, Model Collapse Theory | 经典 10+，前沿 7+ |

跨方向的交叉分析见 [research/synthesis/](research/synthesis/)。

## 仓库结构

```
research/                    研究方向（每个方向含 papers.md / classics.md / frontier.md / pdfs/）
  synthesis/                 六方向交叉综合（交叉节点 / 论争 / 路线图 / 概念图）
notes/
  agenda/                    按期管理的研究课题
  journal/                   研究日志
  ideas/                     灵感与种子
projects/                    从研究衍生的工程项目
```

完整的目录规范、命名规则和操作流程见 [STRUCTURE.md](STRUCTURE.md)。

## 理论覆盖

完整的学科谱系、学科 × 方向交叉矩阵、学者 × 学科归属索引见 [research/disciplines.md](research/disciplines.md)。

### 经典文献（71+ 部）

涵盖从 Frege（1892）到 Stockwell（2002）的完整理论谱系。按学科门类归属如下：

**Philosophy（哲学）**
- *Philosophy of Language*：Frege, Wittgenstein (PI), Austin, Grice, Searle (Speech Acts), Kripke (Naming and Necessity)
- *Philosophy of Mind*：Brentano, Searle (Chinese Room), Nagel, Dennett, Chalmers, Putnam, Fodor
- *Phenomenology*：Husserl, Heidegger, Merleau-Ponty, Dreyfus
- *Aesthetics*：Kant (Critique of Judgment), Dewey (Art as Experience), Goodman (Languages of Art)
- *Logic*：Frege (Begriffsschrift), Wittgenstein (Tractatus), Kripke (Modal Logic)

**Linguistics（语言学）**
- *Semiotics*：Saussure (structural linguistics), Peirce (triadic sign theory)
- *Pragmatics*：Grice (implicature), Sperber & Wilson (Relevance Theory), Stalnaker (common ground)
- *Sociolinguistics*：Labov (social stratification of language), Bernstein (codes)
- *Cognitive Linguistics*：Lakoff & Johnson (conceptual metaphor)

**Literary Studies（文学研究）**
- *Russian Formalism*：Shklovsky (defamiliarization)
- *Structuralist Narratology*：Genette (narrative discourse), Jakobson (poetic function)
- *Dialogism*：Bakhtin (polyphony, heteroglossia)
- *Cognitive Poetics*：Stockwell, Tsur

**Rhetoric（修辞学）**
- *Classical Rhetoric*：Aristotle (logos / ethos / pathos)
- *New Rhetoric / Argumentation Theory*：Perelman & Olbrechts-Tyteca, Toulmin

**Psychology（心理学）**
- *Cognitive Psychology*：Kahneman (dual process theory)
- *Psychology of Creativity*：Boden, Koestler, Csikszentmihalyi (flow, systems model)
- *Personality Psychology*：Allport (trait theory), Goldberg (Big Five)
- *Narrative Psychology*：Bruner (narrative thinking), McAdams (life story model), Ricoeur (narrative identity)

**Sociology（社会学）**
- *Microsociology / Symbolic Interactionism*：Goffman (dramaturgical approach)
- *Sociology of Knowledge*：Berger & Luckmann (social construction of reality)
- *Ethnomethodology*：Garfinkel
- *Field Theory*：Bourdieu (habitus, cultural capital, field)
- *Science and Technology Studies (STS)*：Latour (ANT), Bijker / Hughes / Pinch (SCOT), Haraway (cyborg theory)

**Cybernetics & Systems Theory（控制论与系统论）**
- *First-Order Cybernetics*：Wiener, Ashby (requisite variety, ultrastability)
- *Second-Order Cybernetics*：von Foerster
- *Organizational Cybernetics*：Beer (Viable System Model)

**Computer Science（计算机科学）**
- *Artificial Intelligence*：Minsky (Society of Mind), Brooks (subsumption architecture), Newell & Simon (GPS)
- *Design Science*：Simon (Sciences of the Artificial, bounded rationality)

**Mathematics（数学）**
- *Mathematical Logic*：Gödel (incompleteness), Tarski (semantic truth)
- *Computability Theory*：Turing (Turing machine, halting problem), Church (lambda calculus)

**Electrical Engineering（电气工程）**
- *Information Theory*：Shannon (entropy, channel capacity), Shannon & Weaver

### 前沿研究（65+ 篇，2024-2026）

覆盖 AI 语言特征、符号接地、语用推理、RLHF/对齐、模型趋同、机械可解释性、心理语言学、数字孪生、偏好建模、计算创造力、AI 社会性等交叉领域。

## 研究原则

- **第一性原理**：所有研究问题追溯至学科基本假设层面，拒绝未经审查的共识。
- **理论与实践闭环**：文献研究服务于问题理解，问题理解服务于系统构建，系统构建反过来验证和修正理论。
- **学科服从问题**：方向划分是组织手段，问题跨越多个方向时以问题本身为优先。
- **唯一事实源**：任何数据、配置、定义在项目中只存在一份权威来源。
- **原子化推进**：每一步变更自包含、可追溯、可回滚。
