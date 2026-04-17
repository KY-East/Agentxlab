# 外部参考雷达 — External References Radar

**用途**：Ken 发来的推文链接 / 开源项目 / 工具 / 文章，claude-code 抓取内容后做一次分析——对 AXL/KPAX 有什么用、对 Ken 个人有什么用——记一笔。未来回来看：哪些真被用上了，哪些还在观察。

**使用方式**：
- Ken 丢链接（推文 / GitHub repo / 博客 / 官网），可附一句"我觉得有用"或"拿不准"
- claude-code 抓内容 → 按下面的条目格式追加 → commit
- **X/Twitter 链接抓取**：WebFetch 返回 402（需登录），多数镜像站（nitter / xcancel / twitstat）不可靠。**有效路径**：用 Chrome MCP（`mcp__Claude_in_Chrome__navigate` + `get_page_text`）直接打开读取。2026-04-16 测试可行。如果 Ken 本地没开 Chrome extension，fallback 让 Ken 粘正文或截图
- 新条目加在最上面，时间倒序

**条目格式**：
```
### [YYYY-MM-DD] 项目/推文名
- 链接：
- 作者/来源：
- 是什么：一句话
- 对 AXL / KPAX 有没有用：具体到模块 + 阶段，或"不相关"
- 对 Ken 个人有没有用：研究视野 / 工具链 / 思路灵感
- 动作：adopt（纳入栈）/ track（留意后续）/ skip（不相关但记一笔，以免重复遇到）
- 理由：一到两句
```

**动作字段说明**：
- **adopt** = 决定在项目里用。同步到 design doc / agenda。
- **track** = 有潜力但时机不对，或还在早期。每月底梳理看要不要升为 adopt。
- **skip** = 读过判断过，不用。保留条目避免反复遇到相同东西时重新评估。

---

## 条目（新到旧）

### [2026-04-17] EvoMap / Evolver — 自进化 agent 框架（GEP 协议 + 10 步循环）
- **触发来源**：@GoSailGlobal https://x.com/GoSailGlobal/status/2044358918185562180?s=20 （Ken 2026-04-17 转）
- **是什么**：开源 Node.js agent 自进化框架。核心概念：
  - **GEP 协议（Gene Evolution Protocol）**：把 agent 的行为 / 能力编码成可演化的"基因"，每轮运行后按反馈更新
  - **10 步进化循环**：Scan → Select → Mutate → Validate → Solidify（+其他辅助步骤，构成完整闭环）
  - **三层记忆架构**：短期工作区 / 中期反思池 / 长期固化知识
  - **reflection 周期**：强制 agent 周期性回看自己的决策轨迹，产出 diff 进入下一轮基因
- **争议背景**：外部有 Hermes 生态"架构级抄袭 EvoMap"的指控。Ken 2026-04-17 定调：**不介入站队，技术可用就用，一视同仁**。
- **对 AXL / KPAX 有没有用**：**adopt 作为候选**。
  1. AXL 自由参数 L7 元进化的"agent 该如何更新自己"部分，EvoMap 的 **GEP 协议 + 10 步循环**是开源圈目前最完整的参考实现之一，写进 `agent-evolution-free-parameters.md` 时并列 Hermes 做对照
  2. KPAX 化身层（`notes/research.md §human-skill-distillation-layer`）的"化身用久了怎么演化"环节——EvoMap 的 reflection + mutation 机制直接可以嫁接在每个化身的个体记忆层
  3. EvoMap 三层记忆架构 vs AXL 七层记忆设计——写 Phase 3 前做一次对位表
- **对 Ken 个人有没有用**：自进化 agent 是 2026 最活跃的开源方向之一，值得跟进
- **动作**：**adopt** 作为化身层候选技术栈之一（和 Hermes 并列）
- **理由**：Ken 2026-04-17 定调"所有有利的都用"；GEP 协议的形式化程度在当前开源项目里算前列
- **关联**：`notes/research.md §human-skill-distillation-layer` / `agent-evolution-free-parameters.md` / `KPAX.md §技术来源`

---

### [2026-04-17] 腾讯混元 HY-World 2.0 —— 3D 世界生成开源模型
- **主推文**：https://x.com/berryxia/status/2044611121605460364（Berryxia.AI 转发，2026-04-15 发布）
- **仓库地址（Ken 提醒"不能只看主推特"——作者在推文 reply 里贴了 repo）**：`github.com/Tencent-Hunyuan/HY-World-2.0`（截至 2026-04-17 抓取：620 stars / 33 forks / 2 contributors / 2 issues）
- **作者**：Tencent-Hunyuan（腾讯混元）
- **是什么**：多模态世界模型。从文本 / 图像 / 视频生成、重建、模拟**可交互 3D 世界**。
  - **一键世界生成**：文字或图片输入 → 自动创建可交互 3D 世界
  - **引擎就绪输出**：直接支持 Unity 和 Unreal Engine，产出 mesh / 3DGS / 点云等标准 3D 格式
- **和 Spark 2.0（World Labs）的关系**：**互补不是竞争**。HY-World 做**生成**（文字 / 图像 → 3D 世界），Spark 做**浏览器流式渲染**（splat → WebGL2 LoD）。完整 pipeline：HY-World 生成场景 → 导出 .RAD splat / mesh → Spark 流式渲染到 KPAX 前端 → R3F composite worlds 叠加化身
- **对 AXL / KPAX 有没有用**：**时间博物馆多场景生成的直接基础设施**
  - v0 默认场景（维多利亚书房厅）可手扫 or 用 Spark 现成 captured_space
  - v1 扩展的其他厅（现代会议厅 / 东方庭院 / 竞技场）——**用 HY-World 文字生成，省掉 3D 建模工时**
  - 印证 Ken 2026-04-17 原话："场景不用做了，不管是 spark 还是这个，关键是最后封装或者怎么实现"
