import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from kiracore.context import ContextCompiler
from kiracore.genome import GenomeLoader
from kiracore.models import SessionState
from kiracore.rendering import PlainTextPromptRenderer
from kiracore.terminal import TerminalHost


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


class TerminalLocalizationTests(unittest.TestCase):
    def test_banner_and_status_are_russian(self) -> None:
        host = TerminalHost()
        output = io.StringIO()
        with redirect_stdout(output):
            host.banner("0.1.0-alpha.1")
            host.status("Проверка среды", True)
            host.status("Подключение", None)
        text = output.getvalue()

        self.assertIn("КИРА:ЯДРО", text)
        self.assertIn("Альфа 0.1.0-alpha.1", text)
        self.assertNotIn("KiraCoreAI 0.1.0-alpha.1", text)
        self.assertIn("[ГОТОВО]", text)
        self.assertIn("[….]", text)
        self.assertNotIn("[OK]", text)
        self.assertNotIn("[!!]", text)

    def test_error_marker_is_russian(self) -> None:
        host = TerminalHost()
        output = io.StringIO()
        with redirect_stderr(output):
            host.error("Проверочная ошибка")
        self.assertIn("[ОШИБКА]", output.getvalue())
        self.assertNotIn("[!!]", output.getvalue())
