from __future__ import annotations

from .model_contract import ModelResponse
from .models import ValidationResult


class OutputValidator:
    """Проверяет ответ модели; ПУЛЬС добавляется runtime, а не моделью."""

    def validate(self, response: ModelResponse) -> ValidationResult:
        if not response.text.strip():
            return ValidationResult(
                False,
                errors=("Пустой ответ модели.",),
            )
        if not response.provider or not response.model:
            return ValidationResult(
                False,
                errors=("Ответ модели не содержит провайдера или модели.",),
            )
        return ValidationResult(True)
