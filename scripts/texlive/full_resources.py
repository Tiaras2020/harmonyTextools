"""Pinned TeX Live resource planning and verified, non-executing extraction.

No upstream installation actions or scripts are executed. Existing runtime files
are frozen; this tool writes only to a new candidate tree and a dedicated cache.
"""
import argparse
import concurrent.futures
import hashlib
import json
import lzma
import pathlib
import re
import shutil
import tarfile
import urllib.request


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def read_database(data):
    packages = {}
    for block in data.split('\n\n'):
        p = {'depend': [], 'execute': [], 'runfiles': [], 'runBlocks': 0}
        section = ''
        for line in block.splitlines():
            if line.startswith(' '):
                if section == 'runfiles': p['runfiles'].append(line.strip().split(' ', 1)[0])
                continue
            key, _, value = line.partition(' ')
            section = key
            if key in ('depend', 'execute'): p[key].append(value)
            elif key == 'runfiles':
                match = re.search(r'\bsize=(\d+)', value)
                p['runBlocks'] = int(match[1]) if match else 0
            elif key not in ('docfiles', 'srcfiles', 'binfiles', 'longdesc'): p[key] = value
        if 'name' in p:
            if p['name'] in packages: raise ValueError('Duplicate package: '+p['name'])
            packages[p['name']] = p
    return packages


def relative(name):
    if name.startswith('RELOC/'): return name[6:]
    if name.startswith('texmf-dist/'): return name[11:]
    return None


def safe_path(name):
    return (bool(name) and not name.startswith('/') and not any(c in name for c in '\\:\x00')
            and all(x not in ('', '.', '..') for x in name.split('/')))


def path_allowed(name, policy):
    if not safe_path(name): return False
    if not any(name.startswith(p) for p in policy['allowedPrefixes']): return False
    if any(name.startswith(p) for p in policy['blockedPrefixes']): return False
    # CMap files often have no extension; other unknown file types need review.
    if name.startswith('fonts/cmap/'): return True
    extension = pathlib.PurePosixPath(name).suffix.lstrip('.').lower()
    return extension in policy['allowedExtensions'] or any(name.startswith(prefix) and extension in extensions
        for prefix,extensions in policy.get('reviewedResourceExtensions',{}).items())


def select_runfiles(p, policy):
    """Omit only explicitly reviewed optional backends; unknown files still fail."""
    rules=policy.get('reviewedPackages',{}).get(p.get('name',''),{}).get('omitPrefixes',{})
    if any(not safe_path(prefix.rstrip('/')) or not prefix.endswith('/') or not reason for prefix,reason in rules.items()):
        raise ValueError('Invalid reviewed omission rule')
    selected=[]; omitted={}
    for name in p['runfiles']:
        rel=relative(name)
        reason=next((reason for prefix,reason in rules.items() if rel and rel.startswith(prefix)),None)
        if reason: omitted[name]=reason
        else: selected.append(name)
    return selected,omitted


