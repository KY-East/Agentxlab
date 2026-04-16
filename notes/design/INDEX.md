# notes/design/ — 设计方案索引

**定位**：产品 / 系统 / UI 设计方案。和 `research/` 的区别：

- `research/` = 回答"为什么" / "是否成立"（理论 / 假设 / 论证）
- `design/` = 回答"怎么做" / "长什么样"（方案 / 架构 / 交互 / 视觉）

---

## 文件清单

### `kpax-v0-deliberation-room.md`
**主题**：KPAX v0 前端形态——7 席座谈会（Deliberation Room）。
**核心决策**：
- 非聊天框、非卡片。3D 书房 + 7 位顾问在场，"满席 + 动态前景"（相关 3/5/7 位发言，其他人在场但做自己的事）
- 视觉锚：维多利亚黑神话 UE5 写实质感
- 7 人阵容：5 男 2 女，2 位东亚（数学女 / CS 男），不要印度裔
- 技术栈（2026 拼装）：Rodin Gen-1 / Meshy 4 / Tripo 2（图→rigged 3D）+ Spark 2.0（场景）+ ElevenLabs（声音）+ NVIDIA Audio2Face-3D（面部）+ R3F + Next.js
- 三周 v0 落地
**关联文件**：
- 上游：`KPAX.md`（产品承诺）、`AGENTS.md`（协作规则）、`notes/research/seven-layer-memory-design.md`（L1–L7 在 UI 上的落地面）
- 下游：`kpax/backend/*`（骨架已就位）、`projects/knowledge-graph/backend/app/routers/kpax_api_spec.md`（HTTP 边界）
**状态**：v0 主结构锁定。7 人角色 prompt + 美术风格生成中。

---

## 写作约定

1. 设计决策必须有**关联文件**段落（上游依据 / 下游影响），不要孤岛
2. 关键决策写**可回滚的版本**：每个大改版新建 `xxx-v2.md`，旧版保留做对比
3. 代码落地后在对应代码顶部注释 link 回设计文档
4. TODO 不写在本目录文件里，抽到 `notes/agenda/next.md`

---

*最后更新：2026-04-15 晚。新增设计方案请同步在本文件加一条。*
