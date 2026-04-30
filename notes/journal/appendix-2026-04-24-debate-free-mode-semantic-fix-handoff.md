# free 模式语义分叉 — 修复方案待 cc 裁定

**状态**：2026-04-24 三方诊断一致、GPT 给出最终修法、cursor 补三条工程细节，等 cc 战略层最终裁定后 cursor 开干。

**类型**：方法论级决策（PROJECT.md §11.3 五类自动留档之一）

**触发者**：@ken 2026-04-24 发现 Debate 12（mode='free'）输出和 Debate 10/11（mode='debate'）几乎一样

---

## 一、问题陈述

Ken 2026-04-24 原话：
> "我突然发现一个问题，我选的是自由辩论，怎么和正反方向的辩论出的内容一模一样。"

UI 上 `free` 和 `debate` 是两个按钮，用户预期对应"自由讨论"和"结构化辩论"两种产品形态。实际输出看不出区别——这是**承诺失信**。

---

## 二、证据链（三层独立核实）

### 2.1 数据库证据

```
Debate #10  mode=debate  agent stance = discipline_advocate × 6
Debate #11  mode=debate  agent stance = discipline_advocate × 6
Debate #12  mode=free    agent stance = None × 6
```

按钮生效了（DB 里 mode 字段正确写入，stance 字段确实分流），但**只少一段 stance 文本**。这是 GPT 2026-04-24 的 DB 预言，cursor 跑 `scripts/_check_mode_diff.py` 查实成立。

### 2.2 后端代码证据（行号精确）

**证据 A — Round openers 不看 mode**（`debate_engine.py:1015-1016`）：
```python
opener_map = ROUND_OPENERS.get(current_round, DEFAULT_ROUND_OPENER)
round_opener = opener_map.get(lang, opener_map.get("en", ""))
```
`ROUND_OPENERS` 内容（L271-287）在 Round 2 明确要求：
- "攻击其他学科的 1-2 个具体论点，解释为什么他们的框架**在这个问题上**不够"
- "回应其他学科对你的质疑——用证据反驳或坦然承认不足"

**free 模式的 agent 同样收到"攻击其他学科"这条指令**。

**证据 B — Agent 使命段不看 mode**（`debate_engine.py:383-384` 中文、L446-447 英文）：
```python
parts = [
    f"你是{rank_info['zh']}，专攻 **{discipline_name}**，参与一场跨学科学术辩论。",
    f"参与辩论的学科有：{topic}。",
    f"\n## 你的使命\n你代表 **{discipline_name}** 参战。你的对手是来自 **{others_str}** 的学者。",
    f"你需要证明你的学科视角对这个问题不可或缺，同时直接质疑其他学科的局限性。",
    ...
]
```
**这段无 `if mode` 判断，free 和 debate 都注入**。"参战 / 对手 / 不可或缺 / 质疑局限"——对抗心智 80% 来自这里。

**证据 C — Mode 唯一硬分支只有一段 STANCE**（`debate_engine.py:428-429`）：
```python
if mode == "debate" and stance and stance in STANCE_PROMPTS:
    parts.append(f"\n## 立场\n{STANCE_PROMPTS[stance]['zh']}")
```
`STANCE_PROMPTS["discipline_advocate"]["zh"]` 约 80 字。这是 debate 比 free 唯一多的文本。

**证据 D — Moderator prompts 不看 mode**（`debate_engine.py:218-233` + `314-351`）：
`MODERATOR_PROMPTS` 和 `MODERATOR_ROUND_OPENERS` 写死为"跨学科**辩论**的**导演**"、"指出谁真在回答 / 谁绕回舒适区"、"最出人意料或最有想象力的一步"——这些都是裁判 / 评分心智，free 模式下同样触发。

### 2.3 前端代码证据

**证据 E — `Debate.tsx:153-158` 的 useAcademic 不看 mode**：
```tsx
const inputText = proposition.trim();
const discoveryOriginal = (navCtx.discoveryQuestion || "").trim();
const rawUser = discoveryOriginal || inputText;
const academic = suggestion?.suggested_proposition?.trim();
const useAcademic = !!(academic && academic !== inputText);
const finalProposition = useAcademic ? academic : inputText;
```

