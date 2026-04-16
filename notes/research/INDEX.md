# notes/research/ — 研究笔记索引

**定位**：深度研究笔记，跨 agent 共享。每篇是一个**论证完整**的分析，不是 TODO 清单（任务请抽到 `notes/agenda/next.md`）。

---

## 阅读顺序（新人进项目推荐）

```
emergent-creativity-hypothesis.md    ← 1. 理论起点：我们在验证什么
  ↓
wisland-analysis-and-positioning.md  ← 2. 外部对位：为什么不走效率赛道
  ↓
agent-evolution-free-parameters.md   ← 3. 护城河：5 类自由参数
  ↓
seven-layer-memory-design.md         ← 4. 物理载体：L7 元进化的承载器
  ↓
role-labels-vs-orchestrator.md       ← 5. 架构诚实审视：多 agent vs orchestrator
  ↓
remediation-plan-multi-agent.md      ← 6. 修改方案：4 个修改点 P0/P1
```

---

## 文件清单

### `emergent-creativity-hypothesis.md`
**主题**：涌现创造力假设的理论框架和可检验预测。
**核心判断**：多 agent 跨学科碰撞 → 产生任一单 agent 无法产生的想法（hypothesis 层，正在 `experiments/emergence_decomposition/` 里验证）。
**关联实验**：整个涌现分解实验的理论上游。

### `wisland-analysis-and-positioning.md`
**主题**：Ken 对 WisLand/Faraday 项目尽调后产出的内部分析笔记。
**性质**：研究笔记（Ken 自己理解外部项目用），**不是**项目对外身份标签。主文档（`PROJECT.md`、`KPAX.md`、`README.md`）不引用为对比坐标系。
**内容**：A 项目事实 / B 11 条可偷启发 / C 内部反向清单（"我们不做什么"的依据）。
**硬规则来源**：`PROJECT.md` §5.5 反向清单的论证在这里展开。

### `agent-evolution-free-parameters.md`
**主题**：5 类自由参数清单（fitness / re-rank / diversity 坍缩 / innovation 比例 / decay）。
**核心判断**：这是项目的研究护城河，Phase 3 之前必须冻结清单。
**硬规则**：任何 agent 改相关参数前，若 `experiments/results/` 有数据**必须先读**。

### `seven-layer-memory-design.md`
**主题**：七层记忆系统设计（L1 工作 / L2 情节 / L3 语义 / L4 程序 / L5 反思 / L6 人格 / L7 元进化）。
**核心判断**：基于 2025 SOTA 对照，L7 元进化是自由参数实验的物理载体——这是 CTO 版本没有、也不会有的层。
**当前实施**：Phase 1+2 完成（31 pytest），L3+ 未启动。

### `role-labels-vs-orchestrator.md`
**主题**：三省六部（多 agent 按学科分工）vs orchestrator-worker（单主控调工具）的根本分歧。
**核心判断**：对项目核心假设 (d)「学科标签激发不同推理模式」的诚实审视。可能是幻觉，必须用对照实验证明或证伪。
**直接产出**：`experiments/emergence_decomposition/` 的实验设计（特别是 A 组 去标签）。

### `remediation-plan-multi-agent.md`
**主题**：基于上文产出的修改方案。
**核心判断**：4 个修改点（KPAX 流水线 / 立场身份 / L5 二次校验 / 对照实验），P0 × 2 / P1 × 2。
**执行状态**：部分已落地（见 `CHANGELOG.md` 对应条目）。

---

## 写作约定

1. **不放 TODO**：研究笔记只有分析和结论，行动项抽到 `notes/agenda/next.md`
2. **引用其他笔记**用相对路径：`notes/research/xxx.md` 或 `notes/ideas/yyy.md`
3. **论证完整**：每个结论有依据，引用数据 / 论文 / 实验 / 其他笔记
4. **冲突解决**：两篇笔记结论矛盾时，新笔记必须**显式标注**："与 `xxx.md` §N 结论不一致，原因：..."
5. **更新 vs 新建**：小修直接编辑，大版本（比如记忆体系 v2）新建 `xxx-v2.md`，旧版保留做历史对照
6. **归档**：已过时的笔记加 `_archived_YYYYMMDD.md` 后缀，不删

---

*最后更新：2026-04-15 晚。新增研究笔记请同步在本文件加一条。*
