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
/*
 * Decorated block.
 */
void decorated(void);
/* Wrapped first line.
 * Wrapped second line.
 */
// Function-specific note.
void wrapped(void);
/** Doxygen-style opening.
 * Another line.
 */
void doxygen(void);
// Keep /* and */ as literal text in a line comment.
void literal_line(void);
/* Keep the literal opening marker /* in this block. */
void literal_block(void);
/*
 * Division remains a / b.
 * /
 */
void intentional_slash(void);
/* First block.
 */
/* Second block.
 */
void adjacent_wrapped(void);
'''
expected={
    'earlier':'Earlier block.',
    'block':'Own block.',
    'line':'Own line.',
    'undocumented':'',
    'adjacent':'First adjacent block. \n Second adjacent block.',
    'mixed':'Mixed block. \nMixed line.',
    'decorated':'Decorated block.',
    'wrapped':'Wrapped first line.\nWrapped second line.\n \nFunction-specific note.',
    'doxygen':'Doxygen-style opening.\nAnother line.',
    'literal_line':'Keep /* and */ as literal text in a line comment.',
    'literal_block':'Keep the literal opening marker /* in this block.',
    'intentional_slash':'Division remains a / b.\n/',
    'adjacent_wrapped':'First block.\n \n Second block.',
}
original=catalog.ROOT
try:
    with tempfile.TemporaryDirectory(prefix='kitaq-comment-check-') as directory:
        catalog.ROOT=Path(directory)
        path=catalog.ROOT/'comments.h'
        for newline in ['\n','\r\n']:
            path.write_bytes(source.replace('\n',newline).encode('utf-8'))
            rows={r['name']:r['comment'] for r in catalog.definitions(path)}
            assert rows==expected,(newline,rows,expected)
finally:
    catalog.ROOT=original
print('PASS: thirteen API comment cases with both LF and CRLF (26 checks)')
