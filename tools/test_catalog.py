"""Guard API examples against declarations and strings mistaken for calls."""
import re
import unittest
from catalog import clean, declaration_name_offsets


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


if __name__ == '__main__':
    unittest.main()
