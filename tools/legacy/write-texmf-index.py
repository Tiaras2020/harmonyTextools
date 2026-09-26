"""Generate the portable ls-R database used by Kpathsea and TeXstudio."""
import os,pathlib,sys
root=pathlib.Path(sys.argv[1]).resolve()
lines=['% ls-R -- filename database for kpathsea; do not change this line.','']
for directory,dirs,files in os.walk(root):
    dirs.sort(); files.sort()
    relative=pathlib.Path(directory).relative_to(root).as_posix()
    prefix='.' if relative=='.' else './'+relative
    lines += [prefix+':',*dirs,*files,'']
(root/'ls-R').write_text('\n'.join(lines)+'\n')
print('Indexed',sum(line.endswith(('.sty','.cls')) for line in lines),'package/class files')
