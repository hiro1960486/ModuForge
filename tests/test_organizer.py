import ast
from unittest.mock import patch
import unittest,tempfile,sys,os
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'00_shared/src'))
from fileworkbench.services.diagnostic_log import emit,log_folder
from run_component import assemble
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('organizer_core',HERE/'08_organizer/module/service.py');m=module_from_spec(spec);spec.loader.exec_module(m)
class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
        self.a=self.base/'a';self.b=self.base/'b';self.a.mkdir();self.b.mkdir();self.file=self.a/'test.txt';self.file.write_text('hello',encoding='utf-8');self.s=m.OrganizerService()
    def test_plan_only(self):
        p=self.s.plan(self.file,self.b);self.assertTrue(self.file.exists());self.assertFalse(Path(p['target']).exists())
    def test_blank_destination_rejected_without_mutation(self):
        for action in ('copy','move'):
            for blank in ('', '   ', '\t\n', None):
                with self.subTest(action=action,blank=blank):
                    with self.assertRaisesRegex(ValueError,'整理先フォルダー'):
                        self.s.plan(self.file,blank,action)
                    self.assertEqual(self.file.read_bytes(),b'hello')
                    self.assertEqual(list(self.b.iterdir()),[])
    def test_blank_source_rejected(self):
        for blank in ('', '   ', '\t\n', None):
            with self.subTest(blank=blank):
                with self.assertRaisesRegex(ValueError,'整理対象ファイル'):
                    self.s.plan(blank,self.b)
    def test_copy_collision_after_validation_preserves_existing_file(self):
        plan=self.s.plan(self.file,self.b)
        target=self.b/'test.txt'
        original_plan=self.s.plan
        def competing_plan(*args,**kwargs):
            fresh=original_plan(*args,**kwargs)
            target.write_bytes(b'competing file')
            return fresh
        with patch.object(self.s,'plan',side_effect=competing_plan):
            with self.assertRaises(FileExistsError):
                self.s.execute(plan,confirm=True)
        self.assertEqual(target.read_bytes(),b'competing file')
        self.assertEqual(self.file.read_bytes(),b'hello')
    def test_failed_copy_removes_own_partial_target(self):
        plan=self.s.plan(self.file,self.b)
        def fail_copy(inp,out,*args):
            out.write(b'partial')
            raise OSError('simulated copy failure')
        with patch.object(m.shutil,'copyfileobj',side_effect=fail_copy):
            with self.assertRaises(OSError):self.s.execute(plan,confirm=True)
        self.assertFalse((self.b/'test.txt').exists())
        self.assertEqual(self.file.read_bytes(),b'hello')
    def test_confirm_required(self):
        with self.assertRaises(PermissionError):self.s.execute(self.s.plan(self.file,self.b))
    def test_copy_preserves_source(self):
        p=self.s.plan(self.file,self.b);self.s.execute(p,confirm=True);self.assertTrue(self.file.exists());self.assertEqual((self.b/'test.txt').read_text(),'hello')
    def test_collision(self):
        (self.b/'test.txt').write_text('existing');
        with self.assertRaises(FileExistsError):self.s.plan(self.file,self.b)
    def test_move(self):
        p=self.s.plan(self.file,self.b,'move');self.s.execute(p,confirm=True);self.assertFalse(self.file.exists());self.assertTrue((self.b/'test.txt').exists())
    def test_plan_tamper_rejected(self):
        p=self.s.plan(self.file,self.b);p['bytes']=999
        with self.assertRaises(ValueError):self.s.execute(p,confirm=True)
    def test_log(self):
        self.assertEqual(emit('test','ok')['event'],'ok');self.assertTrue(log_folder().exists())
    def test_gui_adapter_bind_contract(self):
        # Qtを起動できないCIでもGUIの接続契約があることをASTで確認。
        tree=ast.parse((HERE/'08_organizer/module/module.py').read_text(encoding='utf-8'))
        cls=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='OrganizerModule')
        methods={n.name:n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        self.assertIn('bind_port',methods)
        self.assertEqual([arg.arg for arg in methods['bind_port'].args.args],['self','port'])
        self.assertIn('self.port',ast.unparse(methods['bind_port']))

    def test_organizer_manifest_entrypoint(self):
        import json
        manifest=json.loads((HERE/'08_organizer/api/module.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['entrypoint'],'fileworkbench.modules.organizer.module')
        self.assertEqual(manifest['interface_entrypoint'],'fileworkbench.modules.organizer.interface')

    def test_assemble(self):
        with tempfile.TemporaryDirectory() as t:
            src=assemble(HERE,Path(t),'organizer');self.assertTrue((src/'fileworkbench/modules/organizer/interface.py').exists())
if __name__=='__main__':unittest.main(verbosity=2)
