"""Record the signed, installed candidate without asserting device acceptance."""
import hashlib,json,pathlib,shutil
root=pathlib.Path(__file__).resolve().parents[1]
out=root/'validation/biber'
sign=json.loads((root/'validation/device-signing-1.0.18/result.json').read_text())
assert sign['signature_verified'] and sign['original_payloads_identical']
checks={}
for name in ('assembled-dependency-audit.json','workflow/result.json','remaining-upstream/result.json','tls/result.json','runtime-data-result.json','launcher-result.json','payload-check-1.0.18.json'):
    value=json.loads((out/name).read_text());assert value['passed'],name
    checks[name]={'passed':True,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest()}
report={'schema':1,'version':'1.0.18','biberVersion':'2.21','status':'signed_installed_device_acceptance_pending',
        'lastAcceptedRelease':'1.0.17','packaged':True,'installed':True,'deviceValidated':False,
        'checks':checks,'signedArtifact':sign,'remaining':['HiShell automatic Biber workflow','application compilation and preview','device cancellation and orphan process check','device HTTPS separately unvalidated']}
(out/'candidate-result-1.0.18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path=root/'DELIVERY-MANIFEST.json';manifest=json.loads(path.read_text(encoding='utf-8'))
manifest['biberB32']={'status':report['status'],'version':'2.21','candidateVersion':'1.0.18','report':'BIBER-B32.md',
    'evidence':'validation/biber/candidate-result-1.0.18.json','lock':'validation/biber/dependencies.lock.json','packaged':True,'installed':True,'deviceValidated':False}
for name in ('artifacts/texlive-1.0.18.hnp','artifacts/TeXstudioHarmony-1.0.18-arm64-device-signed.hap'):
    if name not in manifest['artifacts']:manifest['artifacts'].insert(0,name)
for name in ('validation/biber/candidate-result-1.0.18.json','validation/device-signing-1.0.18/result.json'):
    if name not in manifest['evidence']:manifest['evidence'].append(name)
path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
start=root/'START-HERE.md';text=start.read_text(encoding='utf-8')
text=text.replace('Biber 已完成第一批核心 XS（CSV、XML/XSLT、BibTeX）的 OHOS 静态移植与 QEMU 验证，尚未交付 Biber，见 `BIBER-B32.md`。','Biber 2.21 已完成全部直接依赖组装及 OHOS/QEMU 工作流验证；1.0.18 候选完整版已签名安装，待真机验收，见 `BIBER-B32.md`。')
text=text.replace('`BIBER-B32.md`：下一阶段依赖缺口','`BIBER-B32.md`：Biber 候选版与真机验收')
old='B3.2 已初步锁定 107 个 CPAN 发行包，并在独立试验树验证 CSV、XML/XSLT、BibTeX 核心 XS。下一步按 BIBER-B32.md 移植剩余模块并组装 Biber，尚未生成 Biber 安装包；试验树预留 1.0.18 前缀不是交付版本。'
new='B3.2 已锁定 107 个 CPAN 发行包、完成 17 个原生模块和 Biber 2.21 组装；45 项直接依赖及实际文献工作流已在 OHOS/QEMU 通过。1.0.18 候选包已签名安装；真机因锁屏暂未验收，解锁后继续 B318 样例，详见 BIBER-B32.md。不要重复构建或覆盖已签名候选包。'
text=text.replace(old,new);start.write_text(text,encoding='utf-8')
snapshot=out/'source-1.0.18';snapshot.mkdir(exist_ok=True);hashes=[]
paths=list((root/'build-support').glob('*biber*'))
paths += [root/p for p in ['build-support/patch-perl-ohos.py','build-support/stage-latexmk.py','build-support/package-resource-release.sh','build-support/sync-baseline.py','build-support/verify-latexmk-payload.py','texstudio-harmony/scripts/texlive/biber_launcher.c','texstudio-harmony/scripts/texlive/latexmk_launcher.c','texstudio-harmony/scripts/texlive/HarmonyCwd.pm','texstudio-harmony/scripts/common/build_texlive_hnp.sh','texstudio-harmony/release.json','BIBER-B32.md','START-HERE.md']]
paths += list(out.glob('*smoke.pl'))+[out/'xs-bootstrap/build.sh']
for path in paths:
    if not path.is_file():continue
    relative=path.relative_to(root);target=snapshot/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    hashes.append(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+relative.as_posix())
(snapshot/'SHA256SUMS.txt').write_text('\n'.join(sorted(hashes))+'\n')
print('Candidate, source snapshot and acceptance boundary recorded.')
