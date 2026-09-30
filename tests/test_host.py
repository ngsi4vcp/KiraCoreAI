import unittest
from pathlib import Path

from kiracore.context import ContextCompiler
from kiracore.genome import GenomeLoader
from kiracore.models import SessionState
from kiracore.reference_host import PlainTextHost


class ReferenceHostTests(unittest.TestCase):
    def test_reference_host_preserves_genome_identity_in_context(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)
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
