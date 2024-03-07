from dataclasses import dataclass
from typing import TypedDict


class RequestEventDict(TypedDict, total=False):
    message: str
    token: str


@dataclass(frozen=True)
class Payload:
    statusCode: int
    body: str
    event: RequestEventDict
    message_id: str | None = None


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