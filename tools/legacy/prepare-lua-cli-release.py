import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
release = root/'texstudio-harmony/release.json'
data = json.loads(release.read_text(encoding='utf-8'))
assert data['version'] in ('1.0.22', '1.0.23')
data.update(version='1.0.23', versionCode=1000023)
release.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
for old, new in [('build-ui-polish.sh','build-lua-cli.sh'),('stage-ui-app.sh','stage-lua-cli-app.sh'),
                 ('assemble-ui-package.py','assemble-lua-cli-package.py'),('check-ui-package.py','check-lua-cli-package.py')]:
    text = (root/'build-support'/old).read_text(encoding='utf-8')
    text = text.replace('ui-polish-1.0.22','lua-cli-1.0.23').replace('1.0.22','1.0.23').replace('1000022','1000023')
    text = text.replace('build-ui-polish.sh','build-lua-cli.sh').replace('check-ui-package.py','check-lua-cli-package.py')
    (root/'build-support'/new).write_text(text, encoding='utf-8', newline='\n')