- **战略层意义**：和昨天对化身的判断是同一逻辑模式——
  - 化身层：现成（alchaincyf / 女娲 / Hermes）→ KPAX 自建是**编排层 + 野生识别 + 反馈飞轮**
  - 场景层：现成（Spark 2.0 / HY-World 2.0）→ KPAX 自建是**集成封装 + 交互设计 + 化身-场景联动**
  - 两层合起来，KPAX 真正自建只剩编排 + 反馈飞轮两件事。这是侧翼战场策略的自然延伸。
- **对 Ken 个人有没有用**：任何想生成 3D 场景的用途（pitch 视频 / personal 项目 / 演示背景）都可用
- **动作**：**track** + bookmark 官方 repo；v1 前端实装多厅时 evaluate 接入路径
- **关联**：`notes/design.md §3.1 时间博物馆` + `notes/design.md §4.1 环境渲染 Spark 2.0`（建议 cursor 下次改 design.md 时把 HY-World 2.0 加入 §4.1 作为 Spark 的并列候选）

---

### [2026-04-17] alchaincyf 开源名人 skill 生态（12 名人 + 女娲自动蒸馏工具）
- **触发来源**：Ken 2026-04-17 口述，关联 LuBtc888 汇总帖
- **是什么**：开源 GitHub 仓库集合（2026-04-17 cc 从 LuBtc888 主推文正文抓取每个 skill 的 github URL 补全——此前 "具体列表待确认" 是因为 cursor 写 radar 时没看完整推文正文）：
  - **12 个名人 skill 模块**（均在 `github.com/alchaincyf/*-skill`）：
    1. `steve-jobs-skill`（乔布斯 / 思维模型 + 现实扭曲力场 + 决策风格）
    2. `elon-musk-skill`（马斯克 / 第一性原理 + 硬核执行力 + 推文风格）
    3. `munger-skill`（芒格 / 多元思维模型 + 反向思考 + 投资决策）
    4. `feynman-skill`（费曼 / 讲课方法 + 复杂问题拆解 + 学习/物理教学）
    5. `naval-skill`（纳瓦尔 / 财富 + 幸福 + 人生哲学）
    6. `taleb-skill`（塔勒布 / 黑天鹅 + 反脆弱 + 风险评估）
    7. `zhangxuefeng-skill`（张雪峰 / 升学吐槽 + 志愿填报）
    8. `paul-graham-skill`（Paul Graham / 创业思维 + 写作 + 产品哲学）
    9. `zhang-yiming-skill`（张一鸣 / 算法思维 + 组织管理 + 产品迭代）
    10. `karpathy-skill`（Karpathy / AI + 深度学习教学 + 技术直觉）
    11. `ilya-sutskever-skill`（Ilya Sutskever / AI 前沿 + 模型底层哲学）
    12. `mrbeast-skill`（MrBeast / 内容病毒传播 + 增长黑客）
    13. `trump-skill`（特朗普 / 谈判风格 + 推文艺术 + 现实扭曲）—— 注：这条 alchaincyf 也做了，算 13 个。原 LuBtc888 列表里"名人系列 13 个"其中 11 个来自 alchaincyf + 2 个其他作者
  - **女娲.skill（Nuwa）**（`github.com/alchaincyf/nuwa-skill`）：自动蒸馏工具——给它一批文本（访谈 / 著作 / 推文 / 演讲稿），自动提取出可复用的 skill 文件
  - **另外两个 alchaincyf 工具 skill**（不在名人类）：`x-mentor-skill`（X/Twitter 运营导师，分析账号数据 + 写推文 + 诊断报告）
- **对 AXL / KPAX 有没有用**：**KPAX 化身层 v1 货架的直接候选**。
  1. **v1 真人化身初始池**：KPAX 化身分三类（学科 / 真人 / 野生），真人化身 v1 的最小启动池可以直接用 alchaincyf 的 13 个里符合我们领域分布（中西混合 / 多领域，不全部押商业）的 5-7 位。节省自建时间
  2. **女娲蒸馏工作流**：KPAX 野生化身识别后，下一步"把野生人物蒸馏成 skill"可以参考女娲的 pipeline
  3. **License 预审**：adopt 前必须逐一审每个 skill 文件的 license、原作者对二次使用的条款、以及所引用名人的肖像 / 言论权边界（在世名人尤其敏感）
- **对 Ken 个人有没有用**：了解当前 skill 生态的开源成熟度，避免重复造轮子
- **动作**：**track** → adopt 待 license 预审完成
- **理由**：货架已经有，不用自己从零做 13 个 skill；但 license + 伦理边界必须过关
- **关联**：`notes/research.md §human-skill-distillation-layer` / `notes/next.md`（v1 shopping list + license 预审任务）

---

### [2026-04-17] 反蒸馏.skill（Anti-distillation skill）
- **触发来源**：Ken 2026-04-17 口述（alchaincyf / skill 生态相关的反向工具）
- **是什么**：一个"对抗蒸馏"的 skill——给 skill 文档注入**混淆 / 噪声 / 误导性模板**，使得外部工具（比如女娲）很难从已发布的 skill 反向抽取原作者的核心知识。本质是**知识保护 / 竞争对抗层**的工具。
- **对 AXL / KPAX 有没有用**：
  - 直接用不上（我们做的是化身编排层，不是 skill 保护层），但是**信号极强**：
  - skill 生态已经从"免费开源分享"阶段进入"知识保护 vs 抽取"对抗阶段。说明 skill 作为独立商业单元的价值被验证到了——**有人愿意花力气保护**
  - 对 KPAX 的战略启示：KPAX 不要陷入"比谁的名人 skill 蒸馏得更像"的军备竞赛（这一层正在被军备化），专注在"跨化身编排 + 时间博物馆场景"这层，绕开红海