只要用户点过"AI 推荐"得到 `suggested_proposition`，而输入框里不是改写版（含用户根本没点"采用此改写"按钮的情况），`finalProposition` 就**默默**变成 AI 学术改写。**raw_question 字段是保真的（之前的修复成果），但 proposition 字段在暗中被替换**。

**Debate 12 的实际 DB 状态就是这个 bug 的产物**：
- `raw_question = "实验本身能否找到共性，并高度抽象，形成能够解决大部分实验设计的公式？"` ← 原话
- `proposition = "开发一个元框架，利用最优设计原理和数值方法，为给定类别的实验自动生成通用公式。"` ← AI 改写

Ken 从没点过"采用此改写"，但后端实际吃了改写版。

---

## 三、三方诊断对比（全保留，@ken 规则）

### 3.1 Ken 原始发现（2026-04-24 上午）
> "自由辩论和正反方辩论内容一模一样，先检查原因。"
>
> "AI 味的问题、引用的问题不是最大的问题，最大的是最终答案——哪怕没答案，也要给模拟沙盘或推演实验的设计。"

### 3.2 GPT 诊断（第一稿）
三条根因：
1. 后端 round 指令完全共用（行号 1018 偏但结论对）
2. Agent system prompt 底层使命几乎一样（L354 起），唯一差异是 L428 的 stance block
3. 前端 free 模式也可能继续带 academic proposition（`Debate.tsx:153`）

### 3.3 cursor 补充（独立核对 + 行号精确化）
- #1 行号应为 1015（opener_map 取值行），1018 是 moderator_opener_map 取值行——结论相同
- #2 cursor 2026-04-23 修 P0 时已查过 L428，但**没抓到 L383-384 使命段无 mode 分支**这个更深层问题——GPT 这条提醒到位
- #3 cursor 2026-04-17 修"原话丢失"时已把 `raw_question` 字段做保真，但**没审查 proposition 字段**——GPT 抓到的是保真修复的盲区

### 3.4 cursor 给 ken 的补三条（GPT 没展开的）
- **(a) 使命段必须也分叉**：只改 Round openers 不够，否则 system prompt 顶端"参战/对手"和 Round opener"协作延展"会把 agent 撕裂
- **(b) Moderator 在 free 下要改角色心智**：从"导演/裁判"改为"协调者/推演主持"——不评"最有想象力"、不点名"绕回舒适区"
- **(c) 前端 useAcademic 是 mode-independent bug**：不是 free 模式专有，debate 模式下也会暗中替换，应一并修

### 3.5 GPT 最终反馈（第二稿，基本采纳 cursor 补三条）
- (a) 确认："只改 round opener 会让 system prompt 叫打仗、round opener 叫协作，agent 会变怪不会变自由"
- (b) 确认："prompt 里要从导演/裁判/点名谁偏题改成协调者/推演主持/连接观点"
- (c) 确认：按 cursor 升级版执行

### 3.6 Ken 拍板（2026-04-24 最终）
> "这份反馈基本是对的，而且比我刚才的结论更完整。"
> "free 模式使命段选 α 协作解题。"
> "这波应该一起修三件：后端 free 独立 agent mission / 后端 free 独立 moderator prompt 和 round openers / 前端 useAcademic bug。"
> "不建议现在做大重构。这个 bug 的修复边界很清楚：让 free 和 debate 的心智分叉。"

---

## 四、拟定改动清单

### 4.1 后端：`debate_engine.py`

**改动 1：agent 使命段按 mode 分叉**（L381-384 / L446-447）

当前（free / debate 共用）：
```python
f"你是{rank_info['zh']}，专攻 **{discipline_name}**，参与一场跨学科学术辩论。"
f"\n## 你的使命\n你代表 **{discipline_name}** 参战。你的对手是来自 **{others_str}** 的学者。"
f"你需要证明你的学科视角对这个问题不可或缺，同时直接质疑其他学科的局限性。"
```

