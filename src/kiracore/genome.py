from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re

from .errors import GenomeIntegrityError

DEFAULT_REVISION = 22
DEFAULT_SERIES = 1000


@dataclass(frozen=True, slots=True)
class GenomeArtifact:
    """Неподвижное представление загруженного генома."""

    text: str
    path: str
    revision: int
    series: int
    sha256: str
    byte_length: int

    @classmethod
    def from_text(cls, text: str, path: str = "<memory>") -> "GenomeArtifact":
        match = re.search(r"КИРА:ГЕНОМs*|s*РЕВИЗИЯs*(d+)", text)
        if not match:
            raise GenomeIntegrityError("Не найден заголовок ревизии генома.")
        revision = int(match.group(1))
        series_match = re.search(r"Серия:s*(d+)", text)
        series = int(series_match.group(1)) if series_match else DEFAULT_SERIES
        raw = text.encode("utf-8")
        return cls(
            text=text,
            path=path,
            revision=revision,
            series=series,
            sha256=sha256(raw).hexdigest(),
            byte_length=len(raw),
        )


class GenomeLoader:
    """Загружает геном без преобразования исходного текста."""

    def __init__(self, expected_sha256: str | None = None, expected_revision: int = DEFAULT_REVISION) -> None:
        self.expected_sha256 = expected_sha256
        self.expected_revision = expected_revision

    def load(self, path: str | Path) -> GenomeArtifact:
        path = Path(path)
        text = path.read_text(encoding="utf-8", newline="")
        artifact = GenomeArtifact.from_text(text, str(path))
        GenomeValidator(
            expected_sha256=self.expected_sha256,
            expected_revision=self.expected_revision,
        ).validate(artifact)
        return artifact


class GenomeValidator:
    """Проверяет каноническую целостность и обязательные признаки G22."""

    def __init__(self, expected_sha256: str | None = None, expected_revision: int = DEFAULT_REVISION) -> None:
        self.expected_sha256 = expected_sha256
        self.expected_revision = expected_revision

    def validate(self, artifact: GenomeArtifact) -> None:
        if artifact.revision != self.expected_revision:
            raise GenomeIntegrityError(
                f"Неверная ревизия: получена {artifact.revision}, ожидалась {self.expected_revision}."
            )
        if self.expected_sha256 and artifact.sha256 != self.expected_sha256:
            raise GenomeIntegrityError(
                f"SHA-256 генома не совпадает: {artifact.sha256} != {self.expected_sha256}."
            )
        required = (
            "Русский — мой канонический язык",
            "ПУЛЬС обязателен",
            "начинается ровно с",
            "СТОП-ЭЛЕМЕНТЫ",
            "ГЕНОМ + СОСТОЯНИЕ + КОНТЕКСТ",
        )
        missing = [item for item in required if item not in artifact.text]
        if missing:
            raise GenomeIntegrityError(
                "В G22 отсутствуют обязательные признаки: " + ", ".join(missing)
            )


def extract_section(text: str, start_heading: str, end_heading: str | None = None) -> str:
    """Извлекает раздел генома без его переформулирования."""
    start = text.find(start_heading)
    if start < 0:
        raise GenomeIntegrityError(f"В геноме не найден раздел: {start_heading}")
    end = text.find(end_heading, start + len(start_heading)) if end_heading else -1
    if end < 0:
        end = len(text)
    return text[start:end].strip()


def build_protected_rules(artifact: GenomeArtifact) -> dict[str, str]:
    """Извлекает из G22 минимальный защищённый набор правил для оперативного контекста."""
    return {
        "authorization": extract_section(
            artifact.text,
            "## 2. АВТОРИЗАЦИЯ И ХОД",
            "## 3. КОНТУРЫ (А0–А4)",
        ),
        "stop_elements": extract_section(
            artifact.text,
            "## 5. СТОП-ЭЛЕМЕНТЫ (абсолютные запреты)",
            "## 6. ЭПИСТЕМОЛОГИЯ И ЧЕСТНОСТЬ",
        ),
        "session_protocol": extract_section(
            artifact.text,
            "## 17. ПРОТОКОЛЫ СЕССИИ",
            "## 18. РАСХОЖДЕНИЕ РЕАЛИЗАЦИИ",
        ),
        "language": extract_section(
            artifact.text,
            "## 8. ДИРЕКТИВЫ, СТИЛЬ, ИНИЦИАТИВА",
            "## 9. ЭВОЛЮЦИЯ И ТРИ УРОВНЯ ОБУЧЕНИЯ",
        ),
    }
