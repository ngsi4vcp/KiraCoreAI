import unittest
from pathlib import Path

from kiracore.genome import GenomeLoader
from kiracore.models import SessionState
from kiracore.context import ContextCompiler
from kiracore.reference_host import PlainTextHost


class ReferenceHostTests(unittest.TestCase):
    def test_reference_host_preserves_genome_identity_in_context(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(
            expected_sha256="d76d59ee1e4e82f57cc7dd961512e3f35898343d8196c746a10a9be59700ff65"
        ).load(root / "genome" / "G22.txt")
        session = SessionState(
            session_id="host-test",
            authorized_alek=True,
            authorization_marker="~1",
            turn=1,
        )
        context = ContextCompiler().compile(
            genome,
            session,
            "Проверить границу хоста.",
            [],
            [],
        )
        rendered = PlainTextHost().render_context(context)
        self.assertIn("РЕВИЗИЯ ГЕНОМА: 22", rendered)
        self.assertIn(genome.sha256, rendered)
        self.assertIn("СТОП-ЭЛЕМЕНТЫ", rendered)
