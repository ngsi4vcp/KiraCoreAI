from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def _raw_input() -> Iterator[None]:
    if os.name == "nt" or not sys.stdin.isatty():
        yield
        return

    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _read_key() -> str:
    if os.name == "nt":
        import msvcrt

        char = msvcrt.getwch()
        if char in ("\x00", "\xe0"):
            return {
                "H": "up",
                "P": "down",
                "K": "left",
                "M": "right",
            }.get(msvcrt.getwch(), "unknown")
        if char == "\r":
            return "enter"
        if char == "\x1b":
            return "esc"
        if char == "\x08":
            return "backspace"
        return char

    char = sys.stdin.read(1)
    if char == "\x1b":
        second = sys.stdin.read(1)
        third = sys.stdin.read(1)
        return {
            "[A": "up",
            "[B": "down",
            "[C": "right",
            "[D": "left",
        }.get(second + third, "esc")
    if char in ("\n", "\r"):
        return "enter"
    if char in ("\x7f", "\b"):
        return "backspace"
    return char


def select_from_list(
    title: str,
    items: list[str],
    initial_filter: str = "",
    visible: int = 20,
) -> int | None:
    if not items:
        return None

    query = initial_filter
    index = 0

    while True:
        filtered = [
            (position, item)
            for position, item in enumerate(items)
            if query.casefold() in item.casefold()
        ]
        os.system("cls" if os.name == "nt" else "clear")
        print(title)
        print(f"Фильтр: {query}")
        print("↑/↓ — выбор; Enter — подтвердить; Backspace — удалить символ; Esc — отмена")
        print()

        if not filtered:
            print("Нет совпадений.")
        else:
            index %= len(filtered)
            window_size = min(visible, len(filtered))
            start = min(
                max(index - window_size // 2, 0),
                max(len(filtered) - window_size, 0),
            )
            stop = start + window_size
            for position, (_, item) in enumerate(filtered[start:stop], start):
                marker = "▶" if position == index else " "
                print(f"{marker} {item}")
            print(f"\nПоказано {start + 1}–{stop} из {len(filtered)}")

        with _raw_input():
            key = _read_key()

        if not sys.stdin.isatty() and key not in {"up", "down", "enter", "esc", "backspace"}:
            query = input("Фильтр: ")
            continue

        if key == "esc":
            return None
        if key == "enter" and filtered:
            return filtered[index][0]
        if key == "up" and filtered:
            index = (index - 1) % len(filtered)
        elif key == "down" and filtered:
            index = (index + 1) % len(filtered)
        elif key == "backspace":
            query = query[:-1]
            index = 0
        elif len(key) == 1 and key.isprintable():
            query += key
            index = 0


def select_provider(
    title: str,
    items: list[tuple[str, str]],
) -> str | None:
    labels = [label for _, label in items]
    selected = select_from_list(title, labels)
    if selected is None:
        return None
    return items[selected][0]