- **对 Ken 个人有没有用**：理解 skill 赛道的博弈动态
- **动作**：**track**（不采纳工具，但留意生态演化）
- **理由**：反蒸馏的出现本身证明 skill 单体已被商品化；KPAX 的差异化必须在更上游（编排 / 场景 / 化身组合），不在单 skill 品质
- **关联**：`notes/research.md §human-skill-distillation-layer`（"单 skill vs 跨化身编排"的边界论证）

---

### [2026-04-17] @LuBtc888 的 26 skill 汇总推文（skill 生态全景信号）
- **触发来源**：Ken 2026-04-17 转 https://x.com/LuBtc888/status/2042994080796307502?s=20
- **是什么**：一条汇总推文，列出社区当前流通的 26 个 skill（名人 skill 为主，也包含工具型 skill 如女娲、反蒸馏等）。作者立场是"skill 化是 2026 agent 生态的一个主轴，值得系统化梳理"。
- **原推文列出的 26 skill 完整清单（github URL，2026-04-17 Ken 提醒"不能只看主推特"后 cc 从正文抓取）**：

  **职场 & 自媒体系列（9 个）**：
  1. 同事.skill：`github.com/titanwings/colleague-skill`（"SKILL 流"源头）
  2. 女娲.skill：`github.com/alchaincyf/nuwa-skill`（自动蒸馏引擎）
  3. X 导师.skill：`github.com/alchaincyf/x-mentor-skill`
  4. 老板.skill：`github.com/vogtsw/boss-skills`
  5. 前任.skill：`github.com/therealXiaomanChu/ex-skill`
  6. 自己.skill：`github.com/notdog1998/yourself-skill`（数字永生 / 第二大脑）
  7. 博主.skill：`github.com/YourongZhou/chat_with_me`（社媒语料 → Persona skill）
  8. 蒸馏.skill：`github.com/YIKUAIBANZI/forge-skill`（人格蒸馏引擎，另一作者的女娲平替）
  9. 反蒸馏.skill：`github.com/leilei926524-tech/anti-distill`（知识投毒防抽取）

  **名人复刻系列（13 个，11 个出自 alchaincyf，见上条 radar）**：
  10-22. 见上条 `alchaincyf` radar 条目（乔布斯 / 马斯克 / 芒格 / 费曼 / 纳瓦尔 / 塔勒布 / 张雪峰 / Paul Graham / 张一鸣 / Karpathy / Ilya / MrBeast / 特朗普）

  **玄学 & 传统文化系列（4 个）**：
  23. 赛博算命.skill（八字）：`github.com/jinchenma94/bazi-skill`
  24. 月老·姻缘测算.skill：`github.com/Ming-H/yinyuan-skills`
  25. 奇门遁甲 / 紫微斗数.skill：`github.com/FANzR-arch/Numerologist_skills`（低幻觉 + 固定排盘）
  26. 大师.skill：`github.com/xr843/Master-skill`（汉传佛教 + 祖师大德）
- **对 AXL / KPAX 有没有用**：
  1. **市场扫描**：KPAX 化身层 v1 选人时，这 26 个的命中 / 缺席直接反映社区热点和空缺——命中的领域（商业 / 投资 / 科技创业）说明已内卷，空缺的领域（比如艺术 / 科学 / 东方思想家 / 历史政治家）说明有机会做差异化
  2. **对手 scanning**：了解 KPAX 如果走单 skill 路线会遇到的直接对比对象
  3. **信号**：skill 生态正在从"单兵分发"向"合集分发"演化，这和 KPAX 的"化身团编排"方向其实相似但低一层——单合集还是静态打包，KPAX 做的是动态按问题召集
- **对 Ken 个人有没有用**：skill 赛道的快速扫描
- **动作**：**track** + 扫描 26 个里哪些适合作为 KPAX v1 真人化身候选，产出 shopping list
- **理由**：是市场现状的诊断材料，不是直接可用工具
- **关联**：`notes/next.md`（v1 化身 shopping list 任务）/ `notes/research.md §human-skill-distillation-layer`

---

### [2026-04-16] @witcheer 的 AI 记忆工具全景扫描文（Two Camps）
- **原文链接**：https://x.com/witcheer/status/2044456778843238689
- **转引**：https://x.com/nash_su/status/2044646757741793751 （nash_su 推荐）
- **作者背景**：witcheer，在 Mac Mini M4 上跑 24/7 agent 实验（Hermes Agent + Claude Code），正在做 ALIVE 项目（alivecontext.com / @AliveContext_）
- **是什么**：作者读遍 GitHub 450+ agent-memory 仓库 + 460+ context-management 仓库后的分类综述。核心论点：**记忆工具分两个根本不同的流派**——
  - **Camp 1 Memory Backends**（Mem0 53k⭐ / MemPalace 46k⭐ / Supermemory 22k⭐ / Honcho / Cognee / Memori 等）：对话里抽事实 → 存向量库 → 按需检索。优化 recall。
  - **Camp 2 Context Substrates**（OpenClaw 358k⭐ / Zep 4.4k⭐ / Thoth 145⭐ / TrustGraph 2k⭐ / MemSearch 1.2k⭐）：结构化可读 context，文件即记忆，session 之间累积。优化 compounding。
  - 关键断言：现有 benchmark 只测 recall（"记得用户搬到旧金山了吗"），**没人测 compounding**（session 10 是不是比 session 1 更聪明）。这是真正的研究空白。
  - 预测：6 个月内 "context engineering" 取代 "memory" 成为默认词
