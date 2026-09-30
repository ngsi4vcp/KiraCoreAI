from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCAN_ROOTS = [ROOT / "android", ROOT / "src", ROOT / "tests", ROOT / "schemas", ROOT / "android" / "app" / "build"]
FORBIDDEN_PATTERNS = (
    re.compile(r"sk-or-v1-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    re.compile(r"(?i)alek[_ -]?password\s*[:=]\s*[^\s#]{8,}"),
)

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


def main() -> int:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(content):
                    violations.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")

    if violations:
        print("Обнаружены признаки секретов:")
        print("\n".join(violations))
        return 1

    print("Android security smoke: признаков hardcoded credentials/private keys не найдено.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
