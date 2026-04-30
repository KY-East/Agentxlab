# Deployment Guide / 部署指南

> Practical instructions for deploying AgentXLab. If you are just trying to read what the project is, see [README.md](./README.md). If something breaks during deployment, jump straight to **[Common Issues](#common-issues--常见问题)** at the bottom.

> 实际部署指南。如果你只是想了解项目是什么，看 [README.md](./README.md)。部署中遇到问题直接跳到末尾的 **[常见问题](#common-issues--常见问题)** 节。

---

## Prerequisites / 前置要求

| Requirement | Version | Notes |
|---|---|---|
| Python | **3.11+** | SQLAlchemy 2.0 `Mapped` type annotations require 3.10+; debate engine prompts use 3.10 union syntax |
| Node.js | 18+ | Vite 8 + React 19 |
| Git | any | |
| SQLite | bundled with Python | Default; zero configuration |
| Postgres | 14+ | Optional — for production |
| Disk | ~500MB | Most of it is `node_modules` |

**LLM API keys**: at minimum one of `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`. DeepSeek is recommended as default (cheap, reliable, supports debate engine out of the box).

**LLM API 密钥**：至少配一个 `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`。推荐用 DeepSeek 作为默认（便宜可靠，辩论引擎默认模型就是它）。

---

## Step-by-Step / 分步部署

### 1. Clone the repository / 克隆仓库

```bash
git clone https://github.com/KY-East/Agentxlab.git
cd Agentxlab
git checkout v2.0-redesign     # active branch / 当前主线分支
```

### 2. Backend setup / 后端搭建

```bash
cd projects/knowledge-graph/backend

# Virtual env / 虚拟环境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install Python dependencies / 安装 Python 依赖
pip install -r requirements.txt

# Configure environment / 配置环境变量
cp .env.example .env
# 编辑 .env，至少填 DEEPSEEK_API_KEY；其他可选（详见 .env.example 注释）
```

**Critical environment variables / 关键环境变量**:

| Variable | Required | What it does / 作用 |
|---|---|---|
| `DEEPSEEK_API_KEY` | **Yes** | Default model for all AI tasks (debate / discovery / summary / sparks) / 所有 AI 任务的默认模型 |
| `DATABASE_URL` | No | Default SQLite (`sqlite:///./knowledge_graph.db`); change to Postgres for production |
| `DEFAULT_AI_MODEL` | No | Default `deepseek/deepseek-chat`. **Must include LiteLLM provider prefix** (`anthropic/`, `openai/`, `deepseek/`) |
| `DEBATE_MODEL_PRO` / `_CON` / `_MODERATOR` | No | Multi-LLM family pool. Setting all three enables G+F anti-twin constraint (cross-family enforcement) |
| `JWT_SECRET` | **Yes for production** | Default `change-me-in-production` — change before deploying |
| `AUTH_BYPASS_DEV_MODE` | No | Dev-only short-circuit for auth + quota. **Never enable in production**. Startup logs a 70-char banner warning if true |

**Apply database migrations / 应用数据库迁移** (this is the step most often skipped):

```bash
alembic upgrade head
```

This applies migrations 001 → 013 (latest: Phase 2 Final Answer Layer columns). If skipped, the app will throw `OperationalError: no such column: summary_direct_answer` etc.

这一步常被跳过。会应用 001 → 013 全部迁移（最新是 Phase 2 Final Answer Layer 4 字段）。跳过会报 `no such column: summary_direct_answer` 之类的错。

**Seed disciplines / 导入学科种子数据**:

```bash
python -m scripts.import_from_markdown
```

This imports the 4516 OpenAlex discipline taxonomy. Without it the knowledge graph is empty.

导入 OpenAlex 4516 个学科分类。不跑这步知识图谱是空的。

**Start the backend / 启动后端**:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Verify: `curl http://127.0.0.1:8000/api/health` should return `{"status":"ok"}`.

验证：`curl http://127.0.0.1:8000/api/health` 应该返回 `{"status":"ok"}`。

### 3. Frontend setup / 前端搭建

```bash
cd projects/knowledge-graph/frontend
npm install
npm run dev                    # http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://127.0.0.1:8000` (backend). If the backend is not running you'll see `ECONNREFUSED` errors in the browser console — start the backend first.

Vite dev server 把 `/api/*` 代理到 `http://127.0.0.1:8000`（后端）。后端没跑会在浏览器 console 看到 `ECONNREFUSED` ——先起后端。

### 4. Verify end-to-end / 端到端验证

1. Open `http://localhost:5173` — you should see the discipline tree on the left and force-directed graph in the center.
2. Click 2-3 disciplines, click "Start Debate" / "发起辩论", choose `debate` or `free` mode, type a question.
3. Wait ~10-15 minutes for 3 rounds of debate (depends on `depth` setting).
4. After Round 3 completes, the page should show a Final Answer Layer at the top (Direct Answer + Why + Key Conditions + User Takeaway) with the 4-section detailed analysis collapsed below.

打开 `http://localhost:5173`，应能看到左侧学科树 + 中间力导向图。选 2-3 个学科，点"发起辩论"，选 `debate` 或 `free` 模式，敲入问题。等 ~10-15 分钟跑完 3 轮（具体时间取决于 `depth` 设置）。Round 3 结束后页面顶部应显示 Final Answer Layer（直接答案 + 为什么 + 关键条件 + 用户可做），下方折叠 4 段详细分析。

### 5. KPAX backend service (optional) / KPAX 后端服务（可选）

KPAX is the decision-product layer. It runs as a separate service on port 8001 and talks to AXL via HTTP.

KPAX 是决策产品层。独立服务跑在 8001 端口，通过 HTTP 与 AXL 通信。

```bash
cd kpax/backend
pip install -r requirements.txt
uvicorn kpax_svc.main:app --port 8001 --reload
```

Verify: `curl http://127.0.0.1:8001/api/v1/health`.

### 6. Docker deployment / Docker 部署

For one-command deployment with Postgres:

一键部署 + Postgres：

```bash
cd projects/knowledge-graph
cp backend/.env.example backend/.env     # 编辑 .env 填 API key
docker compose up -d                     # http://localhost
```

Docker stack: Postgres 16 + backend + frontend. `docker-compose.yml` lives in `projects/knowledge-graph/` (not the repo root).

Docker 栈：Postgres 16 + backend + frontend。`docker-compose.yml` 在 `projects/knowledge-graph/` 目录里（不是仓库根目录）。

---

## Production Deployment / 生产部署

The dev-mode setup above is fine for local testing. Before deploying to production, do all of the following:

上面的 dev 配置够本地测试。上线前务必：

1. **Disable auth bypass** — set `AUTH_BYPASS_DEV_MODE=false` or remove the line from `.env`. Without this, every request runs as the dev account.
   **关闭 auth bypass** —— 在 `.env` 把 `AUTH_BYPASS_DEV_MODE=false` 或者直接删掉这一行。不关，所有请求都会以 dev 账户身份执行。
2. **Change JWT_SECRET** — the default value is literally the string `change-me-in-production`. JWT signing relies on this; weak value means anyone can forge tokens.
   **改 JWT_SECRET** —— 默认值就是字符串 `change-me-in-production`。这是 JWT 签名依据，弱密钥任何人都能伪造 token。
3. **Switch to Postgres** — SQLite is fine for local dev but does not handle concurrent writes well. Set `DATABASE_URL=postgresql://...`.
   **切到 Postgres** —— SQLite 单机够用，但并发写性能差。生产环境改 `DATABASE_URL=postgresql://...`。
4. **HTTPS** — front the app with nginx / Caddy / Cloudflare. Browser will block CORS without it.
   **HTTPS** —— 前面挂 nginx / Caddy / Cloudflare。不挂浏览器会拦 CORS。
5. **Tighten CORS_ORIGINS** — change from `["http://localhost:5173"]` to your real domain.
   **收紧 CORS_ORIGINS** —— 把 `["http://localhost:5173"]` 改成你的真实域名。
6. **Secret management** — never commit `.env` to git. Use platform secret manager (AWS Secrets Manager / GitHub Actions secrets / etc).
   **密钥管理** —— `.env` 永远不要进 git。用平台的 secret 管理器。
7. **Backup the SQLite/Postgres** — debate sessions, agent transcripts, and Phase 2 Final Answer fields all live in the DB. Treat as primary data.
   **备份数据库** —— 辩论 session、agent 发言、Phase 2 Final Answer 字段全部在 DB 里，按主数据级别备份。

---

## Common Issues / 常见问题

### Issue 1: `OperationalError: no such column: summary_direct_answer`

**Cause / 原因**: `alembic upgrade head` was not run, or the DB is at an older migration revision (Phase 2 added 4 new columns in migration 013).

**原因**：没跑 `alembic upgrade head`，或者 DB 还停在旧的 revision（Phase 2 在 013 加了 4 个新字段）。

**Fix / 解决**:

```bash
cd projects/knowledge-graph/backend
alembic current     # check current revision / 看当前 revision
alembic upgrade head
```

If `alembic current` returns empty but tables already exist (DB created via `Base.metadata.create_all` in old code), use `stamp` to mark the baseline first:

如果 `alembic current` 返回空但表已存在（DB 是用旧代码 `Base.metadata.create_all` 建的），先用 `stamp` 标基线：

```bash
alembic stamp 011    # mark as already at 011
alembic upgrade head # then upgrade through 012 / 013
```

### Issue 2: `401 Unauthorized` on every API call

**Cause / 原因**: No active login session, and `AUTH_BYPASS_DEV_MODE` is not enabled. Most endpoints require `get_verified_user`.

**原因**：没活跃登录 session，`AUTH_BYPASS_DEV_MODE` 也没开。大部分 endpoint 走 `get_verified_user`。

**Fix (development) / 解决（开发）**:

Add to `.env`:

```
AUTH_BYPASS_DEV_MODE=true
```

Restart backend. Startup will log a 70-character banner warning.

重启后端。启动会打 70 字符包围的 WARNING。

**Fix (production) / 解决（生产）**:

Use the actual login flow — POST `/api/auth/register` then `/api/auth/login`, store the JWT, send as `Authorization: Bearer <token>`.

走真实登录流程——POST `/api/auth/register` 然后 `/api/auth/login`，存 JWT，请求带 `Authorization: Bearer <token>`。

### Issue 3: `LiteLLM completion() error: BadRequestError`

**Cause / 原因**: Model slug missing the LiteLLM provider prefix.

**原因**：模型 slug 没带 LiteLLM provider 前缀。

LiteLLM requires `<provider>/<model>` format:

LiteLLM 要求 `<provider>/<model>` 格式：

- `deepseek/deepseek-chat` ✓
- `anthropic/claude-opus-4-6` ✓
- `openai/gpt-4o` ✓
- `gpt-4o` ✗ (no prefix → fails)
- `claude-opus-4-6` ✗

**Fix / 解决**: Update `DEFAULT_AI_MODEL` and `DEBATE_MODEL_*` in `.env` to include provider prefix.

修复：在 `.env` 里 `DEFAULT_AI_MODEL` 和 `DEBATE_MODEL_*` 加 provider 前缀。

### Issue 4: `Port 8000 already in use` (Windows)

**Cause / 原因**: Previous `uvicorn --reload` parent process killed via `taskkill`, but child worker process still holds the port. Common Windows quirk.

**原因**：之前的 `uvicorn --reload` 父进程被 `taskkill` 关了，但子 worker 进程还占着端口。Windows 常见 quirk。

**Fix / 解决** (PowerShell):

```powershell
$pid = (Get-NetTCPConnection -LocalPort 8000 -State Listen).OwningProcess
taskkill /PID $pid /T /F     # /T = kill tree (parent + all children)
```

Or simpler — restart the terminal / IDE that originally launched uvicorn.

或者直接重启原来启动 uvicorn 的终端 / IDE。

### Issue 5: SQLite `database is locked` (Windows OneDrive)

**Cause / 原因**: OneDrive sync occasionally locks `.db` files on Windows. Worse if the repo is inside `OneDrive/Document/...`.

**原因**：Windows OneDrive 同步偶尔锁 `.db` 文件。仓库放在 `OneDrive/Document/...` 下面更严重。

**Fix / 解决**:

- Move the repo outside OneDrive (best long-term fix) / 把仓库移出 OneDrive（长期最佳）
- Pause OneDrive sync during development / 开发期间暂停 OneDrive 同步
- Or switch to Postgres (`DATABASE_URL=postgresql://...`) / 或者切到 Postgres

### Issue 6: `429 Quota Exceeded` even when Ken is the only user

**Cause / 原因**: User's subscription is on the `free` plan (50K tokens/month), and the multi-model debate pool tries to use models not in `allowed_models`.

**原因**：用户的 subscription 是 `free` plan（每月 5 万 tokens），但多模型辩论池试图用 `allowed_models` 之外的模型。

**Fix (development) / 解决（开发）**:

Set `AUTH_BYPASS_DEV_MODE=true`. This short-circuits both `check_quota` and `validate_model`, allowing any model in `.env` to run.

设 `AUTH_BYPASS_DEV_MODE=true`。这会同时短路 `check_quota` 和 `validate_model`，让 `.env` 里配的任何模型都能跑。

**Fix (production) / 解决（生产）**:

Upgrade the user to `pro` plan, or only use models in their `allowed_models` list. See `app/plan_config.py`.

把用户升级到 `pro` plan，或者只用 `allowed_models` 列表里的模型。详见 `app/plan_config.py`。

### Issue 7: Frontend shows blank page / `Cannot find module 'react-markdown'`

**Cause / 原因**: Phase 2 added `react-markdown` and `remark-gfm` dependencies (for true markdown rendering of LLM output instead of literal `**` characters). Older `node_modules` won't have them.

**原因**：Phase 2 加了 `react-markdown` 和 `remark-gfm` 依赖（用于 LLM 输出的真粗体渲染，不是字面 `**`）。旧 `node_modules` 没有。

**Fix / 解决**:

```bash
cd projects/knowledge-graph/frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue 8: Debate sessions disappear after restart

**Cause / 原因**: This shouldn't happen — debate sessions persist to `knowledge_graph.db` (or your configured Postgres). If they disappear, the DB file got recreated.

**原因**：这不该发生——辩论 session 都持久化到 `knowledge_graph.db`（或你配的 Postgres）。如果消失了，是 DB 文件被重建了。

**Diagnose / 诊断**:

```bash
cd projects/knowledge-graph/backend
python scripts/show_debate_archive.py     # lists last 5 debates from DB
```

If empty, check whether `knowledge_graph.db` exists in the backend directory and is non-empty.

如果空，看 backend 目录下 `knowledge_graph.db` 文件是否存在且非空。

### Issue 9: Round 3 output truncated mid-sentence

**Cause / 原因**: `max_tokens` budget too tight for `free` mode Round 3 (six-field spec is longer than `debate` mode's "final answer" output).

**原因**：`free` 模式 Round 3 的 max_tokens 预算不够（六字段 spec 比 debate 模式的"最终答案"输出量大）。

**Status / 状态**: Known issue (Phase 1.2 in roadmap). Workaround: set `depth=deep` or `depth=max` in the debate creation API to give larger budget.

**当前状态**：已知问题（Phase 1.2 在路线图）。临时绕过：创建辩论时把 `depth` 设成 `deep` 或 `max` 给更大预算。

### Issue 10: Discovery → Debate flow loses original question

**Cause / 原因**: When jumping from Discovery to Debate page, `navCtx.hypothesis` (AI rephrasing) overwrites the input box instead of `navCtx.discoveryQuestion` (user's raw words).

**原因**：从 Discovery 跳转到 Debate 页时，`navCtx.hypothesis`（AI 改写版）优先覆盖输入框，而不是 `navCtx.discoveryQuestion`（用户原话）。

**Status / 状态**: Known issue (Phase 1.1 in roadmap). Workaround: manually edit the input box back to your original question before clicking "Start Debate".

**当前状态**：已知问题（Phase 1.1 在路线图）。临时绕过：点"发起辩论"前手动把输入框改回原始问题。

### Issue 11: KPAX backend can't reach AXL

**Cause / 原因**: KPAX `axl_client.py` defaults to `http://127.0.0.1:8000`. If AXL is on a different host/port (e.g. Docker network), this breaks.

**原因**：KPAX `axl_client.py` 默认指向 `http://127.0.0.1:8000`。如果 AXL 在不同 host/port（如 Docker 网络）就连不上。

**Fix / 解决**: Set `AXL_BASE_URL` env var in KPAX `.env` to AXL's actual URL (e.g. `http://axl-backend:8000` inside Docker network).

修复：在 KPAX 的 `.env` 里设 `AXL_BASE_URL` 指向 AXL 实际地址。

### Issue 12: Vite HMR not picking up CSS changes

**Cause / 原因**: Tailwind v4 + Vite 8 sometimes don't hot-reload custom CSS in `index.css` (e.g. the markdown report typography rules).

**原因**：Tailwind v4 + Vite 8 偶尔不热更 `index.css` 里的自定义 CSS（如 markdown 报告排版规则）。

**Fix / 解决**: Hard refresh (Ctrl+Shift+R / Cmd+Shift+R). If still broken, restart `npm run dev`.

修复：硬刷新（Ctrl+Shift+R / Cmd+Shift+R）。还不行重启 `npm run dev`。

---

## Database Migration Reference / 数据库迁移参考

| Revision | Date | What it adds |
|---|---|---|
| 001 | 2026-04 | Initial schema (disciplines, papers, scholars, debates, debate_agents, debate_messages) |
| 002 | 2026-04 | OpenAlex fields on disciplines and papers |
| 003 | 2026-04 | Debate tables refinement |
| 004 | 2026-04 | Paper draft tables |
| 005 | 2026-04 | Paper-discipline join table |
| 006 | 2026-04 | Agent rank weight |
| 007 | 2026-04 | Sparks table (creative idea extraction) |
| 008 | 2026-04 | Experiment meta table |
| 009 | 2026-04 | Users table |
| 010 | 2026-04 | Forum tables |
| 011 | 2026-04 | Debate language column |
| 012 | 2026-04-15 | `debates.raw_question` + `debates.suggested_dimensions` (Phase 1 root-cause fix) |
| 013 | 2026-04-27 | `debates.summary_direct_answer / summary_why / summary_conditions / summary_next_steps` (Phase 2 Final Answer Layer) |

To verify your DB is at head: `alembic current` should print `013 (head)`.

验证 DB 在最新 revision：`alembic current` 应输出 `013 (head)`。

---

## When Things Go Sideways / 实在跑不通

1. Check the backend log first — every request gets a `req_id` and structured JSON output. `grep` by step / agent_id / model to trace a specific debate.
   先看后端日志——每个请求带 `req_id` 和结构化 JSON 输出。按 step / agent_id / model `grep` 追特定辩论。
2. Check `knowledge_graph.db` directly with `sqlite3 knowledge_graph.db "SELECT id, mode, status FROM debates ORDER BY id DESC LIMIT 5"` to confirm the DB state.
   直接用 sqlite3 查 DB 状态确认。
3. Run `python scripts/check_agent_twins.py <debate_id>` to inspect a specific debate's agents and outputs.
   用脚本看具体辩论的 agent 输出。
4. If completely stuck, file an issue at https://github.com/KY-East/Agentxlab/issues with: OS, Python version, Node version, full error traceback, and the output of `alembic current`.
   完全卡住开 issue：OS / Python 版本 / Node 版本 / 完整 traceback / `alembic current` 输出。

---

## See Also / 参考

- [README.md](./README.md) — Project overview / 项目概述
- [KPAX.md](./KPAX.md) — KPAX product spec / KPAX 产品规格
- [PROJECT.md](./PROJECT.md) — Internal navigation / 项目内部导航
- [CHANGELOG.md](./CHANGELOG.md) — Phase 0 → 2.5 release notes
- [`notes/design.md`](./notes/design.md) — Product philosophy (axl-debate-mode-design + Final Answer Layer + 道德层产品原则)
