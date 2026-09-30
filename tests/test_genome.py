import unittest
from pathlib import Path

from kiracore.genome import GenomeLoader, GenomeParser


class GenomeTests(unittest.TestCase):
    ROOT = Path(__file__).parents[1]

    def test_loads_active_genome(self) -> None:
        artifact = GenomeLoader(expected_revision=22).load_active(self.ROOT)
        self.assertEqual(artifact.revision, 22)
        self.assertEqual(artifact.series, 1000)
        self.assertEqual(artifact.language, "ru")
        self.assertEqual(artifact.path, str(self.ROOT / "GENOME" / "genome.txt"))

    def test_default_genome_path_finds_active_file_from_project_root(self) -> None:
        artifact = GenomeLoader(expected_revision=22).load_active(self.ROOT)
        self.assertTrue(Path(artifact.path).is_file())
        self.assertEqual(
            Path(artifact.path).resolve(),
            (self.ROOT / "GENOME" / "genome.txt").resolve(),
        )

    def test_template_and_active_genome_are_parseable(self) -> None:
        loader = GenomeLoader(expected_revision=22)
        template = loader.load(self.ROOT / "G22.txt")
        active = loader.load(self.ROOT / "GENOME" / "genome.txt")
        self.assertEqual(template.revision, active.revision)
        self.assertEqual(template.series, active.series)
        self.assertEqual(len(template.document.sections), 36)
        self.assertEqual(len(active.document.sections), 36)

    def test_sections_are_explicit_and_indexed(self) -> None:
        artifact = GenomeLoader(expected_revision=22).load_active(self.ROOT)
        self.assertEqual(artifact.document.sections[0].id, "status")
        self.assertEqual(artifact.document.sections[-1].id, "anchor_end")
        self.assertEqual(artifact.runtime.section("s05_stop_elements").part, 1)
        self.assertIn(
            "s30_kira_memory",
            {section.id for section in artifact.runtime.sections_for("memory")},
        )
        self.assertIn(
            "s31_genome_state",
            {section.id for section in artifact.runtime.sections_for("state")},
        )

    def test_protected_rules_use_stable_section_ids(self) -> None:
        artifact = GenomeLoader(expected_revision=22).load_active(self.ROOT)
        protocol_ids = {section.id for section in artifact.runtime.sections_for("protocol")}
        self.assertIn("s02_authorization_turn", protocol_ids)
        self.assertIn("s05_stop_elements", protocol_ids)
        self.assertIn("s17_session_protocols", protocol_ids)

    def test_parser_rejects_duplicate_section_ids(self) -> None:
        text = """@@GENOME
FORMAT: KIRA-GENOME
FORMAT_VERSION: 1
REVISION: 1
SERIES: 1000
LANGUAGE: ru
DOCUMENT_KIND: constitutional
GOVERNANCE: manual

@@SECTION status
TYPE: metadata
PART: 0
TARGETS: core
MUTABILITY: immutable
TITLE: СТАТУС
@@BODY
Тест.
@@END

@@SECTION status
TYPE: metadata
PART: 0
TARGETS: core
MUTABILITY: immutable
TITLE: СТАТУС
@@BODY
Дубликат.
@@END
@@ENDGENOME
"""
        with self.assertRaises(Exception):
            GenomeParser().parse(text)