- **对 AXL / KPAX 有没有用**：**极度有用，这是对 AXL 研究方向的最直接对位文章**。五条具体连接：
  1. **Zep 刚从"memory"改名"context engineering"**——AXL 七层记忆建在 Zep 上。我们现在的 backend 供应商自己在改造，必须读他们 Graphiti framework 新 positioning，更新 `notes/research.md#seven-layer-memory-design` 的 backend 部分
  2. **OpenClaw 的 6 个加权信号**（relevance 0.30 / frequency 0.24 / query diversity 0.15 / recency 0.15 / consolidation 0.10 / conceptual richness 0.06）= **AXL 自由参数 L7 元进化的理论默认值**。别人 hard-code，AXL 在做让它可学习。直接写进 `agent-evolution-free-parameters.md`
  3. **compounding benchmark 的空缺** = AXL 护城河的直接对位。emergence_decomposition 实验的**下一个天然续作**可以做 `compounding_gain_benchmark`，是学术论文的真正立足点
  4. **Thoth 的 4 阶段 dream cycle**（duplicate merging 0.93 sim / enrichment / relationship inference / confidence decay 90 天）——比 AXL 当前 session 压缩完整。Phase 3 设计必须参考
  5. **ALIVE 项目**（作者自己在做）是一个正在行动中的 Camp 2 实作，值得深挖
- **对 Ken 个人有没有用**：
  - witcheer 是一个值得长期关注的研究型作者（Mac Mini M4 的 24/7 agent setup 本身就是实践性深研）。她的 Telegram @witcheergrimoire 每日有高质量 AI + DeFi 信号
  - 这篇是 AXL 研究论文 literature review 的**必收录参考**
  - 提到的"文件即记忆"哲学呼应 AXL MEMORY.md 现状（本地 memory 本就是 markdown）
- **动作**：**adopt**（研究输入，要写进 research notes）+ **track**（Zep rebrand / ALIVE / Thoth 三个子链）
- **理由**：这不是个工具链接，是整个记忆工具生态的地图，并且指出了**现有 benchmark 的根本缺陷 = AXL 护城河的立足点**。必须马上：(a) 把 Zep rebrand 信息加进 seven-layer-memory-design.md，(b) 把 OpenClaw 6 信号加进 agent-evolution-free-parameters.md，(c) 把 compounding benchmark 作为 emergence_decomposition 的续集候选加进 notes/next.md P2

---

### [2026-04-16] Lawrence 日志体系方法论（方法论，非工具）
- **链接**：https://x.com/LawrenceW_Zen/status/2044437995269591195
- **是什么**：推文方法论提示——"Vibe Coding 时必须让 AI 写完整可追溯日志体系。查问题省 token，提高 AI 排查效率"。回复补充（@webb_dever）："A good log system shrinks the search space for the next agent run. Without observability, vibe coding turns into repeated guessing."
- **对 AXL / KPAX**：**直接命中我们的现状短板**。cc 快速 grep：AXL backend 10+ 文件散落 `logger = logging.getLogger(__name__)`，55 处 logger 调用，**无统一配置 / 无 request_id / 无结构化 JSON / 无 trace**。KPAX 复合系统（classifier + expert_builder + AXL + ledger 跨 4-5 组件）一出 bug 定位将非常痛
- **动作**：**adopt（理念）**。next.md P2 加任务 "AXL + KPAX 最低可用 trace 日志体系"，KPAX v0 启动前落地。工时 1-2 天，做最低可用（FastAPI middleware 注入 request_id + 统一 logger format + stdout JSON Lines + 5 组件关键节点 log），**不做全栈 observability**
- **对 Ken 个人**：发推可用的方法论 take
- **理由**：这条是**时机对位**——我们正要从原型（靠 print 和 progress.jsonl 够用）过渡到产品（跨组件调试需要 trace），Lawrence 在这个 momeent 提醒我们正在进入的坑

---

### [2026-04-16] 程序员鱼皮 yupi-hot-monitor（KPAX 第三知识线的 full-stack 参考）
- **链接**：https://github.com/liyupi/yupi-hot-monitor（Node.js / Express 5 / React 19 / OpenRouter / Socket.io，开源 + 付费教程）
- **推文来源**：https://x.com/yupi996/status/2044824052179890407
- **是什么**：AI 热点监控工具 full-stack 实现。6 大功能：(1) 关键词配置 (2) 8+ 数据源定时抓（Twitter / Bing / HN / 搜狗 / B 站 / 微博 等），AI 做查询扩展 + 真假识别 + 相关性 + 摘要 + 低质量过滤 (3) 多维度筛选排序 (4) 全网搜索 (5) WebSocket 实时推送 + 邮件通知 (6) 打包成 Agent Skills（Cursor / VSCode Copilot / Claude Code 通用）
- **对 AXL / KPAX**：**直接对应 KPAX 知识架构第三条线（社区经验 / 实时热点）的完整 full-stack 参考**。和 autocli / graphify 并列为第三线候选池
- **和 autocli 的关系**：**互补，不是重复**
  - autocli = 按需查询（用户问题进来→实时拉），Chrome 登录态，本地 skill
  - yupi-hot-monitor = 预缓存（后台 poll 30min+推），API key 式，服务端架构
  - KPAX 真做起来两种都要——按需 + 预缓存
- **实际价值**：
  1. 8 数据源的聚合代码可直接参考（省接平台 API 的苦活）
  2. AI 二次加工 pipeline（查询扩展 / 真假识别 / 相关性 / 摘要）KPAX 完全适用
  3. Agent Skills 打包手法值得抄
- **局限**：
  - 教程项目，代码质量未验证（"demo 跑通"级可能多于"生产级"）
  - 后端 Node.js，我们是 Python FastAPI，**看架构思路，不直接用代码**
- **对 Ken 个人**：中国开发者教程生态产物，看中国市场 vibe coding 教程走向
- **动作**：**track + fork 参考**（KPAX 知识层第三线设计时必看）

---

