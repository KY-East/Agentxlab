# 02 思维与创造力 — 前沿论文摘要

本文档基于已下载论文全文，提取核心论点、原文金句与通俗解读。

---

## Artificial Creativity: Can There Be Creativity Without Cognition? (Da Pelo, 2025)
**来源**: AI & SOCIETY (Springer) | **作者**: Matteo Da Pelo

### 核心论点

本文从一个此前被忽视的基础性前提出发：当代生成式 AI 系统（LLM 和 GMI）是非认知的。这一判断通过"最小认知网格"（Minimal Cognitive Grid, MCG）建立——MCG 是一个用于判定系统是否具备认知属性的诊断框架，其判据包括具身性、生物基础、感知运动循环和现象性体验等。由于 LLM 和图像生成模型缺乏这些基本的认知属性，它们在本体论层面上不可被归类为认知系统。

在确立了这一前提之后，作者进行了两项关键分析。首先，他利用 Wallas-Jaoui 创造过程模型（准备、孵化、启示、验证）将人类创造过程与 AI 生成过程进行对比，发现 AI 系统在功能层面上可以复制创造过程的各个阶段，但每一阶段都以机械化、非认知的方式实现。其次，尽管 AI 输出可以满足创造力的标准定义（新颖性和有用性），但它们缺乏意向性（intentionality）和真实性（authenticity）。

基于上述分析，作者提出了人工创造力的最小定义：一种非认知的、非意向的、非真实的生成机制。这是文献中首次以正面方式（而非通过与人类创造力的排除性对比）定义人工创造力。

### 原文金句

> "Generative AI systems, such as LLMs and GMIs, are non-cognitive. This distinction is established through the application of the Minimal Cognitive Grid."
>
> 生成式 AI 系统（如大语言模型和图像生成模型）是非认知的。这一区分通过最小认知网格的应用得以建立。

> "Although AI systems can replicate the stages of the creative process, they do so in a mechanistic, non-cognitive fashion."
>
> 虽然 AI 系统能够复制创造过程的各个阶段，但它们是以机械化、非认知的方式实现的。

> "This is the first attempt to define the concept directly, rather than by exclusion."
>
> 这是首次以正面方式直接定义人工创造力这一概念，而非通过排除法来界定。

### 关键概念

- **最小认知网格** (MCG): 用于判定系统是否具备认知属性的诊断框架，判据包括具身性、生物基础和现象性体验
- **Wallas-Jaoui 创造过程模型**: 将创造过程分解为准备、孵化、启示和验证四个阶段，作为与 AI 过程对比的基准
- **人工创造力的最小定义**: 非认知的、非意向的、非真实的生成机制——首个正面定义

### 与本方向的关联

本文为"思维与创造力"方向奠定了哲学基础。它明确界定了人类创造力与人工创造力之间的本体论边界，同时避免了两个极端：既不因 AI 产出的新颖性而将其等同于人类创造力，也不因其缺乏认知属性而完全否认其"创造性"。这种分层处理为后续研究提供了概念上的清晰度。

### 通俗理解

想象一台自动作曲机器。你输入"写一段悲伤的钢琴曲"，它就能生成一段旋律，这段旋律甚至可能让你流泪。从结果来看，它的"作品"符合创造力的基本标准——新颖且有用。但这台机器在"创作"时经历了什么？答案是：什么也没经历。它没有悲伤的记忆，没有想要表达的冲动，也不会为自己的作品感到骄傲或遗憾。

Da Pelo 的论文就是要精确描述这种奇怪的状况。他给出的答案是：AI 确实有一种"创造力"，但这种创造力和人类的创造力有本质区别。就像一条河流冲刷出美丽的峡谷——结果是壮观的，过程是有规律的，但整件事情从头到尾都没有意图、没有体验、没有自我意识。我们可以说这条河"创造"了峡谷，但这个"创造"的含义与人类艺术家"创造"一件作品截然不同。

