import tempfile
import unittest

from kiracore.models import MemoryRecord
from kiracore.stores import MemoryStore


class PersistenceTests(unittest.TestCase):
    def test_memory_survives_recreation_and_requires_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = f"{tmp}/memory.json"
            store = MemoryStore(path)
            store.add_candidate(
                MemoryRecord(id="m1", type="FACT", content="кандидат")
            )
            restored = MemoryStore(path)

            self.assertEqual(restored.candidates()[0].id, "m1")
            self.assertEqual(restored.approved(), [])

            restored.approve("m1", authorized_alek=True)
            restored_again = MemoryStore(path)
            self.assertEqual(restored_again.approved()[0].id, "m1")
