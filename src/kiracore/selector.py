from __future__ import annotations

import os
import sys
import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def _raw_input() -> Iterator[None]:
    if os.name == "nt":
        yield
        return

    if not sys.stdin.isatty():
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
        sequence = second + third
        return {
            "[A": "up",
            "[B": "down",
            "[C": "right",
            "[D": "left",
        }.get(sequence, "esc")
    if char in ("\n", "\r"):
        return "enter"
    if char in ("\x7f", "\b"):
        return "backspace"
    return char


def select_from_list(
    title: str,
    items: list[str],
    initial_filter: str = "",
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
        if not filtered:
            filtered = []

        os.system("cls" if os.name == "nt" else "clear")
        print(title)
        print(f"Фильтр: {query}")
        print("↑/↓ выбор, Enter подтверждение, Backspace удаление, Esc отмена")
        print()

        if not filtered:
            print("Нет совпадений.")
        else:
            index = min(index, len(filtered) - 1)
            for position, (_, item) in enumerate(filtered[:20]):
                marker = "▶" if position == index else " "
                print(f"{marker} {item}")

        with _raw_input():
            key = _read_key()

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
        time.sleep(0.02)


def select_provider(
    title: str,
    items: list[tuple[str, str]],
) -> str | None:
    labels = [label for _, label in items]
    selected = select_from_list(title, labels)
    if selected is None:
        return None
    return items[selected][0]
