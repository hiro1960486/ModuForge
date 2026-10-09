"""Static / packaging checks for ALL eight components without GUI dependencies."""
import ast
import json
import tempfile
import unittest
from pathlib import Path
from run_component import assemble

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('tree','rename','preview','compare','hash','recycle','tags','organizer')

class ModulesContractTests(unittest.TestCase):
    def test_every_module_manifest_and_api(self):
        for name in MODULES:
            with self.subTest(module=name):
                matches=list(ROOT.glob('[0-9][0-9]_'+name))
                self.assertEqual(len(matches),1)
                folder=matches[0]
                manifest=json.loads((folder/'api/module.json').read_text(encoding='utf-8'))
                self.assertEqual(manifest['id'],name)
                self.assertEqual(manifest['interface_entrypoint'],f'fileworkbench.modules.{name}.interface')
                self.assertEqual(manifest['entrypoint'],f'fileworkbench.modules.{name}.module')
                self.assertTrue(manifest['commands'])
                for file in (folder/'api/interface.py',folder/'module/module.py'):
                    ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
    def test_all_modules_assemble(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in MODULES:
                with self.subTest(module=name):
                    dest=Path(temp)/name
                    src=assemble(ROOT,dest,name)
                    target=src/'fileworkbench/modules'/name
                    self.assertTrue((target/'interface.py').is_file())
                    self.assertTrue((target/'module.py').is_file())
                    self.assertTrue((target/'module.json').is_file())
