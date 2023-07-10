from pydantic import BaseModel


class ProblemResult(BaseModel):
    tries: int
    submission_id: int | None
    submission_contest_minutes: int | None
    is_accepted: bool
    index: str