def plan(db, policy, pinned):
    records = {}
    def visit(name, parent=None):
        if name in records:
            if parent and parent not in records[name]['requestedBy']: records[name]['requestedBy'].append(parent)
            return
        r = records[name] = {'status':'candidate', 'reasons':[], 'requestedBy':[parent] if parent else []}
        if name.endswith('.ARCH'):
            r['status'] = 'provided' if name[:-5] in policy['nativeProviders'] else 'excluded'
            r['reasons'] = ['Existing Harmony native provider' if r['status']=='provided' else 'No validated Harmony native provider']
            return
        if name not in db:
            r.update(status='unresolved', reasons=['Not found in pinned repository']); return
        p = db[name]
        r.update(revision=p.get('revision'), license=p.get('catalogue-license','unspecified'),
                 downloadBytes=int(p.get('containersize',0)), expandedEstimate=p['runBlocks']*4096,
                 checksum=p.get('containerchecksum'), execute=p['execute'])
        if name in policy['blockedCollections']:
            r.update(status='excluded',reasons=[policy['blockedCollections'][name]]); return
        if p.get('category') in ('Scheme','Collection'):
            r['status'] = 'group'
        elif name in pinned:
            r.update(status='frozen',reasons=['Existing baseline package retained without overwrite'])
        elif name in policy['requiresTools']:
            r.update(status='excluded',reasons=['Missing tools: '+', '.join(policy['requiresTools'][name])])
        else:
            files,omitted = select_runfiles(p,policy)
            if omitted: r['omittedOptionalFiles']=omitted
            invalid = [f for f in files if relative(f) is None or not path_allowed(relative(f),policy)]
            actions = [a for a in p['execute'] if not re.match(r'^add(?:Mixed)?Map\s+\S+$',a)]
            description = p.get('shortdesc','').lower()
            if invalid or actions or re.search(r'\b(luatex|lualatex|context|python|perl|ghostscript|pstricks|metapost|shell|gnuplot|asymptote)\b',description):
                r.update(status='pending',reasons=['Requires capability review'], unsupportedFiles=invalid, unsupportedActions=actions)
            elif not files:
                r.update(status='pending',reasons=['No supported runtime files'])
        if name in policy['conditional']:
            r['conditions'] = policy['conditional'][name]
        if name in policy.get('reviewedPackages',{}):
            r['reviewedFeatures']=policy['reviewedPackages'][name].get('features',[])
        for dep in p['depend']: visit(dep,name)
    for root in policy['roots']: visit(root)
    # Reject the dependent as well, not just a missing mandatory dependency.
    changed=True
    while changed:
        changed=False
        for name,r in records.items():
            if r['status'] != 'candidate': continue
            blocked=[d for d in db[name]['depend'] if records[d]['status'] not in ('candidate','frozen','provided','group')]
            if blocked:
                r.update(status='pending',reasons=['Unsatisfied dependencies'],blockedDependencies=blocked); changed=True
    counts={s:sum(r['status']==s for r in records.values()) for s in sorted({r['status'] for r in records.values()})}
    selected=[n for n,r in records.items() if r['status']=='candidate']
    return {'schema':1,'metadataSha256':policy['metadataSha256'],'policySha256':hashlib.sha256(json.dumps(policy,sort_keys=True).encode()).hexdigest(),
            'supportClaim':policy['supportClaim'],'counts':counts,'packages':dict(sorted(records.items())),
            'selected':sorted(selected),'downloadBytes':sum(records[n]['downloadBytes'] for n in selected),
            'expandedEstimate':sum(records[n]['expandedEstimate'] for n in selected)}


def download(name, p, cache, repository):
    path=cache/(name+'.tar.xz')
    expected=p.get('containerchecksum','')
    if not re.fullmatch('[0-9a-f]{128}',expected): raise ValueError('Missing SHA512: '+name)
    if path.exists():
        if digest(path,'sha512') != expected or path.stat().st_size != int(p['containersize']):
            raise ValueError('Cached archive checksum/size mismatch: '+name)
        return path
    temp=path.with_suffix('.partial')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(repository+'/archive/'+path.name,timeout=90) as response, open(temp,'wb') as out:
                shutil.copyfileobj(response,out)
            if temp.stat().st_size != int(p['containersize']) or digest(temp,'sha512') != expected:
                raise ValueError('Downloaded archive checksum/size mismatch: '+name)
            temp.replace(path); return path
        except Exception:
            if attempt==2: raise


