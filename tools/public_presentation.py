"""Keep captured screens with examples and keep local run records out of manuals.

Raw evidence remains available to the authoring checks. The public export uses
the same allowlist to exclude it from the website and Git repository.
"""
from pathlib import Path
import html
import json
import re
from urllib.parse import urlsplit, unquote
from publication_languages import ORDER, ACTIVE_LANGUAGES
from languages import refresh_language_navigation

SITE = Path(__file__).resolve().parents[1]
LANGUAGES = ORDER
PUBLIC_EVIDENCE_SUFFIXES = {'.png', '.gb', '.nes', '.c', '.html'}
INTRO = [
    'Captured emulator screens appear beside the sample explanations. Compare the output with the stated expected result; a screen alone does not verify sound, controller input, peripherals or physical hardware.',
    'エミュレータで確認した画像を、サンプルの説明とともに掲載しています。説明にある期待結果と見比べてください。画像だけで音、操作入力、周辺機器、実機の動作まで確認できるわけではありません。',
    '에뮬레이터에서 확인한 화면을 샘플 설명과 함께 제공합니다. 설명에 나온 예상 결과와 비교하세요. 화면만으로는 소리, 컨트롤러 입력, 주변 기기 또는 실제 하드웨어의 동작을 확인할 수 없습니다.',
    '模拟器中确认的画面与示例说明一同展示。请对照说明中的预期结果查看。仅凭画面无法验证声音、手柄输入、外设或实机运行情况。',
    '模擬器中確認的畫面與範例說明一同呈現。請對照說明中的預期結果查看。僅憑畫面無法驗證聲音、控制器輸入、周邊設備或實機運作情況。',
    'Las capturas del emulador acompañan las explicaciones de los ejemplos. Compárelas con el resultado esperado. Una imagen por sí sola no verifica el sonido, la entrada del mando, los periféricos ni el funcionamiento en hardware real.',
    'As capturas do emulador aparecem junto às explicações dos exemplos. Compare-as com o resultado esperado. Uma imagem, por si só, não comprova o funcionamento do som, dos controles, dos periféricos ou do hardware real.',
    'Les captures de l’émulateur accompagnent les explications des exemples. Comparez-les au résultat attendu. Une image seule ne permet pas de vérifier le son, les commandes, les périphériques ou le fonctionnement sur le matériel réel.',
    'Die im Emulator aufgenommenen Bilder stehen bei den Erläuterungen der Beispiele. Vergleichen Sie sie mit dem beschriebenen Ergebnis. Ein Bild allein bestätigt weder Ton und Controllereingaben noch die Funktion von Peripheriegeräten oder echter Hardware.',
]
CAPTURE = ['Captured screen', '確認した実行画面', '확인한 실행 화면', '已确认的运行画面', '已確認的執行畫面', 'Captura de la ejecución', 'Captura da execução', 'Capture de l’exécution', 'Aufnahme der Ausführung']


def public_file(relative):
    path = Path(relative)
    if any(part.startswith('.') or part == '__pycache__' for part in path.parts):
        return False
    if path.parts[:2] == ('verification','api-sound'):
        if 'state' in path.parts or 'integration_test' in path.parts:return False
        if 'fc-midi' in path.parts and path.suffix=='.wav':return False
        return path.suffix in PUBLIC_EVIDENCE_SUFFIXES | {'.wav','.fds'}
    if path.parts[:2] in [('samples', 'out'), ('samples', 'sarakura-out')]:
        return False
    if path.suffix == '.pyc':
        return False
    # Per-case memory snapshots and fixtures are private authoring evidence.
    # The three teaching ROMs/screens have distinct gb-dmg, gb-cgb and fc-nrom folders.
    if len(path.parts)>2 and path.parts[0]=='verification' and path.parts[1] in ('api-memory-intrinsics','api-bit-intrinsics','api-rng') and path.parts[2] in ('gb','fc'):
        return False
    if path.parts[:3] in [('verification','api-flags','state'),('verification','api-rle','state'),('verification','api-text-layout','state'),('verification','api-dialogue','state'),('verification','api-batch100','state'),('verification','api-batch200','state')]:
        return False
    if path.parts[:3] in [('verification','api-physics','state'),('verification','api-physics','multiply')]:
        return False
    return path.parts[0] != 'verification' or path.suffix in PUBLIC_EVIDENCE_SUFFIXES


