# experiments/

实验基础设施。所有对照实验的代码、数据、结果都在这里。

## 目录结构

```
experiments/
├── README.md                              ← 你在这里
├── config/
│   ├── experiment_registry.json           ← 所有实验的注册表（三 agent 共享入口）
│   └── benchmark_questions.json           ← 冻结的基准问题集
├── emergence_decomposition/               ← 第一个实验：涌现来源分解
│   ├── spec.md                            ← 实验设计文档（Cursor 写，Claude Code 读）
│   ├── runner.py                          ← 实验 runner（Claude Code 写）
│   ├── judge.py                           ← LLM 评分器（Claude Code 写）
│   ├── results/                           ← 每次运行的结果
│   │   └── run_YYYYMMDD_HHMMSS/
│   │       ├── raw/                       ← 原始 debate transcript
│   │       ├── scores.json                ← 评分结果
│   │       └── summary.md                 ← 自动生成的分析摘要
│   └── analysis.md                        ← 最终分析报告（人工 + LLM 协作）
└── shared/
    ├── evaluator.py                       ← 通用评分框架
    └── utils.py                           ← 共享工具函数
```

## 协议

### 实验注册表（experiment_registry.json）

所有实验必须在这里注册。三个 agent 读这一个文件就知道有什么实验、状态如何。

**`status` 字段**：除通用生命周期外，允许使用 **checkpoint 粒度**字符串（与 `spec.md` 门禁一致），例如 `checkpoint_0_dry_run`、`checkpoint_0_report_ready`、`checkpoint_1_pilot`。**以 registry 为唯一真相源**，`spec.md` 文首「状态」应与之对齐或写明「见 registry」。

```json
{
  "experiments": [
    {
      "id": "emergence_decomposition",
      "name": "涌现来源分解实验",
      "status": "checkpoint_<N>_<phase>  // e.g. checkpoint_0_dry_run, checkpoint_0_report_ready, checkpoint_0_complete, checkpoint_1_pilot, ... | 也允许 completed | paused",
      "spec": "emergence_decomposition/spec.md",
      "results_dir": "emergence_decomposition/results/",
      "created_by": "cursor",
      "executed_by": "claude_code",
      "reviewed_by": "ken",
      "created_at": "2026-04-14",
      "last_updated": "2026-04-14"
    }
  ]
}
```

### 输出协议

每次实验运行生成一个 `run_YYYYMMDD_HHMMSS/` 目录，包含：
- `raw/` — 原始数据（debate transcript JSON）
- `scores.json` — 结构化评分结果
- `summary.md` — 可读的分析摘要

### 三 agent 分工

| 角色 | 职责 |
|------|------|
| **Cursor** | 设计实验 spec、review 结果、更新文档 |
| **Claude Code** | 写 runner/judge 代码、执行实验、生成 raw results |
| **Codex** | 批量数据处理、结果聚合、可视化 |
| **Ken** | 审阅 spec、人工评分子集、最终判断 |
