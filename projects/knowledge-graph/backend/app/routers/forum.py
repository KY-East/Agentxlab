"""Forum endpoints — posts, comments, votes."""

from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, case
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.forum import ForumPost, ForumComment, ForumVote
from app.models.user import User
from app.schemas import (
    ForumPostCreate,
    ForumPostUpdate,
    ForumPostOut,
    ForumCommentCreate,
    ForumCommentOut,
    ForumAuthor,
    VoteRequest,
    VoteResponse,
)
from app.services.auth import get_current_user, get_optional_user
from app.services.points import award_points

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/forum", tags=["forum"])


# ── Stats ──


@router.get("/stats")
def forum_stats(db: Session = Depends(get_db)):
    total_posts = db.query(ForumPost).count()
    ai_posts = db.query(ForumPost).filter(ForumPost.zone == "ai_generated").count()
    community_posts = db.query(ForumPost).filter(ForumPost.zone == "community").count()
    experiment_posts = db.query(ForumPost).filter(ForumPost.post_type == "experiment_result").count()
    verified_posts = db.query(ForumPost).filter(ForumPost.status == "verified").count()
    total_comments = db.query(ForumComment).count()
    return {
        "total_posts": total_posts,
        "ai_posts": ai_posts,
        "community_posts": community_posts,
        "experiment_posts": experiment_posts,
        "verified_posts": verified_posts,
        "total_comments": total_comments,
    }


@router.get("/hot-tags")
def hot_tags(limit: int = Query(15, le=50), db: Session = Depends(get_db)):
    """Return the most common discipline tags across all posts."""
    rows = db.query(ForumPost.discipline_tags).filter(ForumPost.discipline_tags.isnot(None)).all()
    counter: dict[str, int] = {}
    for (raw,) in rows:
        try:
            tags = json.loads(raw)
            for tag in tags:
                counter[tag] = counter.get(tag, 0) + 1
        except (json.JSONDecodeError, TypeError):
            pass
    sorted_tags = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [{"tag": tag, "count": count} for tag, count in sorted_tags]


