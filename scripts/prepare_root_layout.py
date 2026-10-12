"""Safely prepare ModuForge's flat layout in a checked-out *work branch*.

Default mode is dry-run. --apply ONLY COPIES files: it never removes FW33,
overwrites an existing different file, or modifies main/other branches.

Usage:
    python scripts/prepare_root_layout.py
    python scripts/prepare_root_layout.py --apply
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "FW33"
PARTS = {"00_shared", "01_tree", "02_rename", "03_preview", "04_compare",
         "05_hash", "06_recycle", "07_tags", "08_organizer"}
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv",
                "test_output", "build", "dist"}
EXCLUDE_EXT = {".pyc", ".pyo", ".log", ".tmp", ".bak", ".zip"}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def branch_name() -> str:
    p = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT,
                       capture_output=True, text=True, check=True)
    return p.stdout.strip()

def mapping() -> dict[Path, Path]:
    if not SOURCE.is_dir():
        raise RuntimeError("Missing FW33 source")
    result: dict[Path, Path] = {}
    for src in sorted(SOURCE.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(SOURCE)
        if any(segment in EXCLUDE_DIRS for segment in rel.parts) or src.suffix.lower() in EXCLUDE_EXT:
            continue
        if rel.parts[0] in PARTS:
            dest = rel
        elif rel.parts[0] in {"tests", "scripts", "sample_data"}:
            dest = rel
        elif rel.parts[0] == "docs":
            dest = Path("docs") / "legacy_fw33" / Path(*rel.parts[1:])
        elif rel.parts[0] == "test_chord":
            dest = rel  # Preserve subfolder and relative imports.
        elif rel.name in {"run_tests.py", "run_component.py", "requirements.txt"}:
            dest = Path(rel.name)
        elif rel.suffix.lower() in {".bat", ".cmd"}:
            dest = Path("scripts") / rel.name
        else:
            dest = Path("migration_review") / rel
        if dest in result.values():
            raise RuntimeError("Duplicate destination: " + str(dest))
        result[src] = dest
    return result

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    branch = branch_name()
    if branch != "refactor/safe-root-layout":
        raise RuntimeError("Refusing migration outside refactor/safe-root-layout: " + branch)
    result = mapping()
    conflicts = [
        {"from": str(src.relative_to(ROOT)), "to": str(dest)}
        for src, dest in result.items()
        if (ROOT / dest).exists() and sha(src) != sha(ROOT / dest)
    ]
    print(json.dumps({"branch": branch, "files": len(result), "conflicts": conflicts,
                      "mode": "apply" if args.apply else "inspect"}, ensure_ascii=False, indent=2))
    if conflicts:
        print("STOP: conflicting destinations were found. Nothing copied.")
        return 2
    if not args.apply:
        return 0
    # A second pre-flight guard: concurrent branch modifications should not be silently hidden.
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                            capture_output=True, text=True, check=True)
    if status.stdout.strip():
        print("STOP: working tree is not clean. Nothing copied.")
        return 3
    for src, dest in result.items():
        target = ROOT / dest
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    print("Copied new layout without removing FW33. Review and test BEFORE commit.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
