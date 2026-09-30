from __future__ import annotations

import os
import sys


class TerminalHost:
    """Терминальный интерфейс Альфа и одновременно адаптер интерактивной среды."""

    def banner(self, version: str, provider: str | None = None, model: str | None = None) -> None:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║                       КИРА:ЯДРО                         ║")
        print(f"║                 Альфа {version:<27}║")
        print("╚══════════════════════════════════════════════════════════╝")
        if provider and model:
            print(f"Поставщик: {provider} / модель: {model}")
        print()

    def status(self, message: str, ok: bool | None = None) -> None:
        marker = "[ГОТОВО]" if ok is True else "[….]" if ok is None else "[ОШИБКА]"
        print(f"{marker} {message}")

    def error(self, message: str) -> None:
        print(f"[ОШИБКА] {message}", file=sys.stderr)

    def prompt(self) -> str:
        return input("\nКира > ")

    def print_response(self, text: str, pulse: str) -> None:
        print(f"\nКира:\n{text}\n{pulse}")

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
