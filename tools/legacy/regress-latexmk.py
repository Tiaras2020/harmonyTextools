"""Host latexmk integration using only the frozen Harmony resource tree."""
import json, os, pathlib, re, shutil, subprocess, time
import xml.etree.ElementTree as ET
root=pathlib.Path(os.environ['DELIVERY_ROOT'])
repo=pathlib.Path(os.environ['BUILD_REPO'])
out=root/'validation/latexmk/host-regression'
out.mkdir(exist_ok=True)
dist=repo/'build/full-runtime-v2'; texmf=dist/'texmf'
web2c=repo/'build/build-texlive-host/texk/web2c'
driver=repo/'build/build-texlive-host/texk/dvipdfm-x/xdvipdfmx'
binpath=out/'bin'; binpath.mkdir(exist_ok=True)
for alias,target in [('pdflatex',web2c/'pdftex'),('xelatex',web2c/'xetex'),('bibtex',web2c/'bibtex'),('xdvipdfmx',driver)]:
    link=binpath/alias
    if not link.exists(): link.symlink_to(target)
env={k:v for k,v in os.environ.items() if not k.startswith(('TEX','BIB','BST','FONT','TFM','VFF','LUAINPUTS'))}
env.update(TEXMFROOT=str(dist),TEXMFDIST=str(texmf),TEXMF=str(texmf),TEXMFCNF=str(texmf/'web2c'),
           TEXMFHOME=str(out/'empty-home'),TEXMFVAR=str(out/'var'),TEXMFCONFIG=str(out/'config'),PATH=str(binpath)+':'+env['PATH'])
for name in ('empty-home','var','config','font-cache'): (out/name).mkdir(exist_ok=True)
fc=ET.Element('fontconfig')
for name in ('opentype','truetype'): ET.SubElement(fc,'dir').text=str(texmf/'fonts'/name)
ET.SubElement(fc,'cachedir').text=str(out/'font-cache')
ET.ElementTree(fc).write(out/'fonts.conf',encoding='utf-8',xml_declaration=True)
env['FONTCONFIG_FILE']=str(out/'fonts.conf')
report={'scope':'host Perl and engines, frozen Harmony resources; not device acceptance','passed':False,'cases':{}}
try:
    for name,mode in [('beamer-zh','-xelatex'),('pgfplots-test','-pdf'),('newpx-test','-pdf'),('bibtex-zh','-xelatex')]:
        work=out/(name+' 中文 空格'); work.mkdir(exist_ok=True)
        for source in (root/'validation/common-resources/fixtures').iterdir():
            if source.suffix in ('.tex','.bib','.csv'): shutil.copy2(source,work)
        command=['/usr/bin/perl','-I'+str(root/'texstudio-harmony/scripts/texlive'),'-MHarmonyCwd',str(root/'validation/latexmk/latexmk.pl'),'-norc',mode,'-recorder','-interaction=nonstopmode','-halt-on-error',name+'.tex']
        def run(label,ok=True):
            proc=subprocess.run(command,cwd=work,env=env,capture_output=True,timeout=180)
            (work/(label+'.stdout')).write_bytes(proc.stdout+proc.stderr)
            assert (proc.returncode==0)==ok,(name,label,proc.returncode)
            return (proc.stdout+proc.stderr).decode(errors='replace')
        run('initial')
        pdf=work/(name+'.pdf'); assert pdf.exists()
        stamp=pdf.stat().st_mtime_ns
        run('incremental'); assert pdf.stat().st_mtime_ns==stamp,'Unchanged PDF was rebuilt'
        if name=='bibtex-zh':
            bib=work/'references.bib'; content=bib.read_text(); bib.write_text(content.replace('{1984}','{1985}'))
            time.sleep(1.1); run('bibliography-edit'); assert '1985' in (work/(name+'.bbl')).read_text()
        log=(work/(name+'.log')).read_text()
        assert not re.search(r'undefined (references|citations)|Missing character:',log)
        for line in (work/(name+'.fls')).read_text().splitlines():
            if line.startswith('INPUT '):
                path=pathlib.Path(line[6:]); path=(work/path).resolve()
                assert path.is_relative_to(texmf.resolve()) or path.is_relative_to(work.resolve()),str(path)
        if name=='newpx-test':
            source=work/(name+'.tex'); original=source.read_text()
            source.write_text(original.replace('\\begin{document}','\\begin{document}\\UndefinedBThreeCommand'))
            run('intentional-error',False); source.write_text(original); run('recovery')
        report['cases'][name]={'automaticPasses':True,'incrementalNoOp':True,'isolatedResources':True,
            'bibliographyEdit':name=='bibtex-zh','errorRecovery':name=='newpx-test'}
    report['passed']=True
except Exception as error: report['error']=str(error)
finally: (out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(not report['passed'])