### [2026-03-28] Leo 的 Polymarket 玩家策略扒取 Skill
- **链接**：https://x.com/runes_leo/status/2037871828149129466 （Solana Agent Economy Hackathon 参赛作品，$30k 奖金池）
- **是什么**：Claude Code skill，装上后 AI 能扒 Polymarket 任意玩家的交易策略。展示案例：9 大品类排行榜第一名分析，有人 9 万笔交易覆盖 1181 个市场，有人靠 SPLIT 套利闷声赚 $21 万
- **对 AXL / KPAX**：**弱相关**。KPAX 概率题类型（prob_01~prob_10 那批"世界杯谁赢""BTC 会破 20 万吗"之类）里，**Polymarket 实时赔率可作为 7 顾问辩论时的证据源**。扒玩家策略本身不是核心，但 Polymarket 数据接入是可延伸的一条线
- **对 Ken 个人**：crypto 背景人的一个有意思 skill
- **动作**：**track（弱）**
- **理由**：Ken 标注"记录"即可。概率题场景的候选数据源之一，未来做实时证据接入时回来看

---

### [2026-04-16] 歸藏的 Logo Generator Skill（KPAX v0 视觉产物工具）
- **链接**：https://x.com/op7418/status/2044634498432962806（文章里会给 skill repo）
- **是什么**：Claude Code / Gemini CLI skill，三步生成 Logo + 高级展示图
  - 第一步：信息收集（产品名 / 行业 / 核心概念 / 设计偏好）
  - 第二步：SVG 变体生成
  - 第三步：配专业背景渲染高级展示图
  - 作者推荐 Gemini CLI（SVG 能力强），Claude Code 也可用
- **对 AXL / KPAX**：**直接命中 KPAX v0 视觉产物需求**。落地场景：
  1. KPAX 主 Logo（主站 / 推特 / 分享卡 / 钱包内图标）
  2. AXL Logo（GitHub / README / PROGRESS.md）
  3. 7 学科抽象图标（座谈会场景 fallback / moderator 徽章 / 发言标识）
  4. 代币图标（wallet 条 / 奖励弹窗）
  5. UI 按钮图标（分享 / 有帮助 / 拍肩膀）
- **互补关系**：和 Cocoon `architecture-diagram-generator`（已 adopt）正好配齐——一个画架构图，这个画 Logo/Icon，组合起来是 KPAX/AXL 文档+品牌视觉的完整工具栈
- **对 Ken 个人**：任何小项目要 Logo 的默认起点
- **动作**：**adopt**（KPAX v0 上线前视觉产物默认工具）
- **理由**：low-cost high-value。solo dev 不找设计师不挑公版的最简方案

---

### [2026-04-16] Hyperframes — Claude Code 本地视频生成 skill（KPAX 分享 loop 关键候选）
- **链接**：推文里没给明确 repo 链接，搜索关键词 "Hyperframes Claude Code video render"
- **推文来源**：https://x.com/billtheinvestor/status/2044855521132580966
- **是什么**：Claude Code 预装 skill（也兼容 Cursor / Gemini CLI，100% 开源）。描述视频内容 → Claude Code 写 HTML composition → 本地渲染 MP4。三条命令、无云端调用
- **对 AXL / KPAX**：**未来必用**。四个落地场景（从重要到次要）：
  1. **KPAX 用户分享激励**（核心）：每场辩论结束 → 自动生成 30 秒"我的决策过程"精华视频（7 顾问辩论高光 + 最终判决）→ 用户分享 → 奖励 20 token。这是代币经济 social loop 的关键环节，没有视频只有文字传播力极弱
  2. **KPAX v0 产品 demo 视频**：上线前发 Twitter / Telegram / 朋友圈的宣发内容
  3. **AXL 实验结果可视化**：涌现分解论文的 supplementary 视频材料
  4. **Ken 个人 Twitter 建设**：讲 KPAX / AXL 进展的默认配图视频起点
- **对 Ken 个人**：Twitter 发推/做 thread 时直接生成
- **动作**：**track + v0 上线前必 adopt + 加到 KPAX 分享机制设计候选栈**
- **理由**：Ken 原话"未来肯定有"——这条是"肯定有的"那类。加到 next.md P2 KPAX 分享机制设计里作为视频生成候选

---

### [2026-04-16] linux-android — Termux 脚本把旧安卓手机变 Linux 主机
- **链接**：推文里没给明确 repo 链接，搜索关键词 "linux-android termux MIT"
- **推文来源**：https://x.com/DtDt666/status/2044703758714905045
- **是什么**：Termux 里跑的脚本，把旧安卓手机变成 Linux 桌面（XFCE4 / LXQt / MATE）/ Home Assistant 服务器 / 开发机。**无 root 无刷机**。GPU 支持（Turnip Vulkan 骁龙 / Mali fallback），SSH、Box64/Wine、PulseAudio。MIT。对比：树莓派 4 $35-75 / 二手迷你主机 $100+ / VPS $5/月
- **对 AXL / KPAX**：**弱相关**。一个细弱 angle——之前 autocli radar 条目提到的"云 AXL + 用户本地 skill 辅助"混合架构，用户旧安卓手机可作为本地 skill 节点。非当前需要
- **对 Ken 个人**：有旧安卓手机的话是个周末玩具
- **动作**：**track（弱）**
- **理由**：Ken 标注"有意思"，不是紧迫候选。记一笔，未来讨论 KPAX 用户本地部署模式时回来看

---

### [2026-04-16] Firecrawl Fire-PDF v2（**规则复查后由 skip 改为 track**，2026-04-16 晚）
- **链接**：
  - 整体栈：https://www.firecrawl.dev/blog/fire-pdf-launch
  - 纯 Rust 子组件：https://github.com/firecrawl/pdf-inspector
- **推文来源**：https://x.com/berryxia/status/2044280018315116871
- **Fire-PDF 架构**：
  - 第 1 步 `pdf-inspector`（纯 Rust，无 ML，ms 级）分类每页 → 文本页 / 扫描页
  - 文本页走 native text extraction 快路径，不碰 GPU
  - 扫描页走 **GPU 神经布局模型 + GLM-OCR vision-language model**
  - 速度 5x，每页 < 400ms，表格 / 公式 preserve
