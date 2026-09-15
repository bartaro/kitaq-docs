"""Export portable manuals, keeping authoring logs outside the public checkout.

The backup and change manifest must be outside the destination repository.
Only tracked evidence files rejected by the allowlist are removed; existing
untracked files and repository metadata are never swept up by cleanup.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
from public_presentation import SITE, LANGUAGES, normalize, public_file


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_path(path, root):
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escapes the selected directory')
    current = path
    while current != root.parent:
        if current.exists() and current.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('Reparse points are not export targets')
        current = current.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--backup', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    args = parser.parse_args()
    destination, backup = args.destination.absolute(), args.backup.absolute()
    if destination == SITE or not (destination / '.git').exists():
        raise ValueError('Select a separate Git checkout for publication')
    for private in [backup, args.manifest.absolute()]:
        if private.resolve().is_relative_to(destination.resolve()):
            raise ValueError('Keep the backup and manifest outside the public repository')
    for language in LANGUAGES:
        normalize(language)
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=destination).decode().split('\0')
    removed, copied = [], []
    for name in tracked:
        if not name.startswith('verification/') or public_file(name):
            continue
        target, saved = destination / name, backup / name
        check_path(target, destination)
        check_path(saved, backup)
        if not target.is_file():
            continue
        before = digest(target)
        if saved.exists() and digest(saved) != before:
            raise ValueError('Refusing to replace a different evidence backup')
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        if digest(saved) != before:
            raise ValueError('Evidence backup failed verification')
        removed.append({'path': name, 'sha256': before, 'bytes': target.stat().st_size})
        target.unlink()
    for source in SITE.rglob('*'):
        if not source.is_file() or not public_file(source.relative_to(SITE)):
            continue
        name = source.relative_to(SITE).as_posix()
        target = destination / name
        check_path(source, SITE)
        check_path(target, destination)
        expected = digest(source)
        if target.is_file() and digest(target) == expected:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if digest(target) != expected:
            raise ValueError('Export hash mismatch: ' + name)
        copied.append({'path': name, 'sha256': expected})
    ignore = destination / '.gitignore'
    marker = '# Local verification records are not public documentation.'
    text = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    if marker not in text:
        text += '\n' + marker + '\n/verification/**/*.txt\n/verification/**/*.log\n/verification/**/*.json\n/verification/**/*.md\n'
        ignore.write_text(text, encoding='utf-8')
    manifest = {'copied': copied, 'removed': removed, 'protected_evidence_backup_verified': True}
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({'copied': len(copied), 'removed': len(removed)}))


if __name__ == '__main__':
    main()
