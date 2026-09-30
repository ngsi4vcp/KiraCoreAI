import unittest
from pathlib import Path

from kiracore.genome import GenomeLoader


class GenomeTests(unittest.TestCase):
    def test_loads_canonical_g22(self) -> None:
        path = Path(__file__).parents[1] / "genome" / "G22.txt"
        artifact = GenomeLoader(
            expected_sha256="d76d59ee1e4e82f57cc7dd961512e3f35898343d8196c746a10a9be59700ff65"
        ).load(path)
        self.assertEqual(artifact.revision, 22)
        self.assertEqual(artifact.series, 1000)
