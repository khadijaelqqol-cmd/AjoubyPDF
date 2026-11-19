#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a clean source archive for uploading the project to GitHub.

The archive contains only the files that belong in the repository: source,
docs, tests, installer scripts and release metadata. Build folders
(build/, dist/, Python38/) and the installer EXEs are excluded, matching
.gitignore.

Run from the project root:

    python scripts\\make_source_zip.py

The archive is written to dist\\AjoubyPDF-<version>-source.zip.
"""

from __future__ import annotations

import fnmatch
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "dist"

SKIP_DIRS = {".git", "build", "dist", "Python38", "__pycache__",
             ".venv", "venv", "env"}
SKIP_FILES = ("*.pyc", "*.pyo", "*.spec", "*.log", ".DS_Store",
              "Thumbs.db", "Desktop.ini", "~$*")
SKIP_PREFIXES = ("release/installers/",)


def app_version() -> str:
    text = (ROOT / "ajoubi" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else "unknown"


def wanted(relative: str, name: str) -> bool:
    if any(fnmatch.fnmatch(name, pattern) for pattern in SKIP_FILES):
        return False
    if relative.startswith(SKIP_PREFIXES):
        return not name.lower().endswith((".exe", ".zip"))
    return True


def collect() -> list:
    files = []
    for base, dirs, names in os.walk(ROOT):
        rel_base = os.path.relpath(base, ROOT).replace("\\", "/")
        dirs[:] = sorted(d for d in dirs
                         if d not in SKIP_DIRS and not d.startswith("tmp"))
        for name in sorted(names):
            relative = (rel_base + "/" + name) if rel_base != "." else name
            if wanted(relative, name):
                files.append(relative)
    return files


def main() -> int:
    version = app_version()
    files = collect()
    if not files:
        print("No files found - are you running from the project root?")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archive = OUTPUT_DIR / ("AjoubyPDF-%s-source.zip" % version)
    prefix = "AjoubyPDF-%s/" % version

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for relative in files:
            bundle.write(ROOT / relative, prefix + relative)

    size = archive.stat().st_size
    print("Source archive: %s" % archive)
    print("Files: %d   Size: %.1f MB" % (len(files), size / 1_000_000))
    print("\nUpload it to GitHub with:")
    print("  1. Unzip the archive.")
    print("  2. Drag the contents of the %s folder into the repository." % prefix.rstrip("/"))
    print("  3. Do not delete .gitignore - it keeps build folders out of Git.")
    print("\nInstallers are not inside this archive; attach them to a")
    print("GitHub Release instead (see release\\README.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
