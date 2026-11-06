"""Check Markdown links in source or archive maps; --online checks HTTPS links."""
from pathlib import Path, PurePosixPath
import argparse
import posixpath
import re
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen
from release_contents import source_files

def headings(text):
    slugs=set()
    counts={}
    for title in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        slug=re.sub(r'[^\w\- ]','',title.lower()).replace(' ','-')
        number=counts.get(slug,0)
        counts[slug]=number+1
        slugs.add(slug+(f'-{number}' if number else ''))
    return slugs

def check_links(files):
    """files maps normalized relative paths to bytes; return external URLs."""
    external=set()
    count=0
    for name,data in files.items():
        if not name.endswith('.md'):
            continue
        text=data.decode('utf-8-sig')
        for target in re.findall(r'\[[^\]\n]+\]\(([^)\s]+)\)',text):
            target=target.strip('<>')
            parsed=urlsplit(target)
            if parsed.scheme:
                assert parsed.scheme in {'https','http','mailto'},(name,target)
                if parsed.scheme=='https': external.add(target)
                continue
            relative=unquote(parsed.path)
            resolved=posixpath.normpath(posixpath.join(str(PurePosixPath(name).parent),relative)) if relative else name
            assert resolved in files,f'{name}: missing link {target}'
            if parsed.fragment and resolved.endswith('.md'):
                assert unquote(parsed.fragment) in headings(files[resolved].decode('utf-8-sig')),f'{name}: missing anchor {target}'
            count+=1
    print(f'PASS: {count} relative documentation links/anchors')
    return external

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--online',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    external=check_links({p.relative_to(root).as_posix():p.read_bytes() for p in source_files(root)})
    if args.online:
        for url in sorted(external):
            with urlopen(Request(url,headers={'User-Agent':'FieldScoreboard-doc-check'}),timeout=45) as response:
                assert response.status==200,(url,response.status)
            print('PASS:',url)
    else:
        print(f'{len(external)} external HTTPS links: use --online after publication')

if __name__=='__main__':
    main()
