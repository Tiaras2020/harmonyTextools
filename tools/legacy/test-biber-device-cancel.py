"""Observe the test Biber child, click the grounded Stop control, verify its group exits."""
import json,os,pathlib,subprocess,time
root=pathlib.Path(__file__).resolve().parents[1];out=pathlib.Path(os.environ.get('BIBER_DEVICE_OUT',root/'validation/biber/device'))
hdc=r'E:\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\hdc.exe'
def shell(cmd):return subprocess.check_output([hdc,'shell',cmd]).decode('utf-8',errors='replace')
deadline=time.monotonic()+60
while time.monotonic()<deadline:
    before=shell('ps -eo pid,ppid,pgid,args')
    rows=[line.split(None,3) for line in before.splitlines()[1:]]
    targets=[r for r in rows if len(r)==4 and '/share/biber/bin/biber' in r[3] and 'app-cancel' in r[3]]
    if targets:break
    time.sleep(.4)
else:raise RuntimeError('No active app-cancel Biber within 60 seconds; no Stop action sent')
assert len(targets)==1
pid,parent,group,_=targets[0]
members=[r for r in rows if len(r)==4 and r[2]==group]
assert any('latexmk.pl' in r[3] for r in members),members
(out/'cancel-before.txt').write_text(before,encoding='utf-8')
print(shell('uitest uiInput click 673 138'),flush=True)
time.sleep(2)
after=shell('ps -eo pid,ppid,pgid,args');(out/'cancel-after.txt').write_text(after,encoding='utf-8')
remaining=[r for line in after.splitlines()[1:] if len(r:=line.split(None,3))==4 and r[2]==group]
assert not remaining,remaining
report={'passed':True,'biberPid':int(pid),'parentPid':int(parent),'sharedGroup':int(group),'terminatedMembers':members,'noGroupMembersAfterStop':True}
(out/'cancel-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
