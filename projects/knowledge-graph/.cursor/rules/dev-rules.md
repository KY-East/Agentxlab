---
description: Agent X Lab 知识图谱项目开发规则
globs: ["projects/knowledge-graph/**"]
alwaysApply: true
---

# Agent X Lab — 开发规则

## 核心原则

1. **Retrieval-First**: 新建文件前先检查是否已有同类文件
2. **Single Source of Truth**: 配置集中在 `.env`，数据模型集中在 `models/`，不允许硬编码
3. **Atomic Commits**: 一个 commit 只做一件事

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
