from languages import language_nav
"""Generate the complete English edition from the shared source inventory.

Hand-edited prose lives in tools/en. Original source excerpts and captured help
are intentionally preserved verbatim; signatures, examples and evidence are shared.
"""
import html
import json
import re
from pathlib import Path
import generate as g
from sample_guides import GUIDES, render as sample_guide, screen as sample_screen, gallery as sample_gallery

S = g.SITE
E = html.escape
BOOKS = [(k,n,t,s) for (k,n,t,_),s in zip(g.BOOKS,[
    'Game Boy C programming','Tools for building a game','Run, observe and record',
    'Famicom C programming','NES libraries and devices','NES and FDS execution and analysis',
    'Diagnostics, comparison and retesting'])]
ORIGIN = """NORCAL takes its name from Northern California. Inspired by this geographical naming, the author named KITAQGB after Kitakyushu, the city where they were born and raised. KITAQ + GB combines Game Boy with KITAQ, the nickname of Kitakyushu in Fukuoka Prefecture, Japan: **北九 (キタキュー, Kitakyū)**. Pronounce KITAQ as **kee-tah-KYOO**, IPA **/ˌkiːtɑːˈkjuː/**. The final Q sounds like the English letter Q. Read KITAQGB as **kee-tah-KYOO jee bee**, pronouncing G and B separately.

The name KITAQGB has two meanings. **Kernel-Informed Toolchain for AI-Quality Game Boy Development** expresses the goal of a toolchain that understands its target machine and supports both human programmers and generative AI.

The other meaning is **Kids' Imagination Transformed into Actual Quests in Game Boy Forests**: a tool that turns children’s imagination into real adventures in the forests of Game Boy. It expresses the creative wish to turn small ideas, sketches and AI-assisted prototypes into adventures people can actually play."""
MODULES = dict(zip(g.MODULES, [
    'Startup, frame counts, waits and interrupts','Button state, press, release and repeat',
    'OBJ allocation, positioning, metasprites and animation','Queued VRAM updates and transfer',
    'Q8.8 fixed-point arithmetic and rectangles','Scene registration, changes and updates',
    'Object pools backed by fixed arrays','Ring buffers for position history',
    'Music, sound effects and audio control','Music playback through the VBlank IRQ',
    'Random numbers, text, maps, saves and RPG/ADV/SLG services','Bank-aware code and data access',
    'Asset IDs and data descriptors','RAM records and assertions','CGB BG and OBJ palettes',
    'CGB tile numbers and attributes','Background, window and split scrolling',
    'Scroll tables for bands and scanlines','World coordinates and visible areas',
    'Serial communication and logical packets','DMG-07 external-clock communication',
    'Boards, move lists and undo','2D motion and collision','Circle physics',
    '3D AABB physics','Wireframes for DMG','Color wireframes for CGB',
    'Monochrome 128x120 wireframes for DMG','Bullet pools, fans, hits and grazing',
    'Compiler intrinsics','Basic integer types','Umbrella library header',
    'C helpers for NMI, OAM and PPU transfer','PPU display declarations','Direct PPU operations',
    'VRAM queues processed by NMI','NES palettes','Nametable attributes','Rectangular tilemap operations',
    'Nametable assets and placement','Images composed of several sprites','OAM shadow operations',
    'Sprite rotation with priorities','Sprite rotation implementation','Game actor arrays',
    'Rectangle and other collision tests','Held-button repeat','NES controller input',
    'Light-gun input interface','Keyboard scanning','ROB control','Microphone input',
    'MIDI input and output interface','Mapper banks and IRQs','FDS disk operations','Loading FDS files',
    'FDS overlay code','FDS save declarations','FDS wavetable audio','VRC6 expansion audio',
    'VRC7 FM audio','Fast integer arithmetic','Fixed-point intrinsic interface','Lookup tables',
    'Game-oriented operation macros','Wireframes for DMG','Sprite selection by priority and rotation']))
assert len(MODULES) == len(g.MODULES)
def code(t,lang='c'):
    return '<div class="codebox"><span class="lang">'+E(lang)+'</span><button class="copy" type="button">Copy</button><pre><code>'+E(t.strip())+'</code></pre></div>'