论文还做了一件重要的事：它不是说"AI 的创造力不是真正的创造力"然后止步不前，而是给 AI 的这种能力一个正式的名字和定义——"人工创造力"，让我们可以严肃、精确地讨论它。

---

## Artificial Creativity: From Predictive AI to Generative System 3 (Chávez-Autor, 2025)
**来源**: Frontiers in Artificial Intelligence | **作者**: Juan Carlos Chávez-Autor

### 核心论点

本文从认知神经科学的"三系统"（tri-process）框架出发，诊断了当前 LLM 创造力不足的结构性原因，并提出了"生成系统3"（Generative System 3, GS-3）作为解决方案。作者指出，人类创造力依赖于三个认知系统的协调运作：默认模式网络（DMN，类似系统1的自发联想）、中央执行网络（CEN，类似系统2的目标导向评估）、以及系统3——一个通过神经调控增益控制在探索与开发之间动态切换的元认知整合器。

当前 LLM 的问题在于，它们只实现了 DMN 式的序列续写能力，缺乏内部评估器和自主的采样熵控制。GS-3 作为一种架构无关的设计模式，包含三个角色：高熵生成器（创意扩展）、学习型批评者（情境敏感的评价）和自适应增益控制器（根据奖励预测误差自主调节采样熵）。

论文的核心贡献包括：(i) 为新颖性、有用性和多样性提供了操作性定义；(ii) 提出了可证伪的行为指标（联想距离密度、分析验证比、收敛延迟）及其通过/失败标准；(iii) 发展了多种增益更新策略（指数型、线性型、逻辑斯谛型）及其稳定性约束；(iv) 提供了概念验证蓝图和完整的评估方案。

### 原文金句

> "Most LLMs behave like DMN-only decoders: excellent at sequence extension, but lacking an internal evaluator and endogenous gain control."
>
> 大多数 LLM 的行为类似于仅有默认模式网络的解码器：擅长序列续写，但缺乏内部评估器和内源性增益控制。

> "GS-3–level creativity emerges only when a system cycles autonomously between idea expansion and evaluative pruning."
>
> GS-3 级别的创造力仅在系统能自主地在创意扩展和评估修剪之间循环切换时才会涌现。

> "Dual-process accounts are necessary but not sufficient; System 3 coordinates and regulates how ideas are generated and pruned."
>
> 双过程理论是必要但不充分的；系统3负责协调和调控创意如何被生成和修剪。

### 关键概念

- **生成系统3** (GS-3): 一种架构无关的设计模式，包含高熵生成器、学习型批评者和自适应增益控制器三个角色
- **自适应增益控制**: 根据实时的奖励预测误差动态调节采样熵，功能上类似大脑中多巴胺对探索-开发平衡的调节
- **预测-生成连续谱**: 从纯粹预测（序列续写）经由受控生成和反思生成，到GS-3级别的创造性生成的四阶段进化

### 与本方向的关联

GS-3 框架为"思维与创造力"方向提供了一条从认知科学通向工程实现的明确路径。它将创造力的认知理论（包括 Wallas 模型和双过程理论）转化为具有可操作性和可证伪性的工程设计模式。该框架的关键洞见在于：创造力的核心挑战并非生成能力的缺乏，而是评估和调控能力的缺失。

### 通俗理解

想象一个爵士乐队的即兴演奏。萨克斯手在自由地吹奏旋律（创意扩展），鼓手在保持节奏和判断何时该加快、何时该减慢（评估修剪），而乐队指挥在整体把控——现在该让乐手们自由发挥，还是该收拢回到主旋律（增益控制）。当前的 AI 就像一个没有鼓手和指挥的萨克斯手：它可以不停地吹奏新旋律，但不知道什么时候该停、该转调、该收束。