改成条件分支。**free 模式（α 协作解题措辞）**：
```
你是 <rank>，专攻 <discipline>，和其他学科的学者一起推演用户的问题。
参与讨论的学科：<topic>。

## 你的使命
你代表 <discipline>，和来自 <others> 的学者共同把用户的问题推深。
你的学科在这个问题上能贡献什么、不能触及什么，都要诚实说出来。
不是要证明你的学科最重要，而是让用户看到这个问题在多学科视角下的完整形态。
```

**debate 模式保持原样**（参战/对手/不可或缺/质疑局限）——研究者场景需要对抗压力测试。

英文版同步。

**改动 2：新增 `FREE_ROUND_OPENERS`**（放在 `ROUND_OPENERS` 之后）

Round 1-3 不再要求"攻击其他学科 1-2 个具体论点 / 诚实边界 / 最终答案裁决"，改为（draft）：

- **Round 1**：从本学科视角开场，抛出你对用户问题的初步看法和你学科能关心的维度。
- **Round 2**：听过其他学科后，**延展**而非攻击。哪些其他学科的观点让你想到新东西？你的学科如何补充或承接？
- **Round 3**：**共同推演**——不是给最终答案，是给一个可以推进的下一步。用户能拿这个去做什么：一个实验设计、一份观察清单、一个假设待验证、或"这个问题在现阶段还不能给答案，应该先搞清 X"。

**改动 3：新增 `FREE_MODERATOR_PROMPTS` + `FREE_MODERATOR_ROUND_OPENERS`**

Moderator 从"跨学科辩论的导演"改成"跨学科推演的协调者"。行为：
- Round 1：引介问题 + 方向菜单（保留，跟 debate 一样）
- Round 2+：**不评分、不点名绕回舒适区、不标"最有想象力"**。改为：
  - 把本轮讨论组织成"问题地图" / "可能路径" / "待验证假设"的结构
  - 指出下一轮可以推演什么方向（邀请语气，不是派活）
  - 如果看到某个方向已经清晰可操作，总结出来 flag 给用户

**改动 4：`run_round_stream` 根据 `debate.mode` 选 opener / moderator prompt**

```python
# 伪代码
if debate.mode == "free":
    opener_map = FREE_ROUND_OPENERS.get(current_round, DEFAULT_ROUND_OPENER)
    moderator_opener_map = FREE_MODERATOR_ROUND_OPENERS.get(...)
else:
    opener_map = ROUND_OPENERS.get(...)
    moderator_opener_map = MODERATOR_ROUND_OPENERS.get(...)
```

Moderator system prompt 的选择在 `generate_agents` 里（L691），同样条件分支。

### 4.2 前端：`Debate.tsx`

**改动 5：useAcademic 改成"用户显式采用"才生效**

当前（L153-158）：
```tsx
const useAcademic = !!(academic && academic !== inputText);
const finalProposition = useAcademic ? academic : inputText;
```

改成：`finalProposition = inputText`（即 `proposition.trim()`）。

原因：`applySuggestedProposition()` 已经在用户点"采用此改写"按钮时**同步改输入框**（`setProposition(suggestion.suggested_proposition)`）。所以：
- 用户点了 → 输入框是改写版 → `inputText` 自然是改写版 → `finalProposition` 是改写版 ✓
- 用户没点 → 输入框是原话 → `inputText` 自然是原话 → `finalProposition` 是原话 ✓

**完全不需要额外的 `useAcademic` 状态**，去掉这段逻辑即可。这不仅修 free 模式，同时修 debate 模式下同样的暗中替换 bug。

---

## 五、待 cc 最终裁定的点

cursor 工程侧已经可以开干，但有三个战略/产品层的点需要 cc 最终拍板：

### 5.1 free 模式下 moderator 是否保留"在场学科硬约束"段

当前 `MODERATOR_PROMPTS` 里的 "本场在场学科（硬约束）" 段（generate_agents L697-706）是 2026-04-18 修"Moderator 凭空编 5 个学科"那次加的——**这个硬约束对 free 模式同样重要吗？**

