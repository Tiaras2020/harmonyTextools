"""Record scoped final-device evidence and retire only this run's candidate HAPs."""
import hashlib
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / 'validation/ui-polish-1.0.22'
def read(p):
    return json.loads(p.read_text(encoding='utf-8'))
def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

sign = read(root / 'validation/device-signing-1.0.22/result.json')
assert sign['installed'] and sign['signature_verified']
delta = read(out / 'source-delta/manifest.json')
for name, digest in delta['files'].items():
    assert hashlib.sha256((root / 'texstudio-harmony' / name).read_bytes()).hexdigest() == digest, name
screens = ['picker', 'sync-start', 'single-hold', 'touch-double', 'mouse-forward',
           'mouse-reverse', 'touch-drag', 'pinch', 'clean-menu', 'clean-done',
           'link-ready', 'link-after', 'text-select']
for name in screens:
    file = 'ui22-final-' + name + '.png'
    shutil.copy2(root / 'validation/compat-review-2026-09-25' / file, out / file)
result = {
    'date': '2026-09-25', 'version': '1.0.22', 'runtime_version': '1.0.21',
    'status': 'scoped_ui_device_validated', 'signed_sha256': sign['sha256'],
    'device': '6UZ0226107000081',
    'method': 'Installed signed final candidate 9; real-device uinput mouse and uitest/uinput touch injection, screenshots and collected fixture files.',
    'passed': {
        'appearance': 'White full-width menu, all twelve menus visible; flat Colibre icons and light dropdown menu.',
        'external_pdf_action': 'Hidden in final PDF toolbar; source disables the shared action.',
        'mouse_forward_sync': 'Source line 7 double click selects word and locates second PDF page.',
        'mouse_reverse_sync': 'PDF second-page line double click locates source line 9.',
        'touch_double_sync': 'Normal injected double tap locates source line 5.',
        'touch_single_and_hold': 'Single tap and 800 ms hold do not jump or open magnifier.',
        'touch_drag': '900 physical pixel drag scrolls content correspondingly without source jump.',
        'pinch': 'Two-finger gesture changes zoom from 88 to 107 percent.',
        'pdf_link': 'Single touch activates internal link from page 1 to page 2; source remains on line 1.',
        'clean_rebuild': 'Exactly three engine options. XeLaTeX recovered injected old BibTeX failure cache, producing one-page PDF with three references.',
        'preserved_files': read(out / 'fixture-check.json'),
        'source_snapshot': 'All 16 manifest hashes match working source.'
    },
    'source_verified': ['Open-containing-folder actions guarded out in editor tabs and both structure context-menu implementations.'],
    'limits': [
        'Physical mouse and trackpad hardware feel awaits user feedback; injected real-device events are not peripheral hardware acceptance.',
        'Injected right button did not open the context menu, so folder action removal is source/build verified, not a context-menu screenshot claim.',
        'Additional finger text-selection probe in explicit I-beam mode showed no selection; baseline not established. Presentation mode untested.',
        'Clean menu device recovery exercised XeLaTeX only; pdfLaTeX/LuaLaTeX share implementation but were not separately exercised here.',
        'No full TeX Live, all-window-size or LuaTeX-specific UX acceptance.'
    ],
    'screenshots': ['ui22-final-' + n + '.png' for n in screens]
}
write(out / 'device-result.json', result)
manifest_path = root / 'DELIVERY-MANIFEST.json'
manifest = read(manifest_path)
manifest['status'] = '1.0.22_scoped_ui_device_validated'
manifest['latestReport'] = 'UI-POLISH-1.0.22.md'
for key, values in {
    'artifacts': ['artifacts/TeXstudioHarmony-1.0.22-arm64-device-signed.hap', 'artifacts/SHA256SUMS-1.0.22.txt'],
    'evidence': ['validation/ui-polish-1.0.22/device-result.json', 'validation/ui-polish-1.0.22/fixture-check.json', 'validation/device-signing-1.0.22/result.json', 'validation/device-signing-1.0.22/device-profile-check.json']
}.items():
    manifest[key] = values + [v for v in manifest[key] if v not in values]
manifest['uiPolish22'] = {'version': '1.0.22', 'runtimeVersion': '1.0.21', 'signedSha256': sign['sha256'], 'report': 'UI-POLISH-1.0.22.md', 'result': 'validation/ui-polish-1.0.22/device-result.json', 'scope': 'UI and injected real-device input only; see result limits.'}
write(manifest_path, manifest)
start = root / 'START-HERE.md'
s = start.read_text(encoding='utf-8')
intro = '**当前界面交付 1.0.22：** 已签名安装到新设备，复用内容不变的 1.0.21 运行包。菜单、图标、双向定位、触摸浏览与旧失败缓存恢复的结果及边界见 `UI-POLISH-1.0.22.md`。下一步由用户体验实体鼠标/触控板与窗口布局，再推进 GitHub 整理；暂不扩展 LuaTeX 体验。\n\n'
if intro not in s:
    s = s.replace('# 鸿蒙 TeXstudio 开发交接入口\n\n', '# 鸿蒙 TeXstudio 开发交接入口\n\n' + intro)
s = s.replace('**当前交付：1.0.21', '**运行资源基线：1.0.21')
s = s.replace('当前开发交付版本：**1.0.21 默认完整版**', '当前开发交付版本：**1.0.22 默认完整版（运行包 1.0.21）**')
s = s.replace('当前应用是 1.0.21 完整版', '当前应用是 1.0.22 完整版，运行包保持 1.0.21，界面改动和真机验收边界先读 UI-POLISH-1.0.22.md')
start.write_text(s, encoding='utf-8')

# All paths are resolved and checked before deleting any candidate package.
targets = []
for i in range(1, 9):
    parent = (out / f'candidate-{i}').resolve()
    assert parent.is_relative_to(root.resolve())
    for suffix in ('device-signed', 'unsigned'):
        p = (parent / f'TeXstudioHarmony-1.0.22-arm64-{suffix}.hap').resolve()
        assert p.parent == parent and p.is_relative_to(out.resolve())
        if p.exists():
            targets.append((p, p.stat().st_size))
cleanup = {'scope': 'Only self-generated superseded candidate 1-8 HAPs; metadata retained; previous releases and WSL untouched.', 'files': [{'path': str(p.relative_to(root)), 'bytes': n} for p, n in targets], 'bytes_freed': sum(n for _, n in targets)}
for p, _ in targets:
    p.unlink()
write(out / 'candidate-cleanup.json', cleanup)
print('Recorded final evidence; removed candidate HAP bytes:', cleanup['bytes_freed'])
