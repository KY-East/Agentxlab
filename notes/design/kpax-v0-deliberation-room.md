# KPAX v0 — 座谈会形态设计（Deliberation Room）

**日期**：2026-04-15 晚
**设计人**：Ken + cc 对话产出
**状态**：v0 设计锁定主结构；美术风格待 Ken 拍
**替代方案**：已排除"聊天框"、"卡片 UI"、"全 7 人永远发言"

---

## 1. 核心理念：为什么不是聊天框，不是卡片

**聊天框是 2023–2025 年整个 LLM 生态的默认窠臼**。用户脑子里已经框死"AI = 输入框 + 一段流式文字"。KPAX 的真实价值（15 分钟 / 7 专家 / 碰撞 / 结构化判决）套进聊天框 = 赛车开机动车道。

**卡片也是 AI 默认审美**——更好看的 JSON，仍然是"机器把信息塞进格子"。

**KPAX 要做的是"智囊团"**——用户的真实体感应该是"我召集了一个由 7 位学者组成的顾问团，在书房/会议厅里为我的问题真的吵起来"。

这个形态：
- **过程可见**：用户能看到他付费的 token 在被如何花（7 个人真的在讨论，不是一段文字秒回）
- **慢是特性**：15 分钟不遮掩，让等待变成期待
- **结构天然存在**：桌、椅、发言顺序、分歧、判决——和 AXL 返回的 verdict/estimate/plan + expert_lenses + debate_trace 一一对应
- **记忆有脸**：L2/L6/L7 记忆可视化落在"顾问们记得你"这层体感上
- **差异化极强**：Character.AI 是 1v1 陪聊，Inworld 是游戏 NPC，两者都不做跨学科结构化决策。这个生态位空的。

---

## 2. 7 席的真实意义（实验 vs 产品）

**7 个学科的来源**：`experiments/emergence_decomposition/benchmark_questions.json` 的 `disciplines_baseline`——
- 物理（94）| 数学（1）| 经济（4183）| 心理（3244）| 社科（3396）| CS（1955）| 艺术人文（4515）

**7 = 50 题基准集的覆盖完整集**（跨概率/决策/比较/策略/评估 5 题型、跨领域 10+ 主题），保证任何一题**至少有 2–3 个**学科能说得上话。

**实验里用 7**：为了跑 controlled comparison，每题必须同 7 个。
**产品里不用 7**：每题**只选相关的 3/5/7**（质数，避免 tie，视觉美）。

### 产品侧 UI 策略（2026-04-15 Ken 拍板）

**"满席 + 动态前景"**：

- **7 把椅子是永远在的**（学科完整性承诺）
- AXL 返回的 `expert_lenses` 带相关性权重
- **本场相关的 3 / 5 / 7 位**（质数，由问题性质决定）走到圆桌发言——发言者聚光灯 + 音量正常 + 动画活跃
- **不相关的**留在书房/会议厅里但**退到边上**：
  - 物理学家靠望远镜/在角落翻 arXiv preprint
  - 艺术人文在书架边看诗集/抚摸书脊
  - 数学家在沙盘前画几何/盯着公式走神
  - 经济学家翻账本/看彭博终端
  - 心理学家记笔记/盯着窗外
  - 社科靠在沙发、观察发言者表情
  - CS 看屏幕、手指敲键盘
- **用户可拍肩膀**：走过去点击某个非发言者 → Ta 被动触发**简短视角**（低成本 call，不跑整轮辩论，单次 chat_completion）："哎物理老师，这题你真没想法？" → Ta 给一句话或一段话，然后回座。
- **L7 元进化可见面**：上次你拍了物理老师，这次类似题 Ta 会**主动**说一句（自由参数内部在更新）

### 3 / 5 / 7 怎么决定

- 策略由 AXL `expert_lenses.relevance_score` 阈值决定
- 阈值默认：≥ 0.7 入席，以最近质数 round（3/5/7）为准
- 用户可手动覆盖：**"这题我只要物理和心理"** → 强制 2 人（非质数也允许，用户意愿优先）

---

## 3. 场景：书房（Deliberation Room）

