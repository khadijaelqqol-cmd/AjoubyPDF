#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copy the built installers into release/installers and write SHA256SUMS.txt.

Run after scripts\\build_installers.bat:

    python scripts\\package_release.py
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "dist" / "installers"
DST = ROOT / "release" / "installers"
CHECKSUMS = ROOT / "release" / "SHA256SUMS.txt"

INSTALLERS = (
    ("AjoubyPDF_Setup_win10.exe", "Windows 10/11 (64-bit)"),
    ("AjoubyPDF_Setup_win7.exe", "Windows 7/8 (64-bit + SP1)"),
)


def app_version() -> str:
    text = (ROOT / "ajoubi" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else "unknown"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human_size(size: int) -> str:
    return "%.1f MB" % (size / 1_000_000)


def main() -> int:
    version = app_version()
    missing = [name for name, _ in INSTALLERS if not (SRC / name).is_file()]
    if missing:
        print("Missing installer(s) in dist\\installers:")
        for name in missing:
            print("  - " + name)
        print("\nRun scripts\\build_installers.bat first.")
        return 1

    DST.mkdir(parents=True, exist_ok=True)
    lines = []
    print("Ajouby PDF %s - release assets\n" % version)

    for name, target in INSTALLERS:
        source = SRC / name
        destination = DST / name
        shutil.copy2(source, destination)
        digest = sha256(destination)
        size = destination.stat().st_size
        lines.append("%s  %s" % (digest, name))
        print("  %-32s %10s  %s" % (name, human_size(size), target))

    with CHECKSUMS.open("w", encoding="ascii", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")

    print("\nChecksums: release\\SHA256SUMS.txt")
    print(
        "\nPublish on GitHub:\n"
        "  1. Open the repository -> Releases -> Draft a new release\n"
        "  2. Tag: v%s   Title: Ajouby PDF %s\n"
        "  3. Attach both .exe files from release\\installers\\\n"
        "  4. Paste SHA256SUMS.txt into the release notes\n"
        "  5. Publish\n\n"
        "Do not commit the .exe files: they belong in GitHub Releases.\n"
        "See release\\README.md for details." % (version, version)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
