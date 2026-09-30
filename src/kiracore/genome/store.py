from __future__ import annotations

from .loader import GenomeArtifact
from .parser import GenomeSection


class GenomeStore:
    """Иммутабельное хранилище снимка генома и секционных индексов."""

    def __init__(self, artifact: GenomeArtifact) -> None:
        self._artifact = artifact

    @property
    def artifact(self) -> GenomeArtifact:
        return self._artifact

    def section(self, section_id: str) -> GenomeSection:
        return self._artifact.runtime.section(section_id)

    def sections(self, target: str) -> tuple[GenomeSection, ...]:
        return self._artifact.runtime.sections_for(target)

    def sections_by_part(self, part: int) -> tuple[GenomeSection, ...]:
        return self._artifact.runtime.parts(part)
