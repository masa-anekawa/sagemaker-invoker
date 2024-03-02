from dataclasses import dataclass
from typing import Optional, TypedDict


class RequestEventDict(TypedDict, total=False):
    message: str
    token: Optional[str]


@dataclass(frozen=True)
class Payload:
    statusCode: int
    body: str
    event: RequestEventDict


class ResponseEventDict(TypedDict):
    StatusCode: int
    ExecutedVersion: str
    Payload: Payload


@dataclass(frozen=True)
class HandleMessageResponse:
    statusCode: int
    body: str
    output_path: str | None = None
    failure_path: str | None = None
    message_id: str | None = None