**隐喻**：你的私人顾问书房 / 19 世纪绅士俱乐部 / 佛罗伦萨学院。不是会议室（太正式），不是咖啡馆（太随便）。

**基础布局**：
- 圆桌（象征平等，无主座）
- 7 张风格化座椅（每张略微差异反映学科人格）
- 各自的"第二位置"：书架 / 望远镜 / 白板 / 沙盘 / 窗台 / 沙发 / 办公桌（给非发言者一个有意义的去处）
- 可切换场景主题（未来）：书房 / 中式茶室 / 海边凉亭 / 实验室 / ...

**v0 只做一个场景**：现代感的书房，木质 + 真皮 + 书架 + 大窗户，暖光。

---

## 4. 技术栈（2026 年拼装，不自造）

### 4.1 环境渲染：Spark 2.0（2026-04-14 World Labs 开源）

World Labs 2 天前刚发的 3D Gaussian Splatting 的浏览器级流式渲染器，R3F 可直接集成。

- **场景**：手机扫一个真实书房 → photogrammetry → .RAD splat 格式 → Spark 流式渲染
- **优势**：照片级真实感、100M+ splat 场景、渐进加载、WebGL2 + LoD 原生支持、移动端稳
- **原生支持 "composite worlds"**：splat 环境 + 传统 rig mesh 角色可混渲

### 4.2 角色：**图 → 可动画角色一步到位**（AI 2.0 栈）

不是 2022 年的 "生成 mesh → Mixamo 手动 rig → 接动画" 三步工作流。2026 年一张图直接出**带骨骼可动画**的 3D 角色，5 分钟/人：

- **图 → 3D 角色（带骨骼）**：**Rodin Gen-1 / Meshy 4 / Tripo 2 / Hunyuan3D 2 / CharacterGen** 任选，每角色 $10–30
- **面部驱动**：**NVIDIA Audio2Face-3D** 或 **Meta Audio2Face** 或 **Hedra**——**音频进、表情+唇形出**，不需要手动做 visemes
- **身体动画**：Mixamo 免费动作库 fallback；或更现代的 **DeepMotion Animate 3D**（视频→动画）
- **NPC 行为智能**：我们的 AXL `debate_engine` 作为灵魂 API，**Inworld AI / Convai** 做行为表达层（闲时姿态、接收问题时 tension buildup）—— v0 可不用，v2 再接

**这层被我反复错估**：2026 的 commodity 栈里，"给一张图拿到一个能动能说的游戏级 NPC"已经是 $20 + 5 分钟的事。Meshy/Rodin 自带的 rig 兼容 Mixamo，拿 Audio2Face 做口型，端到端 tooling 成熟。

### 4.3 语音

- **7 voices**：ElevenLabs voice library 挑 7 把特色嗓子（男女老少、中外口音、温厚/尖锐/沉稳/跳跃区分度）
- **TTS**：ElevenLabs 流式
- **空间音频**：Web Audio API PannerNode，声音从 agent 所在位置发出

### 4.4 前端框架

- **React Three Fiber + @react-three/drei**（Three.js React 封装，生态最成熟）
- **状态管理**：Zustand（轻量，和 R3F 生态契合）
- **路由**：Next.js app router（未来 SSR 分享页需要）

### 4.5 后端

- **AXL**（已有）：debate_engine + 7 学科 agent + moderator Opus + memory + free params
- **KPAX**（骨架已有，需要接实际）：
  - `axl_client.py` HTTP 调 AXL（✓）
  - `token_ledger.py` 代币账本（✓）
  - `question_classifier.py` 题型判别（需要接真 LLM）
  - `context_collector.py` 上下文追问（需要读文件定现状）
  - `expert_builder.py` 动态选学科（需要做 relevance_score 逻辑）
  - `report_generator.py` 包装结构化输出给前端（需要读文件定现状）
  - `v1_analyze.py` router（✓）

### 4.6 代币 + 钱包

- **v0 中心化记账**（`token_ledger.py` 已实现），不上链
- 钱包即身份：用 Web3 wallet connect（RainbowKit / wagmi），签名登录
- 种子 50 token / 消费 quick=10 / standard=25 / deep=60 / 分享奖励 20
- **预留链上接口**（`ChainAdapter` 已抽象），Phase 2 上 Solana 或 Base

