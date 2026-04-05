# Interdisciplinary Knowledge Graph

交叉学科知识图谱可视化平台。Agent X Lab 的数据驱动研究探索工具。

## 功能

- **学科图谱可视化**：D3.js 力导向图，学科为节点，交叉关系为边
- **三栏交互界面**：左栏学科树 → 中栏组合画板 → 右栏交叉详情
- **多学科组合查询**：选中多个学科，查看它们的交叉研究
- **研究空白检测**：自动识别尚无研究的学科组合
- **AI 假说生成**：对研究空白调用 LLM 生成研究假说（支持 OpenAI / Anthropic / 本地模型）
- **完整数据管道**：从现有 Markdown 笔记自动导入学科、学者、论文、交叉节点

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 18 + TypeScript + Vite + D3.js + Tailwind CSS |
| 后端 | Python FastAPI + SQLAlchemy + Alembic |
| 数据库 | PostgreSQL |
| AI | LiteLLM（统一多模型接口） |
| 部署 | Docker Compose |

## 快速启动

### Docker Compose（推荐）

```bash
# 1. 配置 AI API keys
cp backend/.env.example backend/.env
# 编辑 .env 填入 API keys

# 2. 一键启动
docker compose up -d

# 3. 导入数据
docker compose exec backend python -m scripts.import_from_markdown

# 4. 访问
# http://localhost
```

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env
uvicorn app.main:app --reload

# 导入数据（需要 PostgreSQL 运行中）
python -m scripts.import_from_markdown

# 前端
cd frontend
npm install
npm run dev
# http://localhost:5173
```

## 项目结构

```
frontend/              React + Vite
  src/
    components/
      DisciplinePanel/ 左栏：学科树
      GraphCanvas/     中栏：D3 力导向图
      DetailPanel/     右栏：交叉详情
    hooks/             数据获取 hooks
    api/               API 客户端
    types/             TypeScript 类型

backend/               FastAPI
  app/
    models/            SQLAlchemy 数据模型
    routers/           API 路由
    services/          业务逻辑（图构建、AI 调用、空白检测）
    schemas.py         Pydantic 序列化模型
  migrations/          Alembic 数据库迁移
  scripts/             数据导入脚本
```

## API 端点

```
GET    /api/health                 健康检查
GET    /api/disciplines            学科树
GET    /api/disciplines/:id        学科详情
GET    /api/disciplines/:id/scholars  学科下的学者
GET    /api/intersections          交叉点列表（可按 status 筛选）
GET    /api/intersections/:id      交叉点详情
POST   /api/intersections/query    按学科组合查询交叉点
GET    /api/graph                  完整图数据（D3 渲染用）
GET    /api/gaps                   研究空白列表
GET    /api/scholars/:id           学者详情
GET    /api/papers/:id             论文详情
POST   /api/ai/hypothesis          AI 生成研究假说
```

## 关联研究方向

本项目从 Agent X Lab 的以下数据源导入：

- `research/disciplines.md` — 学科谱系
- `research/*/papers.md` — 论文索引
- `research/*/classics.md` / `frontier.md` — 文献笔记
- `research/synthesis/crossroads.md` — 11 个交叉节点
