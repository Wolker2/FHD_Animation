#!/usr/bin/env python3
"""Reproduce supplied FHD_Animation code/assets and audit missing media.

This upload lacks its government/station animations. The output reproduces
the supplied seven runtime files; it is not a complete installable mod.
Python 3.10+, standard library only.
"""
from pathlib import Path
import argparse,hashlib,json,platform,re,sys,zipfile,zlib
from dat_codec import encode,decode

ROOT=Path(__file__).resolve().parent.parent
PREFIX='Mods/FHD_MODS/FHD_Animation/'

def load(path):return json.loads(Path(path).read_text('utf-8'))
def sha(data):return hashlib.sha256(data).hexdigest()
def walk(block,path=''):
    for entry in block['entries']:
        name=path+'.'+entry['name']if path else entry['name']
        if entry['kind']=='block':yield from walk(entry['value'],name)
        else:yield name,entry['value']

def compile_source(root=ROOT):
    source=root/'source';files={};configs={}
    for path in sorted((source/'CFG').rglob('*.json')):
        relative=path.relative_to(source).with_suffix('.dat').as_posix()
        tree=load(path);configs[relative]=tree;files[relative]=encode(tree)
        if decode(files[relative],tree['format'])!=tree:raise ValueError('DAT tree roundtrip failed: '+relative)
    for path in sorted((source/'DATA').rglob('*')):
        if path.is_file():files[path.relative_to(source).as_posix()]=path.read_bytes()
    module=(source/'ModuleInfo.txt').read_text('utf-8').replace('\r\n','\n').replace('\n','\r\n')
    files['ModuleInfo.txt']=module.encode('cp1251')
    return files,configs

def audit(files,configs):
    cache=dict(walk(configs['CFG/CacheData.dat']['root']))
    references=[]
    for alias,path in cache.items():
        normalized=path.replace('\\','/')
        relative=normalized[len(PREFIX):]if normalized.startswith(PREFIX)else None
        references.append({'alias':alias,'path':normalized,'present_in_supplied_files':relative in files})
    code_aliases=set()
    for tree in configs.values():
        for _,value in walk(tree['root']):
            code_aliases.update(re.findall(r'Bm\.FHDStationEmblem\.[A-Za-z0-9_]+',value))
    missing=[v for v in references if not v['present_in_supplied_files']]
    return {'status':'INCOMPLETE_MEDIA_NOT_SUPPLIED'if missing else'COMPLETE_LOCAL_MEDIA',
            'cache_references':len(references),'missing_media_count':len(missing),
            'missing_gai':sum(x['path'].lower().endswith('.gai')for x in missing),
            'missing_gi':sum(x['path'].lower().endswith('.gi')for x in missing),
            'missing_media':missing,
            'code_aliases_not_defined_in_supplied_cache':sorted(code_aliases-set(cache)),
            'alias_scope_note':'Only the supplied local configuration was checked; external definitions were not assumed.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--strict-original',action='store_true',help='require supplied-file hashes to match')
    p.add_argument('--require-complete',action='store_true',help='exit with status 2 when referenced media is missing')
    a=p.parse_args();files,configs=compile_source();expected=load(ROOT/'original-file-sha256.json')
    if set(files)!=set(expected):raise SystemExit('Supplied file list does not match the manifest')
    hashes={k:sha(v)for k,v in sorted(files.items())};different=[k for k in hashes if hashes[k]!=expected[k]]
    if a.strict_original and different:raise SystemExit('Original SHA-256 mismatch: '+repr(different))
    audit_report=audit(files,configs);out=ROOT/'dist';out.mkdir(exist_ok=True)
    archive=out/'FHD_Animation_SUPPLIED_FILES_REBUILT.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(PREFIX+name,date_time=(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(archive)as z:
        if z.testzip():raise SystemExit('ZIP integrity failure')
    report={'scope':'SUPPLIED_CODE_AND_ASSETS_ONLY','full_mod_complete':not audit_report['missing_media_count'],
            'source_derived_dat_files':4,'supplied_runtime_files':len(files),
            'byte_identical_to_supplied_files':not different,'different_files':different,
            'python':platform.python_version(),'zlib':zlib.ZLIB_RUNTIME_VERSION,
            'game_executed':False,'sha256':hashes,'resource_audit':audit_report}
    (out/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: reproduced',len(files),'supplied files;',len(files)-len(different),'original hashes match')
    print('Completeness:',audit_report['status'],'-',audit_report['missing_media_count'],'referenced media files missing')
    print('Output is a supplied-files reconstruction, not a complete installable mod.')
    if a.require_complete and audit_report['missing_media_count']:return 2
    return 0

if __name__=='__main__':sys.exit(main())