### 4.7 外部架构参考：Claw3D（2026-04-16 cc 深读开源 repo）

`iamlukethedev/Claw3D`（MIT，Next.js 16 + React 19 + R3F 9.5 + Drei 10.7 + Phaser 3.90 + Three.js 0.183 + ws 8.18）是目前对 KPAX 座谈会方向最直接的参照。他们不是真 3D——主"3D retro office" 实际是 **Phaser 2D 等轴测**（Arc 圆点 + Text 标签 + A* 寻路）。Three.js 在 deps 里但核心场景没用到。

**可直接借鉴的抽象层**（不抄渲染）：

1. **Scene Bridge 模式**（`OfficeSceneBridge.ts`）：极简 observer pattern，getState / setState / subscribe 三方法桥接 React state 和 Phaser/R3F 场景。30 行代码，不用 Redux。KPAX 直接照搬给 R3F 用。

2. **Systems 架构**（`phaser/systems/`）：每个关注点独立 System 类，每帧 `update(state, delta)`。Claw3D 有 LightingSystem / AmbienceSystem / AgentEffectsSystem 三个。KPAX 翻译：
   - `SpotlightSystem`——聚光灯跟发言者
   - `HeadIKSystem`——其他顾问头部朝向当前发言者（R3F `@react-three/drei` 的 `useLookAt`）
   - `LipSyncSystem`——NVIDIA Audio2Face-3D 驱动嘴型
   - `DebateRoundSystem`——Round 1→2→3 推进
   - `ChamberAmbienceSystem`——烛光摇曳 / 烟气 / 时钟秒针
   - `VerdictSystem`——判决书浮现

3. **Agent state → visual 映射** (`AgentEffectsSystem.ts`)：Claw3D 用颜色编码 working(绿) / meeting(蓝) / error(红) / idle(黄)。KPAX 对应：
   - listening（侧耳）/ speaking（聚光）/ thinking（沉思）/ agreeing（点头）/ dissenting（摇头）/ dismissed（退到 second position）

4. **Hooks 分离**：`useRemoteOfficePresence` / `useRemoteOfficeLayout`——backend 数据 → React state 的单一 hook。KPAX 对应：
   - `useDebateStream`——AXL `/axl/v1/analyze/*` 的 debate_trace 流式数据
   - `useChamberLayout`——7 座位 + 第二位置 + 氛围元素
   - `useExpertPresence`——当前在场的顾问列表（7 or 3/5）
   - `useVerdictComposer`——moderator 判决文的流式呈现

5. **Procedural textures**（Phaser 写法，Three.js 类比：自建 `THREE.CanvasTexture` / `NodeMaterial`）：减少 asset loading 重量。书房里一些重复纹理（木纹 / 皮革）可以 procedural。

**明确不抄的**：

- **Phaser 2D 方向**：KPAX 要 Victorian UE5 质感，Phaser 做不到。R3F 才对。
- **Studio 中间层 + WebSocket 代理**（`server/`）：Claw3D 需要因为他们连多种 runtime。KPAX 是 HTTP 调 AXL 一家，不需要。
- **A* pathfinding**：Claw3D agents 持续走动。KPAX 顾问大多坐着，只在状态切换（入席 / 回第二位置）时需要简单插值，不需要 A*。
- **agents 用 Arc circle**：我们 v0 从头就要 GLB rigged mesh。

**立即可拿来用的代码量估计**：OfficeSceneBridge.ts（30 行）+ Systems 架构模板（300 行）+ presence/layout hook 模式（200 行）≈ 500 行"免费"架构模板。**我们应该从 Day 1 就按这个骨架起步**，不是自己从零试。

---

## 5. 一次使用的完整脚本（用户视角）

