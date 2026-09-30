from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

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


def default_genome_path(project_root: str | Path | None = None) -> Path:
    """Единственный нормативный путь runtime-генома."""
    if project_root is None:
        project_root = Path(__file__).resolve().parents[3]
    return Path(project_root) / "GENOME" / "genome.txt"
