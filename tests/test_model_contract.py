import unittest

from kiracore.connectors import GeminiConnector, LMStudioConnector, OpenRouterConnector
from kiracore.model_contract import ChatMessage, ModelRequest


class FakeClient:
    def __init__(self) -> None:
        self.calls = []

    def request(self, method, url, headers=None, payload=None):
        self.calls.append((method, url, headers, payload))
        if url.endswith("/models"):
            return {
                "data": [{
                    "id": "example/model",
                    "name": "Example",
                    "description": "Тестовая модель",
                    "context_length": 8192,
                }]
            }
        return {
            "id": "req-1",
            "choices": [{
                "message": {"role": "assistant", "content": "Ответ"},
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        }


class ConnectorTests(unittest.TestCase):
    def test_openrouter_catalog_and_generation(self) -> None:
        client = FakeClient()
        connector = OpenRouterConnector("key", client=client)
        models = connector.list_models("example")
        self.assertEqual(models[0].id, "example/model")

        response = connector.generate(
            ModelRequest(
                provider="openrouter",
                model="example/model",
                messages=(ChatMessage(role="user", content="Привет"),),
            )
        )
        self.assertEqual(response.text, "Ответ")
        self.assertEqual(response.usage.total_tokens, 15)

    def test_provider_endpoints_are_distinct(self) -> None:
        self.assertEqual(
            OpenRouterConnector("key", client=FakeClient()).base_url,
            "https://openrouter.ai/api/v1",
        )
        self.assertEqual(
            GeminiConnector("key", client=FakeClient()).base_url,
            "https://generativelanguage.googleapis.com/v1beta/openai",
        )
        self.assertEqual(
            LMStudioConnector(client=FakeClient()).base_url,
            "http://localhost:1234/v1",
        )
