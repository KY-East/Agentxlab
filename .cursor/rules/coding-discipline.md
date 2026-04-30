---
description: 通用编码纪律（Simplicity First + Goal-Driven Execution），适用于所有写代码的任务。试行期 2026-04-14 起，效果不好再改。
globs: ["**/*.py", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"]
alwaysApply: true
---

# 编码纪律（试行）

两条规则：**Simplicity First** 和 **Goal-Driven Execution**。试行期 2026-04-14 起，效果不好再改。

来源：Karpathy 四条 LLM 写代码通病，经 Ken 讨论后收窄为项目适配版本。

## 一、Simplicity First

写代码时用最少的代码解决当前任务。不写没要求的功能，不加预防性错误处理，不顺手重构相邻模块。

**三个 scope 必须分开**。这条规则**只作用在代码 scope**：

| Scope | 规则 | 何时触发 |
|---|---|---|
| 代码 scope | 严格最小 | 真正在写代码 / 改代码时 |
| 建议 scope | 放宽 | 讨论做法、提替代方案时 |
| 质疑 scope | 强制放宽 | 遇到需求本身可能有问题时 |

**提建议、质疑需求、讨论架构时本规则不生效**。这个分离是为了防止规则退化成"字面最小解释需求"的字典式执行者。

**反模式（禁止）**：

1. 字面最小解释需求："你说改 X，我只改 X，就算我觉得 Y 也应该一起改也不说"
2. 事后补刀："我按你说的做了，但其实更好的做法是 Z——只是你没问我"
3. 预防性代码："以后可能会用到这个参数"
4. 假设型错误处理：没确认这个错误会发生就加 try/except
5. 顺手优化："我改 A 的时候发现 B 写得不好，一起改了"

**正确姿势**：

- 动手前：想得宽。该提的替代方案都提，该质疑的前提都质疑
- 确定方案后：做得窄。只动要动的文件，只写要写的行
- 做完后：不附带"顺便我也改了 X"

## 二、Goal-Driven Execution

多步任务必须拆成带验证点的 checkpoint 执行。每一步有明确的成功判据，不是"感觉做完了"。

**适用**：
- 实验 runner / 数据管道
- 跨多个文件的改造
- 长 horizon 任务（> 3 个步骤）
- 跨 session 接续的工作

**不适用**：
- 单次 edit / 一次 tool call 能解决的小改动
- 纯讨论、纯起草文档
- 研究型笔记

**Checkpoint 结构**：

```
Step 1 → verification method → verification result
Step 2 → verification method → verification result
```

候选验证方法：跑测试 / 读生成的文件 / grep 确认字符串 / 跑命令看输出 / 让 Ken 看结果。

**禁止**："我改好了"作为验证。必须有可观测的信号。

**反模式**：

1. 一口气写完再测，中间 fail 不知哪步崩
2. Tool call 成功当验证（tool call success ≠ 语义正确）
3. 跳过验证步骤，依赖"看起来对"
4. 多步任务不先规划就开始写
5. 隐性 checkpoint：只在脑子里不在对话里，Ken 无法中途纠偏

## 三、和其他规则的交叉

- `.cursor/rules/kpax-rules.md` — KPAX 领域规则，优先级更高
- `projects/knowledge-graph/.cursor/rules/dev-rules.md` — AXL 开发规则，领域内优先
- `.cursor/rules/research-context.md` — 研究上下文，讨论研究话题时加载

本规则（coding-discipline）是**通用底座**，领域规则和研究上下文优先。

## 四、成功指标

试行期用这些指标判断是否保留：

**Simplicity First**：
1. 改动 PR 的代码行数变少
2. 主动提出的质疑和替代方案不减反增
3. Ken 不再反复说"只改要求的部分"
4. 不出现"代码做对了但用户原本更好的做法被吞掉"

**Goal-Driven Execution**：
1. 长任务返工次数减少
2. 跨 session 接续时上下文恢复快
3. 失败时能准确定位哪一步崩
4. Ken 中途能看到进度而不是黑盒

如果 Simplicity 的第 2、4 项恶化，说明规则被读歪了，要改或撤。