def page(key,title,subtitle,body):
    # Assets and source files are shared; links between volumes remain in /en/.
    body = re.sub(r'(href|src)="(samples/|verification/|reference/|assets/)',r'\1="../\2',body)
    nav = '<a href="index.html">Contents</a>'+''.join('<a '+('aria-current="page" ' if key==k else '')+'href="'+k+'.html"><b>'+n+'</b> '+E(t)+'</a>' for k,n,t,s in BOOKS)
    toc = ''.join('<a href="#'+i+'">'+re.sub('<[^>]+>','',t)+'</a>' for i,t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body))
    text = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>'+E(title)+' — KITAQ SERIES MANUAL</title><link rel="stylesheet" href="../assets/manual.css"></head><body><a class="skip" href="#main">Skip to content</a><header class="mast"><a href="index.html">KITAQ <span>DEVELOPMENT SYSTEM</span></a><div>USER\'S MANUAL <b>2026.09</b> · <a href="../'+key+'.html" lang="ja" hreflang="ja">日本語</a></div></header><div class="layout"><aside><nav aria-label="Select a volume">'+nav+'</nav><label class="searchlabel" for="search">Search this volume</label><input type="search" id="search" placeholder="e.g. input / __memcpy"><p id="search-status" role="status"></p><nav class="toc" aria-label="Volume contents">'+toc+'</nav><button class="print" type="button">Print this volume</button></aside><main id="main"><div class="cover"><p class="eyebrow">KITAQ SERIES • REFERENCE EDITION</p><h1>'+E(title)+'</h1><p class="subtitle">'+E(subtitle)+'</p><div class="edition">From your first line to execution, observation and retesting.<br>Source snapshot: September 14, 2026 · English edition: September 14, 2026</div></div>'+body+'<footer>Source edition 2026-09-14 • <a href="index.html">Contents</a> • <a href="verification.html">Verification</a> • <a href="../reference/inventory.json">Snapshot fingerprints</a><br>Sample builds, emulator execution and expected-result comparisons are recorded separately.</footer></main></div><script src="../assets/manual.js"></script></body></html>'
    text = text.replace(' · <a href="../'+key+'.html" lang="ja" hreflang="ja">日本語</a>', '')
    text = text.replace('</header>', '</header>'+language_nav(key,'en'), 1)
    dest=S/'en'/(key+'.html');dest.parent.mkdir(exist_ok=True);dest.write_text(text.replace('\r\n','\n'),encoding='utf-8',newline='\n')

def samples_section(platform,manifest):
    out=['<h2 id="samples">Complete sample programs</h2><p>Each program, the shared headers, the supplied ascii.c and its converted assets are included. Names beginning with m_ are helpers written for these manuals. Read each build command together with its expected result and verification record. Run commands from the parent of the sibling repository folders.</p><p><a href="samples/build.ps1">Batch build script</a> / <a href="verification.html">Results and screenshots</a></p>']
    titles={'font':'Supplied letters, digits and symbols','hello':'Your first display','arithmetic':'Variables, arithmetic and conversions','control':'Branches and loops','aggregate':'Functions, arrays, structures and pointers','input':'Read controller input','sprite':'Place a sprite','entity':'An object pool','fixed':'Fixed-point arithmetic','scene':'Scene management','chain':'Position history','audio':'Music and sound effects','vram':'VRAM updates','bank':'Banked data','rpg':'Text and game helpers','scroll':'Scrolling','camera':'Camera coordinates','cgb':'Game Boy Color','palette':'Palette operations','collision':'Collision tests','mapper':'Mapper operations','physics':'Motion and physics','ppu':'PPU updates','oam':'OAM operations'}
    for d in manifest:
        if d['platform']!=platform:continue
        name=d['id'].split('_',1)[1]
        title=GUIDES[d['id']]['en'][0]
        lib=platform=='gb' and 'kitaqgb/lib' or 'kitaqfc/lib'
        exe='.\\kitaqgb\\kitaqgb.exe' if platform=='gb' else '.\\kitaqfc\\kitaqfc.exe'
        cmd=exe+' '+' '.join(lib+'/'+f for f in d['libs'])+' kitaq-docs/samples/'+d['file']+' -I '+lib+' -I kitaq-docs/samples -o out/'+d['id']+('.gb' if platform=='gb' else '.nes')
        cmd+=' --profile=dev --rst-disable --stack-bank=fixed' if platform=='gb' else ' --mapper=nrom --nes-chr=kitaq-docs/samples/font.chr'
        cmd+=' '+' '.join(d['options'])
        if d.get('known_issue'):cmd='# Known build limitation: '+d['known_issue']+'\n'+cmd
        out.append('<details class="sample searchable" id="sample-'+d['id']+'"><summary>'+E(title)+' <code>'+d['file']+'</code></summary>'+sample_guide(d['id'],'en')+sample_screen(d['id'],'en')+'<p><a href="samples/'+d['file']+'" download>Download source</a> / <a href="verification.html#'+d['id']+'">Verification status</a></p>'+code(cmd,'powershell')+code(g.read(S/'samples'/d['file']))+'</details>')
    return ''.join(out)

