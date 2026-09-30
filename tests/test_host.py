import unittest
from pathlib import Path

from kiracore.context import ContextCompiler
from kiracore.genome import GenomeLoader
from kiracore.models import SessionState
from kiracore.rendering import PlainTextPromptRenderer


class PromptRenderingTests(unittest.TestCase):
    def test_renderer_is_not_host_and_does_not_generate_pulse(self) -> None:
        root = Path(__file__).parents[1]
        genome = GenomeLoader(expected_revision=22).load_active(root)
        session = SessionState(
            session_id="host-test",
            turn=1,
            provider="openrouter",
            model="example/model",
        )
        context = ContextCompiler().compile(
            genome,
            session,
            "Проверить границу.",
            [],
            [],
            [],
            "openrouter",
            "example/model",
        )
        request = PlainTextPromptRenderer().render(context)
        self.assertEqual(request.provider, "openrouter")
        self.assertEqual(request.model, "example/model")
        self.assertEqual(request.messages[0].role, "system")
        self.assertIn("Не генерируй его самостоятельно", request.messages[0].content)
