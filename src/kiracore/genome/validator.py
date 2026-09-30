from __future__ import annotations

from typing import TYPE_CHECKING

from ..errors import GenomeIntegrityError

if TYPE_CHECKING:
    from .loader import GenomeArtifact


class GenomeValidator:
    """Проверяет формат и конституционные инварианты активного генома."""

    def __init__(
        self,
        expected_sha256: str | None = None,
        expected_revision: int | None = None,
    ) -> None:
        self.expected_sha256 = expected_sha256
        self.expected_revision = expected_revision

    def validate(self, artifact: GenomeArtifact) -> None:
        document = artifact.document
        if document.format != "KIRA-GENOME":
            raise GenomeIntegrityError(f"Неизвестный формат генома: {document.format!r}")
        if document.format_version != 1:
            raise GenomeIntegrityError(
                f"Неподдерживаемая версия формата: {document.format_version}"
            )
        if document.language != "ru":
            raise GenomeIntegrityError(
                f"Канонический язык генома должен быть ru, получено: {document.language!r}"
            )
        if document.revision <= 0:
            raise GenomeIntegrityError("Ревизия генома должна быть положительным числом.")
        if document.series < 0:
            raise GenomeIntegrityError("Серия генома не может быть отрицательной.")
        if self.expected_revision is not None and document.revision != self.expected_revision:
            raise GenomeIntegrityError(
                f"Неверная ревизия: получена {document.revision}, "
                f"ожидалась {self.expected_revision}."
            )
        if self.expected_sha256 and artifact.sha256 != self.expected_sha256:
            raise GenomeIntegrityError(
                "SHA-256 генома не совпадает: "
                f"{artifact.sha256} != {self.expected_sha256}."
            )

        required_sections = {
            "anchor_start",
            "anchor_end",
            "s02_authorization_turn",
            "s05_stop_elements",
            "s08_directives_style_initiative",
            "s17_session_protocols",
            "s23_core_architecture",
            "s31_genome_state",
        }
        actual = {section.id for section in document.sections}
        missing = sorted(required_sections - actual)
        if missing:
            raise GenomeIntegrityError(
                "В геноме отсутствуют обязательные разделы: " + ", ".join(missing)
            )

        required_phrases = (
            "Русский — мой канонический язык",
            "ПУЛЬС обязателен",
            "начинается ровно с",
            "СТОП-1.",
            "ГЕНОМ + СОСТОЯНИЕ + КОНТЕКСТ",
        )
        missing_phrases = [
            phrase for phrase in required_phrases if phrase not in artifact.text
        ]
        if missing_phrases:
            raise GenomeIntegrityError(
                "В геноме отсутствуют обязательные признаки: "
                + ", ".join(missing_phrases)
            )
