from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .connectors import (
    ModelConnectionError,
    available_connectors,
    connector_for,
    human_provider_name,
)
from .conversation import ConversationStore
from .genome import GenomeLoader, GenomeStore
from .persistence import CoreStatePersistence, JsonPersistence
from .pulse import pulse_stamp
from .rendering import PlainTextPromptRenderer
from .runtime import KiraRuntime
from .secrets import SecretStore
from .selector import select_from_list, select_provider
from .terminal import TerminalHost


VERSION = "0.1.0-alpha.1"


class TerminalApplication:
    """Оркестрирует пользовательский сценарий Alpha."""

    def __init__(self, project_root: str | Path) -> None:
        self.root = Path(project_root).resolve()
        self.host = TerminalHost()
        self.core_persistence = CoreStatePersistence(self.root / "DATA")
        self.runtime = KiraRuntime.start(self.root)
        self.secrets = SecretStore(self.root)
        self.secrets.ensure_template()
        self.credentials = self.secrets.load()
        self.preferences_path = self.root / "DATA" / "preferences.json"
        self.preferences = self._load_preferences()

        self.model = None
        self.provider = ""
        self.model_id = ""

    def _load_preferences(self) -> dict[str, Any]:
        if not self.preferences_path.exists():
            return {}
        try:
            return json.loads(self.preferences_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _save_preferences(self) -> None:
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        self.preferences_path.write_text(
            json.dumps(self.preferences, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def startup(self) -> None:
        self.host.banner(VERSION)
        self.host.status("Определение среды", True)
        self.host.status("Чтение GENOME/genome.txt", True)
        self.host.status(
            f"Геном: ревизия {self.runtime.genome.revision}, "
            f"SHA-256 {self.runtime.genome.sha256[:16]}…",
            True,
        )
        self.host.status("Создание DATA/ и persistent-контуров", True)
        self.host.status("Загрузка локального файла секретов", True)
        self.select_model()
        self.host.status(
            f"Модель подготовлена: {human_provider_name(self.provider)} / {self.model_id}",
            True,
        )
        self.host.status("Запуск KiraRuntime", True)
        self.host.status("Инициализация завершена", True)

    def select_model(self) -> None:
        names = available_connectors(self.credentials)
        labels = [(name, human_provider_name(name)) for name in names]
        if not labels:
            raise ModelConnectionError(
                "Нет доступного коннектора. Заполните "
                "SECRETS/credentials.ini или запустите LM Studio."
            )

        preferred = self.preferences.get("provider")
        provider = preferred if preferred in names else select_provider(
            "Выберите коннектор:",
            labels,
        )
        if provider is None:
            raise KeyboardInterrupt

        self.model = connector_for(provider, self.credentials)
        self.provider = provider

        query = self.preferences.get("model_query", "")
        catalog = self.model.list_models(query)
        if not catalog:
            raise ModelConnectionError(
                f"Коннектор {human_provider_name(provider)} не вернул модели."
            )

        model_labels = [
            f"{item.id} — {item.name}"
            for item in catalog
        ]
        preferred_model = self.preferences.get("model")
        preferred_index = next(
            (
                i
                for i, item in enumerate(catalog)
                if item.id == preferred_model
            ),
            None,
        )
        if preferred_index is not None:
            model_id = catalog[preferred_index].id
        else:
            selected = select_from_list(
                "Выберите модель (пишите часть названия прямо в этом окне):",
                model_labels,
            )
            if selected is None:
                raise KeyboardInterrupt
            model_id = catalog[selected].id

        self.model_id = model_id
        self.preferences.update({
            "provider": provider,
            "model": model_id,
        })
        self._save_preferences()

    def _session_menu(self) -> str:
        sessions = self.runtime.conversation_store.list()
        if not sessions:
            return "new"
        options = [
            "Продолжить последний разговор",
            "Начать новый разговор",
        ]
        selected = select_from_list("Сессия:", options)
        if selected is None:
            raise KeyboardInterrupt
        return "resume" if selected == 0 else "new"

    def run(self) -> int:
        try:
            self.startup()
            action = self._session_menu()
            if action == "resume":
                manifest = self.runtime.conversation_store.list()[0]
                session_id = manifest.session_id
            else:
                manifest = self.runtime.create_session(
                    self.provider,
                    self.model_id,
                )
                session_id = manifest.session_id

            self.host.banner(
                VERSION,
                self.provider,
                self.model_id,
            )

            while True:
                task = self.host.prompt()
                if task.strip() == "/exit":
                    return 0
                if task.strip() == "/help":
                    print(
                        "/help /status /genome /sessions /memory /exit"
                    )
                    continue
                if task.strip() == "/status":
                    self._print_status()
                    continue
                if task.strip() == "/genome":
                    print(
                        f"Ревизия: {self.runtime.genome.revision}\n"
                        f"SHA-256: {self.runtime.genome.sha256}\n"
                        f"Секций: {len(self.runtime.genome.document.sections)}"
                    )
                    continue
                if task.strip() == "/sessions":
                    for item in self.runtime.conversation_store.list():
                        print(
                            f"{item.session_id[:8]}  "
                            f"{item.updated_at}  "
                            f"{item.provider}/{item.model}"
                        )
                    continue
                if task.strip() == "/memory":
                    for item in self.runtime.memory_store.approved():
                        print(f"- {item.type}: {item.content}")
                    continue
                if not task.strip():
                    continue

                output = self.runtime.run(
                    session_id,
                    task,
                    self.model,
                    self.provider,
                    self.model_id,
                )
                self.host.print_response(output.text, output.pulse.render())

        except KeyboardInterrupt:
            self.host.status("Завершение сессии", True)
            return 0
        except Exception as exc:
            self.host.error(str(exc))
            return 1

    def _print_status(self) -> None:
        state = self.runtime.core_state
        print(
            f"Ревизия: {self.runtime.genome.revision}\n"
            f"Сессия: {state.get('active_session_id', '—')}\n"
            f"Ход: {state.get('turn', 0)}\n"
            f"Пульс: {state.get('pulse', '—')}\n"
            f"Модель: {self.provider}/{self.model_id}"
        )


def run_application(project_root: str | Path) -> int:
    return TerminalApplication(project_root).run()