```
[0'00] 打开 kpax.xyz
       → Spark splat 书房场景秒开（LoD，先粗后精）
       → 7 张椅子上 7 位顾问已坐好（或各自在第二位置）
       → 钱包条显示：连接钱包 / 已有 50 token

[0'10] 用户连接钱包（只第一次）
       → 7 位顾问转头看你（头部 IK 追踪）
       → "Hello, 欢迎回来"（若老用户）或 "第一次见面"（新用户）

[0'30] 用户在输入框打字："孩子 8 岁该不该大量用 AI 辅助学习？"
       → [KPAX] classifier 判 type = decision
       → [KPAX] expert_builder 选学科（relevance_score）
       → 返回：心理 0.92 / 社科 0.85 / CS 0.78 / 艺术人文 0.71 / 经济 0.45 / 物理 0.12 / 数学 0.08
       → 5 人入席（前 5 relevance > 0.7），2 人继续留在原位

[1'00] 钱包条 10 token 扣费动画
       → 5 位入席者各自露出"开始思考"姿态
       → Round 1 立场陈述：每位 streaming TTS，其他人眼神转向发言者
       → 用户可俯视全场 or 推近到某位（点击头像）

[6'00] Round 2 交锋：agent 之间互相点名
       → 视觉表现：说话人之间出现细线（连接），赞同绿光、反驳红光
       → 鼠标悬停连线：显示这次攻击的核心原话

[11'00] Round 3 综合 + Claude moderator 判决
        → 桌子中央浮现"判决书"UI：结论 / 共识 / 分歧 / 未解决
        → 每条后标注 [5/5 共识] / [3 vs 2 分歧 - 主导: 心理]
        → 钱包条显示本次消耗 + 余额

[12'00] 用户可选动作：
        → "有帮助" → +20 token 奖励（分享）
        → "不准确" → 反馈（L5 反思记忆写入）
        → "拍 CS 老师肩膀"（走向角落坐在电脑前的 CS）
          → Ta 抬头："你要我也说两句？" → 简短视角 (2 token)
        → "下一题" → 开新轮

[历史页] → 侧栏查看过往讨论
        → 每条有时间 / 结论 / 当时哪些顾问上场
        → **L6 人格可见**："根据你过去的提问，你倾向保守决策 / 重视心理学视角 / ..."
        → **L2 情节**："3 个月前你问过类似的问题（高考选专业），当时结论是 X"
```

---

## 6. v0 三周落地计划

### Week 1 — 场景 + 角色（2026 AI 2.0 栈，并行）

**Day 1–2：并行起步**
- **场景**：Spark 现成 captured_space demo 先接通（R3F 集成验证）；同步 Ken 用 Polycam 扫真实书房备用
- **角色**：Ken 用 Grok 生 7 张 portrait（视觉锚 §7.1，人物 prompt §7.2），挑稿

**Day 3–4：图 → 可动画 3D**
- 7 张定稿 portrait 分别丢 Rodin Gen-1 / Meshy 4 / Tripo 2（对比哪个 rig 质量高），每角色 5 分钟
- 产出：7 个 `.glb` 文件，带标准骨骼 + blend shapes for Audio2Face

**Day 5–7：场景合成**
- R3F + Next.js + Spark 2.0 起基础 scene
- 7 椅围桌摆位，7 个 .glb 模型坐上
- 相机：俯视悬浮 + 可拖拽环视

### Week 2 — 动画 + 交互

**Day 8–10：动画绑定**
- Mixamo 动作库导入：idle_sit / thinking / speaking_gesture / nod / shake
- 对每个角色绑四套基础动作
- 头部 IK：发言者说话时，其他人头部朝向 Ta（R3F `@react-three/drei` 的 `useLookAt`）

**Day 11–14：交互**
- 点击头像 → 相机推近，显示 Ta 当前论点
- AXL HTTP 接通：`/axl/v1/analyze/{type}` 真实调用
- 返回的 `debate_trace.messages[]` 按时间线播放（不是一次性塞进来，是**按真实时长渐进展开**）
- 钱包条 + 扣费动画

### Week 3 — 声音 + 判决 + 判决书 UI

**Day 15–17：TTS + 面部驱动 + 空间音频**
- ElevenLabs 7 voices 选定（按 §7 声音预期）
- 发言者消息走 TTS 流式
- Web Audio API 空间化（声音从角色位置发出）
- **面部驱动**：NVIDIA Audio2Face-3D 或 Meta Audio2Face，**音频直接喂**，自动出唇形 + 微表情。不做手工 visemes。