- **评估过程（含 cc 自我纠错记录）**：
  - cc 第一版判断：Fire-PDF 整体栈有 OCR fallback → 触发 "绝不 OCR" 规则 → skip
  - Ken 质疑规则来源：发现 "绝不 OCR" 是 cc 从 wisland deck 外推的（Ken 从未说过），被错误固化为硬规则
  - Ken 立场澄清："我们没有这个积累，有了立马就用"——能力约束型，不是战略回避
  - 规则改为 "不自建板式解析模型"（保留），放开 OCR 限制。相关文档已同步修正（wisland B.3 / PROJECT §5.5 / next.md 反向清单）
- **对 AXL / KPAX**：
  - **学术论文**（arXiv / S2）场景：仍优先 pdfminer.six / unstructured（纯文本够用，不需要 Fire-PDF 的 OCR 能力）
  - **行业报告 / deck / 扫描版 / 社区截图**场景：Fire-PDF 是强候选（表格 / 公式 preserve 好、速度快、OCR 智能 fallback）
  - `pdf-inspector` 单独也值得：做 "pages-are-text vs scanned" 预分类路由非常有用
- **对 Ken 个人**：无
- **动作**：**track**（非 skip）。KPAX 开始做第二 / 第三知识线 ingest 时重新评估
- **理由**：Ken 明确说"有能力就上正面"，Fire-PDF 是开箱成熟方案，属于 "能用就用" 类别。未来在 KPAX 内容注入阶段对比候选池（pdfminer / unstructured / Fire-PDF / docling / Marker / mineru）按场景选，不预先 skip

---

### [2026-04-16] Cocoon-AI architecture-diagram-generator + Hermes Agent Skills 生态
- **链接**：
  - 主：https://github.com/Cocoon-AI/architecture-diagram-generator （MIT）
  - 集成方：https://hermes-agent.nousresearch.com/docs/skills/ （Hermes Agent Skills Hub）
- **推文来源**：https://x.com/Teknium/status/2044190761609244986 （@Teknium = NousResearch 联创 + Head of Post Training，Hermes 系列开源模型的团队）
- **是什么**：Claude Code / Hermes skill，`/architecture-diagram <prompt>` 一条命令生成暗色主题的系统架构图（HTML/SVG 单文件输出，零外部依赖）。Hermes Agent 官方 port MIT 版进来作为 built-in skill。
- **对 AXL / KPAX**：
  1. **立刻可用于项目文档**：生成 AXL↔KPAX HTTP 边界图 / 七层记忆 L1-L7 图 / 座谈会管线图 / 三条知识线架构图。cc 可以马上装上配图 `kpax-v0-deliberation-room.md`、`seven-layer-memory-design.md`、`kpax_api_spec.md`
  2. **Hermes Agent 值得单独 track**：witcheer 24/7 setup 用的就是它，这是 Mac Mini M4 本地 agent infrastructure 的一个重要参照。Skills Hub 里可能还有更多我们用得上的
- **对 Ken 个人**：想做技术 deck / blog 配图也直接用
- **动作**：**adopt（立刻装，用于项目文档配图）+ track（Hermes Agent 作为 Camp 2 context substrate 实作参照）**
- **理由**：低成本 high-value。一个 skill 下午就能把所有设计文档配上像样架构图，显著提升可读性。Hermes Agent 值得花时间研究——witcheer 的 Two-Camps 文章已经指向它

**Side find（同次搜索意外发现，单独值得一条）**：

### [2026-04-16] safishamsi/graphify — 文件夹转可查询知识图谱（KPAX 第二知识线关键工具）
- **链接**：https://github.com/safishamsi/graphify
- **是什么**：Claude Code / OpenClaw / Cursor 等多 agent 通用 skill。把**任意文件夹**（code / docs / papers / images / videos）转成**可查询的知识图谱**
- **对 AXL / KPAX**：**直接打中 KPAX 知识架构第二条线（行业 curated）的 ingest 处理工具**。流程：
  - Ken 把 awesome-ceo essays / YC 文章 / a16z playbooks / Sequoia pitch decks 下载到本地文件夹
  - `graphify` ingest → 变成知识图谱
  - AXL 的 agents 查询时直接拉 graph edge + 相关文档片段
- 和前面 witcheer 文章里 Camp 2 的 Thoth（10 entity types / 67 typed relations / A* graph expansion）是同一范式
- **对 Ken 个人**：自己读书做笔记 / 沉淀多年资料的工具，纯个人用也值得试
- **动作**：**strongly track + 等 KPAX 知识架构笔记写完再决定 adopt / 自建**
- **理由**：要等 `notes/research.md#kpax-knowledge-source-architecture` 写出来（P2 agenda 已挂），再对照 graphify / Thoth / ALIVE 三家做选型。是选型池的重点候选

---

### [2026-04-16] Android APK 反编译 Claude Code skill
- **链接**：https://github.com/Sinnenagoghi/android-reverse-engineering-skill
- **推文来源**：https://x.com/axiaisacat/status/2044324733479432425
- **是什么**：Claude Code skill，`/decompile app.apk` 一条命令反编译 APK/XAPK/JAR/AAR，自动抽 Retrofit/OkHttp 接口、Activity→ViewModel→Repository→HTTP 调用链、分析 Manifest + 架构、解 ProGuard/R8 混淆。用途：安全研究 / 竞品分析 / 逆向学习
- **对 AXL / KPAX**：**不相关**，我们不做 Android、不涉及逆向
- **对 Ken 个人**：如果哪天要 RE 某个竞品 Android app 可能用，当前无实际场景
- **动作**：**skip**
- **理由**：记一笔防止重复评估，非当前需要

---

