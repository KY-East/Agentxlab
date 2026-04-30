"""Ken 的 3 次辩论存档校验脚本 — 证明后台记录完整。

读 DB 打印：
1. 所有辩论（按时间倒序，最近优先）
2. 对每次辩论：raw_question / proposition / 学者列表 + 分到的 model / 每轮每个人的发言 / 总结
"""
import sqlite3
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

c = sqlite3.connect("knowledge_graph.db")
cur = c.cursor()

print("=" * 80)
print("后台辩论存档总览（最近 5 次，按 created_at 倒序）")
print("=" * 80)
debates = cur.execute("""
    SELECT id, title, mode, raw_question, proposition, status, created_at
    FROM debates
    ORDER BY id DESC
    LIMIT 5
""").fetchall()

for did, title, mode, raw_q, prop, status, ts in debates:
    n_msgs = cur.execute("SELECT COUNT(*) FROM debate_messages WHERE debate_id=?", (did,)).fetchone()[0]
    n_agents = cur.execute("SELECT COUNT(*) FROM debate_agents WHERE debate_id=?", (did,)).fetchone()[0]
    print(f"\n── Debate #{did}  [{mode}]  status={status}  created_at={ts}")
    print(f"   title:        {title}")
    print(f"   raw_question: {raw_q}")
    print(f"   proposition:  {prop}")
    print(f"   agents: {n_agents}   messages: {n_msgs}")

if not debates:
    print("  (数据库里还没有辩论)")
    sys.exit(0)

# 挑最近一次详细展开
latest_id = debates[0][0]
print()
print("=" * 80)
print(f"详细展开最近一次 Debate #{latest_id}（证明每一条 AI 输出都落库）")
print("=" * 80)

agents = cur.execute("""
    SELECT id, agent_name, persona, rank, assigned_model
    FROM debate_agents WHERE debate_id=? ORDER BY sort_order
""", (latest_id,)).fetchall()

print(f"\n学者名单（{len(agents)} 位，每位的 assigned_model 是这次随机分配的）：")
for aid, name, persona, rank, model in agents:
    print(f"  agent#{aid:3d}  {rank:10s} {persona:10s}  model={model!s:35s}  {name}")

print()
msgs = cur.execute("""
    SELECT m.id, m.round_number, m.role, m.agent_id, a.agent_name, length(m.content), m.created_at
    FROM debate_messages m
    LEFT JOIN debate_agents a ON m.agent_id = a.id
    WHERE m.debate_id=?
    ORDER BY m.id
""", (latest_id,)).fetchall()

print(f"所有发言（{len(msgs)} 条，每一条完整内容都在 debate_messages.content 里）：")
current_round = None
for mid, rnd, role, agent_id, agent_name, clen, ts in msgs:
    if rnd != current_round:
        print(f"\n  === Round {rnd} ===")
        current_round = rnd
    speaker = agent_name or f"(role={role})"
    print(f"    msg#{mid:3d}  {speaker:55s}  {clen:5d} chars   {ts}")

# 总结
row = cur.execute("""
    SELECT summary_consensus, summary_disagreements,
           summary_open_questions, summary_directions
    FROM debates WHERE id=?
""", (latest_id,)).fetchone()
print("\n辩论总结（4 段，summary_* 字段）：")
labels = ["共识", "分歧", "开放问题", "建议方向"]
for lab, txt in zip(labels, row):
    got = len(txt) if txt else 0
    status = f"{got} chars" if got else "（未生成）"
    print(f"  {lab:10s}: {status}")

print()
print("=" * 80)
print("结论：这些数据在 SQLite 文件 knowledge_graph.db 里永久保存。")
print("     uvicorn 重启 / 代码 reload 都不会碰 DB。只要不删 .db 文件就一直在。")
print("=" * 80)