def extract_package(archive, p, tree, policy):
    selected,omitted=select_runfiles(p,policy)
    expected={relative(f) for f in p['runfiles']}
    selected={relative(f) for f in selected}
    if None in expected or any(not safe_path(f) for f in expected) or any(not path_allowed(f,policy) for f in selected):
        raise ValueError('Unreviewed resource path')
    found=set(); total=0; written=0
    with tarfile.open(archive,'r:xz') as tar:
        for member in tar:
            raw=member.name
            if not safe_path(raw.rstrip('/')): raise ValueError('Unsafe archive path: '+raw)
            if member.isdir(): continue
            if not member.isfile(): raise ValueError('Links and special files are forbidden: '+raw)
            # Relocated archive members may already be relative to texmf-dist.
            name=relative(raw)
            if name is None and p.get('relocated')=='1' and not raw.startswith('tlpkg/'): name=raw
            if raw.startswith('tlpkg/tlpobj/') and raw.endswith('.tlpobj'): continue
            if name not in expected or name in found: raise ValueError('Unexpected/duplicate member: '+raw)
            if member.size > policy['limits']['maxFileBytes']: raise ValueError('Oversized resource: '+raw)
            total+=member.size
            if total>policy['limits']['maxExpandedBytes']: raise ValueError('Expanded package limit exceeded')
            found.add(name)
            if name not in selected: continue
            target=tree/name
            if target.exists(): raise ValueError('Resource collision: '+name)
            target.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(member) as inp, open(target,'xb') as out: shutil.copyfileobj(inp,out)
            if target.stat().st_size != member.size: raise ValueError('Short archive read: '+raw)
            written+=member.size
    if found != expected: raise ValueError('Missing runtime files: '+str(expected-found))
    return written,len(selected)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--metadata',type=pathlib.Path,required=True)
    parser.add_argument('--policy',type=pathlib.Path,default=pathlib.Path(__file__).with_name('resource-policy.json'))
    parser.add_argument('--baseline-cache',type=pathlib.Path,required=True)
    parser.add_argument('--report',type=pathlib.Path,required=True)
    parser.add_argument('--cache',type=pathlib.Path)
    parser.add_argument('--stage',type=pathlib.Path)
    args=parser.parse_args()
    policy=json.loads(args.policy.read_text())
    if digest(args.metadata)!=policy['metadataSha256']: raise ValueError('Pinned metadata checksum mismatch')
    db=read_database(lzma.decompress(args.metadata.read_bytes()).decode('utf-8'))
    if 'release/'+policy['year'] not in db['00texlive.config']['depend'] or 'frozen/1' not in db['00texlive.config']['depend']:
        raise ValueError('Repository is not the expected frozen release')
    pinned={p.name[:-7] for p in args.baseline_cache.glob('*.tar.xz')}
    if not pinned: raise ValueError('Baseline package list is empty')
    report=plan(db,policy,pinned)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('counts','downloadBytes','expandedEstimate')},indent=2),flush=True)
    if not args.stage: return
    if args.stage.exists(): raise ValueError('Stage already exists; preserve it and select a new path')
    if args.cache is None: raise ValueError('--cache required')
    args.cache.mkdir(parents=True,exist_ok=True)
    args.stage.parent.mkdir(parents=True,exist_ok=True)
    # TLPDB sizes are allocation estimates; exact limits are checked while extracting.
    required=report['downloadBytes']+2*report['expandedEstimate']+policy['limits']['reserveBytes']
    if shutil.disk_usage(args.stage.parent).free<required or shutil.disk_usage(args.cache).free<required:
        raise ValueError('Insufficient staging/cache capacity')
    report['capacityPreflightBytes']=required
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(download,n,db[n],args.cache,policy['repository']):n for n in report['selected']}
        for count,future in enumerate(concurrent.futures.as_completed(futures),1):
            future.result()
            if count%100==0: print('Verified downloads:',count,'/',len(futures),flush=True)
    args.stage.mkdir()
    report['extraction']={'bytes':0,'files':0,'status':'incomplete'}
    try:
        for n in report['selected']:
            size,count=extract_package(args.cache/(n+'.tar.xz'),db[n],args.stage,policy)
            report['extraction']['bytes']+=size; report['extraction']['files']+=count
            if report['extraction']['bytes']>policy['limits']['maxExpandedBytes']: raise ValueError('Total expanded size limit exceeded')
        report['extraction']['status']='complete'
    finally:
        args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['extraction']),flush=True)


if __name__=='__main__': main()
