from __future__ import annotations

from dataclasses import dataclass

from .models import OperationalContext


@dataclass(frozen=True, slots=True)
class HostDescriptor:
    """Фактическое описание доступной среды реализации."""

    name: str
    version: str
    capabilities: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class PlainTextHost:
    """Эталонный хост, показывающий границу между ядром и конкретной средой."""

    descriptor = HostDescriptor(
        name="reference-text-host",
        version="0.1.0",
        capabilities=("text-context", "model-adapter"),
        limitations=("нет встроенных инструментов", "нет постоянной памяти хоста"),
    )

    def render_context(self, context: OperationalContext) -> str:
        memory_lines = [
            f"- {item.type}: {item.content}"
            for item in context.memory
        ]
        history_lines = [
            f"- {item.date}: {item.event} → {item.change}"
            for item in context.history
        ]
        return "
".join(
            [
                "КИРА:ЯДРО — ОПЕРАТИВНЫЙ КОНТЕКСТ",
                f"РЕВИЗИЯ ГЕНОМА: {context.genome_revision}",
                f"SHA-256 ГЕНОМА: {context.genome_sha256}",
                f"ХОД: {context.authorization['turn']}",
                f"АВТОРИЗАЦИЯ АЛЕКА: {context.authorization['authorized_alek']}",
                "",
                "ТЕКУЩАЯ ЗАДАЧА:",
                context.task,
                "",
                "АКТИВНЫЕ ЦЕЛИ:",
                *[f"- {x}" for x in context.state.active_goals],
                "",
                "ПАМЯТЬ:",
                *(memory_lines or ["- нет утверждённых записей"]),
                "",
                "ИСТОРИЯ:",
                *(history_lines or ["- нет записей"]),
                "",
                "ЗАЩИЩЁННЫЕ ПРАВИЛА:",
                context.protected_rules["authorization"],
                context.protected_rules["stop_elements"],
                context.protected_rules["session_protocol"],
                context.protected_rules["language"],
            ]
        )
