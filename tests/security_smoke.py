from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
SCAN_ROOTS = [
    ROOT / "android",
    ROOT / "src",
    ROOT / "tests",
    ROOT / "schemas",
    ROOT / "android" / "app" / "build",
]
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
BINARY_EXTENSIONS = {".apk", ".dex", ".so", ".aar", ".jar"}

PATTERN_TEXTS = (
    r"sk-or-v1-[A-Za-z0-9_-]{20,}",
    r"sk-[A-Za-z0-9_-]{20,}",
    r"AIza[0-9A-Za-z_-]{20,}",
    r"ghp_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----",
    r"(?i)alek[_ -]?password\s*[:=]\s*[^\s#]{8,}",
)
FORBIDDEN_TEXT_PATTERNS = tuple(re.compile(pattern) for pattern in PATTERN_TEXTS)
FORBIDDEN_BINARY_PATTERNS = tuple(pattern.encode("ascii") for pattern in (
    "sk-or-v1-",
    "ghp_",
    "github_pat_",
    "AIza",
    "-----BEGIN",
))


def scan_source(path: Path, violations: list[str]) -> None:
    if path == Path(__file__).resolve():
        return
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    for pattern in FORBIDDEN_TEXT_PATTERNS:
        if pattern.search(content):
            violations.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")


def scan_binary(path: Path, violations: list[str]) -> None:
    try:
        content = path.read_bytes()
    except OSError:
        return
    for marker in FORBIDDEN_BINARY_PATTERNS:
        if marker in content:
            violations.append(f"{path.relative_to(ROOT)}: binary marker {marker!r}")


def main() -> int:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in TEXT_EXTENSIONS:
                scan_source(path, violations)
            elif path.suffix in BINARY_EXTENSIONS:
                scan_binary(path, violations)

    if violations:
        print("Обнаружены признаки секретов:")
        print("\n".join(violations))
        return 1

    print("Android security smoke: признаков hardcoded credentials/private keys не найдено.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
