"""Validate staging layout without touching the original repository."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = ("00_shared", "01_tree", "02_rename", "03_preview", "04_compare",
         "05_hash", "06_recycle", "07_tags", "08_organizer")
ESSENTIAL = ("run_component.py", "run_tests.py", "requirements.txt")

def main():
    stage = ROOT.parent / (ROOT.name + "_staging")
    errors = []
    if not stage.is_dir():
        errors.append("Staging directory missing")
    else:
        for name in (*PARTS, *ESSENTIAL):
            if not (stage / name).exists():
                errors.append("Missing in staging: " + name)
        if (stage / ".git").exists():
            errors.append("Staging must not copy .git")
        if (stage / "FW33").exists():
            errors.append("Staging must not contain FW33")
        for folder in stage.rglob("__pycache__"):
            errors.append("Cache retained: " + str(folder.relative_to(stage)))
    print(json.dumps({"stage": str(stage), "errors": errors}, ensure_ascii=False, indent=2))
    if errors:
        return 1
    result = subprocess.run([sys.executable, str(stage / "run_tests.py")], cwd=stage, timeout=240)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
