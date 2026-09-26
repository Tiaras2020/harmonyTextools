#!/usr/bin/env python3
"""Download immutable release dependencies, check hashes, and relocate build metadata."""
import argparse,hashlib,json,os,shutil,tarfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--asset-dir',type=Path);ap.add_argument('--sources',action='store_true');args=ap.parse_args()
 manifest=json.loads((ROOT/'recovery-assets.json').read_text());cache=ROOT/'build/downloads';cache.mkdir(parents=True,exist_ok=True)
 for asset in manifest['assets']:
  if asset['kind'] not in ('native-deps','runtime') and not (args.sources and asset['kind']=='patched-sources'):continue
  p=cache/asset['name']
  if not p.exists() or sha(p)!=asset['sha256']:
   part=p.with_suffix(p.suffix+'.part')
   if args.asset_dir:shutil.copyfile(args.asset_dir/asset['name'],part)
   else:
    print('Downloading',asset['name'],flush=True)
    with urllib.request.urlopen(asset['url']) as response,part.open('wb') as f:shutil.copyfileobj(response,f)
   if sha(part)!=asset['sha256']:raise SystemExit('Checksum mismatch: '+asset['name'])
   part.replace(p)
  if asset['kind']=='runtime':continue
  with tarfile.open(p) as tf:
   members=tf.getmembers()
   for m in members:
    if (m.issym() or m.islnk()) and m.linkname.startswith(manifest['originalRoot']+'/'):
     relative=m.linkname[len(manifest['originalRoot'])+1:]
     m.linkname=os.path.relpath(ROOT/relative,(ROOT/m.name).parent) if m.issym() else relative
    target=(ROOT/m.name).resolve()
    if not target.is_relative_to(ROOT):raise SystemExit('Unsafe archive path')
    if m.issym() or m.islnk():
     linked=(target.parent/m.linkname if m.issym() else ROOT/m.linkname).resolve()
     if not linked.is_relative_to(ROOT):raise SystemExit('Unsafe archive link')
   tf.extractall(ROOT,members=members)
 tool=os.environ.get('TOOL_HOME','');old=manifest['originalRoot'];oldtool=manifest['originalToolHome']
 if not tool:raise SystemExit('Set TOOL_HOME before relocating native dependencies')
 for base in ['build/build-qt-ohos-install','build/build-poppler-ohos-install','build/build-hpkbuilds-ohos-install','build/biber-native/install']:
  for p in (ROOT/base).rglob('*'):
   if p.is_symlink() or not p.is_file() or p.suffix not in {'.cmake','.pc','.prl','.pri','.la','.conf','.h'}:continue
   try:s=p.read_text()
   except UnicodeError:continue
   n=s.replace(old,str(ROOT)).replace(oldtool,tool)
   if s!=n:p.write_text(n)
 (ROOT/'build/build-qt-ohos-install/bin/qt.conf').write_text('[Paths]\nPrefix=..\n')
 print('Dependencies verified and restored to',ROOT)
if __name__=='__main__':main()