GS-3 的方案就是给 AI 配齐这三个角色。生成器负责"天马行空"，批评者负责"脚踏实地"，增益控制器负责决定此刻是该"放飞自我"还是"回归正题"。这不是简单地让 AI "想想再说"——很多模型已经能做到这一点——而是让它像一个成熟的创作者那样，在灵感迸发和理性审视之间自如切换。

论文还提供了具体的"考试题"来判断一个 AI 是否达到了 GS-3 级别的创造力：它生成的想法之间是否有足够的跳跃性（联想距离密度）？它是否会自主地停下来评估自己的产出（分析验证比）？它在什么时候会从发散思维转向聚合思维（收敛延迟）？

---

## Creative Preference Optimization (Ismayilzada et al., 2025)
**来源**: Findings of EMNLP 2025 | **作者**: Mete Ismayilzada, Antonio Laverghetta Jr., Simone A. Luchini, Reet Patel, Antoine Bosselut, Lonneke van der Plas, Roger E. Beaty

### 核心论点

本文提出了"创造性偏好优化"（Creative Preference Optimization, CRPO），一种直接在偏好学习目标中注入多维创造力信号的对齐方法。CRPO 的核心设计是将新颖性、多样性、惊奇性和质量四个创造力维度的评分以可调权重（λn, λd, λs, λq）的方式整合到 DPO（Direct Preference Optimization）损失函数中，使模型在偏好学习过程中同时优化多个创造力指标。

研究者还构建了 MUCE，一个大规模人类偏好数据集，包含超过20万条人类生成的回复和来自30余种心理学创造力评估工具的评分。在 MUCE 上训练并经过 CRPO 优化的模型在自动评估和人类评估中均超越了 GPT-4o 等强基线，生成了更具新颖性、多样性和惊奇性的内容，同时保持了高质量的输出。在 NOVELTYBENCH 上的额外评估进一步验证了方法的泛化能力。

### 原文金句

> "Directly optimizing for creativity within preference frameworks is a promising direction for advancing the creative capabilities of LLMs without compromising output quality."
>
> 在偏好学习框架中直接优化创造力，是提升 LLM 创造能力而不牺牲输出质量的有前景方向。

> "LLMs have been shown to often lack novelty and surprise in their generations and produce significantly less diverse content compared to humans."
>
> 研究表明，LLM 生成的内容往往缺乏新颖性和惊奇性，且多样性显著低于人类。

> "Creativity is a multifaceted ability that also encompasses novelty, surprise, and quality and manifests itself in a wide range of tasks."
>
> 创造力是一种多维度的能力，涵盖新颖性、惊奇性和质量，并在广泛的任务中展现。

### 关键概念

- **CRPO**: 将新颖性、多样性、惊奇性和质量四个维度的评分以加权方式注入 DPO 损失函数的对齐方法
- **MUCE 数据集**: 包含20万余条人类回复和30余种心理学创造力评估评分的大规模偏好数据集
- **创造力的多维度操作化**: 将心理学的创造力评估工具（如 AUT、TTCT）转化为可用于模型训练的自动化指标

### 与本方向的关联

CRPO 展示了将心理学的创造力研究成果直接转化为 AI 训练信号的可行路径。它证明了偏好对齐不仅可以让模型"更安全"，还可以让模型"更有创造力"——两者并非必然矛盾。这为"思维与创造力"方向提供了一种可复制的方法论框架。

### 通俗理解

传统的 AI 训练就像培养一个循规蹈矩的学生：老师告诉他什么答案是好的、什么是坏的，他就照着学。问题是，这种训练往往让学生变得越来越保守——为了安全起见，总是选择"不会出错"的回答，结果丧失了创造力。

CRPO 做的事情是在"好答案"的标准里加入了新的维度。以前的标准主要是"准确、有帮助、无害"；现在还加入了"是否新颖？是否出人意料？是否跟别的回答不一样？"就好比写作课的评分标准从"语法正确、论点清晰"变成了"语法正确、论点清晰、有独到见解、让人眼前一亮"。模型在训练过程中会逐渐学会：安全的回答未必是最好的，有时候需要冒一点险、走一条没人走过的路。

