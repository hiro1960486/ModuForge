"""分離した研究用ソースを一時領域へ組み立てて単独起動する。"""
import argparse
import importlib
import shutil
import sys
import tempfile
from pathlib import Path


def assemble(root, destination, module_id):
    # 共通パッケージと素材をコピーし、元の相対importを維持する。
    shutil.copytree(root / '00_shared/src', destination / 'src')
    shutil.copytree(root / '00_shared/assets', destination / 'src/assets')
    folders = list(root.glob('[0-9][0-9]_' + module_id))
    if len(folders) != 1:
        raise ValueError('部品フォルダーを特定できません: ' + module_id)
    target = destination / 'src/fileworkbench/modules' / module_id
    # 実装とAPIを元のPythonパッケージ内へ組み直す。
    shutil.copytree(folders[0] / 'module', target)
    shutil.copytree(folders[0] / 'api', target, dirs_exist_ok=True)
    return destination / 'src'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('module', choices=('tree','rename','preview','compare','hash','recycle','tags','organizer'))
    args = parser.parse_args()
    # 一時ソースは終了後に消える。部品原本には変更を加えない。
    with tempfile.TemporaryDirectory(prefix='fileworkbench_part_') as work:
        src = assemble(Path(__file__).resolve().parent, Path(work), args.module)
        sys.path.insert(0, str(src))
        from PySide6.QtWidgets import QApplication
        app = QApplication([sys.argv[0]])
        module = importlib.import_module('fileworkbench.modules.' + args.module + '.interface')
        port = getattr(module, args.module.capitalize() + 'Interface')()
        widget = port.create_widget()
        widget.show()
        app.aboutToQuit.connect(port.shutdown)
        return app.exec()


if __name__ == '__main__':
    sys.exit(main())
