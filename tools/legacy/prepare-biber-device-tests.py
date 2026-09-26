"""Prepare self-contained B3.2 device acceptance files, separate from user documents."""
import pathlib
root=pathlib.Path(__file__).resolve().parents[1];dest=root/'validation/biber/device-input/B318';dest.mkdir(parents=True,exist_ok=True)
bib='''@book{parent,author={Parent, Peter},title={中文合集},year={2024},publisher={离线出版社}}
@inbook{child,author={Child, Clara},title={交叉引用章节},crossref={parent},pages={1--9}}
@article{zh,author={{张三} and {李四}},title={鸿蒙中文文献 FIRSTTITLE},journaltitle={中文期刊},year={2025}}
@article{en,author={Example, Alice},title={Offline bibliography},journaltitle={Example Journal},year={2023}}
'''
(dest/'refs-original.bib').write_text(bib,encoding='utf-8');(dest/'refs.bib').write_text(bib,encoding='utf-8')
tex=r'''\documentclass[UTF8,fontset=fandol]{ctexart}
\usepackage[backend=biber,style=authoryear,sorting=nyt]{biblatex}
\addbibresource{refs.bib}
\begin{document}
\section*{Biber 鸿蒙文献验收}
中文引用：\autocite{zh}。英文引用：\autocite{en}。
章节继承：\autocite{child}。
\nocite{*}
\printbibliography[title={参考文献}]
\end{document}
'''
for name in ('main.tex','app-biber.tex'):(dest/name).write_text(tex,encoding='utf-8')
(dest/'app-cancel.tex').write_text(tex.replace('refs.bib','large.bib').replace(r'\autocite{zh}',r'\autocite{entry0}').replace(r'\autocite{en}',r'\autocite{entry1}').replace(r'\autocite{child}',r'\autocite{entry2}'),encoding='utf-8')
with (dest/'large.bib').open('w',encoding='utf-8') as f:
    for i in range(16000):f.write('@article{entry'+str(i)+',author={Author, Alice},title={Cancellation fixture '+str(i)+'},journaltitle={Journal},year={2025}}\n')
script='''#!/system/bin/sh
set -eu
cd /storage/Users/currentUser/Download/TeXstudioResourceTest/B318
biber --version > version.txt 2>&1
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex > initial.log 2>&1
cp main.bbl initial.bbl
biber --validate-control --validate-datamodel main > direct-biber.log 2>&1
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex > settle.log 2>&1
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex > repeat.log 2>&1
sed 's/FIRSTTITLE/UPDATEDTITLE/g' refs-original.bib > refs.bib
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex > update.log 2>&1
cp main.bbl updated.bbl
cp refs.bib refs-updated.bib
printf '@article{broken,title={unclosed\n' > refs.bib
if latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex > invalid.log 2>&1; then
    printf 'Invalid bibliography unexpectedly succeeded\n' > failed.txt
    cp refs-updated.bib refs.bib
    exit 1
fi
cp refs-updated.bib refs.bib
latexmk -g -xelatex -interaction=nonstopmode -halt-on-error main.tex > recovery.log 2>&1
printf 'passed\n' > completed.txt
'''
(dest/'run.sh').write_text(script,encoding='utf-8',newline='\n')
terminal=dest/'中文 空格';terminal.mkdir(exist_ok=True)
(terminal/'主文献.tex').write_text(tex,encoding='utf-8')
for name in ('refs.bib','refs-original.bib'):(terminal/name).write_text(bib,encoding='utf-8')
script=script.replace('cd /storage/Users/currentUser/Download/TeXstudioResourceTest/B318','cd "/storage/Users/currentUser/Download/TeXstudioResourceTest/B318/中文 空格"')
script=script.replace('main.tex','"主文献.tex"').replace('main.bbl','"主文献.bbl"').replace('--validate-datamodel main >','--validate-datamodel "主文献" >')
(dest/'run.sh').write_text(script,encoding='utf-8',newline='\n')
print(dest)
