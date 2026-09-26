import pathlib,re,subprocess,json,os
repo=pathlib.Path(os.environ['BUILD_REPO'])
sdk=pathlib.Path(os.environ['NATIVE_OHOS_SDK'])
readelf=sdk/'llvm/bin/llvm-readelf'
system={p.name for p in (sdk/'sysroot/usr/lib/aarch64-linux-ohos').iterdir()}
records=[]
groups={'hap':[repo/'texstudio_harmony/entry/libs/arm64-v8a'],'hnp':[repo/'build/build-texlive-ohos-dist/bin',repo/'build/build-texlive-ohos-dist/lib']}
for group,roots in groups.items():
    supplied={p.name for root in roots if root.exists() for p in root.rglob('*') if p.is_file()}
    for root in roots:
        if not root.exists(): continue
        for p in sorted(root.rglob('*')):
            if not p.is_file() or p.is_symlink(): continue
            with p.open('rb') as f:
                if f.read(4)!=b'\x7fELF': continue
            head=subprocess.check_output([str(readelf),'-h',str(p)],text=True)
            dyn=subprocess.check_output([str(readelf),'-d',str(p)],text=True)
            needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dyn)
            record={'group':group,'file':str(p.relative_to(repo)),'arm64':'AArch64' in head,'needed':needed,'missing':[n for n in needed if n not in supplied and n not in system],'runpath':re.findall(r'\((?:RUNPATH|RPATH)\).*?\[(.*?)\]',dyn),'bytes':p.stat().st_size}
            records.append(record)
out=pathlib.Path(os.environ['DELIVERY_ROOT'])/'validation/elf-report.json'
out.write_text(json.dumps(records,indent=2)+'\n')
failed=[r for r in records if not r['arm64'] or r['missing']]
print('ELF files:',len(records),'failed:',len(failed))
for r in failed: print(r)
print('System dependency availability is checked against API 24 SDK; device runtime loading is not verified.')
if not records or failed: raise SystemExit(1)
