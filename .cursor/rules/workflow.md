---
description: 工作流纪律。每次 session 开始时自动加载，确保 Cursor 遵循跨 agent 协调协议。
globs: []
alwaysApply: true
---

# 工作流

## 开工

每次 session 开始，先读 `notes/agenda/next.md`，找标记 `@cursor` 的任务。有 P0 先做 P0。

## 收工

session 结束前：
1. 完成的任务从 `notes/agenda/next.md` 删掉
2. 在 `notes/journal/project-log-2026-04.md`（或当月文件，格式 `project-log-YYYY-MM.md`）追加一条：`[YYYY-MM-DD @cursor] 完成 XXX — 结果/输出`
3. 有代码改动的同步更新 `CHANGELOG.md`
4. 新浮现的任务加到 agenda，不藏在 research note 正文里

## 四件套分工

| 文件 | 记什么 |
|---|---|
| `notes/agenda/next.md` | 未来要做的事（唯一 TODO 板） |
| `notes/journal/project-log-YYYY-MM.md` | 项目全记录：已发生的事、决策、对话结论 |
| `CHANGELOG.md` | 代码层变更 |
| `experiments/config/experiment_registry.json` | 实验状态机 |

不要在 research note 或 spec 里写 TODO，统一抽到 agenda。
