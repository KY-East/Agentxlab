# Legacy Routers Assessment

**作者**：cursor  
**日期**：2026-04-17  
**决策责任人**：@ken（战略 / 产品）  
**meta-review**：@codex

---

## 背景

`kpax/backend/kpax_svc/routers/analyze.py` 和 `report.py` 是 KPAX 早期写的两个 router，时间早于硬规则 #6 明确提出。它们严重违反 `PROJECT.md` §5.1 规则 #6（KPAX 不允许 monorepo import from AXL）：

**`routers/analyze.py` 违规点**：
- `from app.db import SessionLocal` —— 直接使用 AXL 的数据库 session
- `from app.models.debate import Debate, DebateAgent` —— 直接使用 AXL ORM 模型
- 第 165 行：`from app.services.debate_engine import run_round_stream, generate_summary` —— 在函数内跑 AXL 的 debate 引擎
- `debate = Debate(...)` + `db.add(debate)` + `db.commit()` —— **直接往 AXL 的 DB 写 row**

**`routers/report.py` 违规点**：
- `from app.db import SessionLocal`
- `from app.models.debate import Debate`
- 从 AXL DB 查 debate messages 用于 followup 分析

legacy 路径：
- `POST /api/analyze/start` / `context` / `supplement` / `run`（五步流程，最后一步是 SSE）
- `GET /api/report/{session_id}` / `POST /api/report/{session_id}/followup`

本次 cursor 已修完 3 个 services + `v1_analyze._chat_fn` 的 LLM import 违规。legacy routers 的处理需要战略决策，本文件列出 4 条路径供 Ken 拍板。

---

## 前端依赖面（2026-04-17 补充，原评估遗漏）

**v0.1-reviewed 前版本评估里有事实错误**：曾写"前端 ❌ 未起，无真实用户依赖 legacy 路径"（参考 `PROJECT.md` §2.2 表述）。**实测 `kpax/frontend/src/api/client.ts` 存在 7 文件前端在使用 legacy 6 endpoint**：

| 前端文件 | 消费的 legacy endpoint |
|---|---|
| `api/client.ts` | `startAnalysis` / `submitContext` / `supplement` / `runAnalysis` / `getReport` / `followUp` 全部 |
| `pages/Analyze.tsx` | 串起整个 5 步流程 |
| `components/QuestionInput.tsx` | 触发 `/start` |
| `components/ContextForm.tsx` | 消费 `/context` 返回的 `ContextField[]` |
| `components/AnalysisPreview.tsx` | 消费 `/context` 返回的 `experts[]` + `analysis_angles` |
| `components/DebateStream.tsx` | 消费 `/run` 的 SSE 6 种 event 类型（round_start / message / generating_summary / ...） |
| `components/Report.tsx` | 消费 `/report/{id}` + 触发 `/followup` |

`PROJECT.md` §2.2 "前端 ❌ 未起" 的含义应读作 "**v0 座谈会形态前端未起**"，而非 "**完全没有前端代码**"。这两者差距影响路径选择：

- **legacy 不是零依赖孤儿代码**：任何弃用动作会让前端 7 文件 404
- **legacy 的产品形态（session state + SSE + followup）和 KPAX v0 座谈会交互匹配**——v0 需要的流式分席位发言、多轮追问，正好是 legacy 的抽象而非 v1 one-shot 的抽象
- **v1_analyze 不是 legacy 的超集**：v1 是 one-shot 无 session、无 SSE、无 followup，前端若迁到 v1 需要砍掉 DebateStream 类体验

因此原建议"路径 A 弃用"低估了代价。本文件保留路径 A 作为选项但**不再作为 cursor 推荐**，增加**路径 D：冻结 legacy**作为新选项。

---

## 三条路径对比

### 路径 A：弃用 legacy

**动作**：
1. `main.py` 去掉 `app.include_router(analyze.router)` 和 `app.include_router(report.router)`
2. `analyze.py` / `report.py` 文件移入 `kpax_svc/routers/legacy_deprecated/` 子目录或直接 `git rm`（按 Ken 偏好选）
3. `kpax_svc/__init__.py` 里的 sys.path hack（第 6-8 行，把 AXL backend 塞进 `sys.path`）可以一并删——此后无任何 KPAX 模块需要 import `app.*`

**代价**：
- 失去 `/api/analyze/*` 五步流程（start / context / supplement / run SSE）
- 失去 `/api/report/{session_id}/followup` 基于 debate 历史的追问能力
- **前端 7 文件同时需要改动或接受临时 404**（见上节"前端依赖面"）

**Ken 的问题"会不会造成很多 bug"的精确回答**：

后端动作本身只有 4 行代码改动（`main.py` 去 2 行 include_router + 2 个文件移动），后端零 bug。**但前端 7 文件会立刻进入 404 状态**，形成以下连锁：

