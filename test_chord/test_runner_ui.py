"""Compatibility wrapper for the central tests/gui runner."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[1] / "tests" / "gui" / "test_runner_ui.py"), run_name="__main__")