更重要的是，研究者为此专门收集了大量的人类创造力评估数据——不是让普通人随便打分，而是用心理学家设计的专业创造力测试来评估。这确保了模型学到的"创造力"确实对应着人类对创造力的理解。

---

## Probing and Inducing Combinational Creativity in Vision-Language Models (Peng, Ma, Wang et al., 2025)
**来源**: AAAI 2025 (Peking University, BIGAI) | **作者**: Yongqian Peng, Yuxi Ma, Mengmeng Wang 等

### 核心论点

本文聚焦于 Boden 所定义的"组合创造力"——通过将已有概念进行新颖组合来生成新思想的能力。受认知科学中概念融合理论（conceptual blending theory）的启发，研究者提出了"识别-解释-蕴意"（Identification-Explanation-Implication, IEI）三层框架来分解组合创造过程：识别（组合了哪些对象？）、解释（如何组合的？即共享了哪些属性？）、蕴意（组合传达了什么含义？）。

为验证该框架，研究者构建了 CreativeMashup 数据集，包含666幅由艺术家创作的视觉混搭作品，每幅均按 IEI 框架进行了标注。实验表明，在理解任务中，最好的 VLM 已超越了普通人的平均水平，但仍未达到专家级理解；在生成任务中，将 IEI 框架纳入生成流程后，VLM 输出的创造性质量显著提升。

### 原文金句

> "Best VLMs have surpassed average human performance while falling short of expert-level understanding."
>
> 最优的视觉语言模型已超越了普通人的平均表现，但仍未达到专家级的理解水平。

> "Incorporating our IEI framework into the generation pipeline significantly enhances the creative quality of VLMs' outputs."
>
> 将我们的 IEI 框架整合到生成流程中，能显著提升视觉语言模型输出的创造性质量。

> "We lack a systematic framework for evaluating whether these models implement genuine combinational creative processes or merely leverage statistical patterns."
>
> 我们缺乏一个系统性框架来评估这些模型是否实现了真正的组合创造过程，还是仅仅利用了统计模式。

### 关键概念

- **IEI 框架**: 将组合创造力分解为识别（What）、解释（How）和蕴意（Why）三个层次的分析框架
- **CreativeMashup 数据集**: 666幅艺术家视觉混搭作品及其按 IEI 框架的专家标注
- **概念融合** (Conceptual Blending): 认知科学理论，描述人类如何通过整合两个"输入空间"来产生具有涌现结构的"融合空间"

### 与本方向的关联

本文为评估 AI 创造力提供了一个理论根基深厚且操作性强的框架。IEI 的三层分解使研究者能够精确定位 AI 在创造过程中的瓶颈——是在识别素材、发现联系，还是在推导深层含义的环节出了问题。更重要的是，它证明了认知科学的理论框架可以直接提升 AI 的创造性表现。

### 通俗理解

把一条鱼和一堆垃圾组合在一起，一个艺术家能创作出一幅呼吁海洋环保的震撼作品。这种"将两个不相干的东西巧妙结合产生新含义"的能力，就是组合创造力。

这篇论文问的是：AI 能理解和模仿这种能力吗？研究者设计了一个"创意鉴赏考试"，包含三道题：第一题"画面里组合了什么？"（鱼和垃圾），第二题"它们是怎么组合的？"（形状相似），第三题"这个组合想表达什么？"（海洋污染正在吞噬海洋生命）。结果发现，AI 在第一题上已经做得相当好，在第二题上也不错，但第三题——理解深层含义——仍然是最大的短板。

更有趣的发现是：如果你在让 AI 创作时也给它这三步指引——先确定要组合什么、再想怎么组合、最后思考要表达什么——它的作品质量会大幅提升。这就像教一个美术生画画，与其让他凭感觉画，不如先教他一套创作方法论。

---

