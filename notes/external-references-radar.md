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
