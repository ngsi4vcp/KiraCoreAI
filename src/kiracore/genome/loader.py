from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import sys

from .compiler import GenomeCompiler, GenomeRuntimeIndex
from .parser import GenomeDocument, GenomeParser
from .validator import GenomeValidator


@dataclass(frozen=True, slots=True)
class GenomeArtifact:
    """Неизменяемый снимок текста активного генома и его производного индекса."""

    text: str
    path: str
    revision: int
    series: int
    language: str
    sha256: str
    byte_length: int
    document: GenomeDocument
    runtime: GenomeRuntimeIndex

    @classmethod
    def from_text(cls, text: str, path: str = "<memory>") -> "GenomeArtifact":
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        document = GenomeParser().parse(normalized)
        raw = normalized.encode("utf-8")
        return cls(
            text=normalized,
            path=path,
            revision=document.revision,
            series=document.series,
            language=document.language,
            sha256=sha256(raw).hexdigest(),
            byte_length=len(raw),
            document=document,
            runtime=GenomeCompiler().compile(document),
        )


class GenomeLoader:
    """Загружает только указанный файл; runtime использует GENOME/genome.txt."""

    def __init__(
        self,
        expected_sha256: str | None = None,
        expected_revision: int | None = None,
    ) -> None:
        self.expected_sha256 = expected_sha256
        self.expected_revision = expected_revision

    def load(self, path: str | Path) -> GenomeArtifact:
        path = Path(path)
        with path.open("r", encoding="utf-8", newline="") as handle:
            text = handle.read()
        artifact = GenomeArtifact.from_text(text, str(path))
        GenomeValidator(
            expected_sha256=self.expected_sha256,
            expected_revision=self.expected_revision,
        ).validate(artifact)
        return artifact

    def load_active(self, project_root: str | Path | None = None) -> GenomeArtifact:
        return self.load(default_genome_path(project_root))


def _candidate_roots() -> tuple[Path, ...]:
    candidates: list[Path] = []

    frozen_root = Path(sys.executable).resolve().parent
    candidates.append(frozen_root)

    cwd = Path.cwd().resolve()
    candidates.append(cwd)

    source_root = Path(__file__).resolve().parents[3]
    candidates.append(source_root)

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            unique.append(candidate)
    return tuple(unique)


def default_genome_path(project_root: str | Path | None = None) -> Path:
    """Ищет активный геном в корне приложения без привязки к способу установки."""
    if project_root is not None:
        root = Path(project_root).resolve()
        path = root / "GENOME" / "genome.txt"
        if not path.is_file():
            raise FileNotFoundError(f"Активный геном не найден: {path}")
        return path

    for root in _candidate_roots():
        path = root / "GENOME" / "genome.txt"
        if path.is_file():
            return path

    searched = ", ".join(str(root) for root in _candidate_roots())
    raise FileNotFoundError(
        "Не найден GENOME/genome.txt. Проверены корни: " + searched
    )
