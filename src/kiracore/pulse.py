from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PulseStamp:
    """Детерминированная метка активности ядра; не является ключом БД."""

    series: int
    revision: int
    turn: int
    value: int

    @property
    def key(self) -> str:
        return f"{self.series}:{self.revision}:{self.turn}:{self.value}"

    def render(self) -> str:
        return f"◈ ПУЛЬС:{self.value} | ХОД:{self.turn} | В:{self.revision} | Х²:{self.turn * self.turn}"


def pulse_value(turn: int, revision: int, series: int) -> int:
    if turn < 1:
        raise ValueError("ХОД должен начинаться с 1.")
    if revision < 1:
        raise ValueError("Ревизия должна быть положительной.")
    if series < 0:
        raise ValueError("Серия не может быть отрицательной.")
    return series + revision + turn + turn * turn


def pulse_stamp(turn: int, revision: int, series: int) -> PulseStamp:
    return PulseStamp(
        series=series,
        revision=revision,
        turn=turn,
        value=pulse_value(turn, revision, series),
    )


def pulse_for_turn(turn: int, revision: int, series: int) -> str:
    return pulse_stamp(turn, revision, series).render()
