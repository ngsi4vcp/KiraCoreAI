from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .parser import GenomeDocument, GenomeSection


@dataclass(frozen=True, slots=True)
class GenomeRuntimeIndex:
    """Производный индекс генома для runtime-контуров; не источник истины."""

    sections_by_id: Mapping[str, GenomeSection]
    sections_by_target: Mapping[str, tuple[GenomeSection, ...]]
    sections_by_part: Mapping[int, tuple[GenomeSection, ...]]

    def section(self, section_id: str) -> GenomeSection:
        return self.sections_by_id[section_id]

    def sections_for(self, target: str) -> tuple[GenomeSection, ...]:
        return self.sections_by_target.get(target, ())

    def parts(self, part: int) -> tuple[GenomeSection, ...]:
        return self.sections_by_part.get(part, ())


class GenomeCompiler:
    """Компилирует документ генома в индексы по runtime-целям."""

    def compile(self, document: GenomeDocument) -> GenomeRuntimeIndex:
        by_id = {section.id: section for section in document.sections}
        by_target: dict[str, list[GenomeSection]] = {}
        by_part: dict[int, list[GenomeSection]] = {}

        for section in document.sections:
            by_part.setdefault(section.part, []).append(section)
            for target in section.targets:
                by_target.setdefault(target, []).append(section)

        return GenomeRuntimeIndex(
            sections_by_id=MappingProxyType(dict(by_id)),
            sections_by_target=MappingProxyType(
                {key: tuple(value) for key, value in by_target.items()}
            ),
            sections_by_part=MappingProxyType(
                {key: tuple(value) for key, value in by_part.items()}
            ),
        )



PROTECTED_SECTION_IDS = {
    "authorization": "s02_authorization_turn",
    "stop_elements": "s05_stop_elements",
    "session_protocol": "s17_session_protocols",
    "directives": "s08_directives_style_initiative",
}


def protected_section_ids() -> dict[str, str]:
    """Возвращает только идентификаторы защищённых секций."""
    return dict(PROTECTED_SECTION_IDS)
