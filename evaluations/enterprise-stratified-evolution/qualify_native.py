"""Qualify the exact direct builder interface used by native retrieval trials."""
from __future__ import annotations

import json
import subprocess
import time

from prepare import WORK, NAME, IMAGE, tree, read, write, posix


def main():
    output = WORK/'native-oracle'
    output.mkdir(exist_ok=False)
    source = WORK/'corpus/input'
    baseline = WORK/'baseline'/NAME
    before, skill_before = tree(source), tree(baseline)
    argv = ['wsl','-d','Ubuntu','--exec','docker','run','--rm','--network=none','--cpus=2',
            '--memory=6g','--memory-swap=6g','-e','PYTHONDONTWRITEBYTECODE=1','-e','PYTHONUTF8=1']
    for host,target,readonly in ((source,'/input',True),(baseline,'/skill',True),(output,'/out',False)):
        argv += ['--mount','type=bind,source='+posix(host)+',target='+target+(',readonly' if readonly else '')]
    # Exactly the native builder/validator contract used by bridge.build_family.
    program = '''import json,subprocess,sys,time,resource
start=time.monotonic()
scripts="/skill/assets/families/legacy/builder/scripts/"
for name in ("knowledge","rebuild"):
    subprocess.run([sys.executable,"-B",scripts+"build_semantic_okf.py","/input/manifest.json","/out/"+name,"--concept-layout","source-packed-v1","--output-format","json"],check=True)
    subprocess.run([sys.executable,"-B",scripts+"validate_semantic_okf.py","/out/"+name,"--output-format","json"],check=True)
json.dump(dict(status="pass",seconds=time.monotonic()-start,peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),open("/out/resources.json","x"))
'''
    started = time.monotonic()
    with (output/'execution.log').open('xb') as stream:
        result = subprocess.run(argv+[IMAGE,'python','-B','-c',program],stdout=stream,stderr=subprocess.STDOUT,timeout=3600)
    if result.returncode:
        write(output/'failed.json',{'status':'failed','exit_code':result.returncode,'retrieval_queries':0})
        raise ValueError('Native source qualification failed; preserve the preflight evidence')
    first = tree(output/'knowledge')
    if first != tree(output/'rebuild') or before != tree(source) or skill_before != tree(baseline):
        raise ValueError('Deterministic source construction or frozen input drift')
    summary = {'status':'pass','direct_native_builds':2,'independent_validations':2,
               'builds_byte_identical':True,'source_files':before,'skill_files':skill_before,
               'knowledge_files':first,'resources':read(output/'resources.json'),
               'wall_seconds':time.monotonic()-started,'retrieval_queries':0}
    write(output/'qualification.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if not k.endswith('_files')}),flush=True)


if __name__ == '__main__':
    main()
