"""Remove successful API builds' disposable metadata, retaining ROMs, sources, logs and images."""
from pathlib import Path

def cleanup_build_outputs(folder):
    root = Path(folder).resolve(strict=True)
    removable_suffixes = ('.banks.txt', '.funcsizes.txt', '.source_map.txt', '.build_report.json', '.dbg2.json')
    for path in root.rglob('*'):
        if not path.is_file(): continue
        relative = path.relative_to(root)
        if not ('debug_output' in relative.parts or path.suffix in ('.dbc','.dbg','.map') or path.name.endswith(removable_suffixes)):
            continue
        # Refuse an unexpected link or a resolved path outside this verification case.
        if path.is_symlink() or not path.resolve(strict=True).is_relative_to(root):
            raise ValueError('Refusing linked build output: '+str(path))
        path.unlink()
