from pydantic import BaseModel

from uuid import UUID


class UserHistorySchema(BaseModel):
    uuid: UUID
    requests_history: dict[str, dict[str, int]]


class HistorySchema(BaseModel):
    city: str
    country: str
    request_count: int
