from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];b=r/'validation/refresh-cli-1.0.26/ProjectCli26';b.mkdir(parents=True,exist_ok=True)
(b/'main.tex').write_text(r'''\documentclass{article}
\usepackage{hyperref}
\begin{document}
BEFORE external edit. See section \ref{sec:one}; unresolved \ref{missing}.
\section{One}\label{sec:one}
\end{document}
''',encoding='utf-8')
(b/'fail.tex').write_text(r'\documentclass{article}\begin{document}\undefinedcommand\end{document}'+'\n')
shutil.copy2(r/'tools/texstudioctl.py',b/'texstudioctl.py')
shutil.copy2(r/'build-support/device-refresh-probe.py',b/'probe.py')
