from pydantic import BaseModel
from typing import Generic, TypeVar
DataT = TypeVar('DataT')

class JSendResponse(BaseModel, Generic[DataT]):
    message: str
    data: DataT | None