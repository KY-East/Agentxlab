---
description: 研究上下文。当讨论 AXL debate 质量、记忆系统参数、re-rank 权重、diversity / 坍缩监控、涌现创造力假设、cognition distill、memory decay、agent 自进化、或对照实验时，加载这份研究笔记。
globs: ["notes/research/**", "experiments/**", "projects/knowledge-graph/backend/app/services/cognition_distiller.py", "projects/knowledge-graph/backend/app/services/agent_memory.py", "kpax/**/memory*.py"]
alwaysApply: false
---

# 研究上下文索引

项目的**研究护城河**不在 idea 层，在自由参数的数值化。任何涉及以下话题的代码修改前，先读对应笔记：

## 核心研究笔记

- **`notes/research.md#emergent-creativity-hypothesis`** — 涌现创造力假设的理论框架（Minsky Society of Mind + 进化选择压力 + Kahneman 双系统），含 4 条可检验预测
- **`notes/research.md#agent-evolution-free-parameters`** — agent 进化的五类自由参数清单（fitness / re-rank 权重 / 多样性坍缩阈值 / innovation 比例 / memory decay），以及实验台建设路线
- **`notes/research.md#seven-layer-memory-design`** — 七层记忆系统设计（L1-L7），基于 2025 SOTA，L7 是自由参数实验台的物理载体
- **`notes/research.md#role-labels-vs-orchestrator`** — 三省六部 vs orchestrator-worker，核心假设的对照实验设计
- **`notes/research.md#remediation-plan-multi-agent`** — 4 个修改点 + 不改清单
- **`experiments/emergence_decomposition/spec.md`** — 涌现来源分解实验设计（6 组 × 50 题 × 3 次）
- **`notes/research.md#role-labels-vs-orchestrator`** — 三省六部式多 agent 架构 vs orchestrator-worker 的根本分歧。核心判断：角色标签制造虚假专业化，真实收益来自异质性 + 外部状态。含核心研究假设的对照实验设计
- **`notes/research.md#remediation-plan-multi-agent`** — 基于上文的修改方案。P0：KPAX 五步流水线改 orchestrator + tools，对照实验组建设。P1：专家立场改临时 lens，L5 反思二次校验硬规则。明确列出"不改"的部分防止误伤

## 核心判断（摘要）

1. AXL/KPAX 的学术价值在"跨学科 debate 涌现"，EvoMap 等同类项目在"agent 能力流通"，方向正交，不集成
2. 现有 re-rank 权重（peer_reviewed ×1.3 / external ×1.2 / generated ×0.9）是拍脑袋的 bootstrap，必须升级为数据驱动
3. "涌现创造力"要从玄学变可检验假设，必须先定义 diversity metric 和坍缩警报阈值
4. Phase 3（KPAX 接 Zep）之前要冻结自由参数清单，否则结构凝固后改不动

## 写代码前要问

- 这次改动是否涉及上述自由参数？
- 是否引入了新的拍脑袋常数？如果是，是否需要同时定义它的可观测指标？
- 是否让 generated 来源的内容获得了更高权重，导致自我强化风险？
- `experiments/results/` 里有没有相关实验数据？**如果有，必须先读数据再做决策，不能凭直觉改参数**
