from pathlib import Path
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QLineEdit,QFileDialog,QMessageBox,QTextEdit
from .service import OrganizerService
class OrganizerModule(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.port=None;self.service=OrganizerService();self.setWindowTitle('FileWorkbench Next | ファイル整理 試験版');self.resize(760,470)
        layout=QVBoxLayout(self)
        self.source=QLineEdit();self.dest=QLineEdit()
        for label,field,callback in [('整理対象ファイル',self.source,self.pick_file),('整理先フォルダー',self.dest,self.pick_folder)]:
            layout.addWidget(QLabel(label));r=QHBoxLayout();r.addWidget(field);b=QPushButton('選択');b.clicked.connect(callback);r.addWidget(b);layout.addLayout(r)
        self.info=QTextEdit();self.info.setReadOnly(True);layout.addWidget(self.info)
        r=QHBoxLayout();layout.addLayout(r)
        for name,action in [('コピー予定を確認','copy'),('移動予定を確認','move')]:
            b=QPushButton(name);b.clicked.connect(lambda checked=False,a=action:self.run(a));r.addWidget(b)
        layout.addWidget(QLabel('移動・コピーは必ず確認が必要。同名上書きなし。削除機能なし。'))
    def bind_port(self, port):
        """共通WidgetModuleAdapterとの接続契約。"""
        self.port = port

    def pick_file(self):
        file,_=QFileDialog.getOpenFileName(self,'対象ファイル');
        if file:self.source.setText(file);self.show_info()
    def pick_folder(self):
        folder=QFileDialog.getExistingDirectory(self,'整理先');
        if folder:self.dest.setText(folder)
    def show_info(self):
        try:self.info.setPlainText(str(self.service.inspect(self.source.text())))
        except Exception as e:self.info.setPlainText(str(e))
    def run(self,action):
        try:
            plan=self.service.plan(self.source.text(),self.dest.text(),action)
            self.info.setPlainText(str(plan))
            response=QMessageBox.question(self,'最終確認',f"{action.upper()} を実行しますか？\n元: {plan['source']}\n先: {plan['target']}\nサイズ: {plan['bytes']} bytes",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
            if response==QMessageBox.StandardButton.Yes:
                result=self.service.execute(plan,confirm=True);self.info.append('\n結果: '+str(result))
        except Exception as e:QMessageBox.warning(self,'安全停止',str(e))
