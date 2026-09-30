#!/usr/bin/env python3
"""Verify that the Android APK contains the Python bridge and core modules."""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path


REQUIRED_MODULES = (
    "android_bridge.pyc",
    "kiracore/runtime.pyc",
    "kiracore/genome/__init__.pyc",
)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} APK", file=sys.stderr)
        return 2

    apk_path = Path(sys.argv[1])
    if not apk_path.is_file():
        print(f"APK not found: {apk_path}", file=sys.stderr)
        return 2

    with zipfile.ZipFile(apk_path) as apk:
        try:
            app_imy = apk.read("assets/chaquopy/app.imy")
        except KeyError:
            print("Missing assets/chaquopy/app.imy", file=sys.stderr)
            return 1

    with zipfile.ZipFile(io.BytesIO(app_imy)) as imy:
        names = set(imy.namelist())
        missing = [
            module
            for module in REQUIRED_MODULES
            if module not in names
            and f"{module}c" not in names
            and not any(name.endswith(f"/{module}") for name in names)
        ]

    if missing:
        print("Chaquopy packaging smoke FAILED")
        print("Missing:")
        for module in missing:
            print(f"  - {module}")
        return 1

    print("Chaquopy packaging smoke PASS")
    for module in REQUIRED_MODULES:
        print(f"  + {module}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
