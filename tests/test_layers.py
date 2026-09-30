import unittest
from pathlib import Path

from kiracore.context import ContextCompiler
from kiracore.genome import GenomeLoader
from kiracore.models import HistoryEntry, MemoryRecord, SessionState
from kiracore.stores import HistoryStore, MemoryStore


class LayerTests(unittest.TestCase):
    def test_only_approved_memory_enters_context(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)
        session = SessionState(
            session_id="s",
            authorized_alek=True,
            authorization_marker="~1",
            turn=1,
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
        )
        self.assertEqual([x.id for x in context.memory], ["a"])
        self.assertEqual(context.genome_revision, 22)
        self.assertEqual(context.genome_sha256, genome.sha256)
        self.assertIn("СТОП-ЭЛЕМЕНТЫ", context.protected_rules["stop_elements"])

    def test_zero_history_limit_means_empty_history(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)
        session = SessionState(session_id="s")
        history = [
            HistoryEntry(
                id="h1",
                date="2026-01-01",
                event="e",
                change="c",
                cause="cause",
                significance="sig",
                consequence="cons",
            )
        ]
        context = ContextCompiler().compile(
            genome,
            session,
            "задача",
            [],
            history,
            history_limit=0,
        )
        self.assertEqual(context.history, ())

    def test_duplicate_memory_id_is_rejected(self) -> None:
        store = MemoryStore()
        store.add_candidate(
            MemoryRecord(id="m", type="FACT", content="первое"),
        )
        with self.assertRaises(Exception):
            store.add_candidate(
                MemoryRecord(id="m", type="FACT", content="второе"),
            )

    def test_zero_history_limit_in_store_means_empty(self) -> None:
        store = HistoryStore()
        store.append(
            HistoryEntry(
                id="h1",
                date="2026-01-01",
                event="e",
                change="c",
                cause="cause",
                significance="sig",
                consequence="cons",
            )
        )
        self.assertEqual(store.recent(0), [])
