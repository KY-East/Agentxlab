"""Import OpenAlex taxonomy, custom discipline extensions, scholars, papers,
and intersections into the PostgreSQL database.

Usage:
    cd backend
    python -m scripts.import_from_markdown

Loads the OpenAlex two-level taxonomy from app/data/openalex_taxonomy.json,
then merges hand-curated 3rd-level disciplines, scholars, papers, and
cross-disciplinary intersections.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from app.db import engine, SessionLocal
from app.models import (
    Base,
    Discipline,
    Scholar,
    Paper,
    Intersection,
    scholar_discipline,
    paper_author,
    intersection_discipline,
    intersection_scholar,
)

TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "openalex_taxonomy.json"

# ---------------------------------------------------------------------------
# 1. Custom 3rd-level extensions (parent subfield name -> list of (en, zh))
# ---------------------------------------------------------------------------

CUSTOM_EXTENSIONS: dict[str, list[tuple[str, str]]] = {
    # ── Arts and Humanities ──────────────────────────────────
    "Philosophy": [
        ("Ethics", "伦理学"),
        ("Metaphysics", "形而上学"),
        ("Epistemology", "认识论"),
        ("Philosophy of Language", "语言哲学"),
        ("Philosophy of Mind", "心灵哲学"),
        ("Political Philosophy", "政治哲学"),
        ("Phenomenology", "现象学"),
        ("Aesthetics", "美学"),
        ("Philosophy of Science", "科学哲学"),
        ("Philosophy of Religion", "宗教哲学"),
        ("Eastern Philosophy", "东方哲学"),
        ("Existentialism", "存在主义"),
    ],
    "History": [
        ("Ancient History", "古代史"),
        ("Medieval History", "中世纪史"),
        ("Modern History", "近现代史"),
        ("Economic History", "经济史"),
        ("History of Science and Technology", "科技史"),
        ("Social History", "社会史"),
        ("Cultural History", "文化史"),
        ("Military History", "军事史"),
        ("Intellectual History", "思想史"),
        ("Oral History", "口述史"),
        ("Digital History", "数字史学"),
    ],
    "Language and Linguistics": [
        ("Formal Semantics", "形式语义学"),
        ("Lexical Semantics", "词汇语义学"),
        ("Pragmatics", "语用学"),
        ("Semiotics", "符号学"),
        ("Sociolinguistics", "社会语言学"),
        ("Psycholinguistics", "心理语言学"),
        ("Cognitive Linguistics", "认知语言学"),
        ("Computational Linguistics", "计算语言学"),
        ("Phonetics and Phonology", "语音学与音韵学"),
        ("Syntax", "句法学"),
        ("Historical Linguistics", "历史语言学"),
    ],
    "Literature and Literary Theory": [
        ("Narratology", "叙事学"),
        ("Cognitive Poetics", "认知诗学"),
        ("Dialogism", "对话主义"),
        ("Russian Formalism", "俄国形式主义"),
        ("Structuralism", "结构主义"),
        ("Postcolonial Literature", "后殖民文学"),
        ("Comparative Literature", "比较文学"),
        ("Digital Humanities", "数字人文"),
    ],
    "Visual Arts and Performing Arts": [
        ("Film Studies", "电影学"),
        ("Theatre Studies", "戏剧学"),
        ("Art History", "艺术史"),
        ("Photography", "摄影"),
        ("Digital Art", "数字艺术"),
        ("Dance Studies", "舞蹈学"),
        ("Curatorial Studies", "策展学"),
    ],
    "Music": [
        ("Musicology", "音乐学"),
        ("Ethnomusicology", "民族音乐学"),
        ("Music Theory", "乐理"),
        ("Music Cognition", "音乐认知"),
        ("Sound Studies", "声音研究"),
        ("Music Technology", "音乐技术"),
    ],
    "Religious studies": [
        ("Theology", "神学"),
        ("Comparative Religion", "比较宗教学"),
        ("Sociology of Religion", "宗教社会学"),
        ("Buddhism Studies", "佛学研究"),
        ("Islamic Studies", "伊斯兰研究"),
    ],
    "Classics": [
        ("Classical Rhetoric", "古典修辞学"),
        ("Greek Philosophy", "古希腊哲学"),
        ("Latin Literature", "拉丁文学"),
        ("Classical Archaeology", "古典考古学"),
    ],
    "History and Philosophy of Science": [
        ("Science and Technology Studies", "科学技术研究"),
        ("Social Construction of Technology", "技术的社会建构"),
        ("Feminist Technoscience", "女性主义技术科学"),
    ],
    # ── Computer Science ─────────────────────────────────────
    "Artificial Intelligence": [
        ("Multi-Agent Systems", "多智能体系统"),
        ("Reinforcement Learning from Human Feedback", "基于人类反馈的强化学习"),
        ("AI Alignment", "AI 对齐"),
        ("Mechanistic Interpretability", "机械可解释性"),
        ("Computational Creativity", "计算创造力"),
        ("Natural Language Processing", "自然语言处理"),
        ("Computer Vision", "计算机视觉"),
        ("Robotics", "机器人学"),
        ("Knowledge Representation", "知识表示"),
        ("Machine Learning", "机器学习"),
        ("Deep Learning", "深度学习"),
        ("Generative AI", "生成式AI"),
    ],
    "Human-Computer Interaction": [
        ("User Experience Design", "用户体验设计"),
        ("Interaction Design", "交互设计"),
        ("Accessibility", "无障碍设计"),
        ("Social Computing", "社会计算"),
    ],
    "Information Systems": [
        ("Data Science", "数据科学"),
        ("Information Retrieval", "信息检索"),
        ("Database Systems", "数据库系统"),
    ],
    "Software": [
        ("Software Engineering", "软件工程"),
        ("Programming Languages", "编程语言"),
        ("Open Source Software", "开源软件"),
    ],
    # ── Psychology ───────────────────────────────────────────
    "Experimental and Cognitive Psychology": [
        ("Cognitive Psychology", "认知心理学"),
        ("Psychology of Creativity", "创造力心理学"),
        ("Narrative Psychology", "叙事心理学"),
        ("Attention and Perception", "注意与知觉"),
        ("Memory and Learning", "记忆与学习"),
        ("Decision Making", "决策心理学"),
    ],
    "Social Psychology": [
        ("Group Dynamics", "群体动力学"),
        ("Prejudice and Discrimination", "偏见与歧视"),
        ("Social Cognition", "社会认知"),
        ("Persuasion and Influence", "说服与影响"),
    ],
    "Clinical Psychology": [
        ("Psychotherapy", "心理治疗"),
        ("Psychopathology", "精神病理学"),
        ("Trauma Psychology", "创伤心理学"),
    ],
    "Developmental and Educational Psychology": [
        ("Child Development", "儿童发展"),
        ("Adolescent Psychology", "青少年心理学"),
        ("Educational Technology", "教育技术"),
        ("Learning Sciences", "学习科学"),
    ],
    # ── Neuroscience ─────────────────────────────────────────
    "Cognitive Neuroscience": [
        ("Embodied Cognition", "具身认知"),
        ("Dual Process Theory", "双过程理论"),
        ("Computational Theory of Mind", "心智计算理论"),
        ("Conceptual Metaphor Theory", "概念隐喻理论"),
        ("Consciousness Studies", "意识研究"),
        ("Neuroaesthetics", "神经美学"),
    ],
    "Behavioral Neuroscience": [
        ("Neuroeconomics", "神经经济学"),
        ("Affective Neuroscience", "情感神经科学"),
    ],
    # ── Social Sciences ──────────────────────────────────────
    "Sociology and Political Science": [
        ("Symbolic Interactionism", "符号互动论"),
        ("Dramaturgical Approach", "拟剧论"),
        ("Sociology of Knowledge", "知识社会学"),
        ("Ethnomethodology", "常人方法学"),
        ("Field Theory", "场域理论"),
        ("Actor-Network Theory", "行动者网络理论"),
        ("Social Stratification", "社会分层"),
        ("Urban Sociology", "城市社会学"),
        ("Digital Sociology", "数字社会学"),
    ],
    "Education": [
        ("Curriculum Studies", "课程研究"),
        ("Higher Education", "高等教育"),
        ("STEM Education", "STEM 教育"),
        ("Online Learning", "在线学习"),
        ("Critical Pedagogy", "批判教育学"),
    ],
    "Communication": [
        ("Media Studies", "媒体研究"),
        ("Journalism", "新闻学"),
        ("Digital Communication", "数字传播"),
        ("Rhetoric", "修辞学"),
        ("New Rhetoric", "新修辞学"),
        ("Argumentation Theory", "论证理论"),
    ],
    "Anthropology": [
        ("Cultural Anthropology", "文化人类学"),
        ("Linguistic Anthropology", "语言人类学"),
        ("Biological Anthropology", "生物人类学"),
        ("Digital Anthropology", "数字人类学"),
    ],
    "Political Science and International Relations": [
        ("Comparative Politics", "比较政治学"),
        ("International Relations Theory", "国际关系理论"),
        ("Public Policy", "公共政策"),
        ("Political Economy", "政治经济学"),
    ],
    "Law": [
        ("Constitutional Law", "宪法学"),
        ("International Law", "国际法"),
        ("AI and Law", "AI 与法律"),
        ("Intellectual Property", "知识产权"),
        ("Human Rights Law", "人权法"),
    ],
    "Cultural Studies": [
        ("Postmodernism", "后现代主义"),
        ("Identity Politics", "身份政治"),
        ("Popular Culture", "流行文化"),
        ("Digital Culture", "数字文化"),
    ],
    # ── Business & Economics ─────────────────────────────────
    "Economics and Econometrics": [
        ("Behavioral Economics", "行为经济学"),
        ("Development Economics", "发展经济学"),
        ("Macroeconomics", "宏观经济学"),
        ("Microeconomics", "微观经济学"),
        ("Computational Economics", "计算经济学"),
        ("Environmental Economics", "环境经济学"),
    ],
    "Strategy and Management": [
        ("Entrepreneurship", "创业学"),
        ("Innovation Management", "创新管理"),
        ("Strategic Management", "战略管理"),
        ("Organizational Theory", "组织理论"),
    ],
    "Finance": [
        ("Financial Economics", "金融经济学"),
        ("Fintech", "金融科技"),
        ("Risk Management", "风险管理"),
        ("Quantitative Finance", "量化金融"),
    ],
    # ── Engineering ──────────────────────────────────────────
    "Control and Systems Engineering": [
        ("First-Order Cybernetics", "一阶控制论"),
        ("Second-Order Cybernetics", "二阶控制论"),
        ("Organizational Cybernetics", "组织控制论"),
        ("General Systems Theory", "一般系统论"),
        ("Complex Systems", "复杂系统"),
    ],
    "Biomedical Engineering": [
        ("Neural Engineering", "神经工程"),
        ("Tissue Engineering", "组织工程"),
        ("Medical Devices", "医疗器械"),
    ],
    # ── Mathematics ──────────────────────────────────────────
    # ── Mathematics (continued) ────────────────────────────────
    "Discrete Mathematics and Combinatorics": [
        ("Mathematical Logic", "数理逻辑"),
        ("Modal Logic", "模态逻辑"),
        ("Proof Theory", "证明论"),
        ("Model Theory", "模型论"),
    ],
    "Applied Mathematics": [
        ("Game Theory", "博弈论"),
        ("Optimization", "优化"),
        ("Dynamical Systems", "动力系统"),
        ("Mathematical Biology", "数学生物学"),
    ],
    "Statistics and Probability": [
        ("Bayesian Statistics", "贝叶斯统计"),
        ("Causal Inference", "因果推断"),
        ("Time Series Analysis", "时间序列分析"),
    ],
    # ── Physics ──────────────────────────────────────────────
    "Statistical and Nonlinear Physics": [
        ("Classical Mechanics", "经典力学"),
        ("Thermodynamics", "热力学"),
        ("Fluid Dynamics", "流体力学"),
    ],
    "Atomic and Molecular Physics, and Optics": [
        ("Quantum Mechanics", "量子力学"),
        ("Electromagnetism", "电磁学"),
        ("Photonics", "光子学"),
    ],
    "Astronomy and Astrophysics": [
        ("Cosmology", "宇宙学"),
        ("Exoplanets", "系外行星"),
        ("Gravitational Physics", "引力物理"),
        ("General Relativity", "广义相对论"),
    ],
    "Condensed Matter Physics": [
        ("Quantum Materials", "量子材料"),
        ("Superconductivity", "超导"),
        ("Semiconductor Physics", "半导体物理"),
    ],
    "Nuclear and High Energy Physics": [
        ("Particle Physics", "粒子物理"),
        ("Quantum Field Theory", "量子场论"),
        ("String Theory", "弦理论"),
    ],
    # ── Medicine ─────────────────────────────────────────────
    "Public Health, Environmental and Occupational Health": [
        ("Global Health", "全球健康"),
        ("Health Policy", "卫生政策"),
        ("Social Determinants of Health", "健康的社会决定因素"),
    ],
    "Epidemiology": [
        ("Infectious Disease Epidemiology", "传染病流行病学"),
        ("Chronic Disease Epidemiology", "慢性病流行病学"),
        ("Molecular Epidemiology", "分子流行病学"),
    ],
    "Psychiatry and Mental health": [
        ("Addiction Medicine", "成瘾医学"),
        ("Child Psychiatry", "儿童精神科"),
        ("Neuropsychiatry", "神经精神科"),
    ],
    "Health Informatics": [
        ("Clinical Decision Support", "临床决策支持"),
        ("Electronic Health Records", "电子健康记录"),
        ("AI in Healthcare", "医疗AI"),
    ],
    # ── Environmental Science ────────────────────────────────
    "Ecology": [
        ("Conservation Biology", "保护生物学"),
        ("Climate Change Ecology", "气候变化生态学"),
        ("Biodiversity", "生物多样性"),
    ],
    "Environmental Engineering": [
        ("Sustainable Design", "可持续设计"),
        ("Carbon Capture", "碳捕获"),
        ("Circular Economy", "循环经济"),
    ],
    # ── Energy ───────────────────────────────────────────────
    "Renewable Energy, Sustainability and the Environment": [
        ("Solar Energy", "太阳能"),
        ("Wind Energy", "风能"),
        ("Energy Storage", "储能"),
        ("Green Hydrogen", "绿氢"),
    ],
    # ── Earth Sciences ───────────────────────────────────────
    "Atmospheric Science": [
        ("Climate Modeling", "气候建模"),
        ("Weather Forecasting", "天气预报"),
        ("Air Quality", "空气质量"),
    ],
    "Oceanography": [
        ("Marine Biology", "海洋生物学"),
        ("Ocean Circulation", "海洋环流"),
        ("Deep Sea Ecology", "深海生态学"),
    ],
    # ── Biology ──────────────────────────────────────────────
    "Ecology, Evolution, Behavior and Systematics": [
        ("Evolutionary Biology", "进化生物学"),
        ("Behavioral Ecology", "行为生态学"),
        ("Phylogenetics", "系统发生学"),
    ],
    # ── Signal Processing (original) ─────────────────────────
    "Signal Processing": [
        ("Information Theory", "信息论"),
        ("Speech Processing", "语音处理"),
        ("Audio Signal Processing", "音频信号处理"),
    ],
}

# ---------------------------------------------------------------------------
# 2. Scholars (name -> list of discipline name_en references)
# ---------------------------------------------------------------------------

SCHOLARS = [
    ("Gottlob Frege", ["Philosophy of Language", "Mathematical Logic"]),
    ("Ludwig Wittgenstein", ["Philosophy of Language", "Logic"]),
    ("J.L. Austin", ["Philosophy of Language"]),
    ("H.P. Grice", ["Philosophy of Language", "Pragmatics"]),
    ("John Searle", ["Philosophy of Language", "Philosophy of Mind"]),
    ("Saul Kripke", ["Philosophy of Language", "Logic", "Modal Logic"]),
    ("Franz Brentano", ["Philosophy of Mind"]),
    ("Thomas Nagel", ["Philosophy of Mind"]),
    ("Daniel Dennett", ["Philosophy of Mind"]),
    ("David Chalmers", ["Philosophy of Mind"]),
    ("Hilary Putnam", ["Philosophy of Mind"]),
    ("Jerry Fodor", ["Philosophy of Mind"]),
    ("Edmund Husserl", ["Phenomenology"]),
    ("Martin Heidegger", ["Phenomenology"]),
    ("Maurice Merleau-Ponty", ["Phenomenology"]),
    ("Hubert Dreyfus", ["Phenomenology"]),
    ("Immanuel Kant", ["Aesthetics"]),
    ("John Dewey", ["Aesthetics"]),
    ("Nelson Goodman", ["Aesthetics"]),
    ("Ferdinand de Saussure", ["Semiotics"]),
    ("Charles S. Peirce", ["Semiotics"]),
    ("Dan Sperber & Deirdre Wilson", ["Pragmatics"]),
    ("Robert Stalnaker", ["Pragmatics"]),
    ("George Lakoff & Mark Johnson", ["Cognitive Linguistics"]),
    ("William Labov", ["Sociolinguistics"]),
    ("Basil Bernstein", ["Sociolinguistics"]),
    ("Viktor Shklovsky", ["Russian Formalism"]),
    ("Roman Jakobson", ["Narratology"]),
    ("Gérard Genette", ["Narratology"]),
    ("Mikhail Bakhtin", ["Dialogism"]),
    ("Peter Stockwell", ["Cognitive Poetics"]),
    ("Reuven Tsur", ["Cognitive Poetics"]),
    ("Aristotle", ["Philosophy"]),
    ("Chaïm Perelman & Lucie Olbrechts-Tyteca", ["Philosophy"]),
    ("Stephen Toulmin", ["Philosophy"]),
    ("Daniel Kahneman", ["Cognitive Psychology"]),
    ("Margaret Boden", ["Psychology of Creativity"]),
    ("Arthur Koestler", ["Psychology of Creativity"]),
    ("Mihaly Csikszentmihalyi", ["Psychology of Creativity"]),
    ("Gordon Allport", ["Experimental and Cognitive Psychology"]),
    ("Lewis Goldberg", ["Experimental and Cognitive Psychology"]),
    ("Paul Ricoeur", ["Narrative Psychology"]),
    ("Jerome Bruner", ["Narrative Psychology"]),
    ("Dan McAdams", ["Narrative Psychology"]),
    ("Erving Goffman", ["Symbolic Interactionism", "Dramaturgical Approach"]),
    ("Peter Berger & Thomas Luckmann", ["Sociology of Knowledge"]),
    ("Harold Garfinkel", ["Ethnomethodology"]),
    ("Pierre Bourdieu", ["Field Theory"]),
    ("Bruno Latour", ["Actor-Network Theory"]),
    ("Wiebe Bijker, Thomas Hughes, Trevor Pinch", ["Sociology and Political Science"]),
    ("Donna Haraway", ["Sociology and Political Science"]),
    ("Norbert Wiener", ["First-Order Cybernetics"]),
    ("W. Ross Ashby", ["First-Order Cybernetics"]),
    ("Heinz von Foerster", ["Second-Order Cybernetics"]),
    ("Stafford Beer", ["Organizational Cybernetics"]),
    ("Marvin Minsky", ["Artificial Intelligence"]),
    ("Rodney Brooks", ["Artificial Intelligence"]),
    ("Herbert Simon", ["Artificial Intelligence"]),
    ("Allen Newell", ["Artificial Intelligence"]),
    ("Stevan Harnad", ["Artificial Intelligence"]),
    ("Kurt Gödel", ["Mathematical Logic"]),
    ("Alfred Tarski", ["Mathematical Logic"]),
    ("Alan Turing", ["Artificial Intelligence"]),
    ("Alonzo Church", ["Artificial Intelligence"]),
    ("Claude Shannon", ["Information Theory"]),
    ("Warren Weaver", ["Information Theory"]),
]

# ---------------------------------------------------------------------------
# 3. Classic papers
# ---------------------------------------------------------------------------

CLASSIC_PAPERS = [
    ("Über Sinn und Bedeutung", 1892, "Gottlob Frege"),
    ("Philosophical Investigations", 1953, "Ludwig Wittgenstein"),
    ("How to Do Things with Words", 1962, "J.L. Austin"),
    ("Logic and Conversation", 1975, "H.P. Grice"),
    ("Speech Acts", 1969, "John Searle"),
    ("Naming and Necessity", 1980, "Saul Kripke"),
    ("The Symbol Grounding Problem", 1990, "Stevan Harnad"),
    ("Course in General Linguistics", 1916, "Ferdinand de Saussure"),
    ("Relevance: Communication and Cognition", 1986, "Dan Sperber & Deirdre Wilson"),
    ("Pragmatic Presuppositions", 1974, "Robert Stalnaker"),
    ("Collected Papers (triadic sign theory)", 1931, "Charles S. Peirce"),
    ("Problems of Dostoevsky's Poetics", 1929, "Mikhail Bakhtin"),
    ("Metaphors We Live By", 1980, "George Lakoff & Mark Johnson"),
    ("The Social Stratification of English in New York City", 1966, "William Labov"),
    ("Class, Codes and Control", 1971, "Basil Bernstein"),
    ("Art as Device", 1917, "Viktor Shklovsky"),
    ("Linguistics and Poetics", 1960, "Roman Jakobson"),
    ("Narrative Discourse", 1972, "Gérard Genette"),
    ("Cognitive Poetics: An Introduction", 2002, "Peter Stockwell"),
    ("Toward a Theory of Cognitive Poetics", 1992, "Reuven Tsur"),
    ("Rhetoric", -350, "Aristotle"),
    ("The New Rhetoric", 1958, "Chaïm Perelman & Lucie Olbrechts-Tyteca"),
    ("The Uses of Argument", 1958, "Stephen Toulmin"),
    ("Psychology from an Empirical Standpoint", 1874, "Franz Brentano"),
    ("What Is It Like to Be a Bat?", 1974, "Thomas Nagel"),
    ("Consciousness Explained", 1991, "Daniel Dennett"),
    ("Facing Up to the Problem of Consciousness", 1995, "David Chalmers"),
    ("Minds and Machines", 1960, "Hilary Putnam"),
    ("The Language of Thought", 1975, "Jerry Fodor"),
    ("Logical Investigations", 1900, "Edmund Husserl"),
    ("Being and Time", 1927, "Martin Heidegger"),
    ("Phenomenology of Perception", 1945, "Maurice Merleau-Ponty"),
    ("What Computers Can't Do", 1972, "Hubert Dreyfus"),
    ("Minds, Brains, and Programs", 1980, "John Searle"),
    ("Critique of Judgment", 1790, "Immanuel Kant"),
    ("Art as Experience", 1934, "John Dewey"),
    ("Languages of Art", 1968, "Nelson Goodman"),
    ("Thinking, Fast and Slow", 2011, "Daniel Kahneman"),
    ("The Creative Mind", 1990, "Margaret Boden"),
    ("The Act of Creation", 1964, "Arthur Koestler"),
    ("Creativity", 1996, "Mihaly Csikszentmihalyi"),
    ("Personality", 1937, "Gordon Allport"),
    ("Phenotypic Personality Traits", 1993, "Lewis Goldberg"),
    ("Oneself as Another", 1990, "Paul Ricoeur"),
    ("Acts of Meaning", 1990, "Jerome Bruner"),
    ("The Redemptive Self", 2006, "Dan McAdams"),
    ("The Presentation of Self in Everyday Life", 1956, "Erving Goffman"),
    ("The Social Construction of Reality", 1966, "Peter Berger & Thomas Luckmann"),
    ("Studies in Ethnomethodology", 1967, "Harold Garfinkel"),
    ("Distinction", 1979, "Pierre Bourdieu"),
    ("Reassembling the Social", 2005, "Bruno Latour"),
    ("The Social Construction of Technological Systems", 1987, "Wiebe Bijker, Thomas Hughes, Trevor Pinch"),
    ("A Cyborg Manifesto", 1985, "Donna Haraway"),
    ("Cybernetics", 1948, "Norbert Wiener"),
    ("Design for a Brain", 1952, "W. Ross Ashby"),
    ("An Introduction to Cybernetics", 1956, "W. Ross Ashby"),
    ("On Self-Organizing Systems", 1960, "Heinz von Foerster"),
    ("Brain of the Firm", 1972, "Stafford Beer"),
    ("The Society of Mind", 1986, "Marvin Minsky"),
    ("Intelligence Without Representation", 1991, "Rodney Brooks"),
    ("The Sciences of the Artificial", 1969, "Herbert Simon"),
    ("Über formal unentscheidbare Sätze", 1931, "Kurt Gödel"),
    ("The Concept of Truth in Formalized Languages", 1933, "Alfred Tarski"),
    ("On Computable Numbers", 1936, "Alan Turing"),
    ("An Unsolvable Problem of Elementary Number Theory", 1936, "Alonzo Church"),
    ("A Mathematical Theory of Communication", 1948, "Claude Shannon"),
]

# ---------------------------------------------------------------------------
# 4. Intersections / crossroads
# ---------------------------------------------------------------------------

CROSSROADS = [
    {
        "title": "意义的接地问题",
        "disciplines": ["Philosophy of Language", "Philosophy of Mind", "Artificial Intelligence"],
        "scholars": ["Stevan Harnad", "John Searle", "Kurt Gödel", "Alfred Tarski"],
        "tension": "语言符号的语义内容究竟从何而来？形式操作能否产生真正的理解？",
        "open": "多模态感知输入能否在原则上解决符号接地问题？派生意向性与原初意向性之间的鸿沟是否可以被弥合？",
    },
    {
        "title": "具身性与语言",
        "disciplines": ["Phenomenology", "Philosophy of Language", "Cognitive Linguistics"],
        "scholars": ["Maurice Merleau-Ponty", "Ludwig Wittgenstein", "Pierre Bourdieu", "Hubert Dreyfus", "George Lakoff & Mark Johnson"],
        "tension": "语言理解是否必须以身体经验和社会实践为前提条件？",
        "open": "具身性对语言理解是构成性条件还是发生条件？功能等价物的最低充分条件是什么？",
    },
    {
        "title": "创造力的可计算边界",
        "disciplines": ["Psychology of Creativity", "Artificial Intelligence"],
        "scholars": ["Margaret Boden", "Kurt Gödel", "Alan Turing"],
        "tension": "创造力是否存在原则上不可逾越的计算边界？",
        "open": "变革性创造力的不可计算性是经验事实还是原则性限制？",
    },
    {
        "title": "社会性作为意义来源",
        "disciplines": ["Philosophy of Language", "Symbolic Interactionism", "Sociolinguistics", "Ethnomethodology"],
        "scholars": ["Ludwig Wittgenstein", "Erving Goffman", "Basil Bernstein", "Harold Garfinkel", "Ferdinand de Saussure"],
        "tension": "意义在多大程度上是社会建构的产物？AI系统能否参与意义的社会生产？",
        "open": "AI训练数据偏向是否强化了语言等级秩序？语言游戏是否可以在人机交互中形成新变体？",
    },
    {
        "title": "Agent架构与心灵理论",
        "disciplines": ["Philosophy of Mind", "Artificial Intelligence"],
        "scholars": ["Marvin Minsky", "Rodney Brooks", "Daniel Dennett", "Hilary Putnam", "Jerry Fodor", "Herbert Simon"],
        "tension": "心灵的理论模型与智能系统的工程架构之间存在何种映射关系？",
        "open": "心智社会模型与多Agent架构的结构相似性是否暗示了智能组织的普遍原理？",
    },
    {
        "title": "控制论闭环与语用反馈",
        "disciplines": ["First-Order Cybernetics", "Pragmatics", "Philosophy of Language"],
        "scholars": ["Norbert Wiener", "H.P. Grice", "Dan Sperber & Deirdre Wilson", "Robert Stalnaker", "W. Ross Ashby"],
        "tension": "语言交际中的反馈机制与控制论中的反馈回路是否共享深层结构？",
        "open": "自进化Agent中的反馈机制是否可以被形式化为超稳定系统？",
    },
    {
        "title": "观察者问题",
        "disciplines": ["Second-Order Cybernetics", "Phenomenology", "Actor-Network Theory"],
        "scholars": ["Heinz von Foerster", "Edmund Husserl", "Bruno Latour", "Thomas Nagel"],
        "tension": "研究者对AI系统的观察和评估本身如何构成和塑造了研究对象？",
        "open": "对AI意识或理解的评估在多大程度上反映了评估者自身的理论预设？",
    },
    {
        "title": "形式系统与自然语言的鸿沟",
        "disciplines": ["Philosophy of Language", "Mathematical Logic", "Information Theory"],
        "scholars": ["Gottlob Frege", "Ludwig Wittgenstein", "Claude Shannon", "Saul Kripke"],
        "tension": "形式逻辑的精确性与自然语言的灵活性之间的张力如何在AI系统中具体化？",
        "open": "Wittgenstein的转变是否预示了AI研究需要从逻辑图像转向生活形式？",
    },
    {
        "title": "RLHF与语言扭曲的技术机制",
        "disciplines": ["Information Theory", "First-Order Cybernetics", "Reinforcement Learning from Human Feedback"],
        "scholars": ["Claude Shannon", "W. Ross Ashby"],
        "tension": "RLHF训练如何系统性地扭曲AI的语言输出？模型趋同的技术根源是什么？",
        "open": "RLHF导致的语言扭曲是可矫正的工程缺陷还是范式本身的结构性限制？",
    },
    {
        "title": "叙事身份与个人复制",
        "disciplines": ["Narrative Psychology", "Experimental and Cognitive Psychology", "Philosophy of Mind"],
        "scholars": ["Paul Ricoeur", "Jerome Bruner", "Dan McAdams", "Gordon Allport", "Lewis Goldberg", "Pierre Bourdieu"],
        "tension": "个人身份能否通过叙事和偏好的形式化被充分捕获？",
        "open": "Ricoeur的自性维度是否可以通过偏好模型和叙事模板的组合来近似？",
    },
    {
        "title": "陌生化、审美判断与AI的语言贫困",
        "disciplines": ["Russian Formalism", "Dialogism", "Aesthetics", "Psychology of Creativity"],
        "scholars": ["Viktor Shklovsky", "Roman Jakobson", "Mikhail Bakhtin", "Immanuel Kant", "John Dewey"],
        "tension": "AI的语言同质化是否本质上违反了文学和创造性语言的核心原则？",
        "open": "AI能否实现真正的陌生化？LLM趋向分布众数的生成机制是否与陌生化要求相矛盾？",
    },
    # ── Physics & Astronomy ──────────────────────────────────
    {
        "title": "引力波天文学与系外行星探测",
        "disciplines": ["Gravitational Physics", "Exoplanets", "Astronomy and Astrophysics"],
        "scholars": [],
        "tension": "引力波探测技术能否为系外行星系统提供全新的观测维度？",
        "open": "LISA等空间引力波探测器能否探测到围绕致密天体运行的行星的引力信号？",
    },
    {
        "title": "宇宙学与粒子物理的统一",
        "disciplines": ["Cosmology", "Particle Physics", "Quantum Field Theory"],
        "scholars": [],
        "tension": "宇宙大尺度结构的起源与基本粒子物理之间的深层联系是什么？",
        "open": "暗物质粒子的性质能否通过宇宙学观测与对撞机实验的交叉验证来确定？",
    },
    {
        "title": "量子材料与超导机制",
        "disciplines": ["Quantum Materials", "Superconductivity", "Condensed Matter Physics"],
        "scholars": [],
        "tension": "高温超导的微观机制是否需要超越BCS理论的全新范式？",
        "open": "拓扑量子材料能否为室温超导提供新的实现路径？",
    },
    {
        "title": "弦理论与量子引力",
        "disciplines": ["String Theory", "Gravitational Physics", "Mathematical Physics"],
        "scholars": [],
        "tension": "弦理论能否提供量子引力的自洽描述？",
        "open": "弦理论景观问题是否意味着我们需要重新思考物理学中'预测'的含义？",
    },
    # ── Chemistry & Materials ────────────────────────────────
    {
        "title": "计算化学与药物发现",
        "disciplines": ["Physical and Theoretical Chemistry", "Drug Discovery", "Machine Learning"],
        "scholars": [],
        "tension": "机器学习驱动的分子设计能否取代传统的高通量筛选？",
        "open": "AI预测的分子在合成可行性和临床转化上的成功率能否超越传统方法？",
    },
    {
        "title": "电化学与可再生能源存储",
        "disciplines": ["Electrochemistry", "Energy Storage", "Materials Chemistry"],
        "scholars": [],
        "tension": "电池材料的理论能量密度极限与实际工程实现之间的鸿沟如何弥合？",
        "open": "固态电解质能否同时解决安全性和能量密度的双重挑战？",
    },
    {
        "title": "催化科学与绿色化学",
        "disciplines": ["Catalysis", "Environmental Chemistry", "Organic Chemistry"],
        "scholars": [],
        "tension": "如何设计高选择性催化剂来实现化学工业的绿色转型？",
        "open": "仿生催化能否在温和条件下实现工业规模的化学转化？",
    },
    # ── Earth & Environment ──────────────────────────────────
    {
        "title": "气候建模与大气科学",
        "disciplines": ["Climate Modeling", "Atmospheric Science", "Dynamical Systems"],
        "scholars": [],
        "tension": "气候模型的不确定性如何影响政策制定的可靠性？",
        "open": "AI辅助的气候模型能否突破传统数值模拟的分辨率限制？",
    },
    {
        "title": "海洋环流与气候变化",
        "disciplines": ["Ocean Circulation", "Climate Change Ecology", "Global and Planetary Change"],
        "scholars": [],
        "tension": "大西洋经向翻转环流的减弱对全球气候系统的影响有多大？",
        "open": "深海碳汇机制能否被利用来缓解大气CO2浓度的上升？",
    },
    {
        "title": "生物多样性与生态系统服务",
        "disciplines": ["Biodiversity", "Ecology", "Environmental Economics"],
        "scholars": [],
        "tension": "生物多样性的经济价值评估能否有效推动保护政策？",
        "open": "生态系统临界点的早期预警信号能否被可靠地检测？",
    },
    {
        "title": "碳捕获与循环经济",
        "disciplines": ["Carbon Capture", "Circular Economy", "Chemical Engineering"],
        "scholars": [],
        "tension": "碳捕获技术的规模化部署在经济上是否可行？",
        "open": "直接空气碳捕获的能量效率能否达到大规模部署的门槛？",
    },
    # ── Biology & Medicine ───────────────────────────────────
    {
        "title": "基因编辑与伦理边界",
        "disciplines": ["Genetics", "Ethics", "Biotechnology"],
        "scholars": [],
        "tension": "CRISPR基因编辑技术的治疗应用与增强应用之间的伦理界限在哪里？",
        "open": "生殖系基因编辑的代际影响是否可以被充分预测和控制？",
    },
    {
        "title": "神经工程与脑机接口",
        "disciplines": ["Neural Engineering", "Cognitive Neuroscience", "Biomedical Engineering"],
        "scholars": [],
        "tension": "脑机接口的信号解码精度是否足以实现复杂认知功能的外部化？",
        "open": "长期植入式脑机接口的生物相容性和信号稳定性问题能否被解决？",
    },
    {
        "title": "AI辅助临床决策",
        "disciplines": ["AI in Healthcare", "Clinical Decision Support", "Machine Learning"],
        "scholars": [],
        "tension": "AI诊断系统的黑箱性质与临床决策的透明性要求之间如何调和？",
        "open": "AI辅助诊断的法律责任应当如何在医生、开发者和医疗机构之间分配？",
    },
    {
        "title": "表观遗传学与环境暴露",
        "disciplines": ["Molecular Biology", "Epidemiology", "Environmental Chemistry"],
        "scholars": [],
        "tension": "环境因素导致的表观遗传修饰在多大程度上可以跨代遗传？",
        "open": "环境表观遗传学能否解释慢性疾病的代际传递模式？",
    },
    {
        "title": "微生物组与免疫系统",
        "disciplines": ["Microbiology", "Immunology", "Gastroenterology"],
        "scholars": [],
        "tension": "肠道微生物组如何调控宿主免疫系统的发育和功能？",
        "open": "微生物组移植能否成为自身免疫疾病的可靠治疗策略？",
    },
    {
        "title": "进化医学与疾病易感性",
        "disciplines": ["Evolutionary Biology", "Epidemiology", "Genetics"],
        "scholars": [],
        "tension": "进化适应与现代疾病易感性之间的错配假说有多大解释力？",
        "open": "进化医学视角能否帮助解释为什么某些遗传变异在自然选择下被保留？",
    },
    # ── Engineering & Computing ──────────────────────────────
    {
        "title": "机器人学与具身AI",
        "disciplines": ["Robotics", "Embodied Cognition", "Control and Systems Engineering"],
        "scholars": [],
        "tension": "物理交互经验对AI系统获得通用智能是否是必要条件？",
        "open": "模拟环境中的具身训练能否有效迁移到真实世界的机器人系统？",
    },
    {
        "title": "量子计算与密码学",
        "disciplines": ["Condensed Matter Physics", "Computational Theory and Mathematics", "Computer Networks and Communications"],
        "scholars": [],
        "tension": "量子计算机对现有密码体系的威胁有多紧迫？",
        "open": "后量子密码算法能否在量子计算实用化之前完成标准化部署？",
    },
    {
        "title": "半导体物理与AI芯片",
        "disciplines": ["Semiconductor Physics", "Artificial Intelligence", "Electrical and Electronic Engineering"],
        "scholars": [],
        "tension": "摩尔定律的终结对AI硬件发展意味着什么？",
        "open": "神经形态芯片能否在能效上实现对传统GPU架构的根本性超越？",
    },
    {
        "title": "复杂系统与城市规划",
        "disciplines": ["Complex Systems", "Urban Studies", "Computational Economics"],
        "scholars": [],
        "tension": "城市作为复杂自适应系统，其涌现行为能否被有效预测和引导？",
        "open": "基于Agent的城市模拟能否为规划决策提供可靠依据？",
    },
    # ── Social Sciences & Economics ──────────────────────────
    {
        "title": "行为经济学与公共政策",
        "disciplines": ["Behavioral Economics", "Public Policy", "Social Psychology"],
        "scholars": [],
        "tension": "助推(nudge)策略在多大程度上尊重了个体的自主选择权？",
        "open": "数字环境中的行为干预是否需要全新的伦理框架？",
    },
    {
        "title": "因果推断与社会科学方法论",
        "disciplines": ["Causal Inference", "Sociology and Political Science", "Epidemiology"],
        "scholars": [],
        "tension": "观察性研究中的因果推断在何种条件下可以达到实验研究的可靠性？",
        "open": "机器学习驱动的因果发现算法能否从大规模观察数据中可靠地识别因果关系？",
    },
    {
        "title": "金融科技与金融监管",
        "disciplines": ["Fintech", "Financial Economics", "AI and Law"],
        "scholars": [],
        "tension": "算法交易和去中心化金融对现有金融监管框架构成了哪些根本性挑战？",
        "open": "监管科技(RegTech)能否实时适应金融创新的速度？",
    },
    {
        "title": "数字社会学与平台经济",
        "disciplines": ["Digital Sociology", "Digital Communication", "Political Economy"],
        "scholars": [],
        "tension": "数字平台的权力集中如何重塑社会不平等的形态？",
        "open": "算法推荐系统是否系统性地加剧了社会极化？",
    },
    {
        "title": "博弈论与国际关系",
        "disciplines": ["Game Theory", "International Relations Theory", "Political Economy"],
        "scholars": [],
        "tension": "博弈论模型在多大程度上能够解释和预测国际冲突与合作的动态？",
        "open": "AI辅助的博弈分析能否帮助识别国际谈判中的帕累托改进机会？",
    },
    # ── Mathematics & Computing ──────────────────────────────
    {
        "title": "深度学习的数学基础",
        "disciplines": ["Deep Learning", "Statistics and Probability", "Optimization"],
        "scholars": [],
        "tension": "深度神经网络的泛化能力是否需要全新的统计学习理论来解释？",
        "open": "过参数化模型的良性过拟合现象对传统偏差-方差权衡理论意味着什么？",
    },
    {
        "title": "拓扑数据分析与机器学习",
        "disciplines": ["Geometry and Topology", "Machine Learning", "Applied Mathematics"],
        "scholars": [],
        "tension": "拓扑方法能否揭示高维数据中传统统计方法无法捕捉的结构信息？",
        "open": "持久同调等拓扑特征在实际机器学习任务中的计算效率和可扩展性如何？",
    },
    {
        "title": "贝叶斯方法与科学推理",
        "disciplines": ["Bayesian Statistics", "Philosophy of Science", "Epistemology"],
        "scholars": [],
        "tension": "贝叶斯推理是否提供了科学方法论的统一形式化框架？",
        "open": "先验选择的主观性是否从根本上限制了贝叶斯方法的客观性？",
    },
    # ── Energy & Sustainability ──────────────────────────────
    {
        "title": "绿氢经济与能源转型",
        "disciplines": ["Green Hydrogen", "Renewable Energy, Sustainability and the Environment", "Environmental Engineering"],
        "scholars": [],
        "tension": "绿色氢能的生产成本能否降低到与化石燃料竞争的水平？",
        "open": "大规模氢能基础设施的部署对电网稳定性有何影响？",
    },
    {
        "title": "太阳能与材料科学",
        "disciplines": ["Solar Energy", "Electronic, Optical and Magnetic Materials", "Physical and Theoretical Chemistry"],
        "scholars": [],
        "tension": "钙钛矿太阳能电池的稳定性问题能否被彻底解决？",
        "open": "多结串联太阳能电池的理论效率极限在工程上可以接近到什么程度？",
    },
    # ── Interdisciplinary Frontiers ──────────────────────────
    {
        "title": "AI对齐与道德哲学",
        "disciplines": ["AI Alignment", "Ethics", "Philosophy of Mind"],
        "scholars": [],
        "tension": "如何将人类价值观形式化编码到AI系统中而不丧失其复杂性和语境依赖性？",
        "open": "超级智能系统的价值对齐是否在原则上不可能完全实现？",
    },
    {
        "title": "可解释AI与信任构建",
        "disciplines": ["Mechanistic Interpretability", "Human-Computer Interaction", "Cognitive Psychology"],
        "scholars": [],
        "tension": "模型可解释性与性能之间是否存在根本性的权衡？",
        "open": "人类认知偏差如何影响对AI解释的理解和信任？",
    },
    {
        "title": "计算社会科学与数字人文",
        "disciplines": ["Data Science", "Digital Humanities", "Digital Sociology"],
        "scholars": [],
        "tension": "大数据方法能否为人文社科研究提供真正新颖的洞见？",
        "open": "数字方法是否系统性地偏向可量化的研究问题而忽视了定性理解？",
    },
    {
        "title": "数学生物学与系统生物学",
        "disciplines": ["Mathematical Biology", "Cell Biology", "Dynamical Systems"],
        "scholars": [],
        "tension": "生物系统的复杂性能否被数学模型充分捕捉？",
        "open": "多尺度生物模型的参数可辨识性问题如何解决？",
    },
    {
        "title": "意识科学的整合",
        "disciplines": ["Consciousness Studies", "Cognitive Neuroscience", "Philosophy of Mind"],
        "scholars": [],
        "tension": "意识的主观体验能否被还原为神经科学可测量的物理过程？",
        "open": "整合信息理论(IIT)和全局工作空间理论(GWT)之间的实验性区分是否可能？",
    },
    {
        "title": "深海生态与资源开发",
        "disciplines": ["Deep Sea Ecology", "Marine Biology", "Ocean Engineering"],
        "scholars": [],
        "tension": "深海矿产资源开发与脆弱深海生态系统保护之间如何取得平衡？",
        "open": "深海生态系统的恢复力在采矿扰动后的恢复时间尺度有多长？",
    },
    {
        "title": "生成式AI与知识产权",
        "disciplines": ["Generative AI", "Intellectual Property", "Ethics"],
        "scholars": [],
        "tension": "AI生成内容的版权归属应当如何界定？",
        "open": "训练数据的合理使用(fair use)边界在生成式AI时代是否需要重新定义？",
    },
    {
        "title": "自然语言处理与认知语言学",
        "disciplines": ["Natural Language Processing", "Cognitive Linguistics", "Computational Linguistics"],
        "scholars": [],
        "tension": "大语言模型学到的语言表征与人类认知中的语言表征有多大相似性？",
        "open": "LLM是否真正学会了语言的组合性语义，还是仅仅在模拟统计分布？",
    },
    {
        "title": "计算机视觉与神经科学",
        "disciplines": ["Computer Vision", "Sensory Systems", "Cognitive Neuroscience"],
        "scholars": [],
        "tension": "卷积神经网络与灵长类视觉通路的表征相似性是偶然还是必然？",
        "open": "生物视觉系统的反馈连接和注意力机制能否改进计算机视觉架构？",
    },
    {
        "title": "网络安全与国际法",
        "disciplines": ["Computer Networks and Communications", "International Law", "Political Science and International Relations"],
        "scholars": [],
        "tension": "现有国际法框架是否足以应对国家级网络攻击的治理挑战？",
        "open": "网络空间的主权概念如何与互联网的全球互联特性相调和？",
    },
    # ── Humanities × Humanities ──────────────────────────────
    {
        "title": "思想史与哲学方法论",
        "disciplines": ["Intellectual History", "Philosophy", "Epistemology"],
        "scholars": [],
        "tension": "思想史的历史叙事方法与哲学的规范性论证之间存在何种方法论张力？",
        "open": "对过去思想的历史重建能否避免以当代哲学框架进行的时代错置？",
    },
    {
        "title": "历史编纂学与认识论",
        "disciplines": ["History", "Epistemology", "Philosophy of Science"],
        "scholars": [],
        "tension": "历史知识的客观性主张如何面对后现代主义对宏大叙事的解构？",
        "open": "数字史学工具能否为历史编纂的认识论争论提供新的实证基础？",
    },
    {
        "title": "存在主义文学与现象学",
        "disciplines": ["Existentialism", "Literature and Literary Theory", "Phenomenology"],
        "scholars": [],
        "tension": "文学叙事能否比哲学论证更有效地传达存在主义的核心洞见？",
        "open": "现象学方法在文学批评中的应用是否改变了我们对'文本意义'的理解？",
    },
    {
        "title": "诠释学与文学理论",
        "disciplines": ["Philosophy", "Literature and Literary Theory", "Narratology"],
        "scholars": [],
        "tension": "文本诠释的'正确性'标准在哲学诠释学与文学理论之间如何调和？",
        "open": "数字文本分析能否为诠释学循环提供量化的突破口？",
    },
    {
        "title": "宗教哲学与伦理学",
        "disciplines": ["Philosophy of Religion", "Ethics", "Theology"],
        "scholars": [],
        "tension": "道德义务能否脱离宗教超越性框架而获得充分的理性论证基础？",
        "open": "世俗伦理学与宗教伦理学在全球多元社会中能否找到共同的规范性基础？",
    },
    {
        "title": "神学与比较宗教学",
        "disciplines": ["Theology", "Comparative Religion", "Philosophy"],
        "scholars": [],
        "tension": "不同宗教传统的真理主张之间是否存在深层的不可通约性？",
        "open": "跨宗教对话能否超越礼貌性并肩而产生真正的神学创新？",
    },
    {
        "title": "历史小说研究与叙事理论",
        "disciplines": ["History", "Narratology", "Comparative Literature"],
        "scholars": [],
        "tension": "历史小说中的虚构叙事在多大程度上构成了一种合法的历史认知方式？",
        "open": "AI生成的历史叙事是否模糊了历史与虚构之间的认识论边界？",
    },
    {
        "title": "文学史与文化史的交叉",
        "disciplines": ["Literature and Literary Theory", "Cultural History", "Social History"],
        "scholars": [],
        "tension": "文学作品应当被视为自律的审美对象还是社会文化过程的表征？",
        "open": "计算文学研究（如远读）能否揭示传统文学史方法忽略的宏观文化模式？",
    },
    {
        "title": "音乐治疗与临床心理学",
        "disciplines": ["Music Cognition", "Clinical Psychology", "Psychotherapy"],
        "scholars": [],
        "tension": "音乐对情绪和认知的影响机制能否被充分操作化为标准化的治疗方案？",
        "open": "AI生成的个性化音乐治疗在临床效果上能否匹敌人类治疗师的即兴互动？",
    },
    {
        "title": "音乐认知与神经科学",
        "disciplines": ["Music Cognition", "Cognitive Neuroscience", "Attention and Perception"],
        "scholars": [],
        "tension": "音乐加工是否依赖于专用的神经模块还是通用的认知资源？",
        "open": "音乐训练引发的神经可塑性变化是否可以迁移到非音乐认知领域？",
    },
    {
        "title": "数字艺术与计算美学",
        "disciplines": ["Digital Art", "Artificial Intelligence", "Aesthetics"],
        "scholars": [],
        "tension": "算法生成的视觉作品是否满足传统美学理论对'艺术'的充分条件？",
        "open": "人机协作创作模式是否正在产生一种不可还原为人类或机器创造力的新审美范畴？",
    },
    {
        "title": "视觉艺术与人机交互",
        "disciplines": ["Visual Arts and Performing Arts", "Human-Computer Interaction", "Interaction Design"],
        "scholars": [],
        "tension": "交互设计中的审美维度能否被形式化为可操作的设计原则？",
        "open": "沉浸式技术（VR/AR）是否正在创造一种融合视觉艺术与计算的全新表达媒介？",
    },
    {
        "title": "计算语言学与语音处理",
        "disciplines": ["Computational Linguistics", "Natural Language Processing", "Speech Processing"],
        "scholars": [],
        "tension": "端到端神经网络模型是否使传统的语言学知识在NLP中变得冗余？",
        "open": "多语言大模型能否发现人类语言学家尚未描述的跨语言共性？",
    },
    {
        "title": "自然语言处理与知识表示",
        "disciplines": ["Natural Language Processing", "Knowledge Representation", "Formal Semantics"],
        "scholars": [],
        "tension": "符号知识图谱与分布式语义表示之间的融合路径是什么？",
        "open": "神经符号整合方法能否克服纯统计NLP在逻辑推理任务上的系统性不足？",
    },
    {
        "title": "心理语言学与语言习得",
        "disciplines": ["Psycholinguistics", "Developmental and Educational Psychology", "Cognitive Psychology"],
        "scholars": [],
        "tension": "语言习得的先天机制与经验驱动机制之间的相对贡献如何衡量？",
        "open": "LLM的语言学习过程是否为关于人类语言习得机制的理论争论提供了新证据？",
    },
    {
        "title": "认知语言学与心理语言学",
        "disciplines": ["Cognitive Linguistics", "Psycholinguistics", "Experimental and Cognitive Psychology"],
        "scholars": [],
        "tension": "隐喻性思维是概念系统的基础结构还是语言表层现象？",
        "open": "实验心理语言学的发现在多大程度上支持或挑战了认知语言学的核心理论假设？",
    },
    {
        "title": "语言哲学与形式语义学",
        "disciplines": ["Philosophy of Language", "Formal Semantics", "Mathematical Logic"],
        "scholars": [],
        "tension": "形式语义学能否充分捕捉自然语言意义的全部复杂性？",
        "open": "语境依赖性表达式对组合性原则构成了怎样的挑战？",
    },
    {
        "title": "符号学与数字传播",
        "disciplines": ["Semiotics", "Digital Communication", "Media Studies"],
        "scholars": [],
        "tension": "数字媒介的多模态符号系统是否需要超越索绪尔和皮尔斯的新符号学理论？",
        "open": "表情包、短视频等数字符号形式是否构成了一种新的意义生产机制？",
    },
    # ── Social Sciences × Social Sciences ────────────────────
    {
        "title": "社会心理学与群体行为",
        "disciplines": ["Social Psychology", "Sociology and Political Science", "Group Dynamics"],
        "scholars": [],
        "tension": "个体层面的心理机制能否充分解释集体行为的涌现特征？",
        "open": "社交媒体时代的群体极化现象是否需要超越经典社会心理学模型的新理论？",
    },
    {
        "title": "社会认知与偏见研究",
        "disciplines": ["Social Cognition", "Prejudice and Discrimination", "Behavioral Economics"],
        "scholars": [],
        "tension": "内隐偏见的测量能否可靠地预测歧视性行为？",
        "open": "AI系统中的算法偏见与人类社会认知偏见之间是否存在结构性同构？",
    },
    {
        "title": "经济社会学与社会分层",
        "disciplines": ["Social Stratification", "Economics and Econometrics", "Field Theory"],
        "scholars": [],
        "tension": "经济不平等在多大程度上是市场机制的必然结果，在多大程度上是制度和权力结构的产物？",
        "open": "数字经济是加剧还是缓解了社会流动性的阶层固化？",
    },
    {
        "title": "政治经济学与公共选择理论",
        "disciplines": ["Political Economy", "Microeconomics", "Comparative Politics"],
        "scholars": [],
        "tension": "理性选择模型在解释政治行为时的预测力边界在哪里？",
        "open": "算法辅助的政策分析能否克服公共选择理论揭示的集体行动困境？",
    },
    {
        "title": "国际政治经济学与发展",
        "disciplines": ["Political Economy", "International Relations Theory", "Development Economics"],
        "scholars": [],
        "tension": "全球化进程中发达国家与发展中国家之间的权力不对称如何影响经济发展路径？",
        "open": "数字丝绸之路等新型国际合作模式能否重塑全球政治经济秩序？",
    },
    {
        "title": "教育心理学与学习科学",
        "disciplines": ["Learning Sciences", "Cognitive Psychology", "Education"],
        "scholars": [],
        "tension": "实验室中发现的认知学习原理在多大程度上可以直接迁移到真实课堂情境？",
        "open": "个性化自适应学习系统能否在认知和情感层面同时优化学习效果？",
    },
    {
        "title": "儿童发展与教育实践",
        "disciplines": ["Child Development", "Education", "Developmental and Educational Psychology"],
        "scholars": [],
        "tension": "发展心理学的阶段理论对课程设计的指导价值有多大？",
        "open": "早期数字设备接触对儿童认知发展的长期影响是积极还是消极的？",
    },
    {
        "title": "教育技术与在线学习",
        "disciplines": ["Educational Technology", "Online Learning", "Human-Computer Interaction"],
        "scholars": [],
        "tension": "技术中介的教育体验能否实现与面对面教学同等质量的深层学习？",
        "open": "大规模在线教育平台的学习分析数据能否被用来构建真正个性化的教学路径？",
    },
    {
        "title": "STEM教育与课程改革",
        "disciplines": ["STEM Education", "Curriculum Studies", "Higher Education"],
        "scholars": [],
        "tension": "跨学科整合的STEM教育理念与学科专业化的传统大学建制之间如何调和？",
        "open": "AI辅助教学能否帮助解决STEM教育中的公平性和包容性问题？",
    },
    {
        "title": "文化人类学与民族志方法",
        "disciplines": ["Cultural Anthropology", "Sociology and Political Science", "Ethnomethodology"],
        "scholars": [],
        "tension": "民族志研究者的主体性在多大程度上构成而非扭曲了研究发现？",
        "open": "数字民族志方法能否在保持深度参与观察的同时实现更大规模的跨文化比较？",
    },
    {
        "title": "语言人类学与社会语言学",
        "disciplines": ["Linguistic Anthropology", "Sociolinguistics", "Cultural Studies"],
        "scholars": [],
        "tension": "语言濒危现象的加速是文化全球化的必然结果还是可以逆转的政策失败？",
        "open": "AI语言技术能否在语言记录和复兴中发挥系统性作用？",
    },
    {
        "title": "宪法学与人权理论",
        "disciplines": ["Constitutional Law", "Human Rights Law", "Political Philosophy"],
        "scholars": [],
        "tension": "宪法权利的普遍性主张如何面对文化相对主义的挑战？",
        "open": "数字时代的隐私权和数据权是否需要宪法层面的根本性重构？",
    },
    {
        "title": "AI治理与法律框架",
        "disciplines": ["AI and Law", "Public Policy", "Ethics"],
        "scholars": [],
        "tension": "现有法律框架能否以足够快的速度适应AI技术的发展？",
        "open": "算法可审计性要求与商业秘密保护之间的平衡点在哪里？",
    },
    {
        "title": "知识产权与数字经济",
        "disciplines": ["Intellectual Property", "Digital Communication", "Fintech"],
        "scholars": [],
        "tension": "传统知识产权制度在数据驱动的数字经济中是否已经过时？",
        "open": "开源与专有之间的张力如何在AI时代重新配置？",
    },
    {
        "title": "说服理论与媒体效果",
        "disciplines": ["Persuasion and Influence", "Media Studies", "Communication"],
        "scholars": [],
        "tension": "大众传媒的说服效果模型是否需要针对社交媒体生态进行根本性修订？",
        "open": "算法推荐驱动的信息茧房效应对民主商议的影响有多大？",
    },
    {
        "title": "修辞学与论证理论",
        "disciplines": ["Rhetoric", "Argumentation Theory", "Philosophy"],
        "scholars": [],
        "tension": "修辞说服与理性论证之间的界限是否在数字传播环境中变得更加模糊？",
        "open": "AI生成的修辞性文本对公共话语质量构成了怎样的新挑战？",
    },
    {
        "title": "新闻学与数字传播变革",
        "disciplines": ["Journalism", "Digital Communication", "Digital Culture"],
        "scholars": [],
        "tension": "专业新闻业的守门人角色在信息民主化时代是否仍然具有不可替代性？",
        "open": "AI事实核查工具能否有效应对深度伪造和大规模虚假信息？",
    },
    # ── Social Sciences × STEM ───────────────────────────────
    {
        "title": "数学经济学与博弈论应用",
        "disciplines": ["Game Theory", "Economics and Econometrics", "Applied Mathematics"],
        "scholars": [],
        "tension": "高度形式化的数学模型在多大程度上捕捉了经济行为的真实复杂性？",
        "open": "计算博弈论方法能否为设计更高效的市场机制提供可行方案？",
    },
    {
        "title": "计量经济学与因果推断",
        "disciplines": ["Economics and Econometrics", "Causal Inference", "Bayesian Statistics"],
        "scholars": [],
        "tension": "观察性经济数据中的因果识别策略在何种条件下可以达到实验标准的可靠性？",
        "open": "机器学习方法能否在不牺牲可解释性的情况下改进经济预测模型？",
    },
    {
        "title": "算法经济学与机制设计",
        "disciplines": ["Computational Economics", "Artificial Intelligence", "Game Theory"],
        "scholars": [],
        "tension": "算法驱动的市场设计能否同时满足效率和公平的双重目标？",
        "open": "自主AI代理参与的市场竞争是否会产生人类经济学理论未预见的均衡形态？",
    },
    {
        "title": "量化金融与机器学习",
        "disciplines": ["Quantitative Finance", "Machine Learning", "Statistics and Probability"],
        "scholars": [],
        "tension": "金融市场的非平稳性和制度性变化对机器学习预测模型构成了怎样的根本性挑战？",
        "open": "深度强化学习交易策略的大规模部署是否会改变市场微观结构本身？",
    },
    {
        "title": "神经经济学与决策科学",
        "disciplines": ["Neuroeconomics", "Decision Making", "Behavioral Economics"],
        "scholars": [],
        "tension": "神经活动数据能否为经济决策理论提供超越行为实验的新约束条件？",
        "open": "情绪在经济决策中的神经机制是否支持对理性选择理论的根本修正？",
    },
    {
        "title": "情感神经科学与心理治疗",
        "disciplines": ["Affective Neuroscience", "Psychotherapy", "Clinical Psychology"],
        "scholars": [],
        "tension": "情绪的神经生物学机制理解能否转化为更有效的心理治疗干预方案？",
        "open": "实时神经反馈技术在心理治疗中的应用前景和伦理边界是什么？",
    },
    {
        "title": "认知建模与人工智能",
        "disciplines": ["Cognitive Psychology", "Artificial Intelligence", "Computational Theory of Mind"],
        "scholars": [],
        "tension": "认知架构模型与深度学习系统在解释人类认知方面是否互补还是竞争？",
        "open": "LLM的行为模式在多大程度上可以作为人类认知理论的计算测试平台？",
    },
    {
        "title": "人机交互中的认知偏差",
        "disciplines": ["Human-Computer Interaction", "Decision Making", "Social Computing"],
        "scholars": [],
        "tension": "人类认知偏差在人机交互场景中是被放大还是被缓解？",
        "open": "设计能够'去偏差'的AI界面是否在伦理上构成对用户自主性的干预？",
    },
    {
        "title": "计算社会学与网络分析",
        "disciplines": ["Digital Sociology", "Data Science", "Complex Systems"],
        "scholars": [],
        "tension": "社会网络的大数据分析能否揭示传统社会学调查方法无法捕捉的社会结构？",
        "open": "在线社交网络的结构动态是否遵循与线下社会网络不同的组织原则？",
    },
    {
        "title": "社会计算与集体智慧",
        "disciplines": ["Social Computing", "Artificial Intelligence", "Sociology and Political Science"],
        "scholars": [],
        "tension": "算法中介的集体决策质量是否优于纯人类群体的判断？",
        "open": "人机混合的集体智慧系统能否为复杂社会问题提供更优的解决方案？",
    },
    {
        "title": "AI战略与创新管理",
        "disciplines": ["Artificial Intelligence", "Innovation Management", "Strategic Management"],
        "scholars": [],
        "tension": "AI技术的快速迭代如何挑战传统企业战略规划的时间尺度假设？",
        "open": "AI原生企业的组织形态是否代表了一种根本不同的管理范式？",
    },
    {
        "title": "算法管理与劳动关系",
        "disciplines": ["Artificial Intelligence", "Organizational Behavior and Human Resource Management", "Industrial relations"],
        "scholars": [],
        "tension": "算法管理在提高效率的同时是否系统性地削弱了工人的自主权和尊严？",
        "open": "人机协作的工作模式如何重新定义管理者与员工之间的关系？",
    },
    {
        "title": "消费者心理学与市场营销",
        "disciplines": ["Social Psychology", "Marketing", "Behavioral Economics"],
        "scholars": [],
        "tension": "行为经济学的消费者非理性模型对传统营销理论意味着什么？",
        "open": "超个性化AI推荐系统是否从根本上改变了消费者决策过程的认知结构？",
    },
    {
        "title": "组织理论与社会学",
        "disciplines": ["Organizational Theory", "Sociology and Political Science", "Actor-Network Theory"],
        "scholars": [],
        "tension": "组织是否可以被视为自主行动者还是仅仅是个体行动者的集合？",
        "open": "AI系统作为组织中的'准行动者'如何改变了组织理论的基本分析单位？",
    },
    {
        "title": "教育神经科学与学习",
        "disciplines": ["Cognitive Neuroscience", "Learning Sciences", "Education"],
        "scholars": [],
        "tension": "神经科学发现能否被直接翻译为有效的教育实践指南？",
        "open": "'神经教育学'是否需要一套独立的中间层理论来桥接大脑研究与课堂教学？",
    },
    {
        "title": "青少年大脑发育与教育政策",
        "disciplines": ["Developmental Neuroscience", "Adolescent Psychology", "Education"],
        "scholars": [],
        "tension": "关于青少年前额叶发育的神经科学证据是否应直接影响教育和法律政策？",
        "open": "数字媒体的高强度使用对青少年大脑发育的影响能否被纵向研究可靠量化？",
    },
    # ── Humanities × STEM ────────────────────────────────────
    {
        "title": "生命伦理学与医学实践",
        "disciplines": ["Ethics", "Public Health, Environmental and Occupational Health", "Health Policy"],
        "scholars": [],
        "tension": "生命伦理学的普遍性原则如何应对不同文化和宗教背景下的医学伦理困境？",
        "open": "基因组编辑和AI辅助诊断在多大程度上需要重新构建知情同意的概念框架？",
    },
    {
        "title": "环境伦理学与生态科学",
        "disciplines": ["Ethics", "Ecology", "Environmental Economics"],
        "scholars": [],
        "tension": "自然环境是否具有内在价值还是仅具有工具性价值？",
        "open": "生态系统崩溃的临界点研究如何改变环境伦理学中的代际正义论述？",
    },
    {
        "title": "量子力学诠释与科学哲学",
        "disciplines": ["Philosophy of Science", "Nuclear and High Energy Physics", "Metaphysics"],
        "scholars": [],
        "tension": "量子力学的不同诠释对物理实在的本体论承诺有何根本性分歧？",
        "open": "量子退相干理论能否在不诉诸观察者的情况下解决测量问题？",
    },
    {
        "title": "科学哲学与物理学基础",
        "disciplines": ["Philosophy of Science", "Mathematical Physics", "Epistemology"],
        "scholars": [],
        "tension": "物理理论的数学优美性是否构成了一种可靠的理论选择标准？",
        "open": "弦理论的经验不可验证性是否从根本上挑战了波普尔式的证伪主义科学观？",
    },
    {
        "title": "科技史与物理学发展",
        "disciplines": ["History of Science and Technology", "Nuclear and High Energy Physics", "Philosophy of Science"],
        "scholars": [],
        "tension": "物理学革命是库恩式范式转换还是累积性科学进步？",
        "open": "大科学(Big Science)模式的兴起如何改变了物理学知识生产的社会结构？",
    },
    {
        "title": "生物学史与进化论变迁",
        "disciplines": ["History of Science and Technology", "Evolutionary Biology", "Philosophy of Science"],
        "scholars": [],
        "tension": "进化综合理论的历史发展路径在多大程度上受到了社会文化因素的影响？",
        "open": "表观遗传学的兴起是否构成了对现代综合理论的范式性挑战？",
    },
    {
        "title": "计算机科学史与AI演变",
        "disciplines": ["History of Science and Technology", "Artificial Intelligence", "Philosophy of Mind"],
        "scholars": [],
        "tension": "AI研究史上符号主义与联结主义的交替兴衰反映了怎样的认识论深层张力？",
        "open": "当前大语言模型的突破是否意味着联结主义路线已经最终胜出？",
    },
    {
        "title": "数字人文与文本挖掘",
        "disciplines": ["Digital Humanities", "Natural Language Processing", "Literature and Literary Theory"],
        "scholars": [],
        "tension": "计算方法对文学文本的量化分析是否丧失了传统人文学科重视的细读能力？",
        "open": "大语言模型能否被用作数字人文研究中可靠的文本分析工具？",
    },
    {
        "title": "数字历史与数据可视化",
        "disciplines": ["Digital History", "Data Science", "History"],
        "scholars": [],
        "tension": "历史大数据的可视化呈现是否构成了一种新的历史叙事形式？",
        "open": "数字化历史档案的选择性偏差如何影响计算历史学的结论可靠性？",
    },
    {
        "title": "神经美学与认知科学",
        "disciplines": ["Neuroaesthetics", "Cognitive Neuroscience", "Aesthetics"],
        "scholars": [],
        "tension": "审美体验能否被还原为特定的神经活动模式？",
        "open": "跨文化神经美学研究能否为美学的普遍性与文化相对性之争提供经验证据？",
    },
    {
        "title": "神经美学与艺术创作",
        "disciplines": ["Neuroaesthetics", "Visual Arts and Performing Arts", "Music Cognition"],
        "scholars": [],
        "tension": "关于审美感知的神经科学知识能否指导艺术创作实践？",
        "open": "基于神经美学原理设计的AI艺术系统能否创造出真正有审美冲击力的作品？",
    },
    {
        "title": "科学技术研究与AI社会影响",
        "disciplines": ["Science and Technology Studies", "Artificial Intelligence", "Digital Sociology"],
        "scholars": [],
        "tension": "AI技术的社会建构过程中，哪些行动者的价值观和利益占据了主导地位？",
        "open": "STS视角能否为AI治理提供比纯技术路线更有效的分析框架？",
    },
    {
        "title": "技术的社会建构与创新",
        "disciplines": ["Social Construction of Technology", "Innovation Management", "Sociology and Political Science"],
        "scholars": [],
        "tension": "技术创新的方向在多大程度上由社会力量而非技术内在逻辑所决定？",
        "open": "开源AI开发社区的决策模式是否代表了一种新的技术社会建构路径？",
    },
    {
        "title": "女性主义技术科学与AI偏见",
        "disciplines": ["Feminist Technoscience", "Artificial Intelligence", "Gender Studies"],
        "scholars": [],
        "tension": "AI系统中的性别偏见是训练数据的反映还是系统设计的固有特征？",
        "open": "女性主义技术科学的批判视角如何具体转化为更公平的AI设计实践？",
    },
    # ── Economics × STEM (continued) ─────────────────────────
    {
        "title": "环境经济学与气候政策",
        "disciplines": ["Environmental Economics", "Climate Modeling", "Public Policy"],
        "scholars": [],
        "tension": "气候变化的经济损害函数的巨大不确定性如何影响最优减排政策的制定？",
        "open": "碳定价机制的全球协调是否需要一种全新的国际经济治理架构？",
    },
    {
        "title": "发展经济学与全球健康",
        "disciplines": ["Development Economics", "Global Health", "Epidemiology"],
        "scholars": [],
        "tension": "健康投资对经济发展的因果效应在贫困国家中有多大？",
        "open": "大规模健康干预的随机对照试验的外部有效性能否跨国推广？",
    },
    {
        "title": "创业学与AI技术",
        "disciplines": ["Entrepreneurship", "Artificial Intelligence", "Management of Technology and Innovation"],
        "scholars": [],
        "tension": "AI降低了创业的技术门槛，但是否同时集中了市场权力？",
        "open": "AI原生创业公司的增长动态是否遵循与传统科技创业不同的规律？",
    },
    # ── Psychology × Neuroscience (extended) ──────────────────
    {
        "title": "创伤心理学与神经可塑性",
        "disciplines": ["Trauma Psychology", "Cognitive Neuroscience", "Psychotherapy"],
        "scholars": [],
        "tension": "心理创伤导致的神经结构变化在多大程度上是可逆的？",
        "open": "基于神经可塑性研究的新型创伤治疗方法（如EMDR）的作用机制是什么？",
    },
    {
        "title": "意识与双过程理论",
        "disciplines": ["Dual Process Theory", "Consciousness Studies", "Experimental and Cognitive Psychology"],
        "scholars": [],
        "tension": "系统1的自动化加工是否完全不涉及意识经验？",
        "open": "意识在认知加工中的因果角色是否可以通过双过程框架得到澄清？",
    },
    {
        "title": "记忆研究与神经科学",
        "disciplines": ["Memory and Learning", "Cognitive Neuroscience", "Cellular and Molecular Neuroscience"],
        "scholars": [],
        "tension": "突触层面的分子机制能否完整解释记忆的编码、存储和提取过程？",
        "open": "记忆重新巩固理论对法律证词可靠性评估和PTSD治疗有何具体启示？",
    },
    {
        "title": "注意力机制的计算与生物学",
        "disciplines": ["Attention and Perception", "Artificial Intelligence", "Sensory Systems"],
        "scholars": [],
        "tension": "Transformer架构中的注意力机制与生物注意力系统之间的类比有多深？",
        "open": "生物注意力的选择性和灵活性能否启发下一代更高效的AI注意力架构？",
    },
    # ── Cross-cutting themes ─────────────────────────────────
    {
        "title": "批判教育学与社会正义",
        "disciplines": ["Critical Pedagogy", "Social Stratification", "Political Philosophy"],
        "scholars": [],
        "tension": "教育能否成为消除结构性不平等的有效工具，还是不可避免地再生产既有权力关系？",
        "open": "AI在教育中的应用是否会加剧还是缓解知识获取的不平等？",
    },
    {
        "title": "后殖民文学与文化研究",
        "disciplines": ["Postcolonial Literature", "Cultural Studies", "Identity Politics"],
        "scholars": [],
        "tension": "后殖民批评理论能否超越二元对立的殖民者/被殖民者框架？",
        "open": "AI训练数据中的语言和文化霸权如何延续或变革后殖民时代的知识不对称？",
    },
    {
        "title": "后现代主义与数字文化",
        "disciplines": ["Postmodernism", "Digital Culture", "Communication"],
        "scholars": [],
        "tension": "数字时代的信息碎片化是否印证了后现代主义对宏大叙事的质疑？",
        "open": "深度伪造和AI生成内容是否代表了后现代'超真实'概念的技术实现？",
    },
    {
        "title": "比较政治学与数字治理",
        "disciplines": ["Comparative Politics", "Digital Communication", "Public Administration"],
        "scholars": [],
        "tension": "不同政治体制对数字技术的采纳和监管模式差异反映了怎样的深层制度逻辑？",
        "open": "数字政府的全球扩散是否趋向制度趋同还是路径依赖？",
    },
    {
        "title": "城市社会学与智慧城市",
        "disciplines": ["Urban Sociology", "Urban Studies", "Data Science"],
        "scholars": [],
        "tension": "数据驱动的智慧城市治理是否以技术效率为名侵蚀了城市公共空间的社会性？",
        "open": "城市大数据能否被用于促进空间正义而非加深社会隔离？",
    },
    {
        "title": "数字人类学与平台研究",
        "disciplines": ["Digital Anthropology", "Digital Communication", "Cultural Anthropology"],
        "scholars": [],
        "tension": "数字平台上的社区与传统面对面社区之间是否存在本质性的社会结构差异？",
        "open": "AI中介的在线互动是否正在创造一种新的人类社会性形式？",
    },
    {
        "title": "卫生政策与健康的社会决定因素",
        "disciplines": ["Health Policy", "Social Determinants of Health", "Public Policy"],
        "scholars": [],
        "tension": "个体行为干预与结构性社会变革在改善人口健康方面的相对效力如何？",
        "open": "AI驱动的精准公共卫生能否在不加剧健康不平等的情况下实施？",
    },
    {
        "title": "成瘾医学与社会心理学",
        "disciplines": ["Addiction Medicine", "Social Psychology", "Behavioral Neuroscience"],
        "scholars": [],
        "tension": "成瘾行为的医学模型与社会心理模型之间的张力如何影响干预策略的选择？",
        "open": "社交媒体和数字产品的成瘾性设计是否需要类似烟酒管制的公共卫生监管？",
    },
    {
        "title": "精神病学与文化研究",
        "disciplines": ["Psychiatry and Mental health", "Cultural Anthropology", "Social Psychology"],
        "scholars": [],
        "tension": "精神疾病的分类体系在多大程度上反映了文化建构而非生物学实在？",
        "open": "跨文化精神病学能否发展出真正文化敏感的诊断框架？",
    },
    {
        "title": "东方哲学与认知科学",
        "disciplines": ["Eastern Philosophy", "Cognitive Neuroscience", "Consciousness Studies"],
        "scholars": [],
        "tension": "佛教冥想传统中的意识理论与西方认知神经科学之间能否展开深层对话？",
        "open": "正念冥想的神经科学研究是否验证了东方哲学对意识本质的某些洞见？",
    },
    {
        "title": "古希腊哲学与当代伦理学",
        "disciplines": ["Greek Philosophy", "Ethics", "Political Philosophy"],
        "scholars": [],
        "tension": "亚里士多德式的德性伦理学能否为AI伦理提供比功利主义更优的理论框架？",
        "open": "古典实践智慧(phronesis)的概念能否被形式化并嵌入AI决策系统？",
    },
    {
        "title": "概念隐喻理论与AI语言理解",
        "disciplines": ["Conceptual Metaphor Theory", "Natural Language Processing", "Cognitive Linguistics"],
        "scholars": [],
        "tension": "LLM是否真正理解了隐喻的概念映射结构还是仅仅模拟了表面的语言模式？",
        "open": "具身隐喻理论是否意味着缺乏身体的AI系统在原则上无法完全理解隐喻？",
    },
    {
        "title": "认知诗学与计算文学",
        "disciplines": ["Cognitive Poetics", "Natural Language Processing", "Experimental and Cognitive Psychology"],
        "scholars": [],
        "tension": "文学阅读的认知效果能否通过计算方法被客观测量和预测？",
        "open": "AI生成的文学文本能否产生与人类作品同等深度的认知诗学效果？",
    },
    {
        "title": "对话主义与社会计算",
        "disciplines": ["Dialogism", "Social Computing", "Natural Language Processing"],
        "scholars": [],
        "tension": "巴赫金式的多声部对话理论能否为AI多轮对话设计提供理论基础？",
        "open": "LLM生成的语言是否真正的'众声喧哗'还是统计均值化的独白？",
    },
    {
        "title": "电影学与计算机视觉",
        "disciplines": ["Film Studies", "Computer Vision", "Digital Art"],
        "scholars": [],
        "tension": "AI视频生成技术对电影叙事语法和视觉美学的影响是颠覆性还是工具性的？",
        "open": "观众对AI生成影像的审美接受度与对传统拍摄影像是否存在系统性差异？",
    },
    {
        "title": "音乐技术与AI作曲",
        "disciplines": ["Music Technology", "Generative AI", "Musicology"],
        "scholars": [],
        "tension": "AI作曲是否能产生具有真正音乐性(musicianship)的作品？",
        "open": "AI与人类音乐家的协同创作模式是否正在定义一种新的音乐创作范式？",
    },
    {
        "title": "宗教社会学与数字文化",
        "disciplines": ["Sociology of Religion", "Digital Culture", "Communication"],
        "scholars": [],
        "tension": "宗教实践的数字化转型是否改变了信仰体验的本质？",
        "open": "在线宗教社区能否维持与面对面集会同等程度的精神共同体？",
    },
    {
        "title": "民族音乐学与文化人类学",
        "disciplines": ["Ethnomusicology", "Cultural Anthropology", "Sound Studies"],
        "scholars": [],
        "tension": "音乐实践的跨文化比较是否需要超越西方音乐理论框架的全新分析工具？",
        "open": "全球化时代传统音乐文化的数字保存与'活态传承'之间是否存在根本张力？",
    },
    {
        "title": "艺术史与数字人文",
        "disciplines": ["Art History", "Digital Humanities", "Computer Vision and Pattern Recognition"],
        "scholars": [],
        "tension": "计算机视觉对艺术品的自动分析能否发现艺术史家肉眼未注意到的风格特征？",
        "open": "基于AI的大规模视觉分析是否正在重塑艺术史的方法论基础？",
    },
    {
        "title": "风险管理与AI决策",
        "disciplines": ["Risk Management", "Artificial Intelligence", "Statistics and Probability"],
        "scholars": [],
        "tension": "AI风险评估模型的黑箱特性与金融监管的透明性要求之间如何调和？",
        "open": "AI能否有效评估自身参与所创造的新型系统性风险？",
    },
    {
        "title": "应用心理学与用户体验",
        "disciplines": ["Applied Psychology", "User Experience Design", "Social Psychology"],
        "scholars": [],
        "tension": "心理学原理在UX设计中的应用是否跨越了说服与操纵之间的伦理界限？",
        "open": "AI个性化界面能否实现真正以用户福祉为导向的设计而非仅追求参与度？",
    },
    {
        "title": "历史语言学与计算方法",
        "disciplines": ["Historical Linguistics", "Computational Linguistics", "Phylogenetics"],
        "scholars": [],
        "tension": "计算系统发生学方法在重建语言谱系关系方面比传统比较法更可靠吗？",
        "open": "深度学习方法能否帮助解读尚未破译的古代文字系统？",
    },
    {
        "title": "佛学研究与认知科学",
        "disciplines": ["Buddhism Studies", "Cognitive Neuroscience", "Philosophy of Mind"],
        "scholars": [],
        "tension": "佛教的无我学说与认知科学中的自我模型之间是否存在深层理论对应？",
        "open": "长期冥想修行者的神经可塑性研究能否为意识理论提供独特的经验数据？",
    },
]


# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------


def insert_openalex_taxonomy(db: Session) -> None:
    """Load the two-level OpenAlex taxonomy from JSON and insert as depth 0/1."""
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        fields = json.load(f)

    for field in fields:
        f_disc = Discipline(
            name_en=field["name_en"],
            name_zh=field.get("name_zh") or None,
            openalex_id=field["openalex_id"],
            works_count=field.get("works_count"),
            depth=0,
            level="field",
            is_custom=False,
        )
        db.add(f_disc)
        db.flush()

        for child in field.get("children", []):
            sf_disc = Discipline(
                name_en=child["name_en"],
                name_zh=child.get("name_zh") or None,
                openalex_id=child["openalex_id"],
                parent_id=f_disc.id,
                depth=1,
                level="subfield",
                is_custom=False,
            )
            db.add(sf_disc)
        db.flush()


def insert_custom_extensions(db: Session) -> None:
    """Insert 3rd-level custom disciplines under their OpenAlex subfield parents."""
    subfield_cache: dict[str, Discipline] = {}
    for d in db.query(Discipline).filter(Discipline.depth == 1).all():
        subfield_cache[d.name_en] = d

    for parent_name, extensions in CUSTOM_EXTENSIONS.items():
        parent = subfield_cache.get(parent_name)
        if not parent:
            print(f"  WARNING: subfield '{parent_name}' not found, skipping extensions")
            continue
        for name_en, name_zh in extensions:
            ext = Discipline(
                name_en=name_en,
                name_zh=name_zh,
                parent_id=parent.id,
                depth=2,
                is_custom=False,
            )
            db.add(ext)
    db.flush()


def insert_scholars(db: Session) -> None:
    disc_cache: dict[str, Discipline] = {}
    for d in db.query(Discipline).all():
        disc_cache[d.name_en] = d

    for name, disc_names in SCHOLARS:
        s = Scholar(name=name)
        db.add(s)
        db.flush()
        for dn in disc_names:
            if dn in disc_cache:
                db.execute(
                    scholar_discipline.insert().values(
                        scholar_id=s.id, discipline_id=disc_cache[dn].id
                    )
                )
    db.flush()


def insert_papers(db: Session) -> None:
    from app.models.paper import paper_discipline

    scholar_cache: dict[str, Scholar] = {}
    for s in db.query(Scholar).all():
        scholar_cache[s.name] = s

    scholar_discs: dict[int, set[int]] = {}
    rows = db.execute(scholar_discipline.select()).fetchall()
    for sid, did in rows:
        scholar_discs.setdefault(sid, set()).add(did)

    disc_parent: dict[int, int | None] = {}
    for d in db.query(Discipline).all():
        disc_parent[d.id] = d.parent_id

    def ancestors(did: int) -> set[int]:
        result = {did}
        cur = disc_parent.get(did)
        while cur is not None:
            result.add(cur)
            cur = disc_parent.get(cur)
        return result

    for title, year, author_name in CLASSIC_PAPERS:
        p = Paper(title=title, year=year, paper_type="classic")
        db.add(p)
        db.flush()

        paper_disc_ids: set[int] = set()
        if author_name in scholar_cache:
            s = scholar_cache[author_name]
            db.execute(
                paper_author.insert().values(
                    paper_id=p.id, scholar_id=s.id
                )
            )
            for did in scholar_discs.get(s.id, set()):
                paper_disc_ids |= ancestors(did)

        for did in paper_disc_ids:
            db.execute(
                paper_discipline.insert().values(
                    paper_id=p.id, discipline_id=did
                )
            )
    db.flush()


def insert_intersections(db: Session) -> None:
    disc_cache: dict[str, Discipline] = {}
    for d in db.query(Discipline).all():
        disc_cache[d.name_en] = d

    scholar_cache: dict[str, Scholar] = {}
    for s in db.query(Scholar).all():
        scholar_cache[s.name] = s

    for cr in CROSSROADS:
        ix = Intersection(
            title=cr["title"],
            status="active",
            core_tension=cr["tension"],
            open_questions=cr["open"],
        )
        db.add(ix)
        db.flush()
        for dn in cr["disciplines"]:
            if dn in disc_cache:
                db.execute(
                    intersection_discipline.insert().values(
                        intersection_id=ix.id, discipline_id=disc_cache[dn].id
                    )
                )
        for sn in cr["scholars"]:
            if sn in scholar_cache:
                db.execute(
                    intersection_scholar.insert().values(
                        intersection_id=ix.id, scholar_id=scholar_cache[sn].id
                    )
                )
    db.flush()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _clear_seed_data(db: Session) -> None:
    """Delete all seed-related data. Preserves users, forum posts, comments, votes, point logs."""
    from app.models.spark import Spark
    from app.models.paper_draft import PaperDraft, PaperSection
    from app.models.hypothesis import AIHypothesis
    from app.models.debate import DebateMessage, DebateAgent, Debate, debate_discipline
    from app.models.experiment import DebateExperimentMeta

    counts: dict[str, int] = {}
    for label, model in [
        ("paper_sections", PaperSection),
        ("paper_drafts", PaperDraft),
        ("sparks", Spark),
        ("debate_experiment_meta", DebateExperimentMeta),
        ("debate_messages", DebateMessage),
        ("debate_agents", DebateAgent),
    ]:
        n = db.query(model).delete()
        counts[label] = n

    n = db.execute(debate_discipline.delete())
    counts["debate_discipline"] = n.rowcount

    for label, model in [
        ("debates", Debate),
        ("ai_hypotheses", AIHypothesis),
    ]:
        n = db.query(model).delete()
        counts[label] = n

    from app.models.paper import paper_discipline
    for assoc_name, assoc_table in [
        ("intersection_scholar", intersection_scholar),
        ("intersection_discipline", intersection_discipline),
        ("paper_author", paper_author),
        ("paper_discipline", paper_discipline),
        ("scholar_discipline", scholar_discipline),
    ]:
        n = db.execute(assoc_table.delete())
        counts[assoc_name] = n.rowcount

    for label, model in [
        ("intersections", Intersection),
        ("papers", Paper),
        ("scholars", Scholar),
        ("disciplines", Discipline),
    ]:
        n = db.query(model).delete()
        counts[label] = n

    db.flush()
    print(f"  Cleared: {counts}")


def main():
    force = "--force" in sys.argv

    print("Creating tables...")
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        existing = db.query(Discipline).first()
        if existing:
            if not force:
                print("Data already exists. Use --force to clear and re-import.")
                return
            print("Clearing old seed data (--force)...")
            _clear_seed_data(db)

        print("Inserting OpenAlex taxonomy (fields + subfields)...")
        insert_openalex_taxonomy(db)

        print("Inserting custom 3rd-level extensions...")
        insert_custom_extensions(db)

        print("Inserting scholars...")
        insert_scholars(db)

        print("Inserting classic papers...")
        insert_papers(db)

        print("Inserting intersections from crossroads...")
        insert_intersections(db)

        db.commit()
        print(
            f"Done. Disciplines: {db.query(Discipline).count()}, "
            f"Scholars: {db.query(Scholar).count()}, "
            f"Papers: {db.query(Paper).count()}, "
            f"Intersections: {db.query(Intersection).count()}"
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
