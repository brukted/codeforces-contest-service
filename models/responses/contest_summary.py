from pydantic import BaseModel

from models.domain.standing import ParticipationType


class SingleRow(BaseModel):
    rank: int
    ac_count: int
    participation_type: ParticipationType


class ContestSummary(BaseModel):
    total_problems: int
    rows: dict[str, SingleRow | None]
