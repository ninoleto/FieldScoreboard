#!/usr/bin/env python3
"""Create cross-platform preview archives and checksums. No source/config secrets."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZipInfo
import hashlib
import re
from release_contents import source_files, documentation_files
root=Path(__file__).resolve().parents[1]
dist=root/'dist';dist.mkdir(exist_ok=True)
version=re.search(r'const Version = "([^"]+)"',(root/'internal/scoreboard/model.go').read_text()).group(1)
archives=[]
for platform,binary,target,launcher in [
 ('Windows','fieldscoreboard-windows.exe','fieldscoreboard.exe','start-portable.cmd'),
 ('Linux','fieldscoreboard-linux','fieldscoreboard','start-portable.sh'),
]:
    out=dist/f'FieldScoreboard-{platform}-v{version}.zip'
    files=[(root/'bin'/binary,target),(root/launcher,launcher)]
    files += [(path,path.relative_to(root).as_posix()) for path in documentation_files(root)]
    if platform=='Windows':files += [(root/'bin/fieldscoreboard-windows-console.exe','fieldscoreboard-console.exe'),(root/'fieldscoreboard.ico','fieldscoreboard.ico')]
    with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for src,arc in files:
            assert src.is_file() and src.stat().st_size>0,(src,'missing or empty')
            info=ZipInfo(arc);info.compress_type=ZIP_DEFLATED
            info.external_attr=(0o100755 if arc in {'fieldscoreboard','start-portable.sh'} else 0o100644)<<16
            z.writestr(info,src.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
    print(out.name, out.stat().st_size);archives.append(out)
source=dist/f'FieldScoreboard-Source-v{version}.zip'
with ZipFile(source,'w',ZIP_DEFLATED,compresslevel=9) as z:
    for src in source_files(root):
        arc=f'field-scoreboard-v{version}-source/{src.relative_to(root).as_posix()}'
        info=ZipInfo(arc);info.compress_type=ZIP_DEFLATED
        info.external_attr=(0o100755 if src.suffix=='.sh' else 0o100644)<<16
        z.writestr(info,src.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
archives.append(source);print(source.name,source.stat().st_size)
checksums=dist/'SHA256SUMS.txt'
checksums.write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}\n' for f in archives))
print(checksums.name)
