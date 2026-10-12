"""Windows GUI smoke tests for all eight flat-layout components.

Creates each widget with Qt offscreen, but does not click controls, select
user files, restore Recycle Bin entries, or initiate file operations.
Run: python scripts/smoke_root_gui.py
"""
from __future__ import annotations
import importlib
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Script launched from scripts/: make root-level run_component importable.
sys.path.insert(0, str(ROOT))
MODULES = ("tree", "rename", "preview", "compare", "hash",
           "recycle", "tags", "organizer")

def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QImage, QColor
    from run_component import assemble

    app = QApplication.instance() or QApplication(["ModuForge smoke"])
    outcomes = []
    # Isolated composition for each module; never touch actual user file data.
    for name in MODULES:
        port = widget = None
        try:
            with tempfile.TemporaryDirectory(prefix="moduforge_gui_smoke_") as temp:
                source = assemble(ROOT, Path(temp), name)
                sys.path.insert(0, str(source))
                try:
                    api = importlib.import_module(f"fileworkbench.modules.{name}.interface")
                    port = getattr(api, name.capitalize() + "Interface")()
                    widget = port.create_widget()
                    if widget is None:
                        raise AssertionError("create_widget returned None")
                    widget.show()
                    app.processEvents()
                    if name == "preview":
                        image_file = Path(temp) / "acceptance_image.png"
                        image = QImage(320, 180, QImage.Format_RGB32)
                        image.fill(QColor("skyblue"))
                        if not image.save(str(image_file), "PNG"):
                            raise AssertionError("Could not generate PNG fixture")
                        widget.input_paths([str(image_file)])
                        app.processEvents()
                        if widget._image_pixmap is None or widget.image_label.pixmap().isNull():
                            raise AssertionError("PNG image not rendered in Qt image widget")
                        if widget.btn_play.isEnabled():
                            raise AssertionError("Playback button must be disabled for image")
                    widget.close()
                    app.processEvents()
                    outcomes.append({"module": name, "result": "PASS"})
                finally:
                    if widget is not None:
                        widget.close()
                    if port is not None:
                        port.shutdown()
                    sys.path.remove(str(source))
                    # Components are deliberately loaded from separate temp copies.
                    for key in list(sys.modules):
                        if key == "fileworkbench" or key.startswith("fileworkbench."):
                            del sys.modules[key]
        except Exception as exc:
            outcomes.append({"module": name, "result": "FAIL",
                             "error": str(exc), "trace": traceback.format_exc()})
    print(json.dumps(outcomes, ensure_ascii=False, indent=2))
    return 0 if all(o["result"] == "PASS" for o in outcomes) else 1

if __name__ == "__main__":
    sys.exit(main())
