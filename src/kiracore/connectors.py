from __future__ import annotations

from abc import ABC, abstractmethod
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .errors import KiraCoreError
from .model_contract import (
    ChatMessage,
    ModelCatalogItem,
    ModelRequest,
    ModelResponse,
    ModelUsage,
)


class ModelConnectionError(KiraCoreError):
    """Коннектор не смог получить или обработать ответ внешней модели."""


class HttpJsonClient:
    """Минимальный HTTP-клиент без внешних зависимостей."""

    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = (
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
            if payload is not None
            else None
        )
        request = Request(
            url=url,
            method=method,
            headers={
                "Accept": "application/json",
                **(headers or {}),
                **({"Content-Type": "application/json"} if body is not None else {}),
            },
            data=body,
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ModelConnectionError(
                f"HTTP {exc.code} от {url}: {detail[:500]}"
            ) from exc
        except URLError as exc:
            raise ModelConnectionError(
                f"Не удалось подключиться к {url}: {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise ModelConnectionError(f"Истёк тайм-аут запроса к {url}.") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ModelConnectionError(
                f"Сервис вернул невалидный JSON: {url}"
            ) from exc
        if not isinstance(data, dict):
            raise ModelConnectionError(f"Сервис вернул неожиданный тип ответа: {url}")
        return data


def _as_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


class OpenAICompatibleConnector(ABC):
    """Общий адаптер для OpenAI-совместимых API."""

    provider = "openai-compatible"

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        timeout: float = 90.0,
        client: HttpJsonClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = client or HttpJsonClient(timeout=timeout)

    @property
    def authorization_headers(self) -> dict[str, str]:
        return (
            {"Authorization": f"Bearer {self.api_key}"}
            if self.api_key
            else {}
        )

    def list_models(self, query: str = "") -> list[ModelCatalogItem]:
        data = self.client.request(
            "GET",
            f"{self.base_url}/models",
            headers=self.authorization_headers,
        )
        raw_models = data.get("data", data.get("models", []))
        if not isinstance(raw_models, list):
            raise ModelConnectionError(
                f"Каталог моделей {self.provider} имеет неожиданный формат."
            )
        items = [self._normalize_model(item) for item in raw_models]
        items = [item for item in items if item.id]
        if not query:
            return items
        needle = query.casefold()
        return [
            item
            for item in items
            if needle in item.id.casefold()
            or needle in item.name.casefold()
            or needle in item.description.casefold()
        ]

    def generate(self, request: ModelRequest) -> ModelResponse:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        data = self.client.request(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self.authorization_headers,
            payload=payload,
        )
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ModelConnectionError(
                f"Модель {request.model} не вернула choices."
            )
        message = choices[0].get("message", {})
        text = message.get("content", "")
        if isinstance(text, list):
            text = "".join(
                part.get("text", "")
                for part in text
                if isinstance(part, dict)
            )
        if not isinstance(text, str) or not text.strip():
            raise ModelConnectionError(
                f"Модель {request.model} вернула пустой текст."
            )

        usage_data = data.get("usage")
        usage = None
        if isinstance(usage_data, dict):
            usage = ModelUsage(
                prompt_tokens=usage_data.get("prompt_tokens"),
                completion_tokens=usage_data.get("completion_tokens"),
                total_tokens=usage_data.get("total_tokens"),
            )

        return ModelResponse(
            text=text,
            provider=self.provider,
            model=request.model,
            request_id=data.get("id"),
            finish_reason=choices[0].get("finish_reason"),
            usage=usage,
            raw_metadata={
                "system_fingerprint": data.get("system_fingerprint"),
            },
        )

    @staticmethod
    def _normalize_model(item: dict[str, Any]) -> ModelCatalogItem:
        architecture = item.get("architecture", {})
        context_length = (
            item.get("context_length")
            or item.get("context_window")
            or item.get("inputTokenLimit")
        )
        return ModelCatalogItem(
            id=str(item.get("id", "")),
            name=str(item.get("name") or item.get("display_name") or item.get("id", "")),
            description=str(item.get("description", "")),
            context_length=int(context_length) if context_length else None,
            input_modalities=_as_tuple(architecture.get("input_modalities")),
            output_modalities=_as_tuple(architecture.get("output_modalities")),
            raw=item,
        )


class OpenRouterConnector(OpenAICompatibleConnector):
    provider = "openrouter"

    def __init__(
        self,
        api_key: str,
        timeout: float = 90.0,
        client: HttpJsonClient | None = None,
    ) -> None:
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            timeout=timeout,
            client=client,
        )

    @property
    def authorization_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Title": "KiraCoreAI",
        }


class GeminiConnector(OpenAICompatibleConnector):
    provider = "gemini"

    def __init__(
        self,
        api_key: str,
        timeout: float = 90.0,
        client: HttpJsonClient | None = None,
    ) -> None:
        super().__init__(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai",
            api_key=api_key,
            timeout=timeout,
            client=client,
        )


class LMStudioConnector(OpenAICompatibleConnector):
    provider = "lm_studio"

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        api_key: str = "lm-studio",
        timeout: float = 180.0,
        client: HttpJsonClient | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            client=client,
        )


def connector_for(
    provider: str,
    secrets: dict[str, Any],
) -> OpenAICompatibleConnector:
    normalized = provider.casefold()
    secret = secrets[normalized]
    if normalized == "openrouter":
        if not secret.api_key:
            raise ModelConnectionError("Не задан ключ OpenRouter.")
        return OpenRouterConnector(secret.api_key)
    if normalized == "gemini":
        if not secret.api_key:
            raise ModelConnectionError("Не задан ключ Google Gemini.")
        return GeminiConnector(secret.api_key)
    if normalized == "lm_studio":
        return LMStudioConnector(
            base_url=secret.base_url or "http://localhost:1234/v1",
            api_key=secret.api_key or "lm-studio",
        )
    raise ModelConnectionError(f"Неизвестный коннектор: {provider}")


def available_connectors(secrets: dict[str, Any]) -> list[str]:
    result: list[str] = []
    if secrets.get("openrouter") and secrets["openrouter"].api_key:
        result.append("openrouter")
    if secrets.get("gemini") and secrets["gemini"].api_key:
        result.append("gemini")
    # LM Studio не требует удалённого ключа; доступность проверяется при обращении.
    if secrets.get("lm_studio"):
        result.append("lm_studio")
    return result


def human_provider_name(provider: str) -> str:
    return {
        "openrouter": "OpenRouter",
        "gemini": "Google Gemini",
        "lm_studio": "LM Studio",
    }.get(provider, provider)


__all__ = [
    "GeminiConnector",
    "HttpJsonClient",
    "LMStudioConnector",
    "ModelConnectionError",
    "OpenAICompatibleConnector",
    "OpenRouterConnector",
    "available_connectors",
    "connector_for",
    "human_provider_name",
]