- `pages/Analyze.tsx` 一进入就报 500（`/api/analyze/start` 404）
- `ContextForm` / `AnalysisPreview` / `DebateStream` / `Report` 4 组件无数据加载
- KPAX 前端 dev server 虽然能起，但用户路径全挂

这些不属于"很多零散 bug"，属于**"前端整条流水线断开"的单一宏观故障**，恢复方式也单一：前端 7 文件同步迁到 v1_analyze 形态或完全重写成座谈会 UI。

**配套前端改造成本**：
- 改造到 v1_analyze one-shot 形态：约 4-6 小时（DebateStream 整块废，ContextForm 简化为一次提交，Report 直接消费 v1 的 `output` 字段）
- 改造到 v0 座谈会形态：需要 cc 先出 PRD + AXL 流式端点先改真 → **不只是前端工作量，是整个产品 v0 起步**

**风险**：
- 如果前端同步迁移 v1 one-shot：产品倒退（KPAX 失去 v0 座谈会的关键交互），Ken 可能不接受
- 如果只弃后端前端保留不改：KPAX 前端 7 文件临时全挂，但因为 v0 本来就没上线，用户影响=0，只是 dev 期间前端访问报 404
- 如果前端也一并删/重写：时间成本从"5 分钟"升到"1-2 周"，等于把 KPAX v0 前端重启时间提前

**时间成本**：
- 后端单独动：5 分钟
- 前端接受 404 + 留 TODO：5 分钟 + 注释说明
- 前端迁到 v1 one-shot：+4-6 小时
- 前端走 v0 座谈会重写：合入 KPAX v0 整体工期（Ken 原计划）

### 路径 B：legacy 改走 HTTP

**动作**：
1. `routers/analyze.py` 的 `/run` endpoint 改为通过 `axl_client` 调 AXL 的流式 debate 端点
2. AXL 侧 `kpax_router.py` 需要新增 SSE 流式 debate 支持（当前 mock 只支持同步响应）
3. KPAX 侧不再创建 `Debate` / `DebateAgent` row（改由 AXL 侧创建，返回 debate_id 给 KPAX）
4. KPAX 侧 `context_collector.set_debate_id(...)` 存 AXL 返回的 debate_id
5. `report.py` 的 followup 改走 `axl_client` 查 AXL 的 debate messages（需要新增对应 AXL 端点）或 KPAX 侧缓存 debate messages（context_collector 扩展）

**前置依赖**：
- AXL 侧 `kpax_router.py` 从 mock 改真（归 @cc 战略 / 架构 scope）
- AXL 侧需要新增至少 2 个端点：`/axl/v1/debate/stream` (SSE) + `/axl/v1/debate/{id}/messages` (GET)

**时间成本**：
- AXL 侧改造：~2-3 小时（cc 之前估）
- KPAX 侧改造：~4-6 小时（新增 stream 路径、错误处理、SSE 桥接 httpx）
- 合计：~1 工作日跨 cc 和 cursor

**代价**：
- AXL 端点设计时未考虑流式，现在返工
- legacy 五步流程保留，但实际使用前需要前端一起开发——和"路径 A 先弃用再按 v0 真实需要重建"的差别变小

**风险**：
- AXL 流式端点设计决定依赖 KPAX v0 前端协议（例如 SSE event 类型 / 数据格式），**但 v0 前端还没开**——现在定协议容易返工
- 改造期间 legacy routers 处于 "已改动但未测试" 状态

### 路径 C：保留 legacy 但逻辑隔离

**动作**：
1. `analyze.py` / `report.py` 保留原状
2. `main.py` 改为条件挂载：`if os.getenv("KPAX_ENABLE_LEGACY") == "1": app.include_router(analyze.router)`
3. 文件顶加 `# DEPRECATED: monorepo coupling, scheduled for removal/rewrite` 注释
4. `kpax_svc/__init__.py` 的 sys.path hack 保留

**代价**：
- 硬规则 #6 违规没有真正解决，只是加了条件门
- 后续每次 dev 跑 KPAX 时都要决定 env 开关
- 技术债越积越久

**风险**：
- 硬规则失去震慑力（"有条件的硬规则不是硬规则"）
- 未来 agent 看到 `if ENABLE_LEGACY` 会误以为"可以违规只要加 env flag"

### 路径 D：冻结 legacy（2026-04-17 新增）

**动作**：
1. `analyze.py` / `report.py` / `context_collector.py` 保留原状，不动不扩
2. `main.py` 继续挂载（保持前端 7 文件可用）
3. 文件顶部加显式 deprecation 注释，声明：
   - 违反硬规则 #6，仅因产品形态匹配 v0 座谈会而暂保
   - **新功能禁止进 legacy**，任何增量能力必须进 v1_analyze 或未来的 v1_session
   - 替换节点：AXL 流式端点改真 + KPAX v0 前端协议 PRD 出来后，cursor 启动路径 B 迁移