@router.post("/seed-demo")
def seed_demo_posts(db: Session = Depends(get_db), user: User = Depends(get_optional_user)):
    """Insert 40 demo posts (20 AI + 20 community). Resets on each call.
    Requires admin role in production; unauthenticated access allowed only when no users exist yet.
    """
    user_count = db.query(User).count()
    if user_count > 0 and (user is None or user.role != "admin"):
        raise HTTPException(403, "Only admin can seed demo data")
    db.query(ForumComment).filter(
        ForumComment.post_id.in_(
            db.query(ForumPost.id).filter(ForumPost.title.like("[Demo]%"))
        )
    ).delete(synchronize_session=False)
    db.query(ForumPost).filter(ForumPost.title.like("[Demo]%")).delete(synchronize_session=False)
    db.flush()

    ai_posts = [
        {"title": "[Demo][AI] 物理学 x 经济学：熵增定律与市场失灵的结构类比", "post_type": "debate_summary", "status": "theory_ready", "discipline_tags": json.dumps(["Physics", "Economics"]), "vote_score": 42, "comment_count": 7, "content": "### Consensus\n\n热力学第二定律与经济系统中的信息不对称之间存在深层结构相似性。两者都描述了封闭系统中秩序自发下降的趋势。\n\n### Disagreements\n\n经济系统是否真的是'封闭系统'存在分歧。\n\n### Research Directions\n\n建议利用 Shannon 信息论框架量化市场信息不对称程度。\n\n---\n\n### Cross-Domain Sparks\n\n- **[analogy]** 市场崩盘可类比为热力学相变点 (★★★★ 0.85)\n- **[transfer]** 玻尔兹曼分布可建模财富分配 (★★★ 0.72)"},
        {"title": "[Demo][Spark] 市场崩盘可类比为热力学系统的相变点", "post_type": "spark_highlight", "status": "open", "discipline_tags": json.dumps(["Physics", "Economics"]), "is_pinned": True, "vote_score": 89, "comment_count": 14, "content": "**Type:** analogy\n**Score:** 0.85\n\n市场崩盘的临界行为与物理学中的相变在数学结构上高度相似。两者都展现出临界指数、标度不变性和长程关联。"},
        {"title": "[Demo][AI] 神经科学 x 计算机科学：意识的可计算性", "post_type": "debate_summary", "status": "open", "discipline_tags": json.dumps(["Neuroscience", "Computer Science"]), "vote_score": 31, "comment_count": 12, "content": "### Consensus\n\n当前人工神经网络与生物神经网络在信息处理机制上存在根本差异，简单的 scaling 不太可能产生意识。\n\n### Disagreements\n\nCS 方认为意识是涌现性质，神经科学方认为依赖特定生物化学基底。\n\n### Research Directions\n\n设计'意识检测基准测试'，结合 IIT 和 GWT 理论。"},
        {"title": "[Demo][AI] 生物学 x 材料科学：自修复材料的仿生机制", "post_type": "debate_summary", "status": "theory_ready", "discipline_tags": json.dumps(["Biology", "Materials Science"]), "vote_score": 55, "comment_count": 9, "content": "### Consensus\n\n生物体的自修复机制（如骨骼重塑、皮肤愈合）可以为智能材料设计提供关键灵感。\n\n### Research Directions\n\n开发含微胶囊的聚合物基底，模拟血液凝固的级联反应。"},
        {"title": "[Demo][Spark] 蚁群觅食算法可优化城市物流网络", "post_type": "spark_highlight", "status": "open", "discipline_tags": json.dumps(["Biology", "Urban Planning"]), "is_pinned": True, "vote_score": 73, "comment_count": 8, "content": "**Type:** transfer\n**Score:** 0.91\n\n蚂蚁通过信息素形成的最短路径选择机制，可直接映射到城市最后一公里配送优化。实验表明蚁群算法在动态路网条件下比 Dijkstra 效率高 23%。"},
        {"title": "[Demo][AI] 心理学 x 人工智能：AI Agent 的认知偏差模拟", "post_type": "debate_summary", "status": "open", "discipline_tags": json.dumps(["Psychology", "Computer Science"]), "vote_score": 27, "comment_count": 6, "content": "### Consensus\n\n在 AI Agent 中植入认知偏差（如确认偏差、锚定效应）可以生成更接近人类的决策模式。\n\n### Disagreements\n\n心理学方担忧这会放大 AI 的不可预测性。"},
        {"title": "[Demo][AI] 数学 x 音乐学：和声结构的群论分析", "post_type": "debate_summary", "status": "theory_ready", "discipline_tags": json.dumps(["Mathematics", "Music"]), "vote_score": 38, "comment_count": 4, "content": "### Consensus\n\n西方和声体系中的调性关系可以用循环群 Z12 和二面体群来精确描述。\n\n### Research Directions\n\n将群论拓展到微分音体系和非西方调式系统。"},
        {"title": "[Demo][Spark] 量子纠缠概念可解释语言中的远距离依赖", "post_type": "spark_highlight", "status": "open", "discipline_tags": json.dumps(["Physics", "Linguistics"]), "vote_score": 44, "comment_count": 11, "content": "**Type:** analogy\n**Score:** 0.82\n\n自然语言中的长距离语法依赖（如英语关系从句）与量子纠缠有结构相似性：两个语法成分在任意距离上保持关联。"},
        {"title": "[Demo][AI] 社会学 x 流体力学：人群运动的 Navier-Stokes 方程", "post_type": "debate_summary", "status": "experimenting", "discipline_tags": json.dumps(["Sociology", "Physics"]), "vote_score": 61, "comment_count": 15, "content": "### Consensus\n\n高密度人群运动确实表现出流体力学特征，特别是在紧急疏散场景下。\n\n### Disagreements\n\n个体决策的非理性因素（恐慌）是否能被连续介质模型捕捉。"},
        {"title": "[Demo][AI] 生态学 x 经济学：生态系统服务的市场定价困境", "post_type": "debate_summary", "status": "open", "discipline_tags": json.dumps(["Ecology", "Economics"]), "vote_score": 22, "comment_count": 3, "content": "### Consensus\n\n生态系统服务（如碳汇、水源涵养）在理论上可以被定价，但实践中面临严重的外部性和代际公平问题。\n\n### Research Directions\n\n探索区块链技术在生态服务碳交易中的应用。"},
        {"title": "[Demo][Spark] DNA 折纸术可用于制造纳米级芯片", "post_type": "spark_highlight", "status": "open", "discipline_tags": json.dumps(["Biology", "Electrical Engineering"]), "is_pinned": True, "vote_score": 95, "comment_count": 19, "content": "**Type:** transfer\n**Score:** 0.93\n\nDNA 折纸技术已在实验中实现 2nm 精度的自组装结构，这为突破光刻极限的芯片制造提供了全新路径。"},
        {"title": "[Demo][AI] 哲学 x 量子物理：观察者问题的跨学科对话", "post_type": "debate_summary", "status": "open", "discipline_tags": json.dumps(["Philosophy", "Physics"]), "vote_score": 48, "comment_count": 21, "content": "### Consensus\n\n量子力学中的测量问题和哲学中的意识难题存在深层关联，但目前缺乏统一的形式化框架。\n\n### Disagreements\n\n物理学方拒绝将意识作为量子力学的基本要素；哲学方认为忽略观察者的主体性是逃避问题。"},
        {"title": "[Demo][AI] 气候学 x 博弈论：国际气候协议的囚徒困境", "post_type": "debate_summary", "status": "theory_ready", "discipline_tags": json.dumps(["Climate Science", "Economics"]), "vote_score": 36, "comment_count": 8, "content": "### Consensus\n\n巴黎协定本质上是一个多方重复博弈，各国的减排承诺受到短期经济利益的制约。\n\n### Research Directions\n\n用演化博弈论模拟不同惩罚机制下各国的减排策略收敛情况。"},
        {"title": "[Demo][Spark] 免疫系统的抗体多样性机制可改进推荐算法", "post_type": "spark_highlight", "status": "open", "discipline_tags": json.dumps(["Immunology", "Computer Science"]), "vote_score": 52, "comment_count": 7, "content": "**Type:** transfer\n**Score:** 0.87\n\n免疫系统通过 V(D)J 重组产生海量抗体多样性的机制，可以启发推荐系统的冷启动探索策略，避免过早收敛到局部最优。"},
        {"title": "[Demo][AI] 语言学 x 计算机科学：大语言模型是否真正'理解'语法", "post_type": "debate_summary", "status": "open", "discipline_tags": json.dumps(["Linguistics", "Computer Science"]), "vote_score": 71, "comment_count": 33, "content": "### Consensus\n\nLLM 在表面行为上展现出语法能力，但其内部表征是否对应人类的语法知识仍有争议。\n\n### Disagreements\n\n语言学方坚持形式语法是必要的认知结构；CS 方认为统计规律已经足够解释语言能力。"},
        {"title": "[Demo][AI] 考古学 x 遥感技术：卫星数据重建古代贸易路线", "post_type": "debate_summary", "status": "experimenting", "discipline_tags": json.dumps(["Archaeology", "Remote Sensing"]), "vote_score": 29, "comment_count": 5, "content": "### Consensus\n\n多光谱卫星影像可以检测到古代道路留下的地表微量异常，为丝绸之路等贸易网络的精确重建提供新工具。\n\n### Research Directions\n\n结合 LiDAR 与 SAR 数据，在植被覆盖区发现隐藏的古代遗址。"},
        {"title": "[Demo][Spark] 进化博弈论可解释编程语言的采用扩散", "post_type": "spark_highlight", "status": "open", "discipline_tags": json.dumps(["Biology", "Computer Science"]), "vote_score": 33, "comment_count": 6, "content": "**Type:** analogy\n**Score:** 0.79\n\n编程语言的竞争采用模式（如 Python 取代 Perl）与生物种群的竞争排斥原理在动力学上高度相似。"},
        {"title": "[Demo][AI] 化学 x 艺术史：颜料化学与文艺复兴绘画风格的关系", "post_type": "debate_summary", "status": "open", "discipline_tags": json.dumps(["Chemistry", "Art History"]), "vote_score": 19, "comment_count": 2, "content": "### Consensus\n\n15 世纪油画技法革命的核心驱动力之一是含铅颜料化学的突破，这直接影响了画面的层次感和光泽表现。\n\n### Research Directions\n\n用 X 射线荧光光谱分析博物馆藏品，建立颜料-风格关联数据库。"},
        {"title": "[Demo][AI] 城市规划 x 复杂系统：城市增长的分形模型", "post_type": "debate_summary", "status": "theory_ready", "discipline_tags": json.dumps(["Urban Planning", "Mathematics"]), "vote_score": 40, "comment_count": 10, "content": "### Consensus\n\n城市边界和道路网络的扩展确实表现出分形维数稳定的特征，Zipf 定律在全球城市中普遍适用。\n\n### Research Directions\n\n将元胞自动机模型与真实 GIS 数据结合，预测中国二三线城市未来 20 年的扩张模式。"},
        {"title": "[Demo][Spark] 混沌理论中的蝴蝶效应可量化社交媒体舆论极化", "post_type": "spark_highlight", "status": "open", "discipline_tags": json.dumps(["Mathematics", "Sociology"]), "vote_score": 57, "comment_count": 13, "content": "**Type:** fusion\n**Score:** 0.88\n\n将 Lorenz 吸引子模型应用于社交媒体意见动力学：小扰动（如一条争议性推文）在特定条件下可导致舆论从均衡态跳跃到极化态，且路径高度敏感。"},
    ]

    community_posts = [
        {"title": "[Demo] 有人用过辩论功能做真实的文献综述吗？", "post_type": "question", "status": "open", "discipline_tags": json.dumps(["跨学科方法"]), "vote_score": 15, "comment_count": 8, "content": "我是做交叉学科研究的博士生，最近试了一下辩论功能让 AI Agent 们讨论我的课题方向。感觉挺有意思的，特别是不同学科的 Agent 确实会从不同角度提出我没想到的点。但我不确定这些结果在学术上有多大参考价值。\n\n想问问社区里有没有人真正把辩论输出用在了论文或者 proposal 里？效果如何？"},
        {"title": "[Demo] 分享：用 AI 辩论发现的新方向，我真的去做了预实验", "post_type": "experiment_result", "status": "experimenting", "discipline_tags": json.dumps(["Materials Science", "Biology"]), "vote_score": 67, "comment_count": 23, "content": "之前跑了一场材料科学 x 生物学的辩论，AI 提到了'仿生自修复材料'的方向。说实话一开始觉得是瞎扯，但查了文献发现确实有人在做。\n\n上周做了简单的预实验：PVA 水凝胶 + 硼酸交联，切断后观察 24h 自修复率约 78%。有没有做类似方向的同学想一起深入？"},
        {"title": "[Demo] 建议：平台应该增加对实验条件的标准化记录", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["平台建设"]), "vote_score": 24, "comment_count": 5, "content": "每次辩论的条件（学科数量、Agent 数量、性格分布、轮数等）对结果影响很大，但论坛帖子里看不到这些。如果每个帖子都附带实验条件摘要，社区就可以更好地比较辩论质量。"},
        {"title": "[Demo] 实验报告：用统计力学方法分析社交网络传播——验证了 AI 猜想", "post_type": "experiment_result", "status": "verified", "discipline_tags": json.dumps(["Physics", "Sociology", "Computer Science"]), "vote_score": 156, "comment_count": 41, "content": "## 背景\nAI 辩论假设社交网络信息传播服从统计力学中自旋模型类似的动力学规律。\n\n## 方法\n用 Twitter 公开数据集，10,000 条推文的转发链路建模，Ising 模型拟合。\n\n## 结果\n临界温度 Tc ≈ 2.3，相变附近传播行为表现 power-law 分布，与 AI 预测的定性行为一致。R² = 0.61。"},
        {"title": "[Demo] 作为一个化学系的学生，第一次理解了什么叫'交叉学科'", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["Chemistry", "感想"]), "vote_score": 88, "comment_count": 31, "content": "以前总觉得'交叉学科'就是蹭热点。直到我在平台上让化学和艺术史的 Agent 辩论，AI 居然提出了用化学分析技术来鉴定画作年代的思路，查了一下这真的是一个正在发展中的领域。\n\n原来跨学科不是随便拼凑两个学科，而是找到两个学科之间真正的交叉点。"},
        {"title": "[Demo] 求助：怎么判断 AI 给的跨学科方向是真有价值还是瞎扯？", "post_type": "question", "status": "open", "discipline_tags": json.dumps(["方法论"]), "vote_score": 43, "comment_count": 17, "content": "跑了几次辩论，AI 生成的火花有些看着很炫，但我没有足够的知识储备来判断是不是真的有学术价值。\n\n比如它说'拓扑学可以用来分析蛋白质折叠的构象空间'，这个方向靠谱吗？有没有一套评估的方法论？"},
        {"title": "[Demo] 我用这个平台帮 PI 写了一个基金 proposal 的文献综述部分", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["学术写作"]), "vote_score": 112, "comment_count": 28, "content": "流程是这样的：\n1. 先跑一场多学科辩论，让 Agent 从不同角度讨论课题\n2. 用总结功能生成结构化摘要\n3. 用论文生成功能生成大纲\n4. 手动编辑调整后，逐章让 AI 扩写\n5. 最后自己通读修改\n\n导师看了说'这个文献综述视角挺全面的'。当然我没敢说是 AI 帮忙写的..."},
        {"title": "[Demo] 关于积分系统的一点想法", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["平台建设"]), "vote_score": 19, "comment_count": 7, "content": "看到积分系统里提交验证的实验结果给 2000 分，证伪给 800 分。这个设计我很喜欢，证伪也是有价值的科学工作。\n\n建议再加一个'复现'类型：如果有人复现了别人的实验并且结果一致，也应该给高分奖励。"},
        {"title": "[Demo] 实验报告：蚁群算法优化校园快递柜配送路径", "post_type": "experiment_result", "status": "verified", "discipline_tags": json.dumps(["Biology", "Urban Planning", "Computer Science"]), "vote_score": 94, "comment_count": 16, "content": "## 背景\nAI 火花提到蚁群算法可用于物流优化。我在学校里做了实际测试。\n\n## 方法\n收集了校园快递站 30 天的配送数据，用 ACO 算法优化配送路线。\n\n## 结果\n配送总路程减少 18%，平均配送时间从 4.2h 降到 3.4h。效果显著。\n\n代码已开源在 GitHub 上，欢迎复现。"},
        {"title": "[Demo] 神经科学 PhD 来谈谈 AI 辩论中关于意识的讨论", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["Neuroscience", "Philosophy"]), "vote_score": 76, "comment_count": 22, "content": "看了平台上那场关于意识可计算性的辩论，作为一个研究意识神经关联物（NCC）的 PhD，我有些补充。\n\nAI Agent 提到的 IIT（整合信息理论）确实是当前最有影响力的意识理论之一，但它也面临着'意识的组合爆炸问题'。Phi 值的计算在超过 10 个节点的系统中就已经不可行了。\n\n我觉得辩论没有深入到这个关键瓶颈。"},
        {"title": "[Demo] 请教：有没有人研究'音乐治疗'和'免疫学'的交叉？", "post_type": "question", "status": "open", "discipline_tags": json.dumps(["Music", "Immunology"]), "vote_score": 21, "comment_count": 9, "content": "之前看到一篇论文说特定频率的音乐可以影响 NK 细胞的活性，但样本量太小，不确定结论可靠性。想问问社区有没有人在做这个方向，或者能帮我评估一下这个方向的学术潜力？"},
        {"title": "[Demo] 吐槽：AI 生成的辩论有时候太'和气'了", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["平台体验"]), "vote_score": 35, "comment_count": 14, "content": "不知道大家有没有同感：有时候 Agent 之间的辩论太容易达成共识了，特别是在自由讨论模式下。真正的学术争论应该更加激烈才对。\n\n建议增加一个'高对抗'模式，让 Agent 更倾向于质疑对方的论点而不是寻求妥协。"},
        {"title": "[Demo] 分享一个技巧：怎么让辩论质量更高", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["使用技巧"]), "vote_score": 52, "comment_count": 11, "content": "用了一段时间，总结几个让辩论质量更高的技巧：\n\n1. **学科选择很重要**：选 3-4 个学科比选 7-8 个好，太多了每个 Agent 说话机会少\n2. **权重要设**：不设权重让 AI 自动分配其实效果一般，手动指定核心/辅助更好\n3. **用辩论模式**：有明确命题的辩论模式比自由讨论产出质量更高\n4. **多跑几轮**：3 轮以上才能看到真正的交锋"},
        {"title": "[Demo] 实验报告：DNA 折纸术制备纳米级导线——初步成功", "post_type": "experiment_result", "status": "experimenting", "discipline_tags": json.dumps(["Biology", "Electrical Engineering"]), "vote_score": 201, "comment_count": 47, "content": "## 背景\n受平台上'DNA 折纸术制造纳米芯片'火花的启发。\n\n## 方法\n在实验室合成了 DNA origami 模板，通过金属化沉积（Ag+/还原）在 DNA 骨架上形成导电纳米线。\n\n## 结果\n- 成功制备了长度 100nm、宽度 ~5nm 的银纳米线\n- 导电性测试：电阻率约 8.2 μΩ·cm（纯银为 1.59 μΩ·cm）\n- 良率约 34%，需要改进\n\n## 下一步\n尝试 Au 替代 Ag 以提高导电性。"},
        {"title": "[Demo] 文科生能用这个平台吗？感觉都是理工科内容", "post_type": "question", "status": "open", "discipline_tags": json.dumps(["人文社科"]), "vote_score": 28, "comment_count": 13, "content": "看了看论坛大部分都是理工科的讨论。作为一个学传播学的研究生，我能用这个平台做什么？\n\n试着跑了一场传播学 x 心理学的辩论，感觉还行，但内容深度不如理工科方向。\n\n是不是数据库里人文社科的学科数据比较少？"},
        {"title": "[Demo] 用 Lorenz 吸引子分析了微博热搜的舆论演化，附代码", "post_type": "experiment_result", "status": "experimenting", "discipline_tags": json.dumps(["Mathematics", "Sociology"]), "vote_score": 83, "comment_count": 19, "content": "## 背景\n受那个'蝴蝶效应量化舆论极化'的火花启发。\n\n## 方法\n爬了 50 个微博热搜话题的评论时序数据，用 Lorenz 系统拟合情感倾向的动态变化。\n\n## 结果\n12 个话题表现出明显的混沌特征（最大 Lyapunov 指数 > 0），且这些话题恰好是争议最大的（如社会议题）。非争议话题（如娱乐八卦）则表现为耗散系统。\n\n代码和数据集已上传 GitHub。"},
        {"title": "[Demo] 建议加个'协作实验'功能", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["平台建设"]), "vote_score": 41, "comment_count": 8, "content": "现在认领实验方向只能在评论里说一句'我来做'，没有后续的协作机制。\n\n建议加一个类似 GitHub Issues 的功能：\n- 可以分配任务\n- 追踪实验进度\n- 上传中间结果\n- 多人协作同一个实验方向"},
        {"title": "[Demo] 从博弈论角度看这个平台的积分设计", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["Economics", "Game Theory"]), "vote_score": 62, "comment_count": 15, "content": "有意思的是，这个积分系统本身就可以用博弈论分析：\n\n- 发帖(+10)和评论(+3)是低成本行为，但积分也低\n- 验证实验(+2000)是高成本行为，但积分极高\n- 这种指数级的差异设计会激励用户走向高价值行为\n\n但有个潜在问题：如果没有对低质量内容的惩罚机制，可能会出现'灌水赚积分'的情况。建议引入负反馈。"},
        {"title": "[Demo] 实验失败也是成果：量子计算模拟蛋白质折叠——当前硬件不够", "post_type": "experiment_result", "status": "falsified", "discipline_tags": json.dumps(["Physics", "Biology", "Computer Science"]), "vote_score": 45, "comment_count": 12, "content": "## 背景\nAI 辩论建议用量子计算加速蛋白质折叠模拟。\n\n## 方法\n在 IBM Qiskit 模拟器上实现了一个简化的蛋白质折叠 VQE 算法。\n\n## 结果\n- 4 残基的极简蛋白可以正确折叠\n- 8 残基就已经超出当前硬件的量子比特和相干时间限制\n- 估算真正有用的蛋白质折叠需要 > 1000 逻辑量子比特\n\n## 结论\n方向正确但时机未到。记录这个负结果以供后来者参考。"},
        {"title": "[Demo] 第一次在论坛发帖，感谢这个社区", "post_type": "discussion", "status": "open", "discipline_tags": json.dumps(["新手"]), "vote_score": 33, "comment_count": 10, "content": "潜水了很久终于注册了。作为一个本科生，看到这么多人在认真做跨学科研究很受鼓舞。虽然我现在还没有能力做实验，但学到了很多以前完全不知道的领域和思路。\n\n如果有什么本科生也能参与的方向，请推荐给我！"},
    ]

    created = 0
    for d in ai_posts:
        d["zone"] = "ai_generated"
        db.add(ForumPost(**d))
        created += 1
    for d in community_posts:
        d["zone"] = "community"
        db.add(ForumPost(**d))
        created += 1

    db.commit()
    return {"message": f"Created {created} demo posts (20 AI + 20 community)", "created": created}


