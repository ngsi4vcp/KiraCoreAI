from __future__ import annotations

import sys
from pathlib import Path


def application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def main() -> int:
    root = application_root()
    source_root = root / "src"
    if source_root.exists():
        sys.path.insert(0, str(source_root))

    from kiracore.application import VERSION, run_application

    if len(sys.argv) > 1 and sys.argv[1] in {"--version", "-V"}:
        print(f"Кира:Ядро | версия {VERSION}")
        return 0

    return run_application(root)


if __name__ == "__main__":
    raise SystemExit(main())
