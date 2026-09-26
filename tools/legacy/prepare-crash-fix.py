from pathlib import Path
import json, shutil
r=Path(__file__).resolve().parents[1]
src=r/'texstudio-harmony/third_party/texstudio/src'
out=r/'validation/crash-fix-1.0.30';out.mkdir(exist_ok=True)
for name in ('cppcrash-com.ohos.texstudio-20020247-20260926000208453.log',
             'fdsan-com.ohos.texstudio-20020247-20260926000159122.log',
             'cppcrash-com.ohos.texstudio-20020247-20260925221642793.log'):
    shutil.copy2(Path('C:/Users/1/AppData/Local/Temp')/name,out/name)
old='''            const QString path=HarmonyProject::resolve(s->root,r.value("path").toString());
            if(path.isEmpty()||!HarmonyProject::textFile(path))return error("invalid_text_path");'''
new='''            const QString requested=r.value("path").toString();
            if(!HarmonyProject::textFile(requested))return error("invalid_text_path");
            QString pathFailure;
            const QString path=HarmonyProject::resolve(s->root,requested,false,&pathFailure);
            if(path.isEmpty()) {
                auto result=error(pathFailure);
                if(pathFailure=="file_missing")result.insert("recoveryHint",QStringLiteral("工程内文件已不存在，请恢复磁盘文件后重试；编辑器缓冲区不会因此被清空。"));
                return result;
            }'''
for p in (src/'texstudio.cpp',r/'build-support/project-session-function.txt'):
    s=p.read_text(encoding='utf-8');assert s.count(old)==2;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
p=r/'tools/texstudio-cli-help.json';d=json.loads(p.read_text(encoding='utf-8'))
d['commands']['document.reload']['errors']={
    'file_missing':'授权工程内路径合法，但磁盘文件已不存在；先恢复磁盘文件。',
    'invalid_text_path':'路径不合法、越界、隐藏路径、符号链接或不支持的文件类型。',
    'document_not_open':'文件存在，但未在应用内打开。',
    'read_failed':'文件存在，但无法读取。'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=r/'build-support/sync-baseline.py';s=p.read_text(encoding='utf-8');s=s.replace("'harmonyreload.h']","'harmonyreload.h', 'latexdocument.cpp']");p.write_text(s,encoding='utf-8')
