from app.models.base import Base
from app.models.discipline import Discipline
from app.models.scholar import Scholar, scholar_discipline
from app.models.paper import Paper, paper_author, paper_discipline
from app.models.intersection import (
    Intersection,
    intersection_discipline,
    intersection_scholar,
    intersection_paper,
)
from app.models.hypothesis import AIHypothesis
from app.models.debate import (
    Debate,
    DebateAgent,
    DebateMessage,
    debate_discipline,
)
from app.models.paper_draft import PaperDraft, PaperSection
from app.models.spark import Spark
from app.models.experiment import DebateExperimentMeta
from app.models.user import User
from app.models.forum import ForumPost, ForumComment, ForumVote
from app.models.points import PointLog

__all__ = [
    "Base",
    "Discipline",
    "Scholar",
    "scholar_discipline",
    "Paper",
    "paper_author",
    "paper_discipline",
    "Intersection",
    "intersection_discipline",
    "intersection_scholar",
    "intersection_paper",
    "AIHypothesis",
    "Debate",
    "DebateAgent",
    "DebateMessage",
    "debate_discipline",
    "PaperDraft",
    "PaperSection",
    "Spark",
    "DebateExperimentMeta",
    "User",
    "ForumPost",
    "ForumComment",
    "ForumVote",
    "PointLog",
]
