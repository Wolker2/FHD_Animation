from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import compile_source,audit,load

class ReviewTests(unittest.TestCase):
    def test_supplied_hashes_and_missing_resource_inventory(self):
        files,configs=compile_source()
        expected=load(ROOT/'original-file-sha256.json')
        self.assertEqual({k:hashlib.sha256(v).hexdigest()for k,v in files.items()},expected)
        result=audit(files,configs)
        self.assertEqual([result['missing_media_count'],result['missing_gai'],result['missing_gi']],[72,36,36])
        self.assertEqual(result['code_aliases_not_defined_in_supplied_cache'],['Bm.FHDStationEmblem.Fei','Bm.FHDStationEmblem.Peleng'])

    def test_editable_runtime_code_changes_only_its_language_dat(self):
        original,_=compile_source()
        with tempfile.TemporaryDirectory()as folder:
            target=Path(folder);shutil.copytree(ROOT/'source',target/'source')
            path=target/'source/CFG/Eng/Lang.json';data=load(path)
            def change(block):
                for e in block['entries']:
                    if e['kind']=='block':change(e['value'])
                    elif e['value']=='dword station = ScriptItemActShip();':e['value']+=' // source edit test'
            change(data['root']);path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            files,_=compile_source(target)
            self.assertEqual([k for k in files if files[k]!=original[k]],['CFG/Eng/Lang.dat'])

    def test_complete_build_gate_refuses_missing_media(self):
        result=subprocess.run([sys.executable,str(ROOT/'scripts/build.py'),'--strict-original','--require-complete'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2,result.stdout+'\n'+result.stderr)
        self.assertIn('72 referenced media files missing',result.stdout)
        report=load(ROOT/'dist/build-report.json')
        self.assertFalse(report['full_mod_complete'])
        self.assertTrue(report['byte_identical_to_supplied_files'])

if __name__=='__main__':unittest.main()
