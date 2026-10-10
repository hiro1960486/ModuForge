"""Repair BAT paths in the disposable staging copy; never modify the Git checkout.

Usage:
  python scripts/repair_staging_bat.py           # inspect only
  python scripts/repair_staging_bat.py --apply   # create backups, then fix

The wrappers call the root Python entrypoints using absolute paths based on %~dp0.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT.parent / (ROOT.name + "_staging")
COMMANDS = {
    "run_tags.bat": ("run_component.py", "tags"),
    "run_organizer.bat": ("run_component.py", "organizer"),
    "test_tags.bat": ("run_tests.py", "--module tags"),
    "test_organizer.bat": ("run_tests.py", "--module organizer"),
    "test_all.bat": ("run_tests.py", ""),
}

def expected(entry: str, arguments: str) -> str:
    return (
        '@echo off\n'
        'setlocal\n'
        'set "ROOT=%~dp0.."\n'
        'if not exist "%ROOT%\\' + entry + '" (\n'
        '  echo [ERROR] Missing ' + entry + '\n'
        '  exit /b 2\n'
        ')\n'
        'py "%ROOT%\\' + entry + '" ' + arguments + '\n'
        'set "RC=%ERRORLEVEL%"\n'
        'exit /b %RC%\n'
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not STAGE.is_dir() or (STAGE / ".git").exists() or (STAGE / "FW33").exists():
        raise RuntimeError("Expected isolated staging directory without .git or FW33")
    target = STAGE / "scripts"
    results = []
    # Check all preconditions before touching any file.
    for name, (entry, arguments) in COMMANDS.items():
        path = target / name
        if not path.is_file():
            raise FileNotFoundError(path)
        if not (STAGE / entry).is_file():
            raise FileNotFoundError(STAGE / entry)
        backup = path.with_suffix(".bat.original")
        proposed = expected(entry, arguments)
        if args.apply and backup.exists() and path.read_text(encoding="utf-8-sig") != proposed:
            raise FileExistsError("Existing backup prevents overwrite: " + str(backup))
        results.append((path, backup, proposed))
    print(json.dumps({"stage": str(STAGE), "files": [p.name for p, _, _ in results],
                      "mode": "apply" if args.apply else "inspect"}, indent=2))
    if args.apply:
        for path, backup, proposed in results:
            if path.read_text(encoding="utf-8-sig") == proposed:
                continue
            path.rename(backup)  # Preserve original BAT for comparison.
            path.write_text(proposed, encoding="utf-8", newline="\r\n")
        print("Staging launchers fixed; original copies saved as *.bat.original.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
