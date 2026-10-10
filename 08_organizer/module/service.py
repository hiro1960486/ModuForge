"""Safe file organizer core. No implicit file mutations."""
from pathlib import Path
import os,shutil,hashlib,uuid
from datetime import datetime
from fileworkbench.services.diagnostic_log import emit
def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()
class OrganizerService:
    def inspect(self,path):
        p=Path(path).resolve(strict=True)
        if not p.is_file():raise ValueError('通常ファイルのみ対応')
        s=p.stat();return {'path':str(p),'name':p.name,'size':s.st_size,'extension':p.suffix.lower(),'modified':datetime.fromtimestamp(s.st_mtime).isoformat()}
    def plan(self,source,folder,action='copy'):
        if action not in ('copy','move'):raise ValueError('未対応操作: '+str(action))
        if source is None or not str(source).strip():raise ValueError('整理対象ファイルを指定してください')
        if folder is None or not str(folder).strip():raise ValueError('整理先フォルダーを指定してください')
        src=Path(source).resolve(strict=True);dest=Path(folder).resolve(strict=True)
        if not src.is_file() or src.is_symlink():raise ValueError('通常ファイルのみ対応')
        if not dest.is_dir():raise NotADirectoryError(folder)
        target=dest/src.name
        if src==target:raise ValueError('元ファイルと整理先が同じ場所です。別のフォルダーを指定してください')
        if target.exists():raise FileExistsError('整理先に同名ファイルがあります: '+str(target))
        return {'action':action,'source':str(src),'target':str(target),'bytes':src.stat().st_size,'confirmation_required':True}
    def execute(self,plan,confirm=False):
        if confirm is not True:raise PermissionError('確認が必須です')
        if not isinstance(plan,dict) or plan.get('action') not in ('copy','move'):raise ValueError('無効な計画')
        fresh=self.plan(plan['source'],str(Path(plan['target']).parent),plan['action'])
        if any(plan.get(k)!=fresh[k] for k in ('source','target','action','bytes')):raise ValueError('計画が変更されています。再確認してください')
        src=Path(fresh['source']);target=Path(fresh['target'])
        emit('organizer','operation_start',action=fresh['action'],source=str(src),target=str(target))
        # Exclusive creation prevents overwrite even under concurrent races.
        copy_created=False
        try:
            if fresh['action']=='copy':
                with src.open('rb') as inp, target.open('xb') as out:
                    copy_created=True
                    shutil.copyfileobj(inp,out,1024*1024)
                if digest(src)!=digest(target):raise IOError('コピー結果のハッシュ不一致')
            else:
                # Do not silently copy+delete across disks. Disallow cross-device moves.
                if src.stat().st_dev!=target.parent.stat().st_dev:raise OSError('異なるファイルシステム間の移動はこの試験版では禁止')
                # Reserve target name using exclusive create, then atomic replacement of *our empty placeholder* only.
                with target.open('xb'):pass
                try:os.replace(src,target)
                except BaseException:
                    target.unlink(missing_ok=True);raise
            emit('organizer','operation_success',action=fresh['action'],source=str(src),target=str(target))
            return {'status':'ok',**fresh}
        except BaseException as exc:
            # For failed copy, leave no truncated target behind.
            if copy_created and target.exists():target.unlink()
            emit('organizer','operation_error',level='ERROR',error=type(exc).__name__,detail=str(exc))
            raise
