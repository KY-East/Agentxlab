"""Restore first-gen seed intersections mapped to OpenAlex disciplines.

Also cleans up dangling intersection_discipline refs.

Usage:
    cd backend
    python -m scripts.restore_seed_data
"""
import sys
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import (
    Discipline, Intersection, Scholar,
    intersection_discipline, intersection_scholar,
)

# Map old discipline names -> best-match OpenAlex subfield name in our DB
OLD_TO_OALEX = {
    "Philosophy of Language": "Philosophy",
    "Philosophy of Mind": "Philosophy",
    "Phenomenology": "Philosophy",
    "Aesthetics": "Visual Arts and Performing Arts",
    "Computability Theory": "Computational Theory and Mathematics",
    "Cognitive Linguistics": "Linguistics and Language",
    "Microsociology": "Sociology and Political Science",
    "Sociolinguistics": "Linguistics and Language",
    "Ethnomethodology": "Sociology and Political Science",
    "First-Order Cybernetics": "Control and Systems Engineering",
    "Second-Order Cybernetics": "Control and Systems Engineering",
    "Pragmatics": "Linguistics and Language",
    "Psychology of Creativity": "Social Psychology",
    "Artificial Intelligence": "Artificial Intelligence",
    "Actor-Network Theory": "Sociology and Political Science",
    "Narrative Psychology": "Social Psychology",
    "Personality Psychology": "Social Psychology",
    "Russian Formalism": "Literature and Literary Theory",
    "Dialogism": "Literature and Literary Theory",
    "Mathematical Logic": "Logic",
    "Information Theory": "Computer Networks and Communications",
    "Reinforcement Learning from Human Feedback": "Artificial Intelligence",
}

CROSSROADS = [
    {
        "title": "意义的接地问题",
        "old_disciplines": ["Philosophy of Language", "Philosophy of Mind", "Computability Theory"],
        "scholars": ["Stevan Harnad", "John Searle", "Kurt Gödel", "Alfred Tarski"],
        "tension": "语言符号的语义内容究竟从何而来？形式操作能否产生真正的理解？",
        "open": "多模态感知输入能否在原则上解决符号接地问题？派生意向性与原初意向性之间的鸿沟是否可以被弥合？",
    },
    {
        "title": "具身性与语言",
        "old_disciplines": ["Phenomenology", "Philosophy of Language", "Cognitive Linguistics"],
        "scholars": ["Maurice Merleau-Ponty", "Ludwig Wittgenstein", "Pierre Bourdieu", "Hubert Dreyfus", "George Lakoff & Mark Johnson"],
        "tension": "语言理解是否必须以身体经验和社会实践为前提条件？",
        "open": "具身性对语言理解是构成性条件还是发生条件？功能等价物的最低充分条件是什么？",
    },
    {
        "title": "创造力的可计算边界",
        "old_disciplines": ["Psychology of Creativity", "Computability Theory"],
        "scholars": ["Margaret Boden", "Kurt Gödel", "Alan Turing"],
        "tension": "创造力是否存在原则上不可逾越的计算边界？",
        "open": "变革性创造力的不可计算性是经验事实还是原则性限制？",
    },
    {
        "title": "社会性作为意义来源",
        "old_disciplines": ["Philosophy of Language", "Microsociology", "Sociolinguistics", "Ethnomethodology"],
        "scholars": ["Ludwig Wittgenstein", "Erving Goffman", "Basil Bernstein", "Harold Garfinkel", "Ferdinand de Saussure"],
        "tension": "意义在多大程度上是社会建构的产物？AI系统能否参与意义的社会生产？",
        "open": "AI训练数据偏向是否强化了语言等级秩序？语言游戏是否可以在人机交互中形成新变体？",
    },
    {
        "title": "Agent架构与心灵理论",
        "old_disciplines": ["Philosophy of Mind", "Artificial Intelligence"],
        "scholars": ["Marvin Minsky", "Rodney Brooks", "Daniel Dennett", "Hilary Putnam", "Jerry Fodor", "Herbert Simon"],
        "tension": "心灵的理论模型与智能系统的工程架构之间存在何种映射关系？",
        "open": "心智社会模型与多Agent架构的结构相似性是否暗示了智能组织的普遍原理？",
    },
    {
        "title": "控制论闭环与语用反馈",
        "old_disciplines": ["First-Order Cybernetics", "Pragmatics", "Philosophy of Language"],
        "scholars": ["Norbert Wiener", "H.P. Grice", "Dan Sperber & Deirdre Wilson", "Robert Stalnaker", "W. Ross Ashby"],
        "tension": "语言交际中的反馈机制与控制论中的反馈回路是否共享深层结构？",
        "open": "自进化Agent中的反馈机制是否可以被形式化为超稳定系统？",
    },
    {
        "title": "观察者问题",
        "old_disciplines": ["Second-Order Cybernetics", "Phenomenology", "Actor-Network Theory"],
        "scholars": ["Heinz von Foerster", "Edmund Husserl", "Bruno Latour", "Thomas Nagel"],
        "tension": "研究者对AI系统的观察和评估本身如何构成和塑造了研究对象？",
        "open": "对AI意识或理解的评估在多大程度上反映了评估者自身的理论预设？",
    },
    {
        "title": "形式系统与自然语言的鸿沟",
        "old_disciplines": ["Philosophy of Language", "Mathematical Logic", "Information Theory"],
        "scholars": ["Gottlob Frege", "Ludwig Wittgenstein", "Claude Shannon", "Saul Kripke"],
        "tension": "形式逻辑的精确性与自然语言的灵活性之间的张力如何在AI系统中具体化？",
        "open": "Wittgenstein的转变是否预示了AI研究需要从逻辑图像转向生活形式？",
    },
    {
        "title": "RLHF与语言扭曲的技术机制",
        "old_disciplines": ["Information Theory", "First-Order Cybernetics", "Reinforcement Learning from Human Feedback"],
        "scholars": ["Claude Shannon", "W. Ross Ashby"],
        "tension": "RLHF训练如何系统性地扭曲AI的语言输出？模型趋同的技术根源是什么？",
        "open": "RLHF导致的语言扭曲是可矫正的工程缺陷还是范式本身的结构性限制？",
    },
    {
        "title": "叙事身份与个人复制",
        "old_disciplines": ["Narrative Psychology", "Personality Psychology", "Philosophy of Mind"],
        "scholars": ["Paul Ricoeur", "Jerome Bruner", "Dan McAdams", "Gordon Allport", "Lewis Goldberg", "Pierre Bourdieu"],
        "tension": "个人身份能否通过叙事和偏好的形式化被充分捕获？",
        "open": "Ricoeur的自性维度是否可以通过偏好模型和叙事模板的组合来近似？",
    },
    {
        "title": "陌生化、审美判断与AI的语言贫困",
        "old_disciplines": ["Russian Formalism", "Dialogism", "Aesthetics", "Psychology of Creativity"],
        "scholars": ["Viktor Shklovsky", "Roman Jakobson", "Mikhail Bakhtin", "Immanuel Kant", "John Dewey"],
        "tension": "AI的语言同质化是否本质上违反了文学和创造性语言的核心原则？",
        "open": "AI能否实现真正的陌生化？LLM趋向分布众数的生成机制是否与陌生化要求相矛盾？",
    },
]


