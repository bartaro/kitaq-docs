"""Check complete prompt text, placement and direct links in compiler READMEs."""
import argparse
import html
import json
import re
from pathlib import Path
from generate_prompts import SOURCE, SITE, load_prompt
from languages import LANGUAGES


def check(repositories):
    labels = json.loads((SOURCE / 'placement.json').read_text(encoding='utf-8'))
    results = []
    for platform in ('gb', 'fc'):
        tool = 'kitaq' + platform
        for language in LANGUAGES:
            suffix = 'pt-BR' if language == 'pt' else language
            filename = 'README.md' if language in ('en', 'ja') else 'README.' + suffix + '.md'
            text = (repositories / tool / filename).read_text(encoding='utf-8')
            level = 3 if language in ('en', 'ja') else 2
            start = '<!-- development-prompt:' + language + ':start -->'
            end = '<!-- development-prompt:' + language + ':end -->'
            assert text.count(start) == text.count(end) == 1, (tool, language)
            before, block = text.split(start)
            block = block.split(end)[0]
            headings = re.findall(r'^#{1,' + str(level) + r'} (.*)$', before, re.M)
            assert headings[-1] == labels[language]['policy_heading'], (tool, language, 'placement')
            original = load_prompt(language, platform)
            parts = re.split(r'(^```.*?^```)', original, flags=re.M | re.S)
            expected = ''.join(part if i % 2 else re.sub(r'^(#{1,3}) ', lambda m: '#' * min(6, level + len(m[1])) + ' ', part, flags=re.M)
                               for i, part in enumerate(parts))
            actual = re.search(r'</summary>\n\n(.*?)\n\n</details>', block, re.S)[1]
            assert html.unescape(actual) == expected.rstrip(), (tool, language, 'complete prompt')
            assert re.findall(r'^```.*?^```', actual, re.M | re.S) == re.findall(r'^```.*?^```', expected, re.M | re.S)
            assert not re.search(r'<(?:fill|specify|for example)\b', actual), (tool, language, 'visible placeholders')
            relative = ('' if language == 'ja' else language + '/') + tool + '.html'
            assert 'https://bartaro.github.io/kitaq-docs/' + relative + '#loop-prompts' in block
            assert 'id="loop-prompts"' in (SITE / relative).read_text(encoding='utf-8')
            results.append({'tool': tool, 'language': language, 'after_development_philosophy': True,
                            'complete_localized_prompt': True, 'direct_chapter_link': True})
    report = {'status': 'passed', 'scope': 'README content and placement; no game execution', 'editions': results}
    (SITE / 'verification/readme_prompt_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('All 18 README prompt editions passed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repositories', type=Path)
    check(parser.parse_args().repositories.resolve())
