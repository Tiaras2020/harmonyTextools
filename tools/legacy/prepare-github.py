from pathlib import Path
import os,shutil,json,subprocess
root=Path.cwd();src=root/'texstudio-harmony';dst=root/'github-publish'
exclude={'.git','build','node_modules','oh_modules','.hvigor','.cxx','__pycache__','dependencies','.idea','.ohos','.cache','.vscode'}
skips={'.gitmodules','local.properties','oh-package-lock.json5'}
count=0
for base,dirs,files in os.walk(src):
 dirs[:]=[d for d in dirs if d not in exclude and not (Path(base)/d).is_symlink() and not (Path(base)/d).relative_to(src).as_posix().startswith('texstudio_harmony/entry/libs')]
 for name in files:
  p=Path(base)/name;rel=p.relative_to(src);q=dst/rel
  if name in skips or name=='.git' or p.suffix.lower() in {'.hap','.hnp','.app','.hsp','.p12','.pfx','.jks','.keystore','.p7b','.cer','.dmp','.pyc','.log'} or p.is_symlink():continue
  if rel.as_posix()=='README.md':q=dst/'docs/upstream/README.md'
  q.parent.mkdir(parents=True,exist_ok=True)
  if rel.as_posix()=='texstudio_harmony/build-profile.json5':
   data=json.loads(p.read_text(encoding='utf-8-sig'));data['app']['signingConfigs']=[]
   for product in data['app'].get('products',[]):product.pop('signingConfig',None)
   q.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');continue
  shutil.copy2(p,q);count+=1
# Preserve implementation recipes, but not generated binaries, signing helpers,
# crash/user-device evidence or one-shot UI mutation scripts.
legacy=dst/'docs/porting-history';legacy.mkdir(parents=True,exist_ok=True)
for p in (root/'README').glob('*.md'):
 s=p.read_text(encoding='utf-8-sig').replace('E:\\CodeProjects\\harmonytexlive','<legacy-workspace>').replace('E:/CodeProjects/harmonytexlive','<legacy-workspace>')
 (legacy/p.name).write_text('> Historical record: paths and validation claims describe the original porting workspace. Use ../../README.md and ../BUILD.md for current instructions.\n\n'+s,encoding='utf-8')
out=dst/'tools/legacy';out.mkdir(parents=True,exist_ok=True)
for p in (root/'build-support').iterdir():
 if p.suffix not in {'.py','.sh','.cpp','.h','.json','.txt','.pl','.pm'} or p.stat().st_size>4_000_000:continue
 if any(p.name.startswith(x) for x in ['sign-with','device-','mock-','upgrade-','integrate-','finalize-','deliver-','docs-','closeout-','handoff-','include-','final-handoff','title-menu','tidy-type','adjust-nav']):continue
 shutil.copy2(p,out/p.name)
origins={}
for part in ['.','third_party/texstudio','third_party/poppler']:
 sha=subprocess.check_output(['git','-C',str(src/part),'rev-parse','HEAD'],text=True).strip();origins[part]={'upstreamCommit':sha,'localModificationsIncluded':True,'storage':'vendored source; no submodule clone required'}
(dst/'docs/UPSTREAM-SOURCES.json').write_text(json.dumps(origins,indent=2)+'\n')
print('Source files copied:',count)
