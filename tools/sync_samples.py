"""Copy reviewed examples and verify original-font conversion without a rebuild."""
from pathlib import Path
import hashlib
import json
import re
import shutil

SITE = Path(__file__).resolve().parents[1]
ROOT = SITE.parent


def main():
    """Validate all inputs before replacing bundled source and provenance files."""
    dest = SITE / 'samples'
    manifest = json.loads((dest / 'manifest.json').read_text(encoding='utf-8'))
    pairs = [(ROOT / ('kitaq' + row['platform']) / 'examples' / row['file'], dest / row['file']) for row in manifest]
    for platform in ('gb', 'fc'):
        pairs.append((ROOT / ('kitaq' + platform) / 'examples' / (platform + '_common.h'), dest / (platform + '_common.h')))
    pairs.extend([(ROOT / 'kitaqgb/examples/font_gb.h', dest / 'font_gb.h'),
                  (ROOT / 'kitaqfc/examples/font.chr', dest / 'font.chr'),
                  (ROOT / 'kitaqgb/examples/assets/ascii.c', dest / 'assets/ascii.c')])
    # Preflight every source, including files shared by both platforms.
    payloads = [(source, target, source.read_bytes()) for source, target in pairs]
    original = (ROOT / 'kitaqgb/examples/assets/ascii.c').read_bytes()
    tiles = {int(n): bytes(int(v, 16) for v in re.findall(r'0x([0-9a-fA-F]{2})', body))
             for n, body in re.findall(r'TileLabelTLE(\d+)\[\]\s*=\s*\{([^}]+)\}', original.decode('utf-8-sig'), re.S)}
    assert sorted(tiles) == list(range(92)) and all(len(t) == 16 for t in tiles.values())
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz' + '!"#$%&\'()*+,-./:;<=>?@[]^_`{}~'
    gb = bytearray(2048)
    fc = bytearray(8192)
    mapping = []
    for index, char in enumerate(chars):
        offset = ord(char) * 16
        tile = tiles[index]
        gb[offset:offset + 16] = tile
        fc[offset:offset + 16] = tile[::2] + tile[1::2]
        mapping.append({'char': char, 'ascii': ord(char), 'source_tile': index})
    # Check every byte, rather than inferring fidelity from glyph dimensions.
    text = (ROOT / 'kitaqgb/examples/font_gb.h').read_text(encoding='utf-8-sig')
    body = re.search(r'manual_font\[\]\s*=\s*\{([^}]+)\}', text, re.S)[1]
    assert bytes(int(v) for v in re.findall(r'\d+', body)) == gb
    assert (ROOT / 'kitaqfc/examples/font.chr').read_bytes() == fc
    digest = lambda data: hashlib.sha256(data).hexdigest()
    records = []
    for source, target, data in payloads:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != data:
            shutil.copyfile(source, target)
        records.append({'source': source.relative_to(ROOT).as_posix(), 'copy': target.relative_to(SITE).as_posix(), 'sha256': digest(data)})
    verification = SITE / 'verification'
    verification.mkdir(exist_ok=True)
    font = {'source': 'samples/assets/ascii.c', 'source_sha256': digest(original), 'source_tiles': 92,
            'gb_bytes': len(gb), 'nes_chr_bytes': len(fc), 'mapped_glyphs': mapping,
            'conversion': 'GB interleaved planes to NES plane-0 followed by plane-1; unchanged pixel indices',
            'gb_sha256': digest(gb), 'nes_sha256': digest(fc)}
    (verification / 'font_conversion.json').write_text(json.dumps(font, ensure_ascii=False, indent=2), encoding='utf-8')
    (verification / 'sample_sources.json').write_text(json.dumps({
        'scope': 'Current bundled sources; historical build/runtime records are not refreshed by synchronization.',
        'programs': len(manifest), 'files': records}, indent=2), encoding='utf-8')
    print(f'Synchronized {len(manifest)} programs and verified 92 glyphs; no build or runtime test performed.')


if __name__ == '__main__':
    main()