## Unraveling the Emergence of Collective Behavior in Networks of Cognitive Agents (Zomer & De Domenico, 2026)
**来源**: npj Artificial Intelligence (Nature) | **作者**: Nicola Zomer, Manlio De Domenico

### 核心论点

本文通过将 LLM 驱动的"认知智能体"与经典的非认知粒子进行对比实验，系统探究了 LLM 的认知能力如何改变集体行为的涌现动力学。研究在两个任务上展开：函数优化和 Schelling 隔离模型。

在函数优化任务中，研究者提出了"LLM 智能体群优化"（llmASO），即一个由相互通信的 LLM 智能体组成的集群充当优化器。关键发现是：单个 LLM 智能体凭借模式识别和推理能力在简单景观中表现优异，但其趋同倾向使其容易陷入过早收敛。多智能体协作通过信息扩散缓解了这一问题，但调整网络拓扑以减缓过早收敛往往以整体收敛速度为代价。

在 Schelling 隔离模型中，认知智能体展现出与经典粒子截然不同的涌现行为：它们能够利用过往经验和邻域信息做出知情决策，并通过语言交流进行协调。这使得在相同的容忍度参数下，认知智能体产生了不同的隔离模式——智能嵌入每个个体内部（而非仅作为集体的涌现属性）从根本上改变了系统动力学。

### 原文金句

> "While individual agents outperform particles in decision-making, their consensus tendencies and ability to exploit patterns can make them prone to premature convergence."
>
> 虽然单个智能体在决策上优于粒子，但它们的趋同倾向和模式利用能力反而使其容易过早收敛。

> "With cognitive agents, intelligence is not only an emergent property of the system, as with particles, but is also embedded within each entity, fundamentally altering the underlying dynamics."
>
> 对于认知智能体而言，智能不仅是系统的涌现属性（如粒子群那样），还嵌入在每个个体之中，从根本上改变了底层动力学。

> "Local interactions and homophilic mechanisms allow cognitive agents to generate distinct emergent behaviors."
>
> 局部交互和同质偏好机制使认知智能体产生了独特的涌现行为。

### 关键概念

- **llmASO**: LLM Agent Swarm Optimization，由 LLM 智能体群通过通信网络协作进行优化的方法
- **过早收敛**: LLM 智能体因强大的模式识别和趋同倾向，在多模态优化景观中过早锁定局部最优
- **认知驱动的涌现**: 当智能嵌入每个个体（而非仅为集体属性）时，群体的涌现行为发生质变

### 与本方向的关联

本文将"思维与创造力"的讨论从个体层面拓展到集体层面。它揭示了一个深刻的悖论：LLM 智能体的"聪明"反而可能损害集体的创造性探索。这一发现对于理解 AI 辅助的群体创造力具有重要启示——协作中的认知智能体如何在趋同与多样性之间取得平衡，将成为未来人-AI 协同创造研究的核心问题。

### 通俗理解

想象两个寻找山谷中最低点的团队。第一个团队由一群盲人组成：他们只能感受脚下的坡度，根据简单规则（"哪边低往哪走"）移动。第二个团队由一群有视力、能交流的人组成：他们能观察周围的地形，和队友讨论策略。

你可能以为第二个团队一定更快找到最低点。结果却出人意料：在有很多小坑洼的复杂地形中，第二个团队的成员因为太"聪明"了，大家容易迅速达成一致"这里就是最低的"，然后集体停在了一个局部的小坑里。而第一个团队反而因为"笨拙"的随机游走，有时能碰巧滑进更深的谷底。

这就是本文揭示的 LLM 群体行为的核心矛盾：个体的智能在集体层面可能变成一种"诅咒"。解决方案不是让智能体变笨，而是调整它们的沟通方式——比如减少信息共享的频率或改变网络结构——让一部分智能体保持独立探索。这个发现对于人类组织同样富有启发：创新团队如果成员之间沟通过于频繁、太容易达成共识，反而可能扼杀最具突破性的想法。

---

