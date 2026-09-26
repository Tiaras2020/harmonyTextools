"""Lock CPAN release archives and the required Biber runtime/build dependency closure."""
import concurrent.futures,gzip,hashlib,json,os,pathlib,re,tarfile,urllib.request
root=pathlib.Path(__file__).resolve().parents[1];out=root/'validation/biber';downloads=out/'downloads';downloads.mkdir(exist_ok=True)
def fetch(url,path):
    if not path.exists():
        with urllib.request.urlopen(url,timeout=90) as r: data=r.read()
        path.write_bytes(data)
    return path.read_bytes()
indexpath=downloads/'02packages.details.txt.gz'
index=gzip.decompress(fetch('https://www.cpan.org/modules/02packages.details.txt.gz',indexpath)).decode()
packages={line.split()[0]:line.split()[2] for line in index.split('\n\n',1)[1].splitlines() if len(line.split())==3}
repo=pathlib.Path(os.environ['BUILD_REPO']);lib=repo/'build/perl-ohos-5.40.3/lib'
source=(out/'Build.PL').read_text();section=source.split('    requires => {',1)[1].split('\n                },',1)[0]
pending=dict(re.findall(r"'([^']+)'\s*=>\s*'?([\d.]+)'?",section))
pending.update({'Module::Build':'0.38','Config::AutoConf':'0.15','ExtUtils::LibBuilder':'0.02'})
pending=[(module,str(minimum),'Biber/bootstrap','runtime/build') for module,minimum in pending.items()]
records={};core={};edges=[];unresolved=[];seen=set();constraints=[]
def archive(path):
    url='https://www.cpan.org/authors/id/'+path;local=downloads/path.rsplit('/',1)[1]
    data=fetch(url,local)
    with tarfile.open(local) as t:
        names=t.getnames();meta_names=sorted((n for n in names if n.endswith('/META.json')),key=lambda n:n.count('/'))
        if meta_names: meta=json.load(t.extractfile(meta_names[0]))
        else:
            import yaml
            meta_names=sorted((n for n in names if n.endswith('/META.yml')),key=lambda n:n.count('/'))
            meta=yaml.safe_load(t.extractfile(meta_names[0])) if meta_names else {}
        prereqs=meta.get('prereqs',{})
        deps={};by_phase={}
        for phase in ('runtime','configure','build'):
            by_phase[phase]={str(k):str(v) for k,v in ((prereqs.get(phase) or {}).get('requires',{})).items()}
        for key,phase in [('requires','runtime'),('configure_requires','configure'),('build_requires','build')]:
            by_phase[phase].update({str(k):str(v) for k,v in (meta.get(key) or {}).items()})
        for values in by_phase.values():deps.update(values)
        license_value=meta.get('license','unknown');license_evidence=None
        if license_value=='unknown':
            for n in names:
                if n.endswith('/README') or n.endswith('/lib/Number/Compare.pm'):
                    member=t.extractfile(n)
                    if member and re.search(r'same terms as Perl',member.read().decode(errors='replace'),re.I):
                        license_value=['perl_5'];license_evidence=n;break
        return {'distribution':meta.get('name',local.name),'version':str(meta.get('version','unknown')),'url':url,
          'archive':local.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'license':license_value,'licenseEvidence':license_evidence,
          'containsXS':any(n.endswith('.xs') for n in names),'dynamicConfig':bool(meta.get('dynamic_config',False)),
          'requirements':{str(k):str(v) for k,v in deps.items()},'requirementsByPhase':by_phase,'provides':meta.get('provides',{})}
while pending:
    batch={};current=pending;pending=[]
    for module,minimum,required_by,phase in current:
        constraints.append({'module':module,'constraint':minimum,'requiredBy':required_by,'phase':phase})
        if module in seen:continue
        seen.add(module)
        if module=='perl':core[module]={'minimum':str(minimum),'source':'target Perl 5.40.3'};continue
        if module=='DynaLoader':
            core[module]={'minimum':str(minimum),'source':'Perl core extension','status':'disabled in baseline; must resolve bootstrap support for dependent XS modules'};continue
        pm=lib/(module.replace('::','/')+'.pm')
        if pm.is_file():
            core[module]={'minimum':str(minimum),'path':str(pm),'note':'bundled module; version/loading must be verified on target'};continue
        path=packages.get(module)
        if not path:unresolved.append({'module':module,'minimum':str(minimum)});continue
        edges.append({'module':module,'minimum':str(minimum),'archive':path.rsplit('/',1)[1]})
        if path not in records:batch[path]=module
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for path,record in zip(batch,pool.map(archive,batch)):
            records[path]=record
            for phase,requirements in record['requirementsByPhase'].items():
                pending.extend((module,minimum,record['distribution'],phase) for module,minimum in requirements.items())
    print('Locked distributions:',len(records),'pending modules:',len(pending),flush=True)
result={'schema':2,'biberVersion':'2.21','biblatexVersion':'3.21','perlVersion':'5.40.3',
 'scope':'CPAN metadata runtime/configure/build requires closure; dynamic requirements must be reconciled during builds',
 'indexSha256':hashlib.sha256(indexpath.read_bytes()).hexdigest(),'moduleRequirements':edges,'allVersionConstraints':constraints,'bundledModules':core,
 'unresolved':unresolved,'distributions':sorted(records.values(),key=lambda r:r['distribution'])}
(out/'dependencies.lock.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'distributions':len(records),'xs':sum(r['containsXS'] for r in records.values()),'unresolved':unresolved}))
if unresolved:raise SystemExit(1)