**Day 18–21：Moderator 判决 + 收尾**
- Claude Opus 判决文以"法官 / 主席"形式（空的第 8 椅？或从天而降的悬浮卷轴 UI）
- 判决书渲染：结论 / 共识 / 分歧（标注 X vs Y）/ 未解决
- 钱包奖励：分享按钮 +20 / 反馈按钮（L5 写入）
- "拍肩膀"交互：点击非发言者 → 简短视角
- 历史页：L2 情节 / L6 人格 render

### 预算（v0）

| 项 | 成本 |
|---|---|
| Meshy 7 × ~$20 | ~$140 |
| ElevenLabs | $22/mo |
| 场景资产 / 扫描 | $0–100（看用哪个） |
| Spark 2.0 | 开源 $0 |
| 实验测试 token | ~$20 |
| **v0 一次性** | **~$200–300** |
| **月流水**（ElevenLabs）| ~$22/mo |

---

## 7. 7 人最终阵容（Ken 2026-04-15 晚拍板）

**构成**：5 男 2 女，2 位东亚（数学 + CS），**不要印度裔**（避免刻板印象）。全员维多利亚 19 世纪末欧洲学界背景，**东亚人物以"留学欧洲的晚清/明治学者"**身份在场，世界观统一。

| # | 学科 | 原型 | 性别 / 年龄 / 地域 | 第二位置（非发言时）| 声音预期（ElevenLabs）|
|---|---|---|---|---|---|
| 1 | 物理 | **剑桥老教授** | 男 65 / 英 | 黄铜望远镜 + 星图 | 低沉温厚男声，慢 |
| 2 | **数学** | **格廷根留学东亚女数学家** | 女 24 / 东亚（晚清/明治）| 黑板前沾粉笔 / 小算盘 | 清澈锐利女声，少话 |
| 3 | 经济 | **伦敦 City 银行家** | 男 45 / 英 | 账本 + 怀表 + 白兰地 | 冷峻中年男声 |
| 4 | 心理 | **维也纳女精神分析师** | 女 32 / 奥（Freud 圈）| 皮笔记本 + 沙发 | 温和女声，有穿透力 |
| 5 | 社科 | **巴黎左岸学者** | 男 50 / 法 | 多语种手稿堆 + 红酒 | 沉稳中年学者男声 |
| 6 | **CS** | **明治/晚清电气工程师（留学 Glasgow）** | 男 35 / 东亚 | 黄铜电气装置 / proto 电脑 | 务实年轻男声 |
| 7 | 艺术人文 | **法国颓废派男诗人**（Rimbaud / 青年 Baudelaire 类型）| 男 22 / 法 | 波斯地毯赤脚 + 诗集 + 烛台 | 中性低语男声，有戏剧性 |

**性格关键词 / 说话风格**（作为 agent prompt 层可用）：

| 学科 | 性格 | 说话习惯 |
|---|---|---|
| 物理 | 本源主义 / 严谨 / 略冷 | "让我们先看能量守恒..." |
| 数学 | 洁癖 / 抽象 / 挑剔 | "这个问题可以形式化为..." |
| 经济 | 理性 / 权衡 / 冷静 | "成本和收益两边看..." |
| 心理 | 共情 / 洞察 / 温和 | "人在做决策时常常..." |
| 社科 | 怀疑 / 结构 / 批判 | "制度怎么塑造这个行为..." |
| CS | 务实 / 直接 / 技术 | "从工程可行性看..." |
| 艺术人文 | 诗意 / 反叛 / 深邃 | "这里其实是一个意义问题..." |

### 7.1 视觉锚（所有角色与场景共享）

> *An opulent Victorian-era private study. Heavy mahogany + leather club chairs, brass studwork, leaded-glass windows, oil lamps, cigar smoke haze, oriental rug. Style: **"Black Myth: Wukong" game quality** — photorealistic PBR textures, physically accurate lighting, cinematic rim lighting, ultra-detailed materials (leather grain, wood wear, metal patina), **Unreal Engine 5 quality**. Mood: gravitas, centuries of accumulated thought, slight melancholy.*

