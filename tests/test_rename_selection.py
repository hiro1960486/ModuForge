"""Exercise actual preview/selection methods with Qt-free table doubles."""
import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def method(path, name, namespace):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    node = next(n for cls in tree.body if isinstance(cls, ast.ClassDef)
                for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(path), 'exec'), namespace)
    return namespace[name]


class Item:
    def __init__(self, text):
        self.value = text
        self.roles = {}
    def text(self): return self.value
    def setToolTip(self, text): self.tooltip = text
    def setData(self, role, value): self.roles[role] = value
    def data(self, role): return self.roles.get(role)


class Table:
    def __init__(self): self.items = {}
    def setSortingEnabled(self, value): pass
    def setRowCount(self, count): pass
    def setItem(self, row, col, item): self.items[row, col] = item
    def item(self, row, col): return self.items.get((row, col))
    def selectionModel(self): return self
    def selectedRows(self): return [SimpleNamespace(row=lambda: 0)]


class RenameSelectionTests(unittest.TestCase):
    def test_preview_stores_full_path_for_selected_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'sample_A.txt'
            source.write_text('Test A')
            target = Path(tmp) / 'new_sample_A_1.txt'
            table = Table()
            widget = SimpleNamespace(files=[source], rules=lambda: None,
                filter=SimpleNamespace(text=lambda: ''), table=table)
            namespace = {'Path': Path, 'Qt': SimpleNamespace(UserRole=256),
                         'SortableItem': Item, 'build_plan': lambda files, rules: [(source, target, '自動回避')]}
            preview = method(ROOT / '02_rename/module/module.py', 'preview', namespace)
            preview(widget)
            self.assertEqual(table.item(0, 0).text(), source.name)
            self.assertEqual(table.item(0, 0).data(256), str(source))
            select = method(ROOT / '00_shared/src/fileworkbench/ui/common.py', 'selected_table_paths', namespace)
            self.assertEqual(select(widget, table), [str(source)])
            self.assertEqual(source.read_text(), 'Test A')
