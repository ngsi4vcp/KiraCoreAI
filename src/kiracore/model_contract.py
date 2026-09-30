from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str
    timestamp: str | None = None


@dataclass(frozen=True, slots=True)
class ModelCatalogItem:
    id: str
    name: str
    description: str = ""
    context_length: int | None = None
    input_modalities: tuple[str, ...] = ()
    output_modalities: tuple[str, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ModelUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class ModelRequest:
    provider: str
    model: str
    messages: tuple[ChatMessage, ...]
    temperature: float | None = 0.7
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ModelResponse:
    text: str
    provider: str
    model: str
    request_id: str | None = None
    finish_reason: str | None = None
    usage: ModelUsage | None = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)


class ModelAdapter(Protocol):
    provider: str

    def list_models(self, query: str = "") -> list[ModelCatalogItem]:
        ...

    def generate(self, request: ModelRequest) -> ModelResponse:
        ...
