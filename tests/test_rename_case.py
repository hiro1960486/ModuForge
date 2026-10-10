"""Exercise Windows path equality on every host without touching real trash."""
import sys
import unittest
from pathlib import Path, PureWindowsPath
from unittest.mock import patch, Mock
from threading import RLock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '00_shared/src'))
from fileworkbench.services import naming, file_operations
from fileworkbench.core import safety

class WindowsFile(PureWindowsPath):
    def absolute(self): return self
    def exists(self): return False
    def is_file(self): return True
    def is_symlink(self): return False
    def rename(self, target): moves.append((str(self), str(target)))

moves = []

class RenameCaseTests(unittest.TestCase):
    def test_windows_preview_detects_case_changes(self):
        source = WindowsFile('C:/test/sample_A.txt')
        self.assertEqual(source, WindowsFile('C:/test/sample_a.txt'))
        with patch.object(naming, 'Path', WindowsFile):
            for mode, expected in [('lower', 'sample_a.txt'), ('upper', 'SAMPLE_A.txt'), ('title', 'Sample_A.txt')]:
                row = naming.build_plan([source], naming.RenameRules(letter_case=mode))[0]
                self.assertEqual(row[1].name, expected)
                self.assertEqual(row[2], 'OK')
            self.assertEqual(naming.build_plan([source], naming.RenameRules())[0][2], '変更なし')

    def test_windows_service_dispatches_case_change_with_backup(self):
        service = object.__new__(file_operations.FileOperationsService)
        service.lock = RLock()
        service._backup = Mock(return_value={'id': 'case-test', 'fingerprint': 'verified'})
        service._update = Mock()
        service._record = Mock()
        with patch.object(file_operations, 'Path', WindowsFile), patch.object(file_operations, 'fingerprint', return_value='verified'), patch.object(safety, 'no_replace') as rename:
            result = service.rename_many([('C:/test/sample_A.txt', 'C:/test/sample_a.txt')])[0]
            self.assertEqual(result.status, '成功')
            service._backup.assert_called_once()
            rename.assert_called_once()

    def test_windows_case_change_uses_temporary_name(self):
        moves.clear()
        with patch.object(safety, 'Path', WindowsFile), patch.object(safety.os, 'name', 'nt'):
            safety.no_replace('C:/test/sample_A.txt', 'C:/test/sample_a.txt')
        self.assertEqual(len(moves), 2)
        self.assertEqual(moves[0][0], r'C:\test\sample_A.txt')
        self.assertEqual(moves[1][1], r'C:\test\sample_a.txt')

if __name__ == '__main__': unittest.main()
