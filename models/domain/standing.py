from enum import Enum
from pydantic import BaseModel

from models.domain.problem_result import ProblemResult


class ParticipationType(Enum):
    IN_CONTEST = "InContest"
    AFTER_CONTEST = "AfterContest"
    VIRTUAL = "Virtual"
    MANAGER = "Manager"


class Standing(BaseModel):
    solved: int
    rank: int | None
    handle: str
    penalty: int
    problem_results: list[ProblemResult]
    participation_type: ParticipationType
