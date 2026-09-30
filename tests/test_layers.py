import unittest
from pathlib import Path

from kiracore.context import ContextCompiler
from kiracore.genome import GenomeLoader
from kiracore.models import MemoryRecord, SessionState


class LayerTests(unittest.TestCase):
    def test_only_approved_memory_enters_context(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)
        session = SessionState(
            session_id="s",
            turn=1,
            authorized_alek=True,
            authorization_marker="~1",
            provider="test",
            model="example/model",
        )
        memory = [
            MemoryRecord(
                id="a",
                type="FACT",
                content="утверждено",
                importance=1.0,
                status="approved",
            ),
            MemoryRecord(
                id="b",
                type="FACT",
                content="кандидат",
                importance=1.0,
                status="candidate",
            ),
        ]
        context = ContextCompiler().compile(
            genome,
            session,
            "задача",
            memory,
            [],
            [],
            "test",
            "example/model",
        )
        self.assertEqual([x.id for x in context.memory], ["a"])
        self.assertEqual(context.genome_revision, 22)
        self.assertEqual(context.genome_sha256, genome.sha256)
        self.assertIn(
            "СТОП-ЭЛЕМЕНТЫ",
            context.protected_rules["stop_elements"],
        )

    def test_zero_history_limit_means_empty_history(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)
        session = SessionState(
            session_id="s",
            turn=1,
            provider="test",
            model="example/model",
        )
        context = ContextCompiler().compile(
            genome,
            session,
            "задача",
            [],
            [],
            [],
            "test",
            "example/model",
            history_limit=0,
        )
        self.assertEqual(context.history, ())
