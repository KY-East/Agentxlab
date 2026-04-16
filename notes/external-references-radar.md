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
  1. **Zep 刚从"memory"改名"context engineering"**——AXL 七层记忆建在 Zep 上。我们现在的 backend 供应商自己在改造，必须读他们 Graphiti framework 新 positioning，更新 `notes/research/seven-layer-memory-design.md` 的 backend 部分
  2. **OpenClaw 的 6 个加权信号**（relevance 0.30 / frequency 0.24 / query diversity 0.15 / recency 0.15 / consolidation 0.10 / conceptual richness 0.06）= **AXL 自由参数 L7 元进化的理论默认值**。别人 hard-code，AXL 在做让它可学习。直接写进 `agent-evolution-free-parameters.md`
  3. **compounding benchmark 的空缺** = AXL 护城河的直接对位。emergence_decomposition 实验的**下一个天然续作**可以做 `compounding_gain_benchmark`，是学术论文的真正立足点
  4. **Thoth 的 4 阶段 dream cycle**（duplicate merging 0.93 sim / enrichment / relationship inference / confidence decay 90 天）——比 AXL 当前 session 压缩完整。Phase 3 设计必须参考
  5. **ALIVE 项目**（作者自己在做）是一个正在行动中的 Camp 2 实作，值得深挖
- **对 Ken 个人有没有用**：
  - witcheer 是一个值得长期关注的研究型作者（Mac Mini M4 的 24/7 agent setup 本身就是实践性深研）。她的 Telegram @witcheergrimoire 每日有高质量 AI + DeFi 信号
  - 这篇是 AXL 研究论文 literature review 的**必收录参考**
  - 提到的"文件即记忆"哲学呼应 AXL MEMORY.md 现状（本地 memory 本就是 markdown）
- **动作**：**adopt**（研究输入，要写进 research notes）+ **track**（Zep rebrand / ALIVE / Thoth 三个子链）
- **理由**：这不是个工具链接，是整个记忆工具生态的地图，并且指出了**现有 benchmark 的根本缺陷 = AXL 护城河的立足点**。必须马上：(a) 把 Zep rebrand 信息加进 seven-layer-memory-design.md，(b) 把 OpenClaw 6 信号加进 agent-evolution-free-parameters.md，(c) 把 compounding benchmark 作为 emergence_decomposition 的续集候选加进 notes/agenda/next.md P2

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
  1. 本地 L3–L6 记忆层候选模型（对应 `notes/research/wisland-analysis-and-positioning.md` B.10）
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

*最后更新：2026-04-15 晚。文件建立人：claude-code。*
