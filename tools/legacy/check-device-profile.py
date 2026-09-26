"""Verify the embedded developer profile and match the connected device without logging its UDID."""
import argparse,datetime,json,pathlib,subprocess
from release_config import release
parser=argparse.ArgumentParser()
parser.add_argument('--version',default=release()['version'])
args=parser.parse_args()
assert all(c in '0123456789.' for c in args.version)
root=pathlib.Path(__file__).resolve().parent.parent
out=root/('validation/device-signing' if args.version=='1.0.0' else f'validation/device-signing-{args.version}')
sdk=pathlib.Path(r'E:\Huawei\DevEco Studio\sdk\default\openharmony\toolchains')
java=r'E:\Huawei\DevEco Studio\jbr\bin\java.exe'
proc=subprocess.run([java,'-jar',str(sdk/'lib/hap-sign-tool.jar'),'verify-profile','-inFile',str(out/'verified-profile.p7b'),'-outFile',str(out/'profile-details-local.json')],capture_output=True)
(out/'verify-profile.log').write_bytes(proc.stdout+proc.stderr)
assert proc.returncode==0,'Profile verification failed'
details=json.loads((out/'profile-details-local.json').read_text())
print('Verified profile result keys:',list(details))
assert details['verifiedPassed'] is True
profile=details['content']
if isinstance(profile,str): profile=json.loads(profile)
if not profile:
    raise RuntimeError('Inspect profile result schema without disclosing credentials')
assert profile['bundle-info']['bundle-name']=='com.ohos.texstudio'
assert profile['type']=='debug'
targets=subprocess.run([str(sdk/'hdc.exe'),'list','targets'],capture_output=True)
target_text=targets.stdout.decode(errors='replace').strip()
connected=targets.returncode==0 and bool(target_text) and '[Empty]' not in target_text
ids=profile['debug-info']['device-ids']
matched=None
if connected:
    udidproc=subprocess.run([str(sdk/'hdc.exe'),'shell','bm','get','-u'],capture_output=True)
    lines=udidproc.stdout.decode(errors='replace').strip().splitlines()
    udid=lines[-1].strip() if lines else ''
    matched=udidproc.returncode==0 and udid in ids
validity=profile['validity']
now=datetime.datetime.now(datetime.timezone.utc).timestamp()
valid=validity['not-before']<=now<=validity['not-after']
summary={'profile_verified':True,'bundle_name':'com.ohos.texstudio','profile_type':'debug','authorized_device_count':len(ids),'device_connected':connected,'connected_device_matches':matched,'profile_currently_valid':valid,'expires_utc':datetime.datetime.fromtimestamp(validity['not-after'],datetime.timezone.utc).isoformat()}
(out/'device-profile-check.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
assert matched is not False,'Connected device does not match, or hdc UDID query needs inspection'
assert valid,'Profile outside validity interval'
