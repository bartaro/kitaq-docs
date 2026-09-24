"""Navigation for standalone application guides hosted with the manuals."""

def block(language):
    if language == 'ja':
        return '<h2 id="application-guides">ゲームのプログラム解説</h2><div class="books"><a class="book" href="apps/harapeko_shirohebi/guide-ja.html"><span>APP</span><strong>はらぺこしろへび</strong><small>フローチャート・白ヘビの動き・KITAQGBライブラリの利用</small></a></div>'
    return '<h2 id="application-guides">Game programming guides</h2><div class="books"><a class="book" href="../apps/harapeko_shirohebi/guide-en.html"><span>APP</span><strong>HARAPEKO SHIROHEBI</strong><small>Program flow, snake movement and KITAQGB library usage</small></a></div>'
