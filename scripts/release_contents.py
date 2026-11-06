"""Explicit public-source inventory, shared by packaging and verification."""
from pathlib import Path

ROOT_FILES = (
    '.gitattributes', '.gitignore', 'AGENTS.md', 'CONTRIBUTING.md', 'LICENSE',
    'README.md', 'handoff.md', 'go.mod', 'fieldscoreboard.ico',
    'start-portable.cmd', 'start-portable.sh',
)
DOC_ROOTS = ('README.md', 'CONTRIBUTING.md', 'AGENTS.md', 'handoff.md', 'LICENSE')
DIRECTORIES = {
    'cmd': {'.go'},
    'internal': {'.go', '.js', '.css', '.html'},
    'scripts': {'.py', '.sh', '.ps1'},
    'docs': {'.md'},
}

def source_files(root: Path):
    files = [root / name for name in ROOT_FILES]
    for directory, suffixes in DIRECTORIES.items():
        files.extend(p for p in (root / directory).rglob('*')
                     if p.is_file() and p.suffix in suffixes
                     and not any(part.startswith('.') or part == '__pycache__'
                                 for part in p.relative_to(root / directory).parts))
    files.append(root / 'scripts/fixtures/ui_state.json')
    assert all(p.is_file() and not p.is_symlink() for p in files)
    return sorted(set(files))

def documentation_files(root: Path):
    return [root / name for name in DOC_ROOTS] + sorted((root / 'docs').glob('*.md'))
