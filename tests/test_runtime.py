import unittest
from pathlib import Path

from kiracore.runtime import KiraRuntime


class RuntimeTests(unittest.TestCase):
    def test_start_loads_active_genome_and_builds_runtime_stores(self) -> None:
        root = Path(__file__).parents[1]
        runtime = KiraRuntime.start(root, expected_revision=22)

        self.assertEqual(
            runtime.genome.path,
            str(root / "GENOME" / "genome.txt"),
        )
        self.assertEqual(runtime.genome_store.artifact.revision, 22)
        self.assertTrue(runtime.state_store.exists("nonexistent") is False)
        self.assertIn(
            "s31_genome_state",
            {
                section.id
                for section in runtime.genome_store.sections("state")
            },
        )
