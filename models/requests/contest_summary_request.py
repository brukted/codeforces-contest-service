import datetime

from pydantic import BaseModel, model_validator


class ContestSummaryRequest(BaseModel):
    gym_id: int = -1
    virtual_enabled: bool
    virtual_deadline_utc: datetime.datetime | None
    handles: list[str]

    @model_validator(mode="after")
    def virtual_deadline_utc__provided(cls, m: "ContestSummaryRequest"):
        if m.virtual_enabled and m.virtual_deadline_utc is None:
            raise ValueError(
                "Virtual deadline must be provided if virtual participation is enabled"
            )
        return m
