"""Verify that the flattened tree preserves every FW33 source file.

Read-only: does not delete, copy or modify any file.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "FW33"
MODULES = {"00_shared","01_tree","02_rename","03_preview","04_compare",
           "05_hash","06_recycle","07_tags","08_organizer"}
EXCLUDED_DIRS = {".git","__pycache__",".pytest_cache",".venv","venv",
                 "test_output","build","dist"}
EXCLUDED_EXTS = {".pyc",".pyo",".log",".tmp",".bak",".zip"}
MODIFIED_DOCS = {"run_tests.py","tests/README.md", "03_preview/module/module.py", "03_preview/api/interface.py"}  # Updated to document the new root test entrypoint.
MODIFIED_BATS = {"run_tags.bat","run_organizer.bat","test_tags.bat",
                 "test_organizer.bat","test_all.bat"}

def destination(relative):
    parts = relative.parts
    if parts[0] in MODULES or parts[0] in {"tests","scripts","sample_data","test_chord"}:
        return relative
    if parts[0] == "docs":
        return Path("docs/legacy_fw33", *parts[1:])
    if relative.name in {"run_tests.py","run_component.py","requirements.txt"}:
        return Path(relative.name)
    if relative.suffix.lower() in {".bat",".cmd"}:
        return Path("scripts") / relative.name
    return Path("migration_review") / relative

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    errors, intentional, reviewed = [], [], []
    count = 0
    for src in sorted(SOURCE.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(SOURCE)
        if any(s in EXCLUDED_DIRS for s in rel.parts) or rel.suffix.lower() in EXCLUDED_EXTS:
            continue
        count += 1
        dest = destination(rel)
        new_file = ROOT / dest
        if not new_file.is_file():
            errors.append("Missing: " + str(dest))
        elif digest(src) != digest(new_file):
            if src.name in MODIFIED_BATS and dest == Path("scripts") / src.name:
                intentional.append(dest.as_posix())
                script = new_file.read_text(encoding="utf-8-sig")
                if "%~dp0.." not in script or "run_" not in src.name and "run_tests.py" not in script:
                    errors.append("Invalid migrated BAT: " + str(dest))
            elif dest.as_posix() in MODIFIED_DOCS:
                # Preserve the old document under FW33 while updating canonical docs.
                pass
            else:
                errors.append("Unexpected difference: " + str(dest))
        if dest.parts[0] == "migration_review":
            reviewed.append(str(dest))
    if set(intentional) != {"scripts/" + x for x in MODIFIED_BATS}:
        errors.append("Expected BAT differences not all present: " + repr(intentional))
    print(json.dumps({"files": count, "expected_bat_differences": intentional,
                      "manual_review_files": reviewed, "errors": errors},
                     ensure_ascii=False, indent=2))
    return 1 if errors or count != 133 else 0

if __name__ == "__main__":
    sys.exit(main())
