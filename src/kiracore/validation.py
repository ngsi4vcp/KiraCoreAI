from __future__ import annotations

from .model_contract import ModelResponse
from .models import ValidationResult
from .security import disclosure_violation


class OutputValidator:
    """Проверяет ответ модели; ПУЛЬС добавляется runtime, а не моделью."""

    def validate(self, response: ModelResponse) -> ValidationResult:
        violation = disclosure_violation(response.text)
        if violation is not None:
            return ValidationResult(
                False,
                errors=("Ответ содержит защищённый внутренний маркер.",),
            )
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
