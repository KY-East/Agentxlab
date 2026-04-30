---
description: Agent X Lab 知识图谱项目开发规则
globs: ["projects/knowledge-graph/**"]
alwaysApply: true
---

# Agent X Lab — 开发规则

## 核心原则

0. **Agent X Lab 是底座，KPAX 是上层产品**: 开发任何新能力之前先问——这个该在 AXL 还是 KPAX？"让专家分析"的能力在 AXL，"对接用户"的能力在 KPAX。不要在 KPAX 侧重建 AXL 已有的能力。
1. **Retrieval-First**: 新建文件前先检查是否已有同类文件
2. **Single Source of Truth**: 配置集中在 `.env`，数据模型集中在 `models/`，不允许硬编码
3. **Atomic Commits**: 一个 commit 只做一件事
4. **不重复造轮子**: 能用现成开源方案的就封装进来，不自己重写。自己只做差异化的部分。技术选型优先级：成熟开源 > 自建封装 > 从零开发

## 文件结构

```
projects/knowledge-graph/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py         # 配置（读取 .env）
│   │   ├── db.py             # 数据库连接
│   │   ├── schemas.py        # Pydantic 响应模型
│   │   ├── models/           # SQLAlchemy ORM 模型（唯一事实源）
│   │   ├── routers/          # API 路由（一个功能一个文件）
│   │   └── services/         # 业务逻辑（一个功能一个文件）
│   ├── migrations/           # Alembic 迁移
│   ├── scripts/              # 一次性脚本
│   └── .env                  # 环境变量（不提交）
├── frontend/
│   └── src/
│       ├── components/       # React 组件（按功能分目录）
│       ├── hooks/            # 自定义 hooks
│       ├── api/              # API 客户端
│       └── types/            # TypeScript 类型定义
├── PROGRESS.md               # 开发进度追踪
├── ARCHITECTURE.md           # 架构说明
└── README.md                 # 项目说明
```

## 不可修改的文件

以下文件非经明确指令不得修改：

- `research/` 目录下的所有研究笔记和论文（小说文本规则同理）
- `CHANGELOG.md` 仅允许追加，不允许修改历史记录
- `.env` 中的 API Key 不允许出现在代码或日志中

## 命名规范

- **Python 文件**: snake_case（`debate_engine.py`）
- **React 组件**: PascalCase 目录 + 同名文件（`DebatePanel/DebatePanel.tsx`）
- **API 路由**: `/api/` 前缀，kebab-case 路径（`/api/debate/start`）
- **数据库表**: snake_case 复数（`disciplines`, `papers`, `scholars`）

### 辩论/推演 术语分层

本质是同一件事（多 Agent 跨学科对抗），但对外对内用不同词：

- **代码 / 内部文档**：debate（变量名、文件名、API 路径一律不改）
- **产品对外 / 用户可见文案**：**多维推演**（强调多角度）、**碰撞推演**（强调对抗性）
- **AXL 前端 UI**：学科碰撞（已有，保持）
- 禁止在对外文案里出现"辩论"——听起来像学校社团活动

## 后端规范

- 所有 API 路由使用 `/api/` 前缀
- 数据库操作必须通过 SQLAlchemy ORM，不直接写 SQL（import 脚本除外）
- 新增数据表必须通过 Alembic 迁移
- AI 调用统一通过 LiteLLM，不直接调用各模型 SDK
- 环境变量通过 `app/config.py` 的 settings 对象访问

## 前端规范

- 使用 TypeScript strict mode
- 组件按功能分目录（`components/DebatePanel/`、`components/GraphCanvas/`）
- 样式使用 Tailwind CSS，不写自定义 CSS（除非 Tailwind 无法实现）
- D3.js 操作封装在自定义 hooks 中
- API 调用集中在 `api/client.ts`

## 变更记录

以下操作必须同时更新 CHANGELOG.md 和 PROGRESS.md：
- 新增功能模块
- 数据模型变更
- 新增 API 路由
- 前端页面新增或重构
- 依赖变更

## CSS 语法错误

遇到不影响展示的 CSS 语法错误，先询问用户要不要修改，不允许私自行动。

## 测试

- 新功能先明确预期行为再写实现
- API 路由必须能通过 `/docs` 手动验证
- 前端改动后在浏览器确认效果

## 定期体检流程

每个大版本迭代完成后，主动跑一轮三维度项目体检：

**三个维度（每维 100 分）：**
1. **功能完成度** — 功能有没有做出来，主链路能不能跑通
2. **产品完成度** — 用户用起来顺不顺，文案/状态/反馈像不像成品
3. **生产就绪度** — 能不能部署，能不能稳定运行，出问题能不能恢复

**体检步骤：**
1. 扫描全部 ORM model vs Alembic migration，输出缺口清单
2. 扫描 config.py vs .env vs .env.example，输出环境变量缺口
3. 扫描前端每个页面的 loading / empty / error / disabled 状态覆盖
4. 扫描 i18n 硬编码和旧语义残留
5. 扫描死代码和孤儿文件
6. 输出：评分 → P0/P1/P2 问题清单 → 优化路线图 → 可执行任务列表

**输出记录到：** PROGRESS.md（评分和阻塞点）+ CHANGELOG.md（体检事件）

## 战略级假设

**模型会退化（Brain Rot）。** 所有架构决策要过一遍这个滤镜：如果明年模型比今年蠢 20%，这个设计还能用吗？知识沉淀和人类数据是生存线，不是锦上添花。参考：Nature Model Collapse (2024) + arXiv:2510.13928 Brain Rot。

**记忆越多不等于越好。** 记忆积累会让系统倾向已有路径，可能导致创造力衰减。后续需要设计探索机制（随机浮现低引用记忆、概率性引入非最高分结果）。这和 Brain Rot 是两个方向的风险：一个是模型变蠢，一个是系统变僵化。

## 隔离 vs 隐私

两件不同的事，不要混为一谈：

- **账号隔离 / 数据边界 = 必须做。** 这是工程正确性问题——A 用户的数据不能串到 B 用户，per-user namespace、检索时 user_id 过滤、写入时 source 标记，这些是防 bug，不是做隐私。
- **隐私功能 = 当前不做。** 数据导出、匿名化管线、隐私偏好设置、GDPR 合规 UI——这些是产品功能，当前阶段不投入资源。我们的目的是做出最强的Agent，不是关注白左的傻逼需求。
