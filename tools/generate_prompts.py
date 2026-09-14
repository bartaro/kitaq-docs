"""Publish authored AI development prompts and same-language manual links.

Only the prompt pages and marked navigation blocks are generated here. Existing
manual prose, reference material and recorded verification results are preserved.
"""
from pathlib import Path
import argparse
import html
import json
import re
from languages import LANGUAGES, HTML_LANG, language_nav

SITE = Path(__file__).resolve().parents[1]
SOURCE = SITE / 'tools' / 'prompts'


def write_html(path, text):
    """Keep existing line endings so adding links does not rewrite whole volumes."""
    newline = '\r\n' if path.exists() and b'\r\n' in path.read_bytes() else '\n'
    path.write_text(text, encoding='utf-8', newline=newline)


def inline(text):
    """Escape authored prose before rendering its limited inline Markdown."""
    parts = re.split(r'(`[^`]+`)', text)
    return ''.join('<code>' + html.escape(p[1:-1]) + '</code>' if p.startswith('`')
                   else re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html.escape(p))
                   for p in parts)


def render_markdown(text, prefix, copy_label):
    """Render headings, lists, paragraphs and literal fenced command blocks."""
    lines = text.splitlines()
    output = []
    i = 0
    heading = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith('# '):
            i += 1
            continue
        if line.startswith('```'):
            language = line[3:]
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError('Unclosed command fence: ' + prefix)
            output.append('<div class="codebox"><span class="lang">' + html.escape(language)
                          + '</span><button class="copy" type="button">' + html.escape(copy_label)
                          + '</button><pre><code>' + html.escape('\n'.join(block)) + '</code></pre></div>')
        elif re.match(r'^#{2,3} ', line):
            level = len(line.split(' ', 1)[0]) + 1
            heading += 1
            output.append(f'<h{level} id="{prefix}-section-{heading}">' + inline(line.split(' ', 1)[1]) + f'</h{level}>')
        elif re.match(r'^(?:- |\d+\. )', line):
            ordered = not line.startswith('- ')
            tag = 'ol' if ordered else 'ul'
            pattern = r'^\d+\. ' if ordered else r'^- '
            output.append('<' + tag + '>')
            while i < len(lines) and re.match(pattern, lines[i]):
                output.append('<li>' + inline(re.sub(pattern, '', lines[i])) + '</li>')
                i += 1
            output.append('</' + tag + '>')
            continue
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^(?:#|```|- |\d+\. )', lines[i]):
                paragraph.append(lines[i])
                i += 1
            output.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            continue
        i += 1
    return '\n'.join(output)


def load_prompt(language, platform):
    """Resolve shared commands without translating option names or file paths."""
    path = SOURCE / language / (platform + '.md')
    if path.exists():
        return path.read_text(encoding='utf-8')
    data = json.loads((SOURCE / language / 'text.json').read_text(encoding='utf-8'))
    labels = data['headings']
    parts = ['# ' + data['title_' + platform], data['usage'], '## ' + labels[0],
             data['fields'], data['fields_' + platform], '## ' + labels[1],
             data['task_' + platform], data['task'], '### ' + labels[2], data['prepare'],
             '### ' + labels[3], data['implementation_' + platform], data['implementation'],
             '### ' + labels[4], data['build'], data['build_' + platform],
             (SOURCE / 'commands' / (platform + '.md')).read_text(encoding='utf-8'),
             data['after_build_' + platform]]
    if platform == 'fc':
        parts += ['### ' + labels[5], data['replay'],
                  (SOURCE / 'commands' / 'fc-replay.md').read_text(encoding='utf-8'), data['harness']]
    parts += ['### ' + labels[6], data['observe'], '### ' + labels[7], data['analyze'],
              (SOURCE / 'commands' / (platform + '-delta.md')).read_text(encoding='utf-8'),
              data['delta'], '### ' + labels[8], data['finish']]
    return '\n\n'.join(parts) + '\n'


def publish(language):
    """Publish downloads and numbered examples in the two compiler manuals."""
    folder = SITE if language == 'ja' else SITE / language
    ui = json.loads((SOURCE / 'ui.json').read_text(encoding='utf-8'))[language]
    placement = json.loads((SOURCE / 'placement.json').read_text(encoding='utf-8'))[language]
    shell = (folder / 'index.html').read_text(encoding='utf-8')
    shell = re.sub(r'<!-- loop-prompts:start -->.*?<!-- loop-prompts:end -->', '', shell, flags=re.S)
    shell = re.sub(r'<title>.*?</title>', '<title>' + html.escape(ui['title']) + ' — KITAQ SERIES</title>', shell, count=1, flags=re.S)
    shell = re.sub(r'<nav\b[^>]*class="languages"[^>]*>.*?</nav>',
                   lambda _: language_nav('loop-engineering', language, ui['languages']), shell, count=1, flags=re.S)
    download_dir = SITE / 'prompts' / language
    download_dir.mkdir(parents=True, exist_ok=True)
    body = ['<div class="cover"><p class="eyebrow">KITAQ SERIES</p><h1>' + html.escape(ui['title'])
            + '</h1><p class="subtitle">' + html.escape(ui['intro']) + '</p></div>']
    for platform, tool in [('gb', 'KITAQGB'), ('fc', 'KITAQFC')]:
        text = load_prompt(language, platform)
        (download_dir / (tool.lower() + '-prompt.md')).write_text(text, encoding='utf-8', newline='\n')
        href = ('' if language == 'ja' else '../') + 'prompts/' + language + '/' + tool.lower() + '-prompt.md'
        body.append('<section class="authored"><h2 id="' + platform + '">' + tool + '</h2><p><button type="button" class="copy" data-copy-source="prompt-' + platform + '">' + html.escape(ui['copy_all']) + '</button> · <a download href="' + href + '">' + html.escape(ui['download']) + '</a></p>')
        body.append('<pre id="prompt-' + platform + '" hidden><code>' + html.escape(text) + '</code></pre>')
        body.append(render_markdown(text, platform, ui['copy']))
        body.append('</section>')
    shell = re.sub(r'<main\b[^>]*>.*?</main>', lambda _: '<main id="main">' + '\n'.join(body) + '</main>', shell, count=1, flags=re.S)
    shell = re.sub(r'(<nav\b[^>]*class="toc"[^>]*>).*?</nav>', lambda m: m[1] + '<a href="#gb">KITAQGB</a><a href="#fc">KITAQFC</a></nav>', shell, count=1, flags=re.S)
    shell = shell.replace('aria-current="page" href="index.html"', 'href="index.html"')
    write_html(folder / 'loop-engineering.html', shell)
    # Marked blocks make repeated generation idempotent and removable before translation.
    for key in ('index', 'kitaqgb', 'gb-library', 'kokura', 'kitaqfc', 'fc-library', 'kurosaki', 'sarakura'):
        path = folder / (key + '.html')
        page = path.read_text(encoding='utf-8')
        page = re.sub(r'<!-- loop-prompts:start -->.*?<!-- loop-prompts:end -->', '', page, flags=re.S)
        if key not in ('kitaqgb', 'kitaqfc'):
            write_html(path, page)
            continue
        platform = 'gb' if key == 'kitaqgb' else 'fc'
        text = load_prompt(language, platform)
        href = ('' if language == 'ja' else '../') + 'prompts/' + language + '/' + key + '-prompt.md'
        # Insert after the final teaching chapter and before the source/reference material.
        main_start = page.index('<main')
        headings = list(re.finditer(r'<h2\b[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', page[main_start:], re.S))
        numbered = [i for i, h in enumerate(headings) if re.match(r'^\d+[.．、]?', html.unescape(re.sub('<[^>]+>', '', h[2])))]
        if not numbered or numbered[-1] + 1 >= len(headings):
            raise ValueError('Final numbered chapter not found: ' + str(path))
        last = headings[numbered[-1]]
        numbering = re.match(r'^(\d+)([\s.．、]+)', html.unescape(re.sub('<[^>]+>', '', last[2])))
        number = int(numbering[1]) + 1
        following = headings[numbered[-1] + 1]
        heading = str(number) + numbering[2] + placement['chapter']
        block = ('<!-- loop-prompts:start --><section data-loop-prompts="true"><h2 id="loop-prompts">'
                 + html.escape(heading) + '</h2><p>' + html.escape(ui['intro'])
                 + '</p><p><button type="button" class="copy" data-copy-source="prompt-' + platform + '">'
                 + html.escape(ui['copy_all']) + '</button> · <a download href="' + href + '">'
                 + html.escape(ui['download']) + '</a></p><pre id="prompt-' + platform
                 + '" hidden><code>' + html.escape(text) + '</code></pre>'
                 + render_markdown(text, 'prompt-example-' + platform, ui['copy'])
                 + '</section><!-- loop-prompts:end -->')
        position = main_start + following.start()
        page = page[:position] + block + page[position:]
        toc_entry = '<!-- loop-prompts:start --><a data-loop-prompts="true" href="#loop-prompts">' + html.escape(heading) + '</a><!-- loop-prompts:end -->'
        anchor = '<a href="#' + following[1] + '"'
        if page.count(anchor) != 1:
            raise ValueError('Reference table-of-contents entry not unique: ' + str(path))
        page = page.replace(anchor, toc_entry + anchor, 1)
        write_html(path, page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=LANGUAGES)
    args = parser.parse_args()
    for language in ([args.language] if args.language else LANGUAGES):
        publish(language)
        print(language + ': prompt downloads and numbered compiler examples generated')
