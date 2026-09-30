from __future__ import annotations

import re
import sys
from pathlib import Path
import zipfile

ROOT = Path(__file__).parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SOURCE_ROOTS = [ROOT / "android", ROOT / "src", ROOT / "tests", ROOT / "schemas"]
BUILD_ROOT = ROOT / "android" / "app" / "build"
TEXT_EXTENSIONS = {
    ".gradle",
    ".gradle.kts",
    ".kt",
    ".py",
    ".xml",
    ".json",
    ".md",
    ".properties",
    ".txt",
    ".yml",
    ".yaml",
}

SOURCE_PATTERNS = (
    re.compile(r"sk-or-v1-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    re.compile(r"(?i)alek[_ -]?password\s*[:=]\s*[^\s#]{8,}"),
)

APK_BINARY_MARKERS = (
    b"sk-or-v1-",
    b"sk-proj-",
    b"AIza",
    b"ghp_",
    b"github_pat_",
)

APK_PATHS = (
    BUILD_ROOT / "outputs" / "apk" / "debug" / "app-debug.apk",
)


def scan_text_file(path: Path, violations: list[str]) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    for pattern in SOURCE_PATTERNS:
        if pattern.search(content):
            violations.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")


def scan_source_tree(violations: list[str]) -> None:
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in TEXT_EXTENSIONS:
                scan_text_file(path, violations)


def scan_apk(path: Path, violations: list[str]) -> None:
    if not path.exists():
        return
    payload = path.read_bytes()
    for marker in APK_BINARY_MARKERS:
        if marker in payload:
            violations.append(f"{path.relative_to(ROOT)}: APK marker {marker!r}")

    try:
        with zipfile.ZipFile(path) as archive:
            for entry in archive.infolist():
                if entry.is_dir():
                    continue
                name = entry.filename
                if not (
                    name.startswith("assets/")
                    or name.startswith("res/raw/")
                    or name.endswith(".dex")
                ):
                    continue
                data = archive.read(entry)
                for marker in APK_BINARY_MARKERS:
                    if marker in data:
                        violations.append(
                            f"{path.relative_to(ROOT)}::{name}: marker {marker!r}"
                        )
    except (OSError, zipfile.BadZipFile):
        violations.append(f"{path.relative_to(ROOT)}: не удалось прочитать APK.")


def main() -> int:
    violations: list[str] = []
    scan_source_tree(violations)

    for apk in APK_PATHS:
        scan_apk(apk, violations)

    if violations:
        print("Обнаружены признаки секретов:")
        print("\n".join(violations))
        return 1

    print("Android security smoke: credential-паттернов не найдено.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
