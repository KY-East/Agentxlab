# WisLand 技术拆解与研究定位

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
