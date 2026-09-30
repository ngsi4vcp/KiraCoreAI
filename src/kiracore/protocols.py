from __future__ import annotations

from typing import Protocol

from .model_contract import ModelAdapter


class HostAdapter(Protocol):
    """Контракт среды: ввод/вывод и фактические ограничения хоста."""

    def prompt(self) -> str:
        ...

    def status(self, message: str, ok: bool | None = None) -> None:
        ...

    def error(self, message: str) -> None:
        ...


class PromptRenderer(Protocol):
    """Преобразует канонический контекст в запрос конкретной модели."""

    def render(self, context) -> object:
        ...


__all__ = ["HostAdapter", "ModelAdapter", "PromptRenderer"]
