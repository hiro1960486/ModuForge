"""タグとメディア整理の単独試験用Qt画面。"""
from pathlib import Path
from PySide6.QtCore import Qt,QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QListWidget,QLineEdit,QFileDialog,QMessageBox,QSplitter,QTextEdit)
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from .service import TagService

class TagsModule(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.service=TagService();self.paths=[];self.port=None
        self.setWindowTitle('FileWorkbench Next | タグ・メディア整理（試験版）')
        self.resize(1030,650)
        outer=QVBoxLayout(self)
        top=QHBoxLayout(); outer.addLayout(top)
        self.open_btn=QPushButton('ファイルを追加');self.open_btn.clicked.connect(self.pick_files);top.addWidget(self.open_btn)
        self.destination=QLineEdit();self.destination.setPlaceholderText('移動先フォルダーを選択（未選択では移動不可）');top.addWidget(self.destination)
        b=QPushButton('移動先を選択');b.clicked.connect(self.pick_destination);top.addWidget(b)
        split=QSplitter(Qt.Orientation.Horizontal);outer.addWidget(split)
        left=QWidget();ll=QVBoxLayout(left);split.addWidget(left)
        ll.addWidget(QLabel('対象ファイル'))
        self.items=QListWidget();self.items.currentRowChanged.connect(self.display_selected);ll.addWidget(self.items)
        self.tag_edit=QLineEdit();self.tag_edit.setPlaceholderText('タグをカンマ区切りで入力');ll.addWidget(self.tag_edit)
        b=QPushButton('タグを保存');b.clicked.connect(self.save_tags);ll.addWidget(b)
        self.find_edit=QLineEdit();self.find_edit.setPlaceholderText('タグ名で検索（完全一致）');ll.addWidget(self.find_edit)
        b=QPushButton('タグ検索');b.clicked.connect(self.search_tag);ll.addWidget(b)
        right=QWidget();rl=QVBoxLayout(right);split.addWidget(right)
        self.preview=QLabel('画像プレビュー');self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter);self.preview.setMinimumHeight(180);self.preview.setScaledContents(False);rl.addWidget(self.preview)
        self.video=QVideoWidget();self.video.setMinimumHeight(170);rl.addWidget(self.video);self.video.hide()
        self.player=QMediaPlayer(self);self.audio=QAudioOutput(self);self.player.setAudioOutput(self.audio);self.player.setVideoOutput(self.video)
        media=QHBoxLayout();rl.addLayout(media)
        for label,callback in [('再生',self.player.play),('一時停止',self.player.pause),('停止',self.player.stop)]:
            btn=QPushButton(label);btn.clicked.connect(callback);media.addWidget(btn)
        self.info=QTextEdit();self.info.setReadOnly(True);rl.addWidget(self.info)
        btn=QPushButton('選択ファイルを移動（確認あり）');btn.clicked.connect(self.move_selected);rl.addWidget(btn)
        split.setSizes([410,620]);self._pixmap=None
    def bind_port(self,port):self.port=port
    def emit(self,name,payload):
        if self.port:self.port.emit(name,payload)
    def set_files(self,paths):
        if not isinstance(paths,(list,tuple)):raise TypeError('paths must be list')
        new=[]
        for path in paths:
            pp=Path(path)
            if pp.is_file():new.append(pp.resolve())
            elif pp.is_dir():new.extend(sorted(q.resolve() for q in pp.iterdir() if q.is_file()))
        self.paths=list(dict.fromkeys(new))
        self.items.clear();self.items.addItems([str(p) for p in self.paths]);
        if self.paths:self.items.setCurrentRow(0)
        else:self.display_selected(-1)
    def pick_files(self):
        files,_=QFileDialog.getOpenFileNames(self,'対象ファイルを選択')
        if files:self.set_files([*self.paths,*files])
    def pick_destination(self):
        folder=QFileDialog.getExistingDirectory(self,'移動先を選択')
        if folder:self.destination.setText(folder)
    def selected(self):
        idx=self.items.currentRow()
        return self.paths[idx] if 0<=idx<len(self.paths) else None
    def display_selected(self,index):
        self.player.stop();self.player.setSource(QUrl());self.video.hide();self.preview.show();self.preview.setText('画像プレビュー')
        p=self.selected()
        if p is None:self.info.clear();self.tag_edit.clear();return
        try:
            data=self.service.inspect(p);self.info.setPlainText('\n'.join(f'{k}: {v}' for k,v in data.items()))
            self.tag_edit.setText(', '.join(data['tags']))
            if data['kind']=='image':
                pic=QPixmap(str(p));self._pixmap=pic
                if not pic.isNull():self.preview.setPixmap(pic.scaled(550,260,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
                else:self.preview.setText('画像を読み込めません')
            elif data['kind'] in ('audio','video'):
                self.preview.setText('再生ボタンでメディアを確認');self.player.setSource(QUrl.fromLocalFile(str(p)))
                if data['kind']=='video':self.video.show()
        except Exception as exc:self.info.setPlainText(str(exc))
    def set_tags_for_path(self,path,tags):
        result=self.service.set_tags(path,tags)
        self.emit('tags.changed',{'path':str(path),'tags':result});self.display_selected(self.items.currentRow());return result
    def save_tags(self):
        if not self.selected():return
        try:self.set_tags_for_path(self.selected(),self.tag_edit.text())
        except Exception as exc:QMessageBox.warning(self,'保存失敗',str(exc))
    def search_tag(self):
        paths=[p for p in self.service.search(self.find_edit.text()) if Path(p).is_file()]
        self.set_files(paths)
    def refresh(self):
        self.set_files([p for p in self.paths if p.is_file()])
    def move_by_api(self,payload):
        source=payload['path'];dest=payload['destination']
        # APIでも明示確認フラグが必須。GUIからは別途ダイアログ確認。
        plan=self.service.plan_move(source,dest)
        if payload.get('confirm') is not True:return plan
        self.player.stop();self.player.setSource(QUrl())
        self.emit('files.will_change',{'source':plan['source'],'target':plan['target']})
        result=self.service.move(source,dest,confirm=True)
        self.emit('files.changed',result)
        self.set_files([result['target'] if str(p)==result['source'] else str(p) for p in self.paths])
        return result
    def move_selected(self):
        p=self.selected();dest=self.destination.text().strip()
        if not p:return
        try:
            plan=self.service.plan_move(p,dest)
            answer=QMessageBox.question(self,'移動確認',f"移動元：\n{plan['source']}\n\n移動先：\n{plan['target']}\n\n移動しますか？",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
            if answer==QMessageBox.StandardButton.Yes:self.move_by_api({'path':str(p),'destination':dest,'confirm':True})
        except Exception as exc:QMessageBox.warning(self,'移動不可',str(exc))
    def closeEvent(self,event):
        self.player.stop();self.player.setSource(QUrl());super().closeEvent(event)