def private_link(page, url):
    parsed = urlsplit(html.unescape(url))
    if parsed.scheme or parsed.netloc or not parsed.path:
        return False
    target = (page.parent / unquote(parsed.path)).resolve()
    if not target.is_relative_to(SITE):
        return False
    return not public_file(target.relative_to(SITE))


def normalize(language):
    if language not in ACTIVE_LANGUAGES:
        raise ValueError('Updates are paused for this edition: ' + language)
    index = LANGUAGES.index(language)
    folder = SITE if language == 'ja' else SITE / language
    prefix = '' if language == 'ja' else '../'
    for path in folder.glob('*.html'):
        refresh_language_navigation(path, language)
        original = path.read_bytes()
        text = original.decode('utf-8').replace('\r\n', '\n')
        if path.name == 'verification.html':
            text = re.sub(r'<p class="subtitle">.*?</p>', '<p class="subtitle">' + html.escape(CAPTURE[index]) + '</p>', text, count=1, flags=re.S)
            # Keep the introductory sample gallery, discarding embedded raw JSON.
            sections = re.findall(r'<section id="(?:gb|fc)_[^"]+">.*?</section>', text, re.S)
            clean = []
            for section in sections:
                section = re.sub(r'(<h2\b[^>]*>.*?</h2>)<p>.*?</p>', r'\1', section, count=1, flags=re.S)
                clean.append(section)
            start = text.index('<h2 id="scope">')
            end = text.index('<footer', start)
            title = re.match(r'<h2[^>]*>.*?</h2>', text[start:], re.S)[0]
            # This marker prevents repeated cleanup from stripping expected text.
            if 'data-public-gallery="true"' not in text:
                text = text[:start] + '<div data-public-gallery="true">' + title + '<p>' + html.escape(INTRO[index]) + '</p>' + ''.join(clean) + '</div>' + text[end:]
            anchors = {'scope'} | set(re.findall(r'id="([^"]+)"', ''.join(sections)))
            def toc(match):
                links = ''.join(m[0] for m in re.finditer(r'<a href="#([^"]+)">.*?</a>', match[2]) if m[1] in anchors)
                return match[1] + links + match[3]
            text = re.sub(r'(<nav\b[^>]*class="toc"[^>]*>)(.*?)(</nav>)', toc, text, flags=re.S)
        else:
            # Complete teaching samples also display their own captured screen.
            def sample(match):
                block, name = match[0], match[1]
                if 'class="example-result"' in block:
                    return block
                shot = SITE / 'verification' / (name + '.png')
                if not shot.is_file():
                    return block
                caption = CAPTURE[index] + ': ' + name
                figure = '<figure class="example-result"><img class="screen" loading="lazy" src="' + prefix + 'verification/' + name + '.png" alt="' + html.escape(caption, quote=True) + '"><figcaption>' + html.escape(caption) + '</figcaption></figure>'
                return re.sub(r'(</summary><p>.*?</p>)', lambda m: m[1] + figure, block, count=1, flags=re.S)
            text = re.sub(r'<details class="sample searchable" id="sample-([^"]+)">.*?</details>', sample, text, flags=re.S)
        if path.name == 'index.html':
            paragraphs = json.loads((SITE / 'tools/public_font_paragraphs.json').read_text(encoding='utf-8'))
            text = re.sub(r'<p>(?:(?!</p>).)*font_source_atlas\.png(?:(?!</p>).)*</p>', lambda m: paragraphs[index].format(prefix=prefix), text, flags=re.S)
        # Removing anchors also removes the impression that raw local records are
        # available; ordinary build commands and useful example output stay intact.
        text = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>.*?</a>', lambda m: '' if private_link(path, m[1]) else m[0], text, flags=re.S)
        text = re.sub(r'<p>[\s/／·|]*</p>', '', text)
        path.write_text(text, encoding='utf-8', newline='\r\n' if b'\r\n' in original else '\n')


if __name__ == '__main__':
    for language in ACTIVE_LANGUAGES:
        normalize(language)
