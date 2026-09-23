"""Guard API examples against declarations and strings mistaken for calls."""
import re
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from catalog import clean, declaration_name_offsets, callable_aliases


class CallSiteTests(unittest.TestCase):
    def test_only_executable_calls_remain(self):
        source = '''u8 query();
u8 query() { return 32; }
void __stackcall example(void) {
    const u8 *label = "query() and { not code }";
    // query();
    u8 remaining = query();
    return query();
}
'''
        masked = clean(source)
        declarations = declaration_name_offsets(masked)
        calls = [match for match in re.finditer(r'\bquery\s*\(', masked)
                 if match.start() not in declarations]
        self.assertEqual([source.count('\n', 0, match.start()) + 1
                          for match in calls], [6, 7])
        self.assertEqual(len(masked), len(source))
        self.assertEqual(masked.count('\n'), source.count('\n'))

    def test_custom_return_type_and_split_signature(self):
        source = 'result_t *\nquery(void);\nresult_t *query(void) { return 0; }\n'
        masked = clean(source)
        declarations = declaration_name_offsets(masked)
        # A line break between the type and name is valid C too.
        self.assertEqual(len(declarations), 2)

    def test_callable_alias_chain_excludes_constants_and_cycles(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            header = root / 'input.h'
            header.write_text('#define chained short_query\n#define short_query query // alias\n'
                              '#define WIDTH 160\n#define OTHER WIDTH\n'
                              '#define cycle_a cycle_b\n#define cycle_b cycle_a\n', encoding='utf-8')
            definition = dict(name='query', path='input.c', line=5, body='return mask != 0;')
            records = {'query': dict(name='query', signature='u8 query(u8 mask)',
                                    definition=definition, comment='Checks input.')}
            with patch('catalog.ROOT', root):
                result = callable_aliases(records, [header])
            self.assertEqual({r['name'] for r in result}, {'short_query', 'chained'})
            self.assertEqual(records['short_query']['line'], 2)
            self.assertEqual(records['chained']['line'], 1)
            self.assertEqual(records['chained']['signature'], 'u8 chained(u8 mask)')
            self.assertEqual(records['chained']['definition'], definition)
            self.assertEqual(records['short_query']['source_macro'], '#define short_query query')
            self.assertEqual(records['query']['comment'], 'Checks input.')


if __name__ == '__main__':
    unittest.main()
