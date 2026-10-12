import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QFileDialog, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QStackedWidget, QPlainTextEdit
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from .renderers import TEXT, read_content
from ...ui import ModuleWidget
from ...core.common import app_icon, choose_folder


# ----------------------------------------------------------------------
# 1. メディア詳細情報ウィンドウ (モーダレス・動的更新対応)
# ----------------------------------------------------------------------
class MediaInfoWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("メディア詳細情報")
        self.resize(540, 380)
        self.setModal(False)

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["項目", "値"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("閉じる")
        close_btn.setStyleSheet("padding: 5px 20px;")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def update_info(self, file_path: str, player_status: str, duration_ms: int):
        p = Path(file_path) if file_path else None
        stat = p.stat() if (p and p.exists()) else None

        if duration_ms > 0:
            total_sec = duration_ms // 1000
            m, s = divmod(total_sec, 60)
            h, m = divmod(m, 60)
            dur_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        else:
            dur_str = "-"

        size_str = f"{stat.st_size / (1024 * 1024):.2f} MB ({stat.st_size:,} bytes)" if stat else "-"
        mtime_str = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S") if stat else "-"

        info_list = [
            ("ファイル名", p.name if p else "-"),
            ("拡張子 / 形式", p.suffix.upper() if p else "-"),
            ("再生状態", player_status),
            ("総再生時間", dur_str),
            ("ファイルサイズ", size_str),
            ("更新日時", mtime_str),
            ("保存場所", str(p.parent) if p else "-"),
        ]

        self.table.setRowCount(len(info_list))
        for row, (k, v) in enumerate(info_list):
            item_k = QTableWidgetItem(k)
            item_k.setFlags(item_k.flags() & ~Qt.ItemIsEditable)
            item_v = QTableWidgetItem(str(v))
            item_v.setFlags(item_v.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, item_k)
            self.table.setItem(row, 1, item_v)


# ----------------------------------------------------------------------
# 2. プレビューモジュール本体
# ----------------------------------------------------------------------
class PreviewModule(ModuleWidget):
    module_name = 'プレビュー'
    IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
    SUPPORTED_EXTS = IMAGE_EXTS | TEXT | {
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm",
        ".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg", ".wma"
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.module_name)
        self.setWindowIcon(app_icon())
        self.resize(1000, 680)

        self.setAcceptDrops(True)

        self.playlist = []
        self.current_index = -1
        self.current_path = ""
        self.media_info_dialog = None

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)

        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.path_label = QLabel("ファイルまたはフォルダーを選択（またはD&D）してください。")
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.path_label.setStyleSheet("font-size: 11px; color: #555; padding: 2px 4px;")
        layout.addWidget(self.path_label)

        self.video_widget = QVideoWidget(self)
        self.player.setVideoOutput(self.video_widget)
        self.video_widget.setStyleSheet("background-color: #000;")
        self.video_widget.setAcceptDrops(False)
        self.image_label = QLabel("画像を選択してください", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #111; color: #ddd;")
        self._image_pixmap = None
        self.preview_stack = QStackedWidget(self)
        self.preview_stack.addWidget(self.video_widget)
        self.preview_stack.addWidget(self.image_label)
        self.text_view = QPlainTextEdit(self)
        self.text_view.setReadOnly(True)
        self.preview_stack.addWidget(self.text_view)
        layout.addWidget(self.preview_stack, 1)

        self.status_msg = QLabel("再生を押してください。対応形式は搭載コーデックによります")
        self.status_msg.setStyleSheet("color: #444; font-size: 12px; padding: 4px;")
        layout.addWidget(self.status_msg)

        ctrl_bar = QHBoxLayout()
        self.btn_play = QPushButton("▶ 再生")
        self.btn_pause = QPushButton("一時停止")
        self.btn_stop = QPushButton("■ 停止")
        ctrl_bar.addWidget(self.btn_play)
        ctrl_bar.addWidget(self.btn_pause)
        ctrl_bar.addWidget(self.btn_stop)

        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 0)
        ctrl_bar.addWidget(self.seek_slider)

        self.time_label = QLabel("0:00 / 0:00")
        ctrl_bar.addWidget(self.time_label)

        ctrl_bar.addWidget(QLabel("音量"))
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.audio_output.setVolume(0.7)
        self.vol_slider.setMaximumWidth(90)
        ctrl_bar.addWidget(self.vol_slider)

        layout.addLayout(ctrl_bar)

        nav_bar = QHBoxLayout()
        self.btn_select_file = QPushButton("ファイルを選択")
        self.btn_select_folder = QPushButton("フォルダーを選択")
        self.btn_prev = QPushButton("◀ 前のファイル")
        self.index_label = QLabel("- / -")
        self.btn_next = QPushButton("次のファイル ▶")

        self.btn_info = QPushButton("ℹ️ メディア情報")
        self.btn_info.setStyleSheet("font-weight: bold; padding: 4px 10px;")

        nav_bar.addWidget(self.btn_select_file)
        nav_bar.addWidget(self.btn_select_folder)
        nav_bar.addWidget(self.btn_prev)
        nav_bar.addWidget(self.index_label)
        nav_bar.addWidget(self.btn_next)
        nav_bar.addSpacing(10)
        nav_bar.addWidget(self.btn_info)
        nav_bar.addStretch()

        layout.addLayout(nav_bar)

    def _setup_connections(self):
        self.btn_play.clicked.connect(self.player.play)
        self.btn_pause.clicked.connect(self.player.pause)
        self.btn_stop.clicked.connect(self.player.stop)
        self.btn_info.clicked.connect(self.toggle_media_info)

        self.btn_select_file.clicked.connect(self._select_file)
        self.btn_select_folder.clicked.connect(self._select_folder)
        self.btn_prev.clicked.connect(self._prev_file)
        self.btn_next.clicked.connect(self._next_file)

        self.vol_slider.valueChanged.connect(lambda v: self.audio_output.setVolume(v / 100.0))
        self.seek_slider.sliderMoved.connect(self.player.setPosition)

        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)

    # 外部や基盤からパスが渡された場合の対応
    def input_paths(self, paths):
        if paths and len(paths) > 0:
            target = Path(paths[0])
            if target.is_file():
                self.playlist = self._collect_media_files(target.parent, max_depth=1)
                if str(target) not in self.playlist:
                    self.playlist.insert(0, str(target))
                self.current_index = self.playlist.index(str(target))
            elif target.is_dir():
                self.playlist = self._collect_media_files(target, max_depth=4)
                self.current_index = 0 if self.playlist else -1
            self._load_current()

    def set_path(self, path_str):
        self.input_paths([path_str])

    # -------------------------------------------------------------
    # ドラッグ＆ドロップ
    # -------------------------------------------------------------
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if not urls:
            return

        dropped_paths = [Path(u.toLocalFile()) for u in urls if u.toLocalFile()]
        if not dropped_paths:
            return

        collected = []
        first_file = None

        for p in dropped_paths:
            if p.is_file():
                if p.suffix.lower() in self.SUPPORTED_EXTS:
                    collected.append(str(p))
                    if not first_file:
                        first_file = str(p)
                sibling_files = self._collect_media_files(p.parent, max_depth=1)
                for sf in sibling_files:
                    if sf not in collected:
                        collected.append(sf)
            elif p.is_dir():
                dir_files = self._collect_media_files(p, max_depth=4)
                collected.extend(dir_files)

        seen = set()
        unique_playlist = []
        for f in collected:
            if f not in seen:
                seen.add(f)
                unique_playlist.append(f)

        if unique_playlist:
            self.playlist = unique_playlist
            self.current_index = 0
            if first_file and first_file in self.playlist:
                self.current_index = self.playlist.index(first_file)
            self._load_current()
        else:
            QMessageBox.information(self, "情報", "ドロップされた対象から対応メディアファイルが見つかりませんでした。")

    # -------------------------------------------------------------
    # 階層探索
    # -------------------------------------------------------------
    def _collect_media_files(self, base_dir: Path, max_depth=4):
        results = []
        base_dir = base_dir.resolve()

        for root, dirs, files in os.walk(base_dir):
            rel = Path(root).relative_to(base_dir)
            if len(rel.parts) >= max_depth:
                dirs.clear()

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.SUPPORTED_EXTS:
                    results.append(os.path.join(root, file))

        results.sort()
        return results

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを開く", "",
            "画像・メディア (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.mp4 *.mkv *.avi *.mov *.mp3 *.m4a *.wav *.flac);;すべてのファイル (*.*)"
        )
        if path:
            folder = Path(path).parent
            self.playlist = self._collect_media_files(folder, max_depth=2)
            if path not in self.playlist:
                self.playlist.insert(0, path)
            self.current_index = self.playlist.index(path)
            self._load_current()

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "フォルダーを開く", "")
        if folder:
            self.playlist = self._collect_media_files(Path(folder), max_depth=4)
            if self.playlist:
                self.current_index = 0
                self._load_current()
            else:
                QMessageBox.information(self, "情報", "選択したフォルダー（および下位フォルダー）内に対象のメディアファイルが見つかりませんでした。")

    def _load_current(self):
        if not (0 <= self.current_index < len(self.playlist)):
            return
        self.current_path = self.playlist[self.current_index]
        self.path_label.setText(self.current_path)
        self.index_label.setText(f"{self.current_index + 1} / {len(self.playlist)}")
        path = Path(self.current_path)
        if path.suffix.lower() in self.IMAGE_EXTS:
            self.player.stop()
            self.player.setSource(QUrl())
            pixmap = QPixmap(str(path))
            self.preview_stack.setCurrentWidget(self.image_label)
            self._image_pixmap = pixmap if not pixmap.isNull() else None
            self._render_image()
            self.status_msg.setText("画像を表示中" if self._image_pixmap else "画像を読み込めませんでした")
            self.btn_play.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.seek_slider.setEnabled(False)
            self._update_time_label(0, 0)
        elif path.suffix.lower() in TEXT:
            self.player.stop()
            self.player.setSource(QUrl())
            self._image_pixmap = None
            self.preview_stack.setCurrentWidget(self.text_view)
            try:
                self.text_view.setPlainText(read_content(path))
                self.status_msg.setText("本文を表示中")
            except Exception as exc:
                self.text_view.setPlainText("読み込めませんでした: " + str(exc))
                self.status_msg.setText("本文の読み込みに失敗")
            self.btn_play.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.seek_slider.setEnabled(False)
            self._update_time_label(0, 0)
        elif path.suffix.lower() in self.SUPPORTED_EXTS:
            self._image_pixmap = None
            self.preview_stack.setCurrentWidget(self.video_widget)
            self.btn_play.setEnabled(True)
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
            self.seek_slider.setEnabled(True)
            self.player.setSource(QUrl.fromLocalFile(self.current_path))
            self.player.play()
        else:
            self.player.stop()
            self.player.setSource(QUrl())
            self._image_pixmap = None
            self.preview_stack.setCurrentWidget(self.image_label)
            self.image_label.setText("この形式はメディアプレビューに対応していません")
            self.status_msg.setText("非対応のファイル形式")
            self.btn_play.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.seek_slider.setEnabled(False)
            self._update_time_label(0, 0)
        self._refresh_dialog()

    def _render_image(self):
        if self._image_pixmap is None:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("画像を読み込めませんでした")
            return
        self.image_label.setText("")
        size = self.image_label.size()
        if size.width() > 0 and size.height() > 0:
            self.image_label.setPixmap(self._image_pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._image_pixmap is not None:
            self._render_image()

    def _prev_file(self):
        if self.playlist and self.current_index > 0:
            self.current_index -= 1
            self._load_current()

    def _next_file(self):
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self._load_current()

    def _on_position_changed(self, pos):
        if not self.seek_slider.isSliderDown():
            self.seek_slider.setValue(pos)
        self._update_time_label(pos, self.player.duration())

    def _on_duration_changed(self, dur):
        self.seek_slider.setRange(0, dur)
        self._update_time_label(self.player.position(), dur)
        self._refresh_dialog()

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.status_msg.setText("▶ 再生中")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.status_msg.setText("⏸ 一時停止")
        else:
            self.status_msg.setText("⏹ 停止中")
        self._refresh_dialog()

    def _get_status_text(self):
        state = self.player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            return "▶ 再生中"
        elif state == QMediaPlayer.PlaybackState.PausedState:
            return "⏸ 一時停止"
        return "⏹ 停止中"

    def _get_effective_path(self):
        """current_path が空の場合は上部ラベルのパスから取得"""
        if self.current_path and Path(self.current_path).exists():
            return self.current_path
        txt = self.path_label.text().strip()
        if txt and Path(txt).is_file():
            self.current_path = txt
            return txt
        return ""

    def _refresh_dialog(self):
        target_path = self._get_effective_path()
        if self.media_info_dialog and self.media_info_dialog.isVisible() and target_path:
            self.media_info_dialog.update_info(
                target_path,
                self._get_status_text(),
                self.player.duration()
            )

    def toggle_media_info(self):
        target_path = self._get_effective_path()
        if not target_path:
            QMessageBox.information(self, "メディア情報", "再生対象のファイルが見つかりません。")
            return

        if self.media_info_dialog is None:
            self.media_info_dialog = MediaInfoWindow(self)

        self.media_info_dialog.show()
        self._refresh_dialog()
        self.media_info_dialog.raise_()
        self.media_info_dialog.activateWindow()

    def _update_time_label(self, pos, dur):
        def fmt(ms):
            s = ms // 1000
            m, s = divmod(s, 60)
            return f"{m}:{s:02d}"
        self.time_label.setText(f"{fmt(pos)} / {fmt(dur)}")


def main():
    app = QApplication(sys.argv)
    w = PreviewModule()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()