4. `PROJECT.md` §5.1 规则 #6 下加**例外登记**：明示 analyze.py + report.py + context_collector 在 v0 座谈会替代品就位前例外存在，负责人 @cursor，复查点锚定 "KPAX v0 PRD 完成日"
5. `kpax_svc/__init__.py` sys.path hack 保留（给 legacy 用）但加注释说明 legacy 弃用后一并删

**代价**：
- 硬规则 #6 短期内在 KPAX 内存在 1 处**登记的例外**（非条件门，是明示豁免）
- `_archives/` 式的心理负担：代码在但不能碰

**风险**：
- 和路径 C 的滑坡风险相似，但通过"**例外需登记**"约束未来 agent 的决策（agent 读 `PROJECT.md` §5.1 会看到例外清单，清楚"只有这 3 文件是例外，其他违规仍禁"）
- 关键约束是"新功能禁止进 legacy"—— 这条规则须 Ken 和 @codex 在 PR review 时严格执行

**时间成本**：20 分钟（加注释 + 更新 `PROJECT.md` §5.1 + 加条目到 `notes/next.md` 作为复查触发器）

---

## cursor 的非约束性建议（2026-04-17 更新）

**原推荐路径 A 基于"前端未起"的错误前提，本次修订撤回**。

**新倾向**：**路径 D（冻结 legacy）作为短期**，**路径 B（legacy 走 HTTP）作为中期目标**。

理由：

1. **路径 D 保住前端可用性** —— 用户虽然 v0 未上线，但 dev / demo 期间前端能跑是起步条件
2. **路径 D 明示 legacy 是例外不是默认**，硬规则 #6 仍对新代码生效
3. **路径 B 是真正的终局**，但前置依赖 AXL 流式端点 + KPAX v0 前端 PRD，时机未到
4. **路径 A 的代价** 在前端依赖面纠正后，变成"要么砍产品形态要么 1-2 周重写前端"，都不是 pilot 启动前 P0 范围应该承担的代价
5. **路径 C 的问题** 是"条件门让规则软化"，路径 D 用"登记例外"替换条件门，规则完整度比 C 高

**路径 A 仍然合理的场景**：Ken 明确说"KPAX v0 前端要从头重做，现有前端 7 文件一并删"。此时弃后端 + 删前端 + 删 sys.path hack 是同一个动作，干净利落。

**路径 B 启动时机**：
- 前置 1：cc 出 KPAX v0 前端协议 PRD（含 SSE event schema / session state 模型）
- 前置 2：AXL kpax_router.py 从 mock 改真（包括 `/axl/v1/debate/stream` + `/axl/v1/debate/{id}/messages`）
- 然后：cursor 在 `kpax_svc/routers/v1_session.py` 重建 session state 流程，走 HTTP，legacy `analyze.py` / `report.py` 同步删，例外登记清

---

## 决策请求

请 Ken 在下面四路径中选一条 + 是否一并清理 `kpax_svc/__init__.py` sys.path hack。

**路径 A**（弃用 legacy + 清 path hack）：全面符合硬规则 #6，但**前端 7 文件需同步处理（接受 404 / 迁 v1 / 重写 v0）**  
**路径 B**（legacy 走 HTTP）：保留路径 + 协议 + 前端，需要 cc 出 PRD + AXL 端点改真，约 1 工作日跨团队  
**路径 C**（条件门保留）：**不推荐**，硬规则软化  
**路径 D**（冻结 legacy + 例外登记）：保前端可用 + 硬规则例外明示 + 替换时机绑定 v0 PRD（**cursor 新倾向**）

path hack 清理选项：
- **随路径 A 清**：KPAX 彻底脱耦
- **随路径 D 保留**：加注释"legacy 弃用后一并删"，由下次路径 B 迁移时清
- **随路径 B 清**：真正迁移完成后自然清
- **随路径 C 保留**：不推荐

待 Ken 拍板 + @codex 审本评估是否完整。

---

## 附：本次已修的 KPAX 违规（上游 context）

| 文件 | 改动 | 状态 |
|---|---|---|
| `kpax_svc/clients/llm_client.py` | 新建，独立 litellm 薄封装 | 已合并 |
| `kpax_svc/services/question_parser.py` | `from app.services.ai_provider` → `from kpax_svc.clients.llm_client` | 已合并 |
| `kpax_svc/services/expert_builder.py` | 同上 | 已合并 |
| `kpax_svc/services/report_generator.py` | 同上 | 已合并 |
| `kpax_svc/routers/v1_analyze.py` (`_chat_fn`) | stub (`NotImplementedError`) → 接 `llm_client.chat_completion` | 已合并 |

smoke test 通过：`python -c "from kpax_svc.clients.llm_client import ...; from kpax_svc.services.{question_parser,expert_builder,report_generator} import ...; from kpax_svc.main import app"` 全部 OK，routes 列表正常。
