"""Test production launcher argv handling and cancellation on a POSIX host."""
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

root=Path(__file__).resolve().parents[1]
out=root/'validation/latexmk'
checks={}
with tempfile.TemporaryDirectory(prefix='harmony-launcher-') as folder:
    folder=Path(folder); runtime=folder/'runtime with spaces'
    (runtime/'bin').mkdir(parents=True);(runtime/'share/latexmk').mkdir(parents=True)
    (runtime/'bin/perl').symlink_to('/usr/bin/perl')
    import shutil
    shutil.copy2(root/'texstudio-harmony/scripts/texlive/HarmonyCwd.pm',runtime/'share/latexmk/HarmonyCwd.pm')
    script=runtime/'share/latexmk/latexmk.pl'
    script.write_text('use JSON::PP; use Encode qw(decode_utf8); @ARGV=map {decode_utf8($_)} @ARGV; print encode_json({args=>\\@ARGV,path=>$ENV{PATH},pid=>$$,group=>getpgrp()}); exit 23;\n')
    launcher=folder/'latexmk'
    subprocess.run(['cc','-Wall','-Wextra','-Werror','-std=c11',f'-DHARMONY_RUNTIME_ROOT="{runtime}"',
        str(root/'texstudio-harmony/scripts/texlive/latexmk_launcher.c'),'-o',str(launcher)],check=True)
    args=['-xelatex','中文 空格文件.tex','literal$(touch should-not-exist).tex',"quote'file.tex"]
    result=subprocess.run([str(launcher),*args],cwd=folder,capture_output=True,text=True)
    assert result.returncode==23,result.stderr
    proof=json.loads(result.stdout)
    assert proof['args']==args and proof['path'].split(':')[0]==str(runtime/'bin')
    assert proof['pid']==proof['group'] and not (folder/'should-not-exist').exists()
    checks['literalArgumentsUnicodeSpacesExitCodeAndPath']=True
    killer=folder/'killer';source=folder/'killer.cpp'
    source.write_text('#include "harmonyprocess.h"\n#include <cstdlib>\nint main(int n,char**v){return n==2 && HarmonyProcess::killChildGroup(atoi(v[1])) ? 0:1;}\n')
    subprocess.run(['c++','-Wall','-Wextra','-Werror','-I'+str(root/'texstudio-harmony/third_party/texstudio/src'),str(source),'-o',str(killer)],check=True)
    assert subprocess.run([str(killer),str(os.getpgrp())]).returncode==1
    checks['ApplicationProcessGroupProtected']=True
    script.write_text('my $child=fork(); die "fork" unless defined $child; if (!$child) {sleep 60;exit 0;} open my $f,">",$ARGV[0] or die $!; print $f "$$ $child";close $f;sleep 60;\n')
    pidfile=folder/'pids'
    p=subprocess.Popen([str(launcher),str(pidfile)])
    try:
        deadline=time.monotonic()+5
        while not pidfile.exists() and time.monotonic()<deadline:time.sleep(.02)
        parent,child=map(int,pidfile.read_text().split())
        assert parent==p.pid
        subprocess.run([str(killer),str(parent)],check=True)
        assert p.wait(timeout=5)==-signal.SIGKILL
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            status=Path(f'/proc/{child}/stat')
            if not status.exists() or status.read_text().split()[2]=='Z':break
            time.sleep(.02)
        else:raise AssertionError('Compiler descendant survived cancellation')
        checks['CancellationStopsCompilerDescendants']=True
    finally:
        if p.poll() is None:os.killpg(p.pid,signal.SIGKILL);p.wait()
report={'passed':True,'scope':'host validation of production launcher and process-group helper','checks':checks}
(out/'launcher-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
