"""All component tests: `py run_tests.py` or `py run_tests.py --module tags`."""
import argparse
import datetime
import json
import os
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MODULES=('tree','rename','preview','compare','hash','recycle','tags','organizer')
class Tee:
    def __init__(self,*streams):self.streams=streams
    def write(self,value):
        for f in self.streams:f.write(value)
    def flush(self):
        for f in self.streams:f.flush()

def main():
    parser=argparse.ArgumentParser(description='FileWorkbench module tests')
    parser.add_argument('--module',choices=MODULES,default=None)
    args=parser.parse_args()
    sys.path.insert(0,str(ROOT))
    tests=ROOT/'tests'
    loader=unittest.TestLoader()
    if args.module in ('tags','organizer'):
        suite=loader.discover(str(tests),pattern='test_'+args.module+'.py',top_level_dir=str(tests))
    else:
        suite=loader.discover(str(tests),pattern='test_*.py',top_level_dir=str(tests))
    base=Path(os.environ.get('LOCALAPPDATA') or (Path.home()/'.local/share'))/'FileWorkbenchNext'/'logs'/'tests'
    base.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    name='all' if args.module is None else args.module
    log=base/f'test_{name}_{stamp}.log'
    with log.open('w',encoding='utf-8') as f:
        report=unittest.TextTestRunner(stream=Tee(sys.stdout,f),verbosity=2).run(suite)
    result={'time':stamp,'scope':name,'ran':report.testsRun,'failures':len(report.failures),'errors':len(report.errors),'skipped':len(report.skipped),'ok':report.wasSuccessful(),'log':str(log)}
    (base/'latest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Test log:',log)
    return 0 if report.wasSuccessful() else 1
if __name__=='__main__':sys.exit(main())
