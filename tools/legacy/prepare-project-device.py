from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1]
out=r/'validation/project-cli-1.0.25/ProjectCli25'
(out/'sub').mkdir(parents=True,exist_ok=True)
(out/'中文 空格').mkdir(exist_ok=True)
(out/'main.tex').write_text(r'''\documentclass{article}
\begin{document}
Project CLI main. \input{sub/section}
\end{document}
''',encoding='utf-8')
(out/'sub/section.tex').write_text('Included section.\n',encoding='utf-8')
(out/'second.tex').write_text(r'\documentclass{article}\begin{document}Second project document.\end{document}',encoding='utf-8')
(out/'fail.tex').write_text(r'\documentclass{article}\begin{document}\unknownprojectcommand\end{document}',encoding='utf-8')
(out/'slow.tex').write_text(r'\documentclass{article}\begin{document}\newcount\n\loop\advance\n by1\ifnum\n<1000000000\repeat Done.\end{document}',encoding='utf-8')
(out/'中文 空格/chinese.tex').write_text(r'''\documentclass{ctexart}
\begin{document}
概率空间与测度，这是中文段落。繁體中文與數學。
The correct English sentence. This is mispelll.
中文hello中文，中文mispelll中文。
\end{document}
''',encoding='utf-8')
shutil.copy2(r/'tools/texstudioctl.py',out/'texstudioctl.py')
print(out)
