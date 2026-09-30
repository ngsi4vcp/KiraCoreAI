import tempfile
import unittest

from kiracore.conversation import ConversationStore
from kiracore.pulse import pulse_stamp


class ConversationTests(unittest.TestCase):
    def test_conversation_is_persisted_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ConversationStore(tmp)
            manifest = store.create("openrouter", "example/model")
            pulse = pulse_stamp(1, 22, 1000)
            store.append(manifest.session_id, 1, "user", "Привет")
            store.append(
                manifest.session_id,
                1,
                "assistant",
                "Ответ",
                pulse=pulse,
            )

            messages = store.recent(manifest.session_id, 10)
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[-1].pulse.value, 1024)
            self.assertEqual(
                store.list()[0].session_id,
                manifest.session_id,
            )
