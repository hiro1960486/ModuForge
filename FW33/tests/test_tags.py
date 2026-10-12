"""標準ライブラリで実行可能なタグモジュール非GUI試験。python test_tags.py"""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_component import assemble

SERVICE=Path(__file__).resolve().parents[1]/'07_tags/module/service.py'
spec=importlib.util.spec_from_file_location('tags_service',SERVICE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.inbox=self.base/'inbox';self.dest=self.base/'dest'
        self.inbox.mkdir();self.dest.mkdir();self.f=self.inbox/'sample.jpg';self.f.write_bytes(b'example bytes')
        self.s=m.TagService(self.base/'tags.db')
    def test_tags_persist_search_and_dedupe(self):
        self.assertEqual(self.s.set_tags(self.f,['旅行','旅行',' 2026 ']),['2026','旅行'])
        self.assertEqual(m.TagService(self.base/'tags.db').list_tags(self.f),['2026','旅行'])
        self.assertEqual(self.s.search('旅行'),[m.TagService._key(self.f)])
    def test_empty_tag_removes(self):
        self.s.set_tags(self.f,'写真');self.s.set_tags(self.f,'  ')
        self.assertEqual(self.s.list_tags(self.f),[])
    def test_metadata(self):
        self.assertEqual(self.s.inspect(self.f)['kind'],'image')
    def test_plan_does_not_move(self):
        plan=self.s.plan_move(self.f,self.dest)
        self.assertTrue(self.f.exists())
        # Windows 8.3 short path names (RUNNER~1) and long names can refer to
        # the same directory; compare filesystem identity, not path spelling.
        planned = Path(plan['target'])
        self.assertEqual(planned.name, 'sample.jpg')
        self.assertTrue(planned.parent.samefile(self.dest))
        with self.assertRaises(PermissionError):self.s.move(self.f,self.dest)
        self.assertTrue(self.f.exists())
    def test_move_and_tags_follow(self):
        self.s.set_tags(self.f,'旅行');result=self.s.move(self.f,self.dest,confirm=True)
        self.assertFalse(self.f.exists());self.assertTrue(Path(result['target']).exists())
        self.assertEqual(self.s.list_tags(result['target']),['旅行']);self.assertEqual(self.s.list_tags(self.f),[])
    def test_collision_no_overwrite(self):
        target=self.dest/self.f.name;target.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):self.s.move(self.f,self.dest,confirm=True)
        self.assertEqual(target.read_bytes(),b'keep');self.assertTrue(self.f.exists())
    def test_same_dir_rejected(self):
        with self.assertRaises(ValueError):self.s.plan_move(self.f,self.inbox)
    def test_invalid_source_rejected(self):
        with self.assertRaises(FileNotFoundError):self.s.set_tags(self.base/'missing','tag')
    def test_assembly_and_manifest(self):
        with tempfile.TemporaryDirectory() as target:
            src=assemble(Path(__file__).resolve().parents[1],Path(target),'tags')
            package=src/'fileworkbench/modules/tags'
            self.assertTrue((package/'interface.py').exists())
            self.assertTrue((package/'module.json').exists())
            manifest=json.loads((package/'module.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['id'],'tags')
            self.assertIn('move',manifest['commands'])

if __name__=='__main__':unittest.main(verbosity=2)
