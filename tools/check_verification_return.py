"""Check exact-item return links in all manual editions using isolated Edge."""
from pathlib import Path
import json
import sys
from urllib.parse import urlsplit, parse_qs
from languages import LANGUAGES

S = Path(__file__).resolve().parents[1]
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.path.insert(0, str(S.parents[1] / '_translation_deps'))
    sys.path.insert(0, str(S.parents[1] / 'publish' / '_translation_deps'))
    from playwright.sync_api import sync_playwright


def main():
    report = {'scope': 'Manual navigation only', 'browser': 'Isolated headless Microsoft Edge', 'checks': [], 'errors': []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda e: report['errors'].append(str(e)))
        for lang in LANGUAGES:
            folder = S if lang == 'ja' else S / lang
            for platform in ['gb', 'fc']:
                sample = platform + '_hello'
                original = (folder / (platform + '-library.html')).as_uri() + '#sample-' + sample
                page.goto(original)
                entry = page.locator('#sample-' + sample)
                assert entry.get_attribute('open') is not None
                entry.locator('a[href*="verification.html"]').click()
                assert urlsplit(page.url).fragment == sample
                assert parse_qs(urlsplit(page.url).query).get('from')
                link = page.locator('#' + sample + ' .verification-return a')
                assert link.count() == 1
                link.click()
                assert page.url == original, (lang, platform, page.url)
                page.wait_for_function('(id) => document.getElementById(id)?.open === true', arg='sample-' + sample)
                assert page.locator('#sample-' + sample).get_attribute('open') is not None
                report['checks'].append({'language': lang, 'platform': platform, 'exact_item_return': 'passed'})
            page.goto((folder / 'verification.html').as_uri())
            assert page.locator('main > .verification-return a').get_attribute('href') == (folder / 'index.html').as_uri()
        page.goto((S / 'verification.html').as_uri() + '?from=https%3A%2F%2Fexample.com%2Findex.html')
        assert page.locator('main > .verification-return a').get_attribute('href') == (S / 'index.html').as_uri()
        page.goto((S / 'verification.html').as_uri() + '?from=gb-library.html%23sample-gb_hello#gb_hello')
        page.locator('nav.languages a[hreflang="en"]').click()
        page.locator('#gb_hello .verification-return a').click()
        assert page.url == (S / 'gb-library.html').as_uri() + '#sample-gb_hello'
        report['language_switch_keeps_origin'] = 'passed'
        report['direct_entry_and_external_origin_fallback'] = 'passed'
        browser.close()
    report['status'] = 'passed' if not report['errors'] else 'failed'
    (S / 'verification/return_navigation_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
    if report['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