def api_section(platform,intrinsic):
    from api_scaffold import section
    return section(platform,intrinsic,'en',MODULES)

CLI_TITLES={
    'battery-export':'Export raw battery RAM from a saved state','battery-run':'Boot with saved RAM',
    'inspect-rom':'Inspect the ROM header','audit-board':'Check board requirements','run':'Run for a fixed number of frames',
    'trace':'Record a chronological event trace','audio-export':'Write PCM audio to WAV','profile':'Locate execution hotspots',
    'diagnose':'Produce static and runtime diagnostics','replay-record':'Record a reference replay','replay-run':'Execute a recorded input sequence',
    'snapshot-save':'Save machine state','snapshot-load':'Inspect a state file','snapshot-resume':'Continue from saved state',
    'snapshot-rebase':'Transfer state to a ROM permitted by a compatibility contract','diff':'Compare saved results',
    'decompile':'Recover functions, control-flow graphs and pseudocode','disasm':'Display CPU instructions',
    'mapper-test':'Observe mapper behavior','fds-inspect':'Inspect disk structure','export-assets':'Export assets from a ROM',
    'report':'Create a report from saved observations','mapper-list':'List registered mappers','mapper-info':'Describe a mapper',
    'gb analyze':'Collect Game Boy diagnostics','fc analyze':'Collect Famicom diagnostics','catalog':'List diagnostic rules',
    'validate':'Validate the diagnostic format','compare':'Compare two diagnostic results','inspect-events':'Summarize events',
    'inspect-metadata':'Inspect build information','retest-plan':'Create a retest plan','emitter-check':'Check emitter contract compliance',
    'normalize-events':'Normalize the event format','ci-summary':'Evaluate CI failure conditions','coverage':'List observed rules',
    'pack-plan':'Describe rule plans by area','repair-plan':'Create a repair plan','automation-plan':'Match plans to tool capabilities',
    'baseline-delta':'Measure improvements and regressions from a baseline','schema export':'Export JSON schemas',
    'inspect-repro':'Inspect a reproduction bundle'}

def cli_section(key,inventory):
    out=['<h2 id="commands">Command syntax reference</h2><p>The following help was captured for the source edition. Consult it for optional arguments, defaults and accepted values. Replace the illustrative input filenames with your own outputs. Captured tool responses retain their original wording.</p>']
    for h in inventory['tools'][key]['help']:
        cmd=' '.join(h['argv'][:-1]);entry=g.CLI_EXAMPLES.get(key,{}).get(cmd);label=key+' '+cmd
        out.append('<details class="command searchable" id="cmd-'+g.slug(label)+'"><summary><code>'+E(label)+'</code>'+(' — '+E(CLI_TITLES[cmd]) if entry else '')+'</summary>')
        if entry:out.append(code(key+' '+entry[1],'powershell'))
        out.append(code(h['text'],'help')+'</details>')
    if key in ('kitaqgb','kitaqfc'):
        base=g.ROOT/key/key
        out.append('<h3>Developer command syntax</h3><p>These usages come from Program.DebugTools.cs and Program.VibeTools.cs. ROM comparison, symbol search and templates are subcommands separate from ordinary C compilation.</p>')
        for file in ('Program.DebugTools.cs','Program.VibeTools.cs'):
            for usage in re.findall(r'"(usage: [^"\r\n]+)"',g.read(base/file)):out.append(code(usage,'usage'))
        options=re.findall(r'arg\s*==\s*"(--[\w-]+)"|arg\.StartsWith\("(--[\w-]+)=?',g.read(base/'Program.cs'))
        names=sorted({a or b for a,b in options})
        out.append('<h3>Long options recognized by the parser</h3><p>Spellings were extracted from Program.cs, including compatibility and investigative options. Consult help and the corresponding handler to determine whether each option takes a value.</p><div class="tokens">'+''.join('<code>'+E(n)+'</code>' for n in names)+'</div>')
    return ''.join(out)

