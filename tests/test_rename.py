"""Rename safety checks using disposable files and an isolated recovery store."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '00_shared/src'))
from fileworkbench.services.naming import RenameRules, build_plan
from fileworkbench.services.file_operations import FileOperationsService


class RenameSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='moduforge_rename_')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.data = self.base / 'data'
        self.data.mkdir()
        self.source = self.data / '写真.txt'
        self.source.write_bytes(b'original content\n')
        self.service = FileOperationsService(self.base / 'recovery', trash_backend=self.reject_trash)

    def reject_trash(self, path):
        self.fail('Rename must not access the real Recycle Bin')

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.data.iterdir() if p.is_file()}

    def test_preview_preserves_files(self):
        before = self.snapshot()
        rows = build_plan([self.source], RenameRules(prefix='new_'))
        self.assertEqual(rows[0][1].name, 'new_写真.txt')
        self.assertEqual(rows[0][2], 'OK')
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.service.history(), [])

    def test_invalid_windows_names_rejected(self):
        for name in ('CON.txt', 'bad?.txt', 'bad .', 'bad.', 'NUL.txt'):
            with self.subTest(name=name):
                result = self.service.rename_many([(self.source, self.data / name)])[0]
                self.assertEqual(result.status, '失敗')
                self.assertTrue(self.source.exists())
        self.assertEqual(self.service.history(), [])

    def test_preview_duplicate_targets_are_unique(self):
        other = self.data / '別.txt'
        other.write_bytes(b'other')
        rows = build_plan([self.source, other], RenameRules(find='.*', replacement='same', regex=True))
        self.assertEqual(len({str(row[1]).casefold() for row in rows}), 2)
        self.assertTrue(any(row[2] == '自動回避' for row in rows))

    def test_collision_preserves_both_contents(self):
        target = self.data / 'existing.txt'
        target.write_bytes(b'keep existing')
        before = self.snapshot()
        result = self.service.rename_many([(self.source, target)])[0]
        self.assertEqual(result.status, '失敗')
        self.assertEqual(self.snapshot(), before)

    def test_cancel_before_start_is_unchanged(self):
        before = self.snapshot()
        self.assertEqual(self.service.rename_many([(self.source, self.data / 'new.txt')], lambda: True), [])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.service.history(), [])

    def test_success_matches_preview_and_backup(self):
        row = build_plan([self.source], RenameRules(prefix='new_'))[0]
        payload = self.source.read_bytes()
        result = self.service.rename_many([(row[0], row[1])])[0]
        self.assertEqual(result.status, '成功')
        self.assertFalse(self.source.exists())
        self.assertEqual(row[1].read_bytes(), payload)
        entry = self.service.history()[0]
        self.assertEqual(Path(entry['backup']).read_bytes(), payload)
        self.assertEqual(entry['state'], 'リネーム済み')

    def test_unchanged_name_has_no_backup(self):
        result = self.service.rename_many([(self.source, self.source)])[0]
        self.assertEqual(result.status, '変更なし')
        self.assertEqual(self.service.history(), [])
        self.assertEqual(self.source.read_bytes(), b'original content\n')

    def test_cross_directory_rejected(self):
        other = self.base / 'other'
        other.mkdir()
        result = self.service.rename_many([(self.source, other / 'new.txt')])[0]
        self.assertEqual(result.status, '失敗')
        self.assertTrue(self.source.exists())
        self.assertEqual(list(other.iterdir()), [])

    def test_missing_source_rejected(self):
        result = self.service.rename_many([(self.data / 'missing.txt', self.data / 'new.txt')])[0]
        self.assertEqual(result.status, '失敗')
        self.assertFalse((self.data / 'new.txt').exists())

    def test_symlink_source_rejected(self):
        link = self.data / 'link.txt'
        try:
            link.symlink_to(self.source)
        except OSError as exc:
            self.skipTest(str(exc))
        result = self.service.rename_many([(link, self.data / 'new.txt')])[0]
        self.assertEqual(result.status, '失敗')
        self.assertTrue(link.is_symlink())
        self.assertTrue(self.source.exists())

    def test_cancel_between_files_keeps_remaining_source(self):
        other = self.data / 'other.txt'
        other.write_bytes(b'other')
        calls = iter((False, True))
        result = self.service.rename_many([(self.source, self.data / 'new.txt'), (other, self.data / 'new_other.txt')], lambda: next(calls))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].status, '成功')
        self.assertEqual(other.read_bytes(), b'other')
        self.assertFalse((self.data / 'new_other.txt').exists())

    def test_rename_failure_keeps_source_and_backup(self):
        with patch('fileworkbench.core.safety.no_replace', side_effect=OSError('injected failure')):
            result = self.service.rename_many([(self.source, self.data / 'new.txt')])[0]
        self.assertEqual(result.status, '失敗')
        self.assertTrue(self.source.exists())
        self.assertFalse((self.data / 'new.txt').exists())
        self.assertEqual(Path(self.service.history()[0]['backup']).read_bytes(), self.source.read_bytes())

    def test_restore_backup_preserves_renamed_file(self):
        target = self.data / 'new.txt'
        result = self.service.rename_many([(self.source, target)])[0]
        restored = self.service.restore_backup(result.history_id)
        self.assertEqual(restored.status, '成功')
        self.assertEqual(self.source.read_bytes(), target.read_bytes())

    def test_restore_collision_does_not_overwrite(self):
        result = self.service.rename_many([(self.source, self.data / 'new.txt')])[0]
        self.source.write_bytes(b'new occupant')
        restored = self.service.restore_backup(result.history_id)
        self.assertEqual(self.source.read_bytes(), b'new occupant')
        self.assertNotEqual(Path(restored.target), self.source)
        self.assertEqual(Path(restored.target).read_bytes(), b'original content\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
