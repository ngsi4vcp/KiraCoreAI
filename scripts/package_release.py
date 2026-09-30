from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tarfile
import zipfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True)
    parser.add_argument("--platform", choices=("windows", "linux"), required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    version = (root / "VERSION.txt").read_text(encoding="utf-8").strip()
    package_name = f"KiraCoreAI-{version}-{args.platform}-x64"
    stage = root / "release" / package_name
    stage.mkdir(parents=True, exist_ok=True)

    binary = Path(args.binary)
    binary_name = "START.exe" if args.platform == "windows" else "START"
    shutil.copy2(binary, stage / binary_name)

    (stage / "GENOME").mkdir()
    shutil.copy2(root / "GENOME" / "genome.txt", stage / "GENOME" / "genome.txt")

    (stage / "SECRETS").mkdir()
    shutil.copy2(
        root / "SECRETS" / "credentials.example.ini",
        stage / "SECRETS" / "credentials.example.ini",
    )

    for filename in ("VERSION.txt", "README_FIRST.txt"):
        shutil.copy2(root / filename, stage / filename)

    if args.platform == "windows":
        archive_path = root / "release" / f"{package_name}.zip"
        with zipfile.ZipFile(
            archive_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for path in stage.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(root / "release"))
    else:
        archive_path = root / "release" / f"{package_name}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as archive:
            archive.add(stage, arcname=stage.name)

    print(archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
