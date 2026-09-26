"""Package locked, unchanged luatex-cn sources into the new import profile."""
import hashlib, json, zipfile
from pathlib import Path
root = Path(__file__).resolve().parents[1]
upstream = root/'validation/luatex-cn/upstream'
files = {}
for path in sorted((upstream/'tex').rglob('*')):
    if not path.is_file(): continue
    assert path.suffix in ('.lua','.sty','.cls','.cfg'), path
    files['texmf/tex/luatex/luatex-cn/'+path.relative_to(upstream/'tex').as_posix()] = path.read_bytes()
files['texmf/doc/luatex-cn/LICENSE.txt'] = (upstream/'LICENSE').read_bytes()
manifest = {'schema':1, 'profile':'additive-lua-v1', 'id':'luatex-cn', 'version':'0.4.1',
    'title':'luatex-cn v0.4.1 Lua 用户宏包', 'compatibilityId':'tl2025-harmony-baseline-1.0.5',
    'upstreamCommit':'3b9297f012d71aa148783695bf7942a37a3c281b',
    'files':{name:{'size':len(data),'sha256':hashlib.sha256(data).hexdigest()} for name,data in files.items()}}
archive = root/'artifacts/luatex-cn-v0.4.1-user-resources.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    for name,data in files.items(): z.writestr(name,data)
out = root/'validation/lua-cli-1.0.23'
(out/'lua-package.json').write_text(json.dumps({'path':str(archive.relative_to(root)), 'files':len(files),
    'luaFiles':sum(n.endswith('.lua') for n in files), 'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2)+'\n')
demo = out/'LuaCli23'; demo.mkdir(exist_ok=True)
(demo/'main.tex').write_text('''\\documentclass{article}
\\usepackage{fontspec}
\\setmainfont{NotoSerifCJK-Regular.ttc}[Path=/system/fonts/,FontIndex=3]
\\usepackage[style=taiwan]{luatex-cn}
\\begin{document}
用户资源中的 Lua 宏包。中文與英文 Lua resource import works.
\\end{document}
''',encoding='utf-8')
(demo/'simple.tex').write_text('\\documentclass{article}\n\\begin{document}CLI application build works.\\end{document}\n')
(demo/'failure.tex').write_text('\\documentclass{article}\n\\begin{document}\\UndefinedCliTestCommand\\end{document}\n')
print('Packaged',len(files),'files, including',sum(n.endswith('.lua') for n in files),'Lua sources')
