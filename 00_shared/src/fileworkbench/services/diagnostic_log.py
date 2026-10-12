"""FileWorkbench Next common log service. Stdlib-only, local storage."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,logging
from logging.handlers import RotatingFileHandler
def log_folder():
    base=Path(os.environ.get('LOCALAPPDATA') or (Path.home()/'.local/share'))
    return base/'FileWorkbenchNext'/'logs'
def emit(module,event,level='INFO',**data):
    folder=log_folder();folder.mkdir(parents=True,exist_ok=True)
    obj={'utc':datetime.now(timezone.utc).isoformat(),'module':str(module),'event':str(event),'level':str(level),'data':data}
    logger=logging.getLogger('fwnext.structured');logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler=RotatingFileHandler(folder/'events.jsonl',maxBytes=2*1024*1024,backupCount=4,encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(message)s'));logger.addHandler(handler)
    logger.info(json.dumps(obj,ensure_ascii=False,default=str))
    return obj
