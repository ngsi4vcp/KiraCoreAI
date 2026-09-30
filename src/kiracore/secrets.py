from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProviderSecret:
    name: str
    api_key: str = ""
    base_url: str = ""


class SecretStore:
    """Читает локальные секреты и параметры коннекторов; содержимое ключей не логируется."""

    PATH = Path("SECRETS") / "credentials.ini"

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self.path = self.project_root / self.PATH

    def ensure_template(self) -> bool:
        if self.path.exists():
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            "[openrouter]\n"
            "api_key=\n\n"
            "[gemini]\n"
            "api_key=\n\n"
            "[lm_studio]\n"
            "api_key=lm-studio\n"
            "base_url=http://localhost:1234/v1\n",
            encoding="utf-8",
        )
        return True

    def load(self) -> dict[str, ProviderSecret]:
        self.ensure_template()
        parser = ConfigParser()
        parser.read(self.path, encoding="utf-8")
        result: dict[str, ProviderSecret] = {}
        for name in ("openrouter", "gemini", "lm_studio"):
            section = parser[name] if parser.has_section(name) else {}
            result[name] = ProviderSecret(
                name=name,
                api_key=section.get("api_key", ""),
                base_url=section.get("base_url", ""),
            )
        return result
