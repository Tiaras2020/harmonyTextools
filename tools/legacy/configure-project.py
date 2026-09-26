import json, os, pathlib
repo=pathlib.Path(os.environ['BUILD_REPO'])
p=repo/'texstudio_harmony/build-profile.json5'
cfg=json.loads(p.read_text())
cfg['app']['signingConfigs']=[]
for product in cfg['app']['products']:
    product.pop('signingConfig', None)
    product['targetSdkVersion']='6.1.1(24)'
p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
p=repo/'texstudio_harmony/entry/build-profile.json5'
p.write_text(p.read_text().replace('"x86_64",',''))
(repo/'texstudio_harmony/local.properties').write_text('sdk.dir='+os.environ['TOOL_HOME']+'/sdk\n')
p=repo/'scripts/texlive/build_pack_texmf.sh'
s=p.read_text().replace('TLNET_MIRROR="https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/archive"','TLNET_MIRROR="https://mirrors.tuna.tsinghua.edu.cn/tex-historic-archive/systems/texlive/2025/tlnet-final/archive"')
p.write_text(s)
print('Configured API 24 target, API 20 minimum, ARM64 and unsigned HAP; pinned TeX Live 2025 packages.')
p=repo/'texstudio_harmony/oh-package.json5'
cfg=json.loads(p.read_text())
# The requested entry HAP does not build the separate ohosTest target.
for name in ('@ohos/hypium','@ohos/hamock'):
    cfg.get('devDependencies',{}).pop(name,None)
p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
