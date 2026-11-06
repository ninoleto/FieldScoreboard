"""Verify ZIP CRCs, manifest hashes, archive hygiene and embedded release assets."""
from pathlib import Path, PurePosixPath
import hashlib
import re
import struct
from zipfile import ZipFile
from release_contents import source_files, documentation_files
from check_docs import check_links

root=Path(__file__).resolve().parents[1]
version=re.search(r'const Version = "([^"]+)"',(root/'internal/scoreboard/model.go').read_text()).group(1)
manifest=(root/'dist/SHA256SUMS.txt').read_text().splitlines()
assert len(manifest)==3
for entry in manifest:
    digest,name=entry.split('  ')
    path=root/'dist'/name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
    with ZipFile(path) as archive:
        assert archive.testzip() is None,name
        names=archive.namelist()
        assert len({n.casefold() for n in names})==len(names),'case-insensitive duplicate'
        for filename in names:
            parts=PurePosixPath(filename).parts
            assert not filename.startswith(('/', '\\')) and '..' not in parts
            assert not any(p in {'.git','.test','.tools','__pycache__','config.json'} for p in parts),filename
            assert not filename.endswith(('.log','.pyc','.tmp')),filename
        if '-Source-' in name:
            prefix=f'field-scoreboard-v{version}-source/'
            assert all(n.startswith(prefix) for n in names)
            expected={prefix+p.relative_to(root).as_posix() for p in source_files(root)}
            assert set(names)==expected,'source inventory differs from publication allowlist'
            for filename in names:
                assert archive.read(filename)==(root/filename.removeprefix(prefix)).read_bytes(),filename
            for file in ['AGENTS.md','handoff.md',*[f'internal/scoreboard/web/{asset}' for asset in ['app.js','app.css','index.html','background.js','render.js','overlay.css']]]:
                assert archive.read(prefix+file)==(root/file).read_bytes(),file
        else:
            binaries=['fieldscoreboard.exe','fieldscoreboard-console.exe'] if '-Windows-' in name else ['fieldscoreboard']
            for filename in binaries:
                data=archive.read(filename)
                if filename.endswith('.exe'):
                    assert data[:2]==b'MZ'
                    pe=struct.unpack_from('<I',data,0x3c)[0]
                    assert data[pe:pe+4]==b'PE\0\0'
                    assert struct.unpack_from('<H',data,pe+4)[0]==0x8664
                    subsystem=struct.unpack_from('<H',data,pe+24+68)[0]
                    assert subsystem==(3 if 'console' in filename else 2)
                else:
                    assert data[:6]==b'\x7fELF\x02\x01'
                    assert struct.unpack_from('<H',data,18)[0]==62
                    assert archive.getinfo(filename).external_attr>>16 & 0o111
                for asset in ['app.js','app.css','index.html','background.js','ocr.js','render.js','overlay.css']:
                    assert (root/'internal/scoreboard/web'/asset).read_bytes() in data,(filename,asset)
            assert archive.read('README.md')==(root/'README.md').read_bytes()
            for doc in documentation_files(root):
                assert archive.read(doc.relative_to(root).as_posix())==doc.read_bytes(),doc
        prefix=f'field-scoreboard-v{version}-source/' if '-Source-' in name else ''
        check_links({n.removeprefix(prefix):archive.read(n) for n in names})
        # Common credential formats; example tokens in regression fixtures are
        # intentionally non-secret. No runtime configuration is packaged.
        for filename in names:
            if PurePosixPath(filename).suffix not in {'.md','.py','.go','.js','.json','.html','.sh','.ps1'}:continue
            content=archive.read(filename)
            assert not re.search(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)',content),filename
    print('PASS',name,digest)
print('Archive integrity, SHA-256, portable formats, embedded assets and hygiene: PASS')