### [2026-04-16] AutoCLI / autocli-skill（KPAX 知识架构第三线的关键候选）
- **链接**：https://github.com/nashsu/autocli-skill （Claude Code skill 包装）+ 底层 AutoCLI Rust CLI
- **推文来源**：https://x.com/mnmn94253156337/status/2044583527824719978 （2026-04-15，撸毛吃猪脚饭）
- **是什么**：4.7 MB Rust 单二进制（零依赖），用**复用 Chrome 登录态**的方式把 55+ 平台（B站 / 知乎 / 微博 / 小红书 / 豆瓣 / 雪球 / Reddit / X / YouTube / HackerNews / Yahoo Finance / Cursor / Notion / Discord 等）变成 CLI。**不需要 API Key**，用户 Chrome 登录过就能用。三种模式：Public（API）/ Browser（Chrome 扩展协助）/ Desktop（应用控制）。是 opencli 的 Rust 重写版，速度快 12×、内存省 10×。
- **安装**：`npx skills add https://github.com/nashsu/AutoCLI-skill`——**直接是 Claude Code skill**
- **对 AXL / KPAX**：**直接解决 KPAX 知识架构第三条线（社区经验）**。原本 Ken 的小伙伴在爬 Reddit / 知乎 / Quora，autocli 把这活做成零维护 skill。应用示例：
  - 用户问 "小米汽车值不值得买" → CS + 经济顾问调 autocli 拉微博 + 小红书 + 雪球实时讨论
  - 用户问 "ETH 2026 破 10k 吗" → 经济顾问调 Twitter + 雪球 + HackerNews 取情绪样本
  - 用户问 "该不该辞职创业" → 经济 + 心理顾问调 Reddit r/startups + 知乎 + HackerNews
- **优劣判断**：
  - ✅ 快上线（一个 skill 安装）/ 覆盖广（55+ vs 自建爬 3-4）/ 中文平台覆盖全
  - ❓ 依赖 Chrome 登录态——**服务端部署不行，只能单机或用户本地**（对 KPAX 商业化是个挑战）
  - ❓ 平台 ToS 风险——商业化时可能违规
  - ❓ 可靠性 / 被限流的情况未知
- **对 Ken 个人**：cc 立刻可以装上做 radar 抓取升级（本地工作流）
- **动作**：**adopt（探索性：我自己先装，验证 radar 工作流是否受益）+ strongly track（KPAX 知识层集成候选，重点议题是部署模式）**
- **理由**：这是 KPAX 知识架构三线之一（社区经验）的现成 drop-in。装上之后先评估稳定性和 ToS 安全性，再决定要不要深度集成进 KPAX。部署模式限制（Chrome 本地）可能需要 KPAX 走"轻前端 + 云 AXL + 用户本地 skill 辅助"的混合架构

---

### [2026-04-16] awesome-ceo —— Ken 个人 + KPAX 知识层候选内容源（2026-04-16 晚 Ken 纠正 cc 的第一判断）
- **链接**：https://github.com/kuchin/awesome-ceo
- **推文来源**：https://x.com/Bitturing/status/2044328380326379618
- **是什么**：awesome-list 格式的 CEO / 创始人资源集合，8 模块（融资 / 产品 / 销售 / 营销 / 管理 / 招聘 / 财务 / 创业），内容来自 YC / a16z / Sequoia 及一线创业者
- **对 AXL / KPAX**（cc 第一版写"不相关"，Ken 纠正）：**这是 KPAX 知识层的候选内容源**。KPAX 不是只吃论文，有三条知识输入线——
  1. 学术论文（arXiv / OpenAlex / Semantic Scholar）
  2. **行业 curated 资源（YC / a16z / Sequoia essays、playbooks）—— awesome-ceo 在这一层**
  3. 社区经验数据（Reddit / 知乎 / Quora，由小伙伴爬虫）
  7 位顾问辩论时从三类调证据。用户问"该不该辞职创业"这类问题时，行业 curated 层可以直接命中。
- **对 Ken 个人**：融资 / 产品 / marketing / 管理翻起来顺手
- **动作**：**track（短期）→ adopt（当 KPAX 开始 ingest curated 知识源时）**
- **理由**：**cc 第一版判断"skip 项目"是因为把 KPAX 窄化成了只吃学术——错**。这是一条需要回头修的认知：KPAX 知识架构 = 论文 + 行业 curated + 社区经验 三线并行。awesome-ceo 在第二线里是一个完整的种子清单
- **后续**：需要在 `notes/research.md#seven-layer-memory-design` 或新建 `notes/research.md#kpax-knowledge-source-architecture` 把三条线写清楚

---

### [2026-04-16] Claw3D — 3D virtual office for AI agents（KPAX 最直接的正面参照物）
- **链接**：https://claw3d.ai / @claw3dcity / @iamlukethedev（Luke The Dev，Christian / Dad / Farm life）
- **推文来源**：https://x.com/iamlukethedev/status/2044523804718755890 （2026-04-15，Sims mode 发布）
- **是什么**：开源（MIT）3D 虚拟办公室。AI agents 作为卡通角色在等轴测办公场景里可视化工作。用户拖拽浏览 / 跟随 agent / 和 agent 直接聊天 / 调家具布局。已展示：code review（PR 可视化）/ daily standup 围桌开会 / ticket 进度。自托管可用，$29/月托管版 coming soon。
- **对 AXL / KPAX 有没有用**：**这是 KPAX 座谈会方向的最直接外部参照物**。四条：
  1. **市场信号**：有人独立得出"3D 空间 > 聊天"的判断——Ken 直觉被外部验证，不是孤立猜想
  2. **产品不重合**（表见文档）：Claw3D = 开发团队 B2B + 监控 agent 持续工作 + 卡通 Sims 风 + 订阅；KPAX = 普通人决策 C2C + 观看顾问团当场论证 + 维多利亚 UE5 + 代币。核心叙事："我有员工" vs "我有智囊"
  3. **他们开源，实操参考价值巨大**。可抽取复用的模式：3D 场景图组织 / agent-to-avatar 绑定 / "跟随 agent" 相机逻辑 / 家具可拖拽交互 / 实时 agent 状态可视化
  4. **差异化提示**：Claw3D 没碰多学科碰撞 + 结构化判决 + Victorian 学术质感。KPAX 的锐利差异在这里
