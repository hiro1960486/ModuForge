"""ModuForge root layout migration: default is READ-ONLY inspection.

Examples:
  python scripts/restructure_safe.py
  python scripts/restructure_safe.py --stage

--stage copies files into a NEW sibling directory; never deletes or overwrites
repository files. It intentionally does not merge to main or rewrite .bat paths.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

COMPONENTS = ("00_shared", "01_tree", "02_rename", "03_preview",
              "04_compare", "05_hash", "06_recycle", "07_tags", "08_organizer")
SKIP_NAMES = {".git", ".venv", "venv", "__pycache__", ".pytest_cache",
              "test_output", "build", "dist"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".log", ".tmp", ".bak", ".zip"}
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "FW33"

def excluded(path: Path) -> bool:
    return any(part in SKIP_NAMES for part in path.parts) or path.suffix.lower() in SKIP_SUFFIXES

def destinations() -> dict[Path, Path]:
    """Determine intended paths without altering repository files."""
    if not SOURCE.is_dir():
        raise FileNotFoundError("FW33/ was not found: " + str(SOURCE))
    mapping: dict[Path, Path] = {}
    for source in SOURCE.rglob("*"):
        if not source.is_file() or excluded(source.relative_to(SOURCE)):
            continue
        rel = source.relative_to(SOURCE)
        if rel.parts[0] in COMPONENTS:
            dest = rel
        elif rel.parts[0] in {"tests", "scripts"}:
            dest = rel
        elif rel.suffix.lower() in {".bat", ".cmd"}:
            dest = Path("scripts") / rel.name
        elif rel.name in {"run_tests.py", "run_component.py", "requirements.txt"}:
            dest = Path(rel.name)
        else:
            dest = Path("migration_review") / rel
        if dest in mapping.values():
            raise RuntimeError("Duplicate destination: " + str(dest))
        mapping[source] = dest
    return mapping

def inspect(mapping: dict[Path, Path]) -> list[str]:
    conflicts = []
    for src, dest in mapping.items():
        existing = ROOT / dest
        if existing.exists() and existing.read_bytes() != src.read_bytes():
            conflicts.append(f"{src.relative_to(ROOT)} -> {dest}")
    return conflicts

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", action="store_true",
                        help="Copy to new sibling folder (never change originals)")
    args = parser.parse_args()
    mapping = destinations()
    conflicts = inspect(mapping)
    summary = {"source": str(SOURCE), "files": len(mapping),
               "conflicts": conflicts, "mode": "stage" if args.stage else "inspect"}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if conflicts:
        print("STOP: existing destination content differs. Resolve before staging.")
        return 2
    if not args.stage:
        print("Read-only inspection complete. Use --stage after review.")
        return 0

    target = ROOT.parent / (ROOT.name + "_staging")
    if target.exists():
        print("STOP: staging directory exists; never overwrite: " + str(target))
        return 3
    target.mkdir()
    try:
        # Retain root metadata and documents; skip source subtree and generated files.
        for item in ROOT.iterdir():
            if item.name in {"FW33", ".git"} or item.name in SKIP_NAMES:
                continue
            dst = target / item.name
            if item.is_dir():
                shutil.copytree(item, dst, ignore=shutil.ignore_patterns(*SKIP_NAMES))
            elif item.is_file() and not excluded(Path(item.name)):
                shutil.copy2(item, dst)
        for source, rel in mapping.items():
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.read_bytes() != source.read_bytes():
                raise RuntimeError("Staging destination collision: " + str(dest))
            shutil.copy2(source, dest)
        (target / "MIGRATION_REVIEW_REQUIRED.txt").write_text(
            "NOT READY TO MERGE. Review BAT relative paths, imports, "
            "license, dependencies, and test results on Windows. "
            "Original FW33 is preserved in the source repository.\n",
            encoding="utf-8")
    except Exception:
        print("Staging incomplete; inspect manually: " + str(target))
        raise
    print("Created staging copy: " + str(target))
    print("No repository files deleted or modified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
