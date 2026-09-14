"""Verify authored prompt coverage, browser copying, links and responsive layout.

Uses an isolated headless Edge session; no user browser profile is touched.
Requires Playwright. The report describes documentation checks, not game tests.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
from datetime import date
from languages import LANGUAGES, HTML_LANG
from generate_prompts import load_prompt, SOURCE

S = Path(__file__).resolve().parents[1]
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.path.insert(0, str(S.parents[1] / '_translation_deps'))
    sys.path.insert(0, str(S.parents[1] / 'publish' / '_translation_deps'))
    from playwright.sync_api import sync_playwright


def main():
    report = {'date': date.today().isoformat(), 'scope': 'Documentation only; no gameplay or hardware claim.',
              'browser': 'Microsoft Edge, isolated headless session', 'editions': [], 'errors': []}
    ui = json.loads((SOURCE / 'ui.json').read_text(encoding='utf-8'))
    source_fields = set(json.loads((SOURCE / 'en/text.json').read_text(encoding='utf-8')))
    for path in SOURCE.glob('*/text.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        assert set(data) == source_fields, path
        assert len(data['headings']) == 9 and all(data.values()), path
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, permissions=['clipboard-read', 'clipboard-write'])
        page = context.new_page()
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        for language in LANGUAGES:
            folder = S if language == 'ja' else S / language
            page.goto((folder / 'loop-engineering.html').as_uri())
            assert page.locator('html').get_attribute('lang') == HTML_LANG.get(language, language)
            assert page.locator('h1').count() == 1
            assert page.locator('[data-copy-source]').count() == 2
            assert page.locator('nav.languages a').count() == 9
            edition = {'language': language, 'prompts': [], 'viewports': []}
            for platform, tool in [('gb', 'kitaqgb'), ('fc', 'kitaqfc')]:
                expected = load_prompt(language, platform)
                downloaded = (S / 'prompts' / language / (tool + '-prompt.md')).read_text(encoding='utf-8')
                assert downloaded == expected
                assert not re.search(r'\{\{(?:CODE|ORIGIN|BUILD)', expected)
                # All executable examples must be byte-identical across languages.
                blocks = re.findall(r'^```powershell\n.*?^```', expected, re.M | re.S)
                original = re.findall(r'^```powershell\n.*?^```', load_prompt('ja', platform), re.M | re.S)
                assert blocks == original, (language, platform)
                button = page.locator('[data-copy-source="prompt-' + platform + '"]')
                button.click()
                page.wait_for_function('(label) => [...document.querySelectorAll("[data-copy-source]")].some(b => b.textContent !== label)', arg=ui[language]['copy_all'])
                actual = page.evaluate('navigator.clipboard.readText()')
                assert actual.replace('\r\n', '\n') == expected, (language, platform, 'clipboard')
                edition['prompts'].append({'platform': platform, 'download_equals_clipboard': True,
                                          'commands_preserved': True, 'sha256': hashlib.sha256(expected.encode()).hexdigest()})
            # An individual command still copies only that command, not the whole prompt.
            command = page.locator('.codebox').first
            command.locator('button.copy').click()
            actual = page.evaluate('navigator.clipboard.readText()')
            assert actual.replace('\r\n', '\n') == command.locator('code').text_content()
            for width in (1440, 390):
                page.set_viewport_size({'width': width, 'height': 1000 if width == 1440 else 844})
                page.goto((folder / 'loop-engineering.html').as_uri())
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), (language, width)
                assert page.locator('[data-copy-source="prompt-gb"]').is_visible()
                edition['viewports'].append(width)
                if (language, width) in [('ja', 1440), ('ko', 1440), ('de', 390)]:
                    page.screenshot(path=str(S / 'verification' / f'prompts-{language}-{width}.png'))
            page.set_viewport_size({'width': 1440, 'height': 1000})
            page.goto((folder / 'kitaqfc.html').as_uri())
            page.locator('section[data-loop-prompts] a').click()
            assert page.url.endswith('loop-engineering.html#fc')
            other = 'ja' if language != 'ja' else 'en'
            page.locator('nav.languages a[hreflang="' + other + '"]').click()
            assert page.url.endswith('loop-engineering.html#fc')
            assert page.locator('html').get_attribute('lang') == other
            edition['fc_anchor_and_language_switch'] = 'passed'
            report['editions'].append(edition)
        browser.close()
    report['status'] = 'passed' if not report['errors'] else 'failed'
    (S / 'verification/prompt_checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    if report['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
