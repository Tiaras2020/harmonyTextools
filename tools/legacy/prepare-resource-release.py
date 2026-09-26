"""Stage a new runtime without changing the locked 1.0.5 dist."""
import hashlib
import json
import os
import pathlib
import shutil
from release_config import release

repo = pathlib.Path(os.environ['BUILD_REPO'])
root = pathlib.Path(os.environ['DELIVERY_ROOT'])
version = release()['version']
profile = os.environ.get('HARMONY_RESOURCE_PROFILE', 'full')
if profile not in ('full', 'slim'): raise SystemExit('Unknown resource build profile')
original = repo/'build'/('full-runtime-v2' if profile == 'full' else 'build-texlive-ohos-dist')
if profile == 'full':
    proof = json.loads((root/'validation/common-resources/result.json').read_text())
    assert proof['hostValidated'] and proof['frozenBaselineUnchanged'] and str(original) == proof['candidate']
candidate = repo/'build'/('resource-release-'+version)
if candidate.exists():
    raise SystemExit('Candidate already exists; inspect before rebuilding')
shutil.copytree(original, candidate, symlinks=True, ignore=shutil.ignore_patterns('.tlpkg-cache', 'map-build', 'reviewed-additions', 'font-adaptations.json'))
cnf = candidate/'texmf/web2c/texmf.cnf'
old = 'TEXMFROOT = /data/service/hnp/texlive.org/texlive_1.0.5'
text = cnf.read_text()
assert text.count(old) == 1
cnf.write_text(text.replace(old, 'TEXMFROOT = /data/service/hnp/texlive.org/texlive_'+version))
if version=='1.0.19':
    import importlib.util
    spec=importlib.util.spec_from_file_location('polish_config',root/'build-support/polish-runtime-config.py')
    config=importlib.util.module_from_spec(spec);spec.loader.exec_module(config)
    cnf.write_text(config.texmf_config(cnf.read_text()))
    driver=candidate/'texmf/dvipdfmx/dvipdfmx.cfg'
    assert not list((candidate/'texmf').rglob('kanjix.map'))
    assert (candidate/'texmf/fonts/map/dvipdfmx/ckx.map').is_file()
    driver.write_text(config.driver_config(driver.read_text()))
report = {'version': version, 'baselineRuntime': str(original), 'candidateRuntime': str(candidate),
          'resourceProfile': profile,
          'runtimeChanges': ['texmf/web2c/texmf.cnf: HNP installation version', 'B2.4 reviewed resources included' if profile == 'full' else 'Frozen slim resource baseline'],
          'fdsanPatchIncluded': False, 'resourceCompatibilityId': release()['compatibilityId']}
if version=='1.0.19':
    report['runtimeChanges'] += ['texmf.cnf: explicit dvipdfmx config and map search paths',
                                 'dvipdfmx.cfg: do not load absent kanjix.map by default']
(root/'validation/resources/candidate-runtime.json').write_text(json.dumps(report,indent=2)+'\n')
print('Candidate resource runtime staged:', candidate)