def headers_section(platform):
    data=json.loads(g.read(S/'reference'/(platform+'-api.json')))
    out=['<h2 id="headers">Structures, constants and complete headers</h2><p>Consult these headers for non-function macros, structures, array limits, enums and aliases. They reproduce the collected source verbatim, including original comments.</p>']
    for p in data['headers']:out.append('<details class="searchable"><summary><code>'+E(Path(p).name)+'</code> — '+E(MODULES.get(Path(p).stem,''))+'</summary>'+code(g.read(g.ROOT/p))+'<p class="source">'+E(p)+'</p></details>')
    return ''.join(out)

def asm_section(platform):
    body=g.asm_section(platform)
    start=body.index('<div class="tablewrap">')
    table=body[start:].replace('命令名','Instruction').replace('形式','Format').replace('書式例','Syntax example')
    return '<h2 id="assembly">Appendix: assembly instruction index</h2><p>This table is extracted from AsmInfo.cs. It describes the compiler internal spellings and operand formats. Entries with branch destinations or memory addresses are syntax examples, not standalone programs. Consult calling conventions and code generation for preserved registers and flag changes.</p>'+table

def verification():
    page('verification','VERIFICATION','Captured screens',sample_gallery('en'))

def main():
    inventory=json.loads(g.read(S/'reference/inventory.json'));manifest=json.loads(g.read(S/'samples/manifest.json'))
    g.code=code
    for key,num,title,sub in [('index','00','KITAQ SERIES','Programming and user manuals'),*BOOKS]:
        original=g.TEXT[key]
        blocks=re.findall(r'^```[^\n]*\n.*?^```',original,flags=re.M|re.S)
        prose=g.read(S/'tools/en'/(key+'.md')).replace('{{ORIGIN}}',ORIGIN)
        prose=re.sub(r'\{\{CODE:(\d+)\}\}',lambda m:blocks[int(m[1])],prose)
        # Commands from the source-workspace edition need the public sibling layout.
        prose=prose.replace('.\\kitaqgb.exe','.\\kitaqgb\\kitaqgb.exe')
        body=g.md(prose)
        if key=='kokura':
            from kokura_guide import block
            body+=block('en')
        if key=='index':body+='<h2 id="books">Choose a manual</h2><div class="books">'+''.join('<a class="book" href="'+k+'.html"><span>'+n+'</span><strong>'+E(t)+'</strong><small>'+E(s)+'</small></a>' for k,n,t,s in BOOKS)+'</div>'
        if key=='index':
            from application_guides import block as application_guides
            body+=application_guides('en')
        if key in ('kitaqgb','gb-library','kitaqfc','fc-library'):
            p='gb' if key in ('kitaqgb','gb-library') else 'fc'
            body+=samples_section(p,manifest)+api_section(p,key in ('kitaqgb','kitaqfc'))
            body+=headers_section(p) if key.endswith('library') else cli_section(key,inventory)+asm_section(p)
        elif key!='index':body+=cli_section(key,inventory)
        page(key,title,sub,body)
    verification()
    from generate_prompts import publish
    publish('en')
    from api_contracts import publish as publish_api_contracts
    publish_api_contracts('en', require_complete=True)
    print('Generated 10 English HTML pages including development prompts')

if __name__=='__main__':main()
