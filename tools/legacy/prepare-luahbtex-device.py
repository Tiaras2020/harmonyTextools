"""Create isolated device cases for Lua, font shaping, Chinese and Biber."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
dest = root / 'validation/luahbtex/device-input/B3320'
dest.mkdir(parents=True, exist_ok=True)
tex = r'''% !TeX program = lualatex
\documentclass[UTF8,fontset=fandol]{ctexart}
\usepackage[backend=biber,style=authoryear]{biblatex}
\addbibresource{refs.bib}
\begin{document}
\section{鸿蒙 LuaLaTeX 验收}\label{sec:test}
中文和 English 混排。$\int_0^1 x^2\,dx=\frac13$。
参见第\ref{sec:test}节。中文引用：\autocite{zh}。
\directlua{assert(status.luatex_engine == "luahbtex"); tex.print("Lua execution passed.")}
\printbibliography[title={参考文献}]
\end{document}
'''
for name in ('main.tex', 'app-lua.tex'):
    (dest / name).write_text(tex, encoding='utf-8', newline='\n')
(dest / 'app-after-cancel.tex').write_text(tex.replace('鸿蒙 LuaLaTeX 验收', '取消后 LuaLaTeX 验收'), encoding='utf-8', newline='\n')
(dest / 'refs.bib').write_text('@book{zh,author={{张三}},title={鸿蒙离线文献 FIRSTTITLE},year={2025},publisher={测试出版社}}\n', encoding='utf-8')
(dest / 'harf.tex').write_text(r'''\documentclass{article}
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}[Renderer=HarfBuzz]
\begin{document}HarfBuzz on HarmonyOS: office, affine, café.\end{document}
''', encoding='utf-8')
(dest / 'app-cancel-lua.tex').write_text(r'''% !TeX program = lualatex
\documentclass{article}
\begin{document}
\directlua{local started=os.clock(); while os.clock()-started < 90 do end}
Cancellation fixture.
\end{document}
''', encoding='utf-8')
(dest / 'environment.lua').write_text('''kpse.set_program_name("lualatex")
print("cwd", lfs.currentdir())
print("PWD", os.getenv("PWD"))
print("cache", kpse.expand_var("$TEXMFCACHE"))
print("var", kpse.expand_var("$TEXMFVAR"))
''', encoding='utf-8')
script = '''#!/system/bin/sh
set -eu
cd /storage/Users/currentUser/Download/TeXstudioResourceTest/B3320
luahbtex --version > engine-version.txt 2>&1
lualatex --version > lualatex-version.txt 2>&1
luahbtex --luaonly environment.lua > lua-environment.txt 2>&1
biber --version > biber-version.txt 2> biber-version.stderr
test ! -s biber-version.stderr
lualatex -interaction=nonstopmode -halt-on-error harf.tex > harf-build.log 2>&1
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex > initial.log 2>&1
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex > repeat.log 2>&1
cp refs.bib refs-original.bib
sed 's/FIRSTTITLE/UPDATEDTITLE/g' refs-original.bib > refs.bib
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex > update.log 2>&1
mkdir -p '中文 空格'
cp main.tex '中文 空格/主文献.tex'
cp refs.bib '中文 空格/refs.bib'
cd '中文 空格'
latexmk -lualatex -interaction=nonstopmode -halt-on-error '主文献.tex' > build.log 2>&1
cd ..
printf 'passed\\n' > completed.txt
'''
(dest / 'run.sh').write_text(script, encoding='utf-8', newline='\n')
print(dest)
