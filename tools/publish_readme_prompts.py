"""Insert localized, complete prompt examples after compiler development policies.

Pass the directory containing the kitaqgb and kitaqfc Git checkouts explicitly.
Only their primary README files are edited; libraries and other tools are excluded.
"""
import argparse
import html
import json
import re
from pathlib import Path
from generate_prompts import SOURCE, load_prompt, write_html
from languages import LANGUAGES


def readme_markdown(prompt, level):
    """Keep placeholders visible on GitHub without changing command literals."""
    lines = []
    fenced = False
    for line in prompt.splitlines():
        if line.startswith('```'):
            fenced = not fenced
            lines.append(line)
        elif fenced:
            lines.append(line)
        else:
            line = re.sub(r'^(#{1,3}) ', lambda m: '#' * min(6, level + len(m[1])) + ' ', line)
            lines.append(''.join(part if part.startswith('`') else html.escape(part, quote=False)
                                 for part in re.split(r'(`[^`]+`)', line)))
    return '\n'.join(lines) + '\n'


def publish_readmes(repositories):
    labels = json.loads((SOURCE / 'placement.json').read_text(encoding='utf-8'))
    ui = json.loads((SOURCE / 'ui.json').read_text(encoding='utf-8'))
    for platform in ('gb', 'fc'):
        tool = 'kitaq' + platform
        for language in LANGUAGES:
            suffix = 'pt-BR' if language == 'pt' else language
            name = 'README.md' if language in ('en', 'ja') else 'README.' + suffix + '.md'
            path = repositories / tool / name
            text = path.read_text(encoding='utf-8')
            start = '<!-- development-prompt:' + language + ':start -->'
            end = '<!-- development-prompt:' + language + ':end -->'
            text = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n*', '', text, flags=re.S)
            level = 3 if language in ('en', 'ja') else 2
            marks = '#' * level
            heading = marks + ' ' + labels[language]['policy_heading']
            policy = re.search('^' + re.escape(heading) + r'\n.*?(?=^#{1,' + str(level) + r'} |\Z)', text, re.M | re.S)
            if not policy:
                if platform != 'fc':
                    raise ValueError('Development philosophy missing: ' + str(path))
                # The bilingual README has independent English and Japanese sections.
                offset = text.index('## ' + ('English' if language == 'en' else '日本語')) if level == 3 else 0
                following = re.search('^' + marks + r' ', text[offset:], re.M)
                if not following:
                    raise ValueError('README insertion point missing: ' + str(path))
                pos = offset + following.start()
                text = text[:pos] + heading + '\n\n' + labels[language]['policy'] + '\n\n' + text[pos:]
                policy = re.search('^' + re.escape(heading) + r'\n.*?(?=^#{1,' + str(level) + r'} |\Z)', text, re.M | re.S)
            prompt = load_prompt(language, platform)
            # Nested headings preserve the surrounding README language hierarchy.
            prompt = readme_markdown(prompt, level)
            url = 'https://bartaro.github.io/kitaq-docs/' + ('' if language == 'ja' else language + '/') + tool + '.html#loop-prompts'
            block = (start + '\n' + marks + ' ' + labels[language]['readme_heading']
                     + '\n\n' + ui[language]['intro'] + '\n\n[' + labels[language]['manual'] + '](' + url + ')'
                     + '\n\n<details>\n<summary>' + labels[language]['expand'] + '</summary>\n\n'
                     + prompt.rstrip() + '\n\n</details>\n' + end + '\n\n')
            text = text[:policy.end()] + block + text[policy.end():]
            write_html(path, text)
            print(tool + '/' + name + ': ' + language)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repositories', type=Path)
    publish_readmes(parser.parse_args().repositories.resolve())