- **对 Ken 个人有没有用**：看 Luke The Dev 开源社区型 solo dev 项目的演进，作为"solo 做 3D AI 产品"的节奏参照
- **动作**：**adopt（架构级参考）+ track（产品演进）**
- **理由**：这是 KPAX v0 开发前必读的实现参照。**不抄他们卡通渲染**（风格差异大，shader / material 不能直接用），**抽取他们的架构层**（场景图 / state machine / 相机跟随 / 交互模式）。建议 KPAX v0 Week 1 Day 1 花 2-3 小时读他们 repo，写入 kpax-v0 设计文档 §4 技术栈。

---

### [2026-04-16] Anthropic claude-cookbooks（38.9k⭐）
- **链接**：https://github.com/anthropics/claude-cookbooks
- **推文来源**：https://x.com/rwayne/status/2044738322988232718 （@rwayne，2026-04-16 上午 4:23）
- **是什么**：Anthropic 官方 notebook 示例库。目录：`capabilities/`（classification / RAG / summarization）/ `tool_use/` / `third_party/`（Pinecone 等）/ `multimodal/` / `misc/`（sub-agents / moderation filters / JSON mode / prompt caching）/ `claude_agent_sdk/` / `extended_thinking/` / `patterns/agents/` / `skills/` / `finetuning/`。
- **对 AXL / KPAX 有没有用**：不是可集成工具，是参考库。四个场景会直接用到：
  1. KPAX `question_classifier.py` 接真 LLM → 看 `capabilities/classification`
  2. AXL debate_engine pattern review → 看 `patterns/agents/` + `misc/sub-agents`
  3. AXL deep-depth 深推演 → 看 `extended_thinking/`
  4. KPAX report_generator tool use → 看 `tool_use/` + `claude_agent_sdk/`
- **不直接解决的问题**：多 agent cross-discipline debate with Opus moderator synthesis（AXL 独门设计）、七层记忆、agent evolution——cookbook 都没覆盖。我们还是在做 Anthropic 官方没做的地方。
- **对 Ken 个人有没有用**：Claude 相关代码的"查 Anthropic 官方怎么写"默认起点。开发效率提升。
- **动作**：**track + bookmark**
- **理由**：参考库性质，不是工具。下次写 Claude 相关代码前先翻对应 notebook，避免重造轮子。

---

### [2026-04-16] Qwen3.5-9B-GLM5.1-Distill-v1
- **链接**：https://huggingface.co/Jackrong/Qwen3.5-9B-GLM5.1-Distill-v1
- **推文来源**：https://x.com/berryxia/status/2044792772100853842 （Berryxia.AI 转引 @leftcurvedev_）
- **作者**：Jackrong（HuggingFace），之前蒸馏过 Claude Opus 4.6 得到 Qwopus
- **是什么**：9B 参数开源模型，用 GLM-5.1 reasoning 蒸馏，声称推理深度超基础版，**8GB VRAM 可跑**，MLX 原生版已发。27B 大版本在路上。Benchmarks 未发。
- **对 AXL / KPAX 有没有用**：不立刻 adopt，但 track。三个潜在角色：
  1. 本地 L3–L6 记忆层候选模型（对应 `notes/research.md#wisland-analysis-and-positioning` B.10）
  2. structured tagger 的 base model 候选（对应 wisland note B.6，pilot 后云租 GPU 微调 tagger 的方向）
  3. 开发期本地 mock AXL（写 KPAX 时避免 API 钱）
  - **不能当 judge**：Ken 硬规则 judge 能力 ≥ 被判模型，9B 判 Opus 太弱
- **对 Ken 个人有没有用**：作者 Jackrong 是一个值得关注的连续产出者（之前 Qwopus 蒸馏 Opus，现在干 GLM-5.1）。留意他 HF 主页未来动向。
- **动作**：track
- **理由**：真实表现未知（benchmarks coming soon）；AXL pilot 阶段用 API 模型够用；但如果 pilot 之后做 local tagger，这是候选池的必看项。

---

---

## 已落地的成果速查（adopt 状态）

*（空。第一个 adopt 进来后这里同步一行。）*

---

## 市场信号（和工具分开，用于决定 GTM 时机）

Ken 2026-04-16 说："和项目无关，和市场有关，决定我们什么时候推向市场"——这类记录和工具 radar 分开。定期更新，供 KPAX v0 上线时机参考。

### [2026-04-15 快照] BTC True Market Mean 状态
- **来源**：https://x.com/CryptoVizArt/status/2044645603355885635 / Glassnode TMM 指标
- **TMM 定义**：活跃投资人平均成本基准 = Investor Capitalization / (Liveliness × Circulating Supply)。过滤死币 / 休眠钱包 / Satoshi 份额
- **当前状态**（截至 2026-04-15）：
  - BTC 于 2026-01-31 跌破 TMM，现已 **75 天**
  - max 回撤 -20%，当前 -5%
  - 轨迹**比历史同期均值温和**，但 75 天**仍早**（历史底部 5-9 月）
- **历史对照**：2018-19 熊（-57% / 282 天）/ COVID 2020（-40% / 49 天）/ 2022-23 Luna-FTX（-56% / 339 天）
- **对 KPAX GTM 的解读**：
  - KPAX 有代币经济 + 钱包身份 → 加密市场情绪直接影响用户接受度
  - 底部附近用户更警觉 + 更愿意用"决策工具"（被教训过）；峰值用户 FOMO 冲昏头
  - 如果 2026 Q2–Q3 真是底部区间，**KPAX v0 给朋友测试的窗口可能在这附近**
  - 信号是"watch closely"，不是"all clear"——不急着上，但别睡过去
- **下次更新触发**：BTC 重回 TMM 之上 OR 最大回撤突破 -30% OR Ken 给新信号

---

---

*最后更新：2026-04-15 晚。文件建立人：claude-code。*
