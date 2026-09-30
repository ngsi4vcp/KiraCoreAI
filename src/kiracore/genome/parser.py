from __future__ import annotations

from dataclasses import dataclass
import re

from ..errors import GenomeIntegrityError

_SECTION_RE = re.compile(r"^@@SECTION ([a-z0-9_]+)$")
_KEY_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*:\s*(.*)$")
_ID_RE = re.compile(r"^[a-z0-9_]+$")


@dataclass(frozen=True, slots=True)
class GenomeSection:
    id: str
    type: str
    part: int
    targets: tuple[str, ...]
    mutability: str
    title: str
    body: str
    order: int


@dataclass(frozen=True, slots=True)
class GenomeDocument:
    format: str
    format_version: int
    revision: int
    series: int
    language: str
    document_kind: str
    governance: str
    sections: tuple[GenomeSection, ...]

    def section(self, section_id: str) -> GenomeSection:
        for section in self.sections:
            if section.id == section_id:
                return section
        raise GenomeIntegrityError(f"Раздел генома не найден: {section_id}")


class GenomeParser:
    """Строго разбирает геном по явным границам секций."""

    REQUIRED_HEADER = (
        "FORMAT",
        "FORMAT_VERSION",
        "REVISION",
        "SERIES",
        "LANGUAGE",
        "DOCUMENT_KIND",
        "GOVERNANCE",
    )
    REQUIRED_SECTION = (
        "TYPE",
        "PART",
        "TARGETS",
        "MUTABILITY",
        "TITLE",
    )

    def parse(self, text: str) -> GenomeDocument:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = normalized.split("\n")
        if not lines or lines[0] != "@@GENOME":
            raise GenomeIntegrityError("Геном должен начинаться с @@GENOME.")

        index = 1
        header: dict[str, str] = {}
        sections: list[GenomeSection] = []
        seen_ids: set[str] = set()

        while index < len(lines):
            line = lines[index]
            if line == "@@ENDGENOME":
                break
            if line.strip() == "":
                index += 1
                continue

            match = _SECTION_RE.match(line)
            if not match:
                self._put_key(header, line, "заголовке генома")
                index += 1
                continue

            section_id = match.group(1)
            if section_id in seen_ids:
                raise GenomeIntegrityError(f"Дублирован ID раздела: {section_id}")
            seen_ids.add(section_id)
            index += 1

            metadata: dict[str, str] = {}
            while index < len(lines):
                line = lines[index]
                if line == "@@BODY":
                    break
                if line == "@@ENDGENOME" or _SECTION_RE.match(line):
                    raise GenomeIntegrityError(
                        f"Раздел {section_id} не содержит @@BODY."
                    )
                if line.strip() == "":
                    index += 1
                    continue
                self._put_key(metadata, line, f"метаданных раздела {section_id}")
                index += 1

            if index >= len(lines) or lines[index] != "@@BODY":
                raise GenomeIntegrityError(
                    f"Раздел {section_id} не содержит маркер @@BODY."
                )
            index += 1

            body_lines: list[str] = []
            while index < len(lines) and lines[index] != "@@END":
                if lines[index] == "@@ENDGENOME" or _SECTION_RE.match(lines[index]):
                    raise GenomeIntegrityError(
                        f"Раздел {section_id} не закрыт маркером @@END."
                    )
                body_lines.append(lines[index])
                index += 1

            if index >= len(lines) or lines[index] != "@@END":
                raise GenomeIntegrityError(
                    f"Раздел {section_id} не закрыт маркером @@END."
                )
            index += 1

            missing = [key for key in self.REQUIRED_SECTION if key not in metadata]
            if missing:
                raise GenomeIntegrityError(
                    f"В разделе {section_id} отсутствуют поля: {', '.join(missing)}"
                )

            part = self._int(metadata["PART"], f"{section_id}.PART")
            targets = tuple(
                item.strip()
                for item in metadata["TARGETS"].split(",")
                if item.strip()
            )
            if not targets:
                raise GenomeIntegrityError(
                    f"В разделе {section_id} отсутствуют TARGETS."
                )
            if not _ID_RE.fullmatch(section_id):
                raise GenomeIntegrityError(f"Недопустимый ID раздела: {section_id}")

            sections.append(
                GenomeSection(
                    id=section_id,
                    type=metadata["TYPE"],
                    part=part,
                    targets=targets,
                    mutability=metadata["MUTABILITY"],
                    title=metadata["TITLE"],
                    body="\n".join(body_lines).strip("\n"),
                    order=len(sections),
                )
            )

        if index >= len(lines) or lines[index] != "@@ENDGENOME":
            raise GenomeIntegrityError("Геном не закрыт маркером @@ENDGENOME.")
        if any(line.strip() for line in lines[index + 1:]):
            raise GenomeIntegrityError("После @@ENDGENOME обнаружено дополнительное содержимое.")

        missing = [key for key in self.REQUIRED_HEADER if key not in header]
        if missing:
            raise GenomeIntegrityError(
                "В заголовке генома отсутствуют поля: " + ", ".join(missing)
            )

        return GenomeDocument(
            format=header["FORMAT"],
            format_version=self._int(header["FORMAT_VERSION"], "FORMAT_VERSION"),
            revision=self._int(header["REVISION"], "REVISION"),
            series=self._int(header["SERIES"], "SERIES"),
            language=header["LANGUAGE"],
            document_kind=header["DOCUMENT_KIND"],
            governance=header["GOVERNANCE"],
            sections=tuple(sections),
        )

    @staticmethod
    def _put_key(target: dict[str, str], line: str, scope: str) -> None:
        match = _KEY_RE.match(line)
        if not match:
            raise GenomeIntegrityError(f"Недопустимая строка в {scope}: {line!r}")
        key, value = match.groups()
        if key in target:
            raise GenomeIntegrityError(f"Дублирован ключ {key} в {scope}.")
        target[key] = value

    @staticmethod
    def _int(value: str, name: str) -> int:
        try:
            return int(value)
        except ValueError as exc:
            raise GenomeIntegrityError(
                f"Поле {name} должно быть целым числом: {value!r}"
            ) from exc
