from __future__ import annotations

from typing import Protocol

from .models import OperationalContext


class HostAdapter(Protocol):
    """Контракт хоста: он отвечает только за представление контекста и среду исполнения."""

    def render_context(self, context: OperationalContext) -> str:
        ...


class ModelAdapter(Protocol):
    """Контракт когнитивного вычислительного компонента."""

    def generate(self, rendered_context: str, task: str) -> str:
        ...
