"""Prepare target-only static XS adapters; no host native libraries are used."""
import hashlib,json,os,pathlib,re,shutil,subprocess
root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path(os.environ['BUILD_REPO']);sdk=pathlib.Path(os.environ['NATIVE_OHOS_SDK'])
work=repo/'build/biber-perl-5.40.3';sources=repo/'build/biber-deps';out=root/'validation/biber'
specs=[('Clone','Clone','Clone.pm'),('DateTime','DateTime','lib/DateTime.pm'),
 ('HTML-Parser','HTML::Parser','lib/HTML/Parser.pm'),('List-MoreUtils-XS','List::MoreUtils::XS','lib/List/MoreUtils/XS.pm'),
 ('PerlIO-utf8_strict','PerlIO::utf8_strict','lib/PerlIO/utf8_strict.pm'),('Sort-Key','Sort::Key','lib/Sort/Key.pm'),
 ('autovivification','autovivification','lib/autovivification.pm'),('Params-Validate','Params::Validate::XS','lib/Params/Validate/XS.pm'),
 ('Unicode-LineBreak','Unicode::LineBreak','lib/Unicode/LineBreak.pm')]
cc=[str(sdk/'llvm/bin/clang'),'--target=aarch64-linux-ohos','--sysroot='+str(sdk/'sysroot'),'-Werror=implicit-function-declaration']
notes=[]
for dist,name,version in specs:
    dest=work/'cpan'/name.replace('::','-')
    if not dest.exists():shutil.copytree(sources/dist,dest)
    if name=='Params::Validate::XS':
        for p in (dest/'lib/Params/Validate').glob('*'):
            if p.suffix in ('.xs','.h','.c'):shutil.copy2(p,dest/p.name)
    if name=='List::MoreUtils::XS':
        probes={'HAVE_TIME_H':'#include <time.h>\nint x;', 'HAVE_SYS_TIME_H':'#include <sys/time.h>\nint x;',
          'HAVE_TIME':'#include <time.h>\nint main(){return time(0)==0;}',
          'HAVE_SIZE_T':'#include <stddef.h>\nsize_t x;', 'HAVE_SSIZE_T':'#include <sys/types.h>\nssize_t x;',
          'HAVE_BUILTIN_EXPECT':'int main(){return __builtin_expect(0,1);}',
          'HAVE_FEATURE_STATEMENT_EXPRESSION':'int main(){return ({1;});}'}
        lines=[]
        for macro,code in probes.items():
            p=dest/'ohos-probe.c';p.write_text(code)
            r=subprocess.run(cc+['-c',str(p),'-o',str(dest/'ohos-probe.o')],capture_output=True)
            if r.returncode:raise RuntimeError(macro+': '+r.stderr.decode())
            lines.append('#define '+macro+' 1')
        (dest/'ohos-probe.c').unlink();(dest/'ohos-probe.o').unlink()
        (dest/'LMUconfig.h').write_text('\n'.join(lines)+'\n')
    inc='-I.';define='-DMARKED_SECTION' if name=='HTML::Parser' else ''
    if name=='Params::Validate::XS':inc+=' -Ic'
    objects='Parser$(OBJ_EXT)' if name=='HTML::Parser' else '$(O_FILES)'
    if name=='PerlIO::utf8_strict':
        xs=dest/'utf8_strict.xs';text=xs.read_text()
        if 'void PerlIOBase_flush_linebuf(pTHX)' in text:
            shutil.copy2(xs,dest/'utf8_strict.xs.upstream')
            text=text.replace('PerlIOBase_flush_linebuf','ohos_utf8_strict_flush_linebuf').replace('void ohos_utf8_strict_flush_linebuf(pTHX)','static void ohos_utf8_strict_flush_linebuf(pTHX)')
            xs.write_text(text)
            for p in [dest/'utf8_strict.c',dest/'utf8_strict.o',dest/'pm_to_blib',work/'lib/auto/PerlIO/utf8_strict/utf8_strict.a',work/'static.list',work/'ext.libs']:
                assert p.resolve().is_relative_to(work.resolve())
                if p.exists():p.unlink()
    if name=='Unicode::LineBreak':
        sombok=dest/'sombok';unicode=(sombok/'UNICODE').read_text().strip();ver=(sombok/'VERSION').read_text().strip()
        header=(sombok/'include/sombok.h.in').read_text().replace('#ifdef HAVE_CONFIG_H','#if 1').replace('"config.h"','"EXTERN.h"\n#include "perl.h"\n#include "XSUB.h"\n#undef USE_LIBTHAI')
        for k,v in {'SOMBOK_UNICHAR_T':'U32','PACKAGE_VERSION':ver,'SOMBOK_UNICHAR_T_IS_WCHAR_T':'','SOMBOK_UNICHAR_T_IS_UNSIGNED_INT':'','SOMBOK_UNICHAR_T_IS_UNSIGNED_LONG':''}.items():header=header.replace('@'+k+'@',v)
        (sombok/'include/sombok.h').write_text(header)
        for file in ['break.c','charprop.c','gcstring.c','linebreak.c','southeastasian.c','utf8.c','utils.c',unicode+'.c']:
            shutil.copy2(sombok/'lib'/file,dest/('sombok_'+file))
        inc+=' -Isombok/include';notes.append({'sombok':ver,'unicode':unicode,'libthai':False})
    makefile=dest/'Makefile.PL'
    assert (dest/version).is_file(),dest/version
    if makefile.exists() and not (dest/'Makefile.PL.upstream').exists():shutil.copy2(makefile,dest/'Makefile.PL.upstream')
    makefile.write_text("use ExtUtils::MakeMaker;\nWriteMakefile(NAME=>'"+name+"', VERSION_FROM=>'"+version+"', OBJECT=>'"+objects+"', INC=>'"+inc+"', DEFINE=>'"+define+"');\n")
    for p in dest.rglob('*.pm'):
        if 'DynaLoader' in p.read_text(errors='replace'):notes.append({'module':name,'bootstrapReview':str(p.relative_to(dest))})
    notes.append({'module':name,'xsFiles':[str(p.relative_to(dest)) for p in dest.glob('*.xs')],'versionFileExists':(dest/version).exists()})
build=out/'xs-bootstrap/build.sh';text=build.read_text()
if '.configured-biber-encodings-v1' not in text:text=re.sub(r'\.configured-biber-[a-z0-9-]+','.configured-biber-remaining-v1',text)
build.write_text(text)
(out/'remaining-xs-adapters.json').write_text(json.dumps(notes,indent=2)+'\n')
print(json.dumps(notes,indent=2))
