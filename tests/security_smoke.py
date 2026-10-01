from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SOURCE_ROOTS = [ROOT / "src", ROOT / "tests", ROOT / "schemas"]
TEXT_EXTENSIONS = {
    ".py", ".json", ".md", ".txt", ".yml", ".yaml", ".toml",
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


def scan_text_file(path: Path, violations: list[str]) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    for pattern in SOURCE_PATTERNS:
        if pattern.search(content):
            violations.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")


def main() -> int:
    violations: list[str] = []
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in TEXT_EXTENSIONS:
                scan_text_file(path, violations)

    if violations:
        print("Обнаружены признаки секретов:")
        print("\n".join(violations))
        return 1

    print("Core security smoke: credential-паттернов не найдено.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
