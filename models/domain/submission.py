from pydantic import BaseModel


class Submission(BaseModel):
    id: int
    # Unix timestamp milli in utc time
    submission_time_utc: int
    handle: str
    is_virtual: bool
    problem_index: str
    language: str
    verdict: str
    # in milliseconds
    time: int
    # in KB
    memory: int