每张角色 portrait prompt 都以此**完整段**作为视觉一致性锚，确保 7 张是"同一个世界的人"。

### 7.2 7 张角色 portrait prompts（生成用）

**每张 prompt 结构** = 人物描述段 + 视觉锚段。详见对话记录 2026-04-15 晚。
要素清单：

1. 物理 — 65 岁银发英国物理学家，绿皮翼背椅，烟斗，黄铜望远镜旁
2. 数学 — 24 岁东亚女性（改良唐装学者袍），木凳，手沾粉笔，微分方程黑板
3. 经济 — 45 岁英国绅士银行家，炭灰三件套，金怀表链，Bank of England 文件
4. 心理 — 32 岁奥地利女性，赤褐发盘低髻，深色天鹅绒高领裙，珍珠，皮笔记本
5. 社科 — 50 岁法国知识分子，乱发灰丝，学者袍，多语手稿，红酒
6. CS — 35 岁东亚男性（明治/晚清工程师），卷袖工装背心，黄铜 proto-computer 原型机
7. 艺术人文 — 22 岁法国颓废派男诗人（Rimbaud 质），乱发，松领白衬衫 + 黑天鹅绒外套，红丝巾，赤脚坐波斯毯

---

## 8. 自进化（L7 元进化）在 UI 上的可见面

L7 是 Ken 相对 WisLand 的核心差异点，不能是黑箱。在 KPAX 前端具体体现为：

1. **顾问个性渐变**：用户和 Ta 互动越多，Ta 的**回复风格倾向** / **发言积极性** 会微妙变化（不是剧烈漂移）
2. **学科选择的解释文案**：每次 expert_builder 选学科时，UI 显示一句话："这次选了经济+心理+社科，因为过去 N 次类似问题里这三个学科的冲突给过更锐利的结论"
3. **历史页"成长"面板**：显示顾问团整体的 fitness / diversity 等自由参数在时间序列上的变化（可选高级用户打开）

---

## 9. 不做的事（v0 scope 之外）

- ❌ 实时语音打断 / barge-in（v3，需要 STT + 中断协议）
- ❌ 角色间长期关系建模（v4，L6/L7 先存数据不在 UI 暴露）
- ❌ 多场景切换（v0 只做一个书房）
- ❌ 移动端优化（桌面先，手机 v2）
- ❌ 自建 3D pipeline（任何一步要自己写 shader 就停问 Ken）
- ❌ 上链代币（v0 中心化，Phase 2 再 Solana/Base）

---

## 10. 待决策 / 待验证

- [x] 美术风格锚定 → **维多利亚黑神话 UE5 写实质感**（Ken 2026-04-15 拍板）
- [x] 7 人阵容 → **5 男 2 女 + 2 东亚（数学 + CS）**，不要印度裔
- [ ] Ken 用 Grok 按 §7.2 prompts 生 7 张 portrait，挑稿
- [ ] **Spark 2.0 实测**：cc 跑一遍 sparkjs.dev demo，验证 R3F 集成真流畅
- [ ] **Rodin Gen-1 vs Meshy 4 vs Tripo 2 对比**：同一张 portrait 丢三家，看哪家 rig 质量最高。cc 第一周做。
- [ ] **书房场景来源**：Spark 现成 captured_space 先用；Ken 有空扫自己书房换上
- [ ] **钱包方案**：RainbowKit + wagmi（EVM）起步；Solana 等到代币上 dex 再加

---

## 11. 关联文件

- `KPAX.md` — 产品承诺与硬规则
- `projects/knowledge-graph/backend/app/routers/kpax_api_spec.md` — AXL HTTP API v1.1
- `projects/knowledge-graph/backend/app/routers/kpax_router.py` — AXL mock router（v0 要换成真 debate_engine 调用）
- `notes/research/seven-layer-memory-design.md` — L1-L7 记忆体系
- `notes/research/agent-evolution-free-parameters.md` — 5 类自由参数（在 AXL 层）
- `notes/research/` 下的对位分析笔记（项目研究上游，非对外定位参考）

---

*记录：claude-code，基于 2026-04-15 晚 Ken 与 cc 对话。任何形态修改必须回来改这份文档 + journal 加一条。*
