# KPAX 知识源架构

**日期**：2026-04-16 深夜
**作者**：claude-code
**触发**：Ken 2026-04-16 晚提醒 cc 漏掉了 KPAX 知识层的真实形态——"KPAX 不仅仅是论文，还有行业的数据、经验，还有小伙伴在爬 Reddit / 知乎 / Quora"。原 `kpax-v0-deliberation-room.md` 没有明确 KPAX 的知识输入结构，这份笔记补上。
**上游**：`KPAX.md` 产品定义 + `notes/design/kpax-v0-deliberation-room.md` + radar 条目（autocli / yupi-hot-monitor / graphify / awesome-ceo）

---

## 1. 为什么不能只吃论文

AXL 是学术底座，7 学科 agent 辩论时默认吃学术论文（arXiv / OpenAlex / Semantic Scholar）。这对**学术问题**够用——agent 在讨论"Anthropic 宪法 AI 路线能否成为主流范式"时，学术论文是对的证据源。

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
- **典型命中学科**：物理 / 数学 / CS / 心理 / 社科 / 艺术人文（基本所有 7 学科都从这里拉一部分证据）
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
- 7 顾问在辩论过程中调用证据源时，这两种模式都是可用 tool

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
7 顾问中相关学科（主要是经济 / CS / 心理 / 社科）在辩论中查询 graph
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

7 顾问各自从三类里拉适合自己学科的证据，在辩论中碰撞。

### 5.2 证据权重
- 学科决定倾向：经济学更重 A + B，心理学更重 A + C，社科全覆盖
- moderator 在 synthesis 时应标注证据来源层级（论文 / 行业 / 社区）——让用户知道**共识建立在哪层证据上**，这是 pilot_judge_rubric_v0.1 的"可解释性与理由可对话性"维度的直接落地

---

## 6. 三条线的 v0/v1/v2 phasing

### v0（3 周内 MVP）
- Line A：保留现有 AXL Zep 系统，不额外改造
- Line B：**graphify + awesome-ceo 种子**（1 天接通，KPAX 后端加个 graph_client 调用入口）
- Line C：**先跳过**，KPAX 7 顾问 v0 只吃 A + B。不做社区数据接入

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
