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
from .errors import KiraCoreError
from .runtime import KiraRuntime
from .secrets import SecretStore
from .selector import select_from_list, select_provider
from .terminal import TerminalHost


VERSION = "0.1.0-alpha.1"


class TerminalApplication:
    """Оркестрирует пользовательский сценарий Альфа."""

    def __init__(self, project_root: str | Path) -> None:
        self.root = Path(project_root).resolve()
        self.host = TerminalHost()
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
        self.host.status("Создание DATA/ и контуров сохранения", True)
        self.host.status("Чтение GENOME/genome.txt", True)
        self.host.status(
            f"Геном: ревизия {self.runtime.genome.revision}, "
            f"SHA-256 {self.runtime.genome.sha256[:16]}…",
            True,
        )
        self.host.status("Загрузка локального файла секретов", True)
        self.select_model()
        self.host.status(
            f"Модель подготовлена: {human_provider_name(self.provider)} / {self.model_id}",
            True,
        )
        self.host.status("Запуск основного рантайма", True)
        self.host.status("Инициализация завершена", True)

    def select_model(self) -> None:
        names = available_connectors(self.credentials)
        labels = [(name, human_provider_name(name)) for name in names]
        if not labels:
            raise ModelConnectionError(
                "Нет доступного коннектора. Заполните "
                "SECRETS/credentials.ini или запустите LM Studio."
            )

        preferred_provider = self.preferences.get("provider")

        while True:
            provider = (
                preferred_provider
                if preferred_provider in names
                else select_provider(
                    "Выберите коннектор:",
                    labels,
                )
            )
            if provider is None:
                raise KeyboardInterrupt

            try:
                self.host.status(
                    f"Подключение к {human_provider_name(provider)}",
                    None,
                )
                model = connector_for(provider, self.credentials)
                catalog = model.list_models("")
            except ModelConnectionError as exc:
                self.host.error(str(exc))
                preferred_provider = None
                continue

            if not catalog:
                self.host.error(
                    f"Коннектор {human_provider_name(provider)} не вернул моделей."
                )
                preferred_provider = None
                continue

            self.host.status(
                f"Каталог моделей получен: {len(catalog)}",
                True,
            )
            self.model = model
            self.provider = provider

            preferred_model = self.preferences.get("model")
            preferred_index = next(
                (i for i, item in enumerate(catalog) if item.id == preferred_model),
                None,
            )
            if preferred_index is not None:
                model_id = catalog[preferred_index].id
            else:
                model_labels = [
                    f"{item.id} — {item.name}"
                    for item in catalog
                ]
                selected = select_from_list(
                    "Выберите модель (поиск фильтрует каталог сразу):",
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
            return

    def _session_menu(self) -> str:
        sessions = self.runtime.conversation_store.list()
        if not sessions:
            return "new"
        selected = select_from_list(
            "Сессия:",
            [
                "Продолжить последний разговор",
                "Начать новый разговор",
            ],
        )
        if selected is None:
            raise KeyboardInterrupt
        return "resume" if selected == 0 else "new"

    def run(self) -> int:
        try:
            self.startup()
            action = self._session_menu()
            if action == "resume":
                manifest = self.runtime.resume_latest_session()
                if manifest is None:
                    action = "new"
                else:
                    session_id = manifest.session_id
            if action == "new":
                manifest = self.runtime.create_session(
                    self.provider,
                    self.model_id,
                )
                session_id = manifest.session_id

            self.host.banner(VERSION, self.provider, self.model_id)

            while True:
                task = self.host.prompt()
                command = task.strip()

                if command == "/exit":
                    return 0
                if command == "/help":
                    print(
                        "Команды:\n"
                        "  /help — показать справку\n"
                        "  /status — показать текущее состояние\n"
                        "  /genome — сведения об активном геноме\n"
                        "  /sessions — список сохранённых разговоров\n"
                        "  /memory — утверждённая память\n"
                        "  /memory candidates — кандидаты памяти\n"
                        "  /memory approve <id> — утвердить запись памяти\n"
                        "  /exit — завершить работу"
                    )
                    continue
                if command == "/status":
                    self._print_status()
                    continue
                if command == "/genome":
                    print(
                        f"Ревизия: {self.runtime.genome.revision}\n"
                        f"SHA-256: {self.runtime.genome.sha256}\n"
                        f"Секций: {len(self.runtime.genome.document.sections)}"
                    )
                    continue
                if command == "/sessions":
                    sessions = self.runtime.conversation_store.list()
                    if not sessions:
                        print("Сохранённых разговоров нет.")
                        continue
                    print("Сохранённые разговоры:")
                    for item in sessions:
                        print(
                            f"{item.session_id[:8]}  "
                            f"{item.updated_at}  "
                            f"{item.provider}/{item.model}"
                        )
                    continue
                if command == "/memory":
                    self._print_memory()
                    continue
                if command == "/memory candidates":
                    self._print_memory(candidates=True)
                    continue
                if command.startswith("/memory approve "):
                    record_id = command.removeprefix("/memory approve ").strip()
                    try:
                        self.runtime.approve_memory(session_id, record_id)
                    except KiraCoreError as exc:
                        self.host.error(str(exc))
                    else:
                        print(f"[ГОТОВО] Память утверждена: {record_id}")
                    continue
                if not task.strip():
                    continue

                try:
                    output = self.runtime.run(
                        session_id,
                        task,
                        self.model,
                        self.provider,
                        self.model_id,
                    )
                    self.host.print_response(
                        output.text,
                        output.raw_metadata["pulse_rendered"],
                    )
                except ModelConnectionError as exc:
                    self.host.error(str(exc))
                except KiraCoreError as exc:
                    self.host.error(str(exc))
                except Exception as exc:
                    self.host.error(f"Непредвиденная ошибка хода: {exc}")

        except KeyboardInterrupt:
            self.host.status("Завершение сессии", True)
            return 0
        except Exception as exc:
            self.host.error(str(exc))
            return 1

    def _print_memory(self, candidates: bool = False) -> None:
        items = (
            self.runtime.memory_store.candidates()
            if candidates
            else self.runtime.memory_store.approved()
        )
        if not items:
            print("Записей памяти нет.")
            return
        print("Кандидаты памяти:" if candidates else "Утверждённая память:")
        for item in items:
            status = {
                "candidate": "кандидат",
                "approved": "утверждено",
                "cancelled": "отменено",
            }.get(item.status, item.status)
            print(
                f"- {item.id} | {status} | {item.type} | "
                f"{item.content}"
            )

    def _print_status(self) -> None:
        state = self.runtime.core_state
        print(
            f"Ревизия: {self.runtime.genome.revision}\n"
            f"Сессия: {state.get('active_session_id', '—')}\n"
            f"Ход: {state.get('turn', 0)}\n"
            f"Пульс: {state.get('pulse', '—')}\n"
            f"Авторизация Алека: {state.get('authorized_alek', False)}\n"
            f"Поставщик / модель: {self.provider}/{self.model_id}"
        )


def run_application(project_root: str | Path) -> int:
    return TerminalApplication(project_root).run()