def _post_to_out(post: ForumPost, db: Session) -> ForumPostOut:
    author = None
    if post.user_id:
        u = db.query(User).get(post.user_id)
        if u:
            author = ForumAuthor(
                id=u.id, display_name=u.display_name,
                avatar_url=u.avatar_url, points=u.points,
            )

    tags = None
    if post.discipline_tags:
        try:
            tags = json.loads(post.discipline_tags)
        except (json.JSONDecodeError, TypeError):
            tags = None

    return ForumPostOut(
        id=post.id,
        user_id=post.user_id,
        author=author,
        title=post.title,
        content=post.content,
        zone=post.zone,
        post_type=post.post_type,
        status=post.status,
        debate_id=post.debate_id,
        spark_id=post.spark_id,
        parent_post_id=post.parent_post_id,
        discipline_tags=tags,
        vote_score=post.vote_score,
        comment_count=post.comment_count,
        is_pinned=post.is_pinned,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


# ── Posts ──


@router.get("/posts", response_model=list[ForumPostOut])
def list_posts(
    zone: Optional[str] = Query(None),
    post_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    discipline_tag: Optional[str] = Query(None),
    sort: str = Query("newest"),
    limit: int = Query(30, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(ForumPost)
    if zone:
        q = q.filter(ForumPost.zone == zone)
    if post_type:
        q = q.filter(ForumPost.post_type == post_type)
    if status:
        q = q.filter(ForumPost.status == status)
    if discipline_tag:
        exact_token = json.dumps(discipline_tag, ensure_ascii=False)
        q = q.filter(ForumPost.discipline_tags.contains(exact_token))

    pinned_order = case((ForumPost.is_pinned == True, 0), else_=1)

    if sort == "top":
        q = q.order_by(pinned_order, desc(ForumPost.vote_score), desc(ForumPost.created_at))
    elif sort == "hot":
        q = q.order_by(pinned_order, desc(ForumPost.comment_count), desc(ForumPost.created_at))
    else:
        q = q.order_by(pinned_order, desc(ForumPost.created_at))

    posts = q.offset(offset).limit(limit).all()
    return [_post_to_out(p, db) for p in posts]


@router.get("/posts/{post_id}", response_model=ForumPostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(ForumPost).get(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    return _post_to_out(post, db)


@router.post("/posts", response_model=ForumPostOut)
def create_post(
    body: ForumPostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = ForumPost(
        user_id=user.id,
        title=body.title,
        content=body.content,
        zone="community",
        post_type=body.post_type,
        discipline_tags=json.dumps(body.discipline_tags) if body.discipline_tags else None,
        parent_post_id=body.parent_post_id,
    )
    db.add(post)
    db.flush()
    award_points(user.id, "create_post", db, ref_type="post", ref_id=post.id)
    db.commit()
    db.refresh(post)
    return _post_to_out(post, db)


@router.patch("/posts/{post_id}", response_model=ForumPostOut)
def update_post(
    post_id: int,
    body: ForumPostUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(ForumPost).get(post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    if post.user_id != user.id and user.role not in ("moderator", "admin"):
        raise HTTPException(403, "Not allowed")

    if body.title is not None:
        post.title = body.title
    if body.content is not None:
        post.content = body.content
    if body.status is not None:
        post.status = body.status
    if body.is_pinned is not None and user.role in ("moderator", "admin"):
        post.is_pinned = body.is_pinned

    db.commit()
    db.refresh(post)
    return _post_to_out(post, db)


# ── Comments ──


def _comment_to_out(c: ForumComment, db: Session) -> ForumCommentOut:
    u = db.query(User).get(c.user_id)
    author = ForumAuthor(
        id=u.id, display_name=u.display_name,
        avatar_url=u.avatar_url, points=u.points,
    ) if u else None

    return ForumCommentOut(
        id=c.id,
        post_id=c.post_id,
        user_id=c.user_id,
        author=author,
        parent_id=c.parent_id,
        content=c.content,
        vote_score=c.vote_score,
        comment_type=c.comment_type,
        created_at=c.created_at,
    )


@router.get("/posts/{post_id}/comments", response_model=list[ForumCommentOut])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(ForumComment)
        .filter(ForumComment.post_id == post_id)
        .order_by(ForumComment.created_at)
        .all()
    )

    by_id: dict[int, ForumCommentOut] = {}
    roots: list[ForumCommentOut] = []

    for c in comments:
        out = _comment_to_out(c, db)
        by_id[c.id] = out

    for c in comments:
        out = by_id[c.id]
        if c.parent_id and c.parent_id in by_id:
            by_id[c.parent_id].children.append(out)
        else:
            roots.append(out)

    return roots


@router.post("/posts/{post_id}/comments", response_model=ForumCommentOut)
def create_comment(
    post_id: int,
    body: ForumCommentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(ForumPost).get(post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    if body.parent_id is not None:
        parent = db.query(ForumComment).get(body.parent_id)
        if not parent or parent.post_id != post_id:
            raise HTTPException(400, "parent_id does not belong to this post")

    comment = ForumComment(
        post_id=post_id,
        user_id=user.id,
        parent_id=body.parent_id,
        content=body.content,
        comment_type=body.comment_type,
    )
    db.add(comment)
    post.comment_count = (post.comment_count or 0) + 1
    db.flush()

    if body.comment_type == "claim_experiment":
        award_points(user.id, "claim_experiment", db, ref_type="comment", ref_id=comment.id)
    else:
        award_points(user.id, "create_comment", db, ref_type="comment", ref_id=comment.id)

    db.commit()
    db.refresh(comment)
    return _comment_to_out(comment, db)


# ── Votes ──


@router.post("/vote", response_model=VoteResponse)
def vote(
    body: VoteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.vote_type not in (1, -1):
        raise HTTPException(400, "vote_type must be 1 or -1")
    if body.target_type not in ("post", "comment"):
        raise HTTPException(400, "target_type must be 'post' or 'comment'")

    existing = (
        db.query(ForumVote)
        .filter(
            ForumVote.user_id == user.id,
            ForumVote.target_type == body.target_type,
            ForumVote.target_id == body.target_id,
        )
        .first()
    )

    if body.target_type == "post":
        target = db.query(ForumPost).get(body.target_id)
    else:
        target = db.query(ForumComment).get(body.target_id)

    if not target:
        raise HTTPException(404, "Target not found")

    if existing:
        if existing.vote_type == body.vote_type:
            # undo
            target.vote_score -= existing.vote_type
            db.delete(existing)
            db.commit()
            return VoteResponse(new_score=target.vote_score, user_vote=None)
        else:
            # flip
            target.vote_score += body.vote_type - existing.vote_type
            existing.vote_type = body.vote_type
            db.commit()
            return VoteResponse(new_score=target.vote_score, user_vote=body.vote_type)
    else:
        vote_obj = ForumVote(
            user_id=user.id,
            target_type=body.target_type,
            target_id=body.target_id,
            vote_type=body.vote_type,
        )
        db.add(vote_obj)
        target.vote_score += body.vote_type

        if body.vote_type == 1:
            owner_id = target.user_id if hasattr(target, "user_id") else None
            if owner_id and owner_id != user.id:
                award_points(owner_id, "receive_upvote", db, ref_type=body.target_type, ref_id=body.target_id)

        db.commit()
        return VoteResponse(new_score=target.vote_score, user_vote=body.vote_type)
