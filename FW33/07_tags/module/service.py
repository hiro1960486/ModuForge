"""依存ゼロのタグ保存・メタデータ・安全なファイル移動。UIから分離。"""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime

class TagService:
    def __init__(self, db_path=None):
        self.db_path=Path(db_path) if db_path is not None else Path.home()/'.fileworkbench_next'/'tags.sqlite3'
        self.db_path.parent.mkdir(parents=True,exist_ok=True)
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS file_tags (file_path TEXT PRIMARY KEY, tags_json TEXT NOT NULL)')
    @contextmanager
    def _db(self):
        """Commit/rollback and always close SQLite handle (especially on Windows)."""
        db = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            with db:
                yield db
        finally:
            db.close()
    @staticmethod
    def _key(path):
        return os.path.normcase(str(Path(path).expanduser().resolve(strict=False)))
    @staticmethod
    def _tags(tags):
        if isinstance(tags,str):
            tags=tags.split(',')
        if not isinstance(tags,(list,tuple)) or any(not isinstance(t,str) for t in tags):
            raise ValueError('タグは文字列の配列、またはカンマ区切り文字列で指定してください')
        return sorted(set(t.strip() for t in tags if t.strip()))
    def set_tags(self,path,tags):
        key=self._key(path); values=self._tags(tags)
        if not Path(path).is_file(): raise FileNotFoundError(path)
        with self._db() as db:
            if values: db.execute('INSERT OR REPLACE INTO file_tags VALUES (?,?)',(key,json.dumps(values,ensure_ascii=False)))
            else: db.execute('DELETE FROM file_tags WHERE file_path=?',(key,))
        return values
    def list_tags(self,path):
        with self._db() as db:
            row=db.execute('SELECT tags_json FROM file_tags WHERE file_path=?',(self._key(path),)).fetchone()
        return json.loads(row[0]) if row else []
    def search(self,tag):
        tag=str(tag).strip()
        with self._db() as db:
            rows=db.execute('SELECT file_path,tags_json FROM file_tags').fetchall()
        return [p for p,s in rows if tag in json.loads(s)]
    def inspect(self,path):
        p=Path(path)
        if not p.is_file(): raise FileNotFoundError(path)
        s=p.stat()
        suffix=p.suffix.lower()
        kind=('image' if suffix in {'.jpg','.jpeg','.png','.gif','.bmp','.webp','.tif','.tiff'} else
              'video' if suffix in {'.mp4','.mkv','.mov','.avi','.webm','.wmv'} else
              'audio' if suffix in {'.mp3','.wav','.flac','.m4a','.ogg','.aac'} else 'other')
        return {'path':str(p.resolve()),'name':p.name,'extension':suffix,'kind':kind,'size_bytes':s.st_size,'modified':datetime.fromtimestamp(s.st_mtime).isoformat(timespec='seconds'),'tags':self.list_tags(p)}
    def plan_move(self,path,destination):
        source=Path(path).expanduser().resolve(strict=True)
        if not source.is_file():raise ValueError('ファイルのみ移動できます')
        dest_folder=Path(destination).expanduser().resolve(strict=True)
        if not dest_folder.is_dir():raise NotADirectoryError(destination)
        target=dest_folder/source.name
        if source==target:raise ValueError('移動元と移動先が同じです')
        if target.exists():raise FileExistsError('移動先に同名ファイルがあります: '+str(target))
        return {'source':str(source),'target':str(target),'action':'move','collision':'reject'}
    def move(self,path,destination,confirm=False):
        plan=self.plan_move(path,destination)
        if confirm is not True:raise PermissionError('実行には confirm=True が必要です')
        source=Path(plan['source']);target=Path(plan['target'])
        # データ破壊を避けるため上書き・自動リネームしない。
        if target.exists():raise FileExistsError(target)
        # os.rename は異なるドライブ間で失敗し得るため shutil.move を使う。
        # move 失敗時にはタグDBを触らない。
        shutil.move(str(source),str(target))
        old_tags=self.list_tags(source)
        if old_tags:
            with self._db() as db:
                db.execute('DELETE FROM file_tags WHERE file_path=?',(self._key(source),))
                db.execute('INSERT OR REPLACE INTO file_tags VALUES (?,?)',(self._key(target),json.dumps(old_tags,ensure_ascii=False)))
        return {'source':str(source),'target':str(target),'tags':old_tags}
