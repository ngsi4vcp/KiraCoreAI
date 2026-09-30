from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
SKIP_DIRS = {
    ".git", ".gradle", ".idea", "__pycache__", "build", "dist", "node_modules",
}
TEXT_EXTENSIONS = {
    ".cfg", ".gradle", ".gradle.kts", ".ini", ".java", ".json", ".jsonl",
    ".kt", ".md", ".properties", ".pro", ".py", ".schema", ".toml", ".txt",
    ".xml", ".yaml", ".yml",
}

def iter_text_files():
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            yield path

def main() -> int:
    violations: list[str] = []
    for path in iter_text_files():
        data = path.read_bytes()
        relative = path.relative_to(ROOT)
        if data.startswith(b'\xef\xbb\xbf'):
            violations.append(f'{relative}: UTF-8 BOM')
            continue
        try:
            data.decode('utf-8', errors='strict')
        except UnicodeDecodeError as error:
            violations.append(f'{relative}: invalid UTF-8 at byte {error.start}')
    if violations:
        print('UTF-8 smoke: обнаружены нарушения:')
        print('\n'.join(violations))
        return 1
    print('UTF-8 smoke: все контролируемые текстовые файлы — UTF-8 без BOM.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())