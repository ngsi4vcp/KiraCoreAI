from __future__ import annotations


def pulse_value(turn: int, revision: int, series: int) -> int:
    if turn < 1:
        raise ValueError("ХОД должен начинаться с 1.")
    return series + revision + turn + turn * turn


def pulse_for_turn(turn: int, revision: int, series: int) -> str:
    value = pulse_value(turn, revision, series)
    return f"◈ ПУЛЬС:{value} | ХОД:{turn} | В:{revision} | Х²:{turn * turn}"
