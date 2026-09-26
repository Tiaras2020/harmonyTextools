"""Reuse the B318 input fixture in a separate directory, add strict warning checks."""
import pathlib
root=pathlib.Path(__file__).resolve().parents[1]
source=(root/'build-support/prepare-biber-device-tests.py').read_text(encoding='utf-8')
source=source.replace('validation/biber/device-input/B318','validation/biber/polish-1.0.19/device-input/B319').replace('TeXstudioResourceTest/B318','TeXstudioResourceTest/B319')
exec(compile(source,__file__,'exec'),{'__file__':__file__})
dest=root/'validation/biber/polish-1.0.19/device-input/B319'
script=(dest/'run.sh').read_text(encoding='utf-8')
script=script.replace('biber --version > version.txt 2>&1','biber --version > version.txt 2> version.stderr\ntest ! -s version.stderr')
script=script.replace("printf 'passed",'xdvipdfmx -vv -E -o driver-config.pdf "主文献.xdv" > driver-config.log 2>&1\n'+
    "if grep -E 'Empty compile time|uninitialized value|Could not open config|Couldn.t open font map' ./*.log; then exit 1; fi\n"+"printf 'passed")
(dest/'run.sh').write_text(script,encoding='utf-8',newline='\n')
