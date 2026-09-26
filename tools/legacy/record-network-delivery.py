"""Record verified 1.0.31 delivery after successful device installation."""
from pathlib import Path
import json, hashlib
r=Path(__file__).resolve().parents[1]
sign_path=r/'validation/device-signing-1.0.31/result.json'
sign=json.loads(sign_path.read_text())
assert sign['signature_verified'] and sign['embedded_hnp_unchanged']
evidence=r/'validation/network-1.0.31/device-result.json'
assert evidence.exists() and json.loads(evidence.read_text())['finalCandidateInstalled']
sign['installed']=True
sign['installationEvidence']='validation/network-1.0.31/device-result.json'
sign_path.write_text(json.dumps(sign,indent=2)+'\n')
paths=[r/'artifacts'/sign['signed_file'],r/'artifacts/texlive-1.0.30.hnp']
(r/'artifacts/SHA256SUMS-1.0.31.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in paths))
p=r/'README/START-HERE.md'; s=p.read_text(encoding='utf-8')
s=s.replace('**当前交付 1.0.30：**','**上一版 1.0.30：**',1)
s=s.replace('# 鸿蒙 TeXstudio 开发交接入口\n','# 鸿蒙 TeXstudio 开发交接入口\n\n**当前交付 1.0.31：** Qt HTTPS、DeepSeek 预设和流式回复、手动中文在线校对、打开 HiShell/复制工程目录命令。已签名安装并完成限定真机测试；真实 DeepSeek 账号对话仍需用户在设备填写 Key 后验收。运行包保持 1.0.30，详见 `NETWORK-AI-1.0.31.md`。\n',1)
s=s.replace('当前开发交付版本：**1.0.30 默认完整版','当前开发交付版本：**1.0.31 默认完整版',1)
s=s.replace('1. `LUAHBTEX-B33.md`：最新交付和真机结果；','1. `NETWORK-AI-1.0.31.md`：当前交付和验收边界；`LUAHBTEX-B33.md`：Lua 引擎验收；',1)
s=s.replace('当前应用是 1.0.27 完整版（帮助见 CLI-HELP-1.0.27.md；外部刷新见 REFRESH-CLI-1.0.26.md；工程 CLI 基础见 PROJECT-CLI-1.0.25.md），运行包保持 1.0.21','当前应用是 1.0.31 完整版（先读 NETWORK-AI-1.0.31.md；CLI 帮助见 CLI-HELP-1.0.27.md；文档重载见 RELOAD-CLI-1.0.29.md），运行包为 1.0.30',1)
p.write_text(s,encoding='utf-8')
p=r/'README/DELIVERY-MANIFEST.json'; m=json.loads(p.read_text(encoding='utf-8'))
m['status']='1.0.31_network_scoped_device_validated_real_ai_pending'
m['latestReport']='NETWORK-AI-1.0.31.md'
for name in reversed(['artifacts/'+sign['signed_file'],'artifacts/SHA256SUMS-1.0.31.txt','validation/network-1.0.31/device-result.json']):
    if name not in m['artifacts']: m['artifacts'].insert(0,name)
m['networkAI1031']=json.loads(evidence.read_text())
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Delivery documentation and checksums updated')