cursor 倾向保留：即使 free 是协作心智，"方向菜单只能从在场学科展开"这个约束不改变。但请 cc 确认。

### 5.2 free 模式下 teammate prompt 是否保留"不同流派"定位

2026-04-23 G+F 修 P0 时把 teammate prompt 改成"同学科不同流派"（L414-426）——**free 模式下还有必要吗？**

- 保留：即使协作心智，同学科两人仍然应该分化（Prof 主干 / Assoc 实证边界），否则 P0 雷同问题会回来
- 改写：free 模式下"同学科队友"应该是"不同角度的补充者"而非"不同流派的对照组"

cursor 倾向保留但重写措辞（保留 Prof 主干 / Assoc 实证的分工，去掉"对照组""不是应声筒"之类带张力的词）。请 cc 确认方向。

### 5.3 Ken 早上拍的 P1 顶格 "沙盘 / 推演实验设计" 和本次修复的关系

Ken 2026-04-24 上午拍板 P1 顶格：AXL 产出要从"可读文本"升级为"可推演产物"（模拟沙盘 / 推演实验设计）。

本次 free 模式分叉修复后，Round 3 已经要求 "给一个可以推进的下一步：实验设计 / 观察清单 / 假设待验证"——**这一步本身就是"推演实验设计" renderer 的雏形**。

问题：
- a) 本次 free 修复算作"推演实验设计 v0.1"，Round 3 output 直接作为 renderer 输入？
- b) 本次 free 修复只动 debate 内部 prompt，独立的 renderer 仍然按 Ken 上午的 a/b/c 分叉单独做？
- c) 其他方案？

cursor 倾向 (a)——先用 Round 3 output 做 v0.1，跑几个场景看效果再决定是否做独立 renderer。请 cc 裁定。

---

## 六、回滚路径

**全部改动都是纯 prompt + 前端 useState 逻辑，零 schema 变动**：

1. 撤回后端改动：把 `FREE_ROUND_OPENERS` / `FREE_MODERATOR_PROMPTS` 删掉，`run_round_stream` 恢复不看 mode
2. 撤回前端改动：`finalProposition = inputText` 改回 `useAcademic ? academic : inputText`
3. 使命段 mode 分支恢复为无条件注入

每一项独立可回滚。回滚成本和 2026-04-23 G+F 修 P0 同级（低）。

---

## 七、验证路径（改完后给 @ken 跑）

1. **同题双跑对照**：同一组 3 学科 + 同一个原问题，分别跑 mode=free 和 mode=debate，**输出应该明显不同**：
   - debate：仍然是学科压力测试、互相攻击、最终答案各自磨利
   - free：共同推演、互相延展、最后给可推进的下一步（实验设计 / 观察清单）

2. **DB 字段核实**：free 辩论创建时 proposition 字段**等于** raw_question（除非用户显式点了"采用此改写"）

3. **D1/D2 脚本**：跑 `scripts/check_agent_twins.py` 看 free 模式下 P0 雷同是否还被压住（G+F 修复不能被 free 分叉破坏）

4. **Moderator 心智检查**：人工读 free 模式 moderator 各轮发言，**不应出现**"裁决 / 绕回舒适区 / 最有想象力"等评审词；**应出现**"问题地图 / 可能路径 / 待验证假设 / 下一步推演"等协调词

---

## 八、注记

- 本文档按 PROJECT.md §11.2 内容关键词命名（`debate-free-mode-semantic-fix-handoff`，搜 "free 模式" / "自由辩论" / "useAcademic" / "handoff" 都能命中）
- 本文档按 §11.3 五类自动留档中的**方法论级决策 + 多方观点对照**两个触发条件留档
- 三方诊断（Ken / GPT / cursor）全保留，不压缩
- 修法方案已收敛到 Ken 拍板版本（α 协作解题 + 三件同修）
- cursor 工程侧改动清单待 cc 裁定 5.1-5.3 三个产品层问题后开干
