"""Exercise reviewed file exceptions through the production C++ importer."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile

root = Path(os.environ['DELIVERY_ROOT'])
cli = root/'validation/resources/resource-cli'
compat = json.loads((root/'texstudio-harmony/release.json').read_text())['compatibilityId']
checks = []
with tempfile.TemporaryDirectory(prefix='harmony-common-profile-') as temp:
    temp = Path(temp)
    cases = [
        ('texmf/tex/latex/beamer/icon.pdf', True),
        ('texmf/tex/latex/beamer/icon.eps', True),
        ('texmf/tex/latex/translator/test.dict', True),
        ('texmf/tex/latex/newpx/newpx.fontspec', True),
        ('texmf/tex/latex/other/icon.pdf', False),
        ('texmf/tex/latex/other/test.dict', False),
        ('texmf/tex/latex/other/test.fontspec', False),
        ('texmf/tex/latex/beamer/tool.sh', False),
        ('texmf/tex/latex/base/latex.ltx', False),
        ('texmf/web2c/texmf.cnf', False),
        ('texmf/tex/latex/beamer/../../base/latex.ltx', False),
        ('bin/xelatex', False),
    ]
    for index, (name, allowed) in enumerate(cases):
        for profile in ('runtime-extension-v1', 'runtime-extension-v2'):
            data = b'reviewed data'
            manifest = {'schema':1, 'profile':profile, 'id':'boundary-test',
                        'version':str(index), 'compatibilityId':compat,
                        'files':{name:{'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}}}
            archive = temp/'test.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('manifest.json', json.dumps(manifest))
                z.writestr(name, data)
            p = subprocess.run([str(cli),'import',str(temp/str(index)/profile),str(archive)],capture_output=True,text=True)
            assert (p.returncode == 0) == (allowed and profile.endswith('v2')), (name,profile,p.stdout,p.stderr)
            checks.append({'path':name,'profile':profile,'accepted':p.returncode == 0})
report = {'passed':True,'checks':checks}
(root/'validation/common-resources/profile-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print('Passed', len(checks), 'production importer boundary checks')
