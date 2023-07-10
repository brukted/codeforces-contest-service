from pydantic import BaseModel

class Problem(BaseModel):
    index: str
    in_contest_name: str
    original_problem_url: str | None = None