def main():
    db = SessionLocal()

    # 1. Clean up ALL existing intersections (they have dangling refs)
    existing_ixs = db.query(Intersection).all()
    if existing_ixs:
        ix_ids = [ix.id for ix in existing_ixs]
        db.execute(intersection_discipline.delete().where(
            intersection_discipline.c.intersection_id.in_(ix_ids)
        ))
        db.execute(intersection_scholar.delete().where(
            intersection_scholar.c.intersection_id.in_(ix_ids)
        ))
        db.query(Intersection).filter(Intersection.id.in_(ix_ids)).delete(synchronize_session=False)
        db.flush()
        print(f"Cleaned {len(ix_ids)} old intersections with dangling refs")

    # 2. Build lookup caches
    disc_cache: dict[str, Discipline] = {}
    for d in db.query(Discipline).all():
        disc_cache[d.name_en] = d

    scholar_cache: dict[str, Scholar] = {}
    for s in db.query(Scholar).all():
        scholar_cache[s.name] = s

    # 3. Insert seed intersections with mapped disciplines
    created = 0
    for cr in CROSSROADS:
        mapped_disc_names = set()
        for old_name in cr["old_disciplines"]:
            oalex_name = OLD_TO_OALEX.get(old_name, old_name)
            mapped_disc_names.add(oalex_name)

        disc_ids = []
        for name in mapped_disc_names:
            d = disc_cache.get(name)
            if d:
                disc_ids.append(d.id)
            else:
                print(f"  WARNING: '{name}' not found in DB, skipping for '{cr['title']}'")

        if len(disc_ids) < 2:
            print(f"  SKIP '{cr['title']}': only {len(disc_ids)} valid disciplines")
            continue

        ix = Intersection(
            title=cr["title"],
            status="active",
            core_tension=cr["tension"],
            open_questions=cr["open"],
        )
        db.add(ix)
        db.flush()

        for did in set(disc_ids):
            db.execute(intersection_discipline.insert().values(
                intersection_id=ix.id, discipline_id=did,
            ))

        for sn in cr.get("scholars", []):
            s = scholar_cache.get(sn)
            if s:
                db.execute(intersection_scholar.insert().values(
                    intersection_id=ix.id, scholar_id=s.id,
                ))

        created += 1
        disc_names = [disc_cache.get(OLD_TO_OALEX.get(n, n), Discipline(name_en="?")).name_en for n in cr["old_disciplines"]]
        print(f"  [{ix.id}] {cr['title']} -> {disc_names}")

    db.commit()
    print(f"\nDone. Created {created} seed intersections.")

    # Verify
    from sqlalchemy.orm import selectinload
    ixs = db.query(Intersection).options(
        selectinload(Intersection.disciplines),
        selectinload(Intersection.scholars),
    ).all()
    print(f"\nVerification: {len(ixs)} intersections in DB")
    for ix in ixs:
        dnames = [d.name_en for d in ix.disciplines]
        snames = [s.name for s in ix.scholars]
        print(f"  [{ix.id}] {ix.title}")
        print(f"      discs: {dnames}")
        print(f"      scholars: {snames[:3]}{'...' if len(snames) > 3 else ''}")

    db.close()


if __name__ == "__main__":
    main()
