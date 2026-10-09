import sys
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLabel, QTextEdit, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QProcess

# パス設定
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parents[1]
RUN_COMPONENT_SCRIPT = ROOT_DIR / "run_component.py"

# ログディレクトリ設定
LOG_DIR = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / ".local/share")) / "FileWorkbenchNext" / "logs" / "test_gui"
LOG_DIR.mkdir(parents=True, exist_ok=True)

SESSION_START_TIME = datetime.now().strftime("%Y%m%d_%H%M%S")
SESSION_LOG_FILE = LOG_DIR / f"test_session_{SESSION_START_TIME}.log"


class ModuleAutoHarness(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileWorkbench - 単独モジュール動作検証UI (Test Runner)")
        self.resize(1000, 700)

        self.process = None
        self._init_ui()
        
        self.log(f"=== テストハーネス起動: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        self.log(f"[ログファイル] {SESSION_LOG_FILE}")
        self.log(f"[プロジェクトルート] {ROOT_DIR}")
        self.log(f"[起動基盤] {RUN_COMPONENT_SCRIPT}")
        
        self._refresh_modules()

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        root_layout = QVBoxLayout(main_widget)

        # 操作コントロールバー
        ctrl_group = QGroupBox("モジュール単独実行 & 検証設定")
        ctrl_layout = QHBoxLayout(ctrl_group)

        ctrl_layout.addWidget(QLabel("検証対象モジュール:"))
        self.module_combo = QComboBox()
        self.module_combo.setMinimumWidth(220)
        ctrl_layout.addWidget(self.module_combo)

        refresh_btn = QPushButton("フォルダ再検出")
        refresh_btn.clicked.connect(self._refresh_modules)
        ctrl_layout.addWidget(refresh_btn)

        ctrl_layout.addSpacing(15)

        self.launch_btn = QPushButton("単独起動 (Run)")
        self.launch_btn.setStyleSheet(
            "font-weight: bold; background-color: #0284c7; color: white; padding: 6px 16px; border-radius: 4px;"
        )
        self.launch_btn.clicked.connect(self._launch_component)
        ctrl_layout.addWidget(self.launch_btn)

        self.stop_btn = QPushButton("プロセス停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(
            "font-weight: bold; background-color: #dc2626; color: white; padding: 6px 12px; border-radius: 4px;"
        )
        self.stop_btn.clicked.connect(self._stop_process)
        ctrl_layout.addWidget(self.stop_btn)

        root_layout.addWidget(ctrl_group)

        # ログコンソール
        log_group = QGroupBox(f"リアルタイム動作・出力ログ ({SESSION_LOG_FILE.name})")
        log_layout = QVBoxLayout(log_group)
        
        log_btn_layout = QHBoxLayout()
        clear_view_btn = QPushButton("画面クリア")
        clear_view_btn.clicked.connect(self._clear_screen_log)

        clear_files_btn = QPushButton("過去ログファイル削除")
        clear_files_btn.clicked.connect(self._clear_saved_logs)

        open_log_folder_btn = QPushButton("ログフォルダを開く")
        open_log_folder_btn.clicked.connect(self._open_log_folder)

        log_btn_layout.addStretch()
        log_btn_layout.addWidget(clear_view_btn)
        log_btn_layout.addWidget(clear_files_btn)
        log_btn_layout.addWidget(open_log_folder_btn)
        log_layout.addLayout(log_btn_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "background-color: #18181b; color: #a1a1aa; font-family: Consolas, monospace; font-size: 13px;"
        )
        log_layout.addWidget(self.log_text)

        root_layout.addWidget(log_group)

    def log(self, text: str):
        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        formatted_line = f"{timestamp}{text}"
        self.log_text.append(formatted_line)
        try:
            with open(SESSION_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted_line + "\n")
        except Exception:
            pass

    def _clear_screen_log(self):
        self.log_text.clear()

    def _clear_saved_logs(self):
        reply = QMessageBox.question(
            self,
            "ログ削除確認",
            "test_log フォルダ内の古いログファイルをすべて削除しますか？\n（現在のセッションログ以外が削除されます）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            for log_file in LOG_DIR.glob("*.log"):
                if log_file.resolve() != SESSION_LOG_FILE.resolve():
                    try:
                        log_file.unlink()
                        deleted_count += 1
                    except Exception:
                        pass
            self.log(f"[システム] 過去ログファイル {deleted_count} 件を削除しました。")

    def _open_log_folder(self):
        if sys.platform == "win32":
            os.startfile(str(LOG_DIR))

    def _refresh_modules(self):
        self.module_combo.clear()
        pattern = re.compile(r"^(\d{2})_(.+)$")

        entries = []
        for p in ROOT_DIR.iterdir():
            if p.is_dir() and pattern.match(p.name) and p.name != "00_shared":
                match = pattern.match(p.name)
                short_name = match.group(2)
                entries.append((p, short_name))

        entries.sort(key=lambda x: x[0].name)
        for folder, short_name in entries:
            label = f"{folder.name} [{short_name}]"
            self.module_combo.addItem(label, userData=short_name)

        self.log(f"[システム] 親階層から {len(entries)} 個のモジュールを検出しました。")

    def _launch_component(self):
        mod_key = self.module_combo.currentData()
        if not mod_key:
            return

        if not RUN_COMPONENT_SCRIPT.exists():
            self.log(f"[エラー] {RUN_COMPONENT_SCRIPT} が見つかりません。")
            return

        if self.process and self.process.state() == QProcess.ProcessState.Running:
            QMessageBox.warning(self, "警告", "既に別のモジュールが実行中です。停止してから再実行してください。")
            return

        self.log("=" * 60)
        self.log(f"[起動リクエスト] python run_component.py {mod_key}")

        self.process = QProcess(self)
        self.process.setWorkingDirectory(str(ROOT_DIR))
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._process_finished)

        python_exe = sys.executable
        self.process.start(python_exe, [str(RUN_COMPONENT_SCRIPT), mod_key])

        self.launch_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.log(f"[プロセス開始] PID: {self.process.processId()} で '{mod_key}' を起動中...")

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        for line in data.strip().splitlines():
            self.log(f"[STDOUT] {line}")

    def _handle_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        for line in data.strip().splitlines():
            self.log(f"[STDERR] {line}")

    def _stop_process(self):
        """プロセスおよび関連子プロセス（FFmpeg/マルチメディア関連）を完全終了"""
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            pid = self.process.processId()
            self.log(f"[停止命令] PID: {pid} のプロセスツリーを強制終了します...")

            if sys.platform == "win32" and pid > 0:
                # Windowsの taskkill /F /T で子孫プロセスごと完全終了
                try:
                    subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"], capture_output=True)
                except Exception as e:
                    self.log(f"[警告] taskkill 実行エラー: {e}")

            # QProcess 側の終了
            self.process.kill()
            self.process.waitForFinished(1000)

            # UI ボタン状態を確実に復帰
            self.launch_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.log("[停止完了] プロセスを停止しました。")

    def _process_finished(self, exit_code, exit_status):
        self.log(f"[プロセス終了] 終了コード: {exit_code}")
        self.launch_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        self._stop_process()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = ModuleAutoHarness()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()