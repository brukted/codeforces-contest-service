import string
from pydantic import BaseModel

from models.domain.problem import Problem
from models.domain.standing import Standing
from models.domain.submission import Submission


class Contest(BaseModel):
    gymId: string
    submissions: list[Submission]
    problems: list[Problem]
    standings: list[Standing]
