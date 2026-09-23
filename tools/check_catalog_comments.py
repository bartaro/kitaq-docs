"""Keep each API's source notes separate from preceding declarations."""
from pathlib import Path
import tempfile
import catalog

source='''/* Earlier block. */
void earlier(void);
/* Own block. */
void block(void);
// Own line.
void line(void);
void undocumented(void);
/* First adjacent block. */
/* Second adjacent block. */
void adjacent(void);
/* Mixed block. */
// Mixed line.
void mixed(void);
'''
expected={
    'earlier':'Earlier block.',
    'block':'Own block.',
    'line':'Own line.',
    'undocumented':'',
    'adjacent':'First adjacent block. \n Second adjacent block.',
    'mixed':'Mixed block. \nMixed line.',
}
original=catalog.ROOT
try:
    with tempfile.TemporaryDirectory(prefix='kitaq-comment-check-') as directory:
        catalog.ROOT=Path(directory)
        path=catalog.ROOT/'comments.h';path.write_text(source,encoding='utf-8')
        rows={r['name']:r['comment'] for r in catalog.definitions(path)}
        assert rows==expected,(rows,expected)
finally:
    catalog.ROOT=original
print('PASS: six API comment boundaries, including intervening declarations')
