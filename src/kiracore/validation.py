from __future__ import annotations

from .models import ValidationResult
from .pulse import pulse_for_turn


class OutputValidator:
    """Проверяет обязательную форму протокола ответа."""

    def validate(
        self,
        text: str,
        turn: int,
        revision: int,
        series: int,
    ) -> ValidationResult:
        expected = pulse_for_turn(
            turn,
            revision=revision,
            series=series,
        )
        if not text.strip():
            return ValidationResult(False, errors=("Пустой ответ модели.",))
        if not text.rstrip().endswith(expected):
            return ValidationResult(
                False,
                errors=(f"Ответ должен завершаться точным ПУЛЬС: {expected}",),
            )
        return ValidationResult(True)
