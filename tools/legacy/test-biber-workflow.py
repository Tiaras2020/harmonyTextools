"""Exercise real Biber CLI using OHOS Perl and official 2.21 BCF structure."""
import hashlib,json,os,pathlib,re,subprocess,xml.etree.ElementTree as ET
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO'])
out=pathlib.Path(os.environ.get('BIBER_TEST_OUT',root/'validation/biber'))/'workflow';out.mkdir(exist_ok=True)
case=pathlib.Path(os.environ.get('BIBER_TEST_CASE',repo/'build/biber-workflow/中文 文献测试'));case.mkdir(parents=True,exist_ok=True)
source=repo/'build/biber-2.21/t/tdata/basic-misc.bcf';tree=ET.parse(source);ns='https://sourceforge.net/projects/biblatex';q=lambda n:'{'+ns+'}'+n
ET.register_namespace('bcf',ns)
bibdata=tree.find(q('bibdata'));bibdata.clear();bibdata.set('section','0')
ET.SubElement(bibdata,q('datasource'),{'type':'file','datatype':'bibtex'}).text='参考 文献.bib'
section=tree.find(q('section'));section.clear();section.set('number','0')
keys=['zulu','中文条目','child','alpha','parent']
for index,key in enumerate(keys,1):ET.SubElement(section,q('citekey'),{'order':str(index),'intorder':'1'}).text=key
tree.write(case/'测试.bcf',encoding='utf-8',xml_declaration=True)
bib='''@book{parent, author={Parent, Peter}, title={中文合集}, year={2024}, publisher={离线出版社}, sortkey={P}}
@inbook{child, author={Child, Clara}, title={交叉引用章节}, crossref={parent}, pages={1--9}, sortkey={C}}
@article{alpha, author={Alpha, Alice}, title={Alpha research}, journaltitle={Offline Journal}, date={2020-02-29}, sortkey={A}}
@article{zulu, author={Zulu, Zoe}, title={Zulu research}, journaltitle={Offline Journal}, year={2026}, sortkey={Z}}
@article{中文条目, author={张三 and 李四}, title={鸿蒙中文文献}, journaltitle={中文期刊}, year={2025}, sortkey={M}}
'''
bibpath=case/'参考 文献.bib';bibpath.write_text(bib,encoding='utf-8')
runner=root/'build-support/run-biber-qemu.sh';results=[]
def run(label,args,success=True):
    p=subprocess.run(['bash',str(runner),*args],cwd=case,capture_output=True,timeout=240)
    (out/(label+'.stdout')).write_bytes(p.stdout);(out/(label+'.stderr')).write_bytes(p.stderr)
    ok=(p.returncode==0) if success else (p.returncode!=0)
    results.append({'test':label,'exitCode':p.returncode,'passed':ok});print(label,p.returncode,flush=True)
    (out/'result.json').write_text(json.dumps({'complete':False,'tests':results},indent=2)+'\n')
    if not ok:raise RuntimeError(label+': '+p.stderr.decode(errors='replace')[-2000:])
    return p
p=run('version',['--version']);assert b'2.21' in p.stdout
args=['--validate-control','--validate-datamodel','--sortlocale=en_US','测试.bcf']
run('initial',args)
bblpath=case/'测试.bbl';bbl=bblpath.read_text(encoding='utf-8')
entries=re.findall(r'\\entry\{([^}]+)\}',bbl)
assert entries==['alpha','child','中文条目','parent','zulu'],entries
assert '鸿蒙中文文献' in bbl and '张三' in bbl and '李四' in bbl
child=bbl.split('\\entry{child}',1)[1].split('\\endentry',1)[0]
assert r'\field{booktitle}{中文合集}' in child and r'\field{year}{2024}' in child,child
initial=bblpath.read_bytes();run('repeat',args);assert initial==bblpath.read_bytes(),'unchanged input changes BBL'
updated=bib.replace('鸿蒙中文文献','鸿蒙更新文献');bibpath.write_text(updated,encoding='utf-8')
run('update',args);assert '鸿蒙更新文献' in bblpath.read_text(encoding='utf-8')
bibpath.write_text('@article{broken, title={unclosed\n',encoding='utf-8')
try:run('invalid',args,success=False)
finally:bibpath.write_text(updated,encoding='utf-8')
run('recovery',args);assert '鸿蒙更新文献' in bblpath.read_text(encoding='utf-8')
for name in ('测试.bcf','测试.bbl','测试.blg','参考 文献.bib'):
    (out/name).write_bytes((case/name).read_bytes())
report={'complete':True,'passed':True,'scope':'Biber CLI on OHOS Perl under QEMU/device libc; no TeX PDF or device acceptance',
 'biberVersion':'2.21','checks':['Chinese and spaces in paths','UTF-8 names and titles','explicit sort keys','crossref inheritance',
 'BCF/schema validation','date processing','deterministic repeat','bibliography update','invalid input failure','recovery'],
 'tests':results,'bblSha256':hashlib.sha256(bblpath.read_bytes()).hexdigest()}
(out/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
