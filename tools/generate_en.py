"""Generate the complete English edition from the shared source inventory.

Hand-edited prose lives in tools/en. Original source excerpts and captured help
are intentionally preserved verbatim; signatures, examples and evidence are shared.
"""
import html
import json
import re
from pathlib import Path
import generate as g

S = g.SITE
E = html.escape
BOOKS = [(k,n,t,s) for (k,n,t,_),s in zip(g.BOOKS,[
    'Game Boy C programming','Tools for building a game','Run, observe and record',
    'Famicom C programming','NES libraries and devices','NES and FDS execution and analysis',
    'Diagnostics, comparison and retesting'])]
ORIGIN = """**KITAQGB has a double meaning.** The first is **Kernel-Informed Toolchain for AI-Quality Game Boy Development**: a toolchain grounded in a deep understanding of the target machine, intended to support both human programmers and generative AI.

The second is **Kids' Imagination Transformed into Actual Quests in Game Boy Forests**. It expresses the wish to turn small ideas, sketches and AI-assisted prototypes into adventures that people can actually play. Both meanings come from the README supplied by the author."""
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
    'X-style wireframes for DMG','Bullet pools, fans, hits and grazing',
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
    'Game-oriented operation macros']))
assert len(MODULES) == len(g.MODULES)
SPECIAL = dict(zip(g.SPECIAL, [
    'The low eight bits hold current keys; the high eight bits hold newly pressed keys. Supply the previous state to detect edges.',
    'Wait for the next display update. Avoid accidentally waiting twice in one game frame.',
    'Copy len bytes from source to destination. The caller must provide sufficient storage and valid bank mappings.',
    'Fill a region with a repeated byte value. len is a byte count.',
    'Get the placement bank of a symbol. This differs from passing an arbitrary numeric address.',
    'Initialize previous and current input, edges and repeat state. Call once at startup.',
    'Read the pad and update press and release edges, normally once per game frame.',
    'Test whether the buttons selected by mask are currently held.',
    'Test whether the buttons selected by mask were newly pressed in this update.',
    'Test whether the buttons selected by mask were released in this update.',
    'Test the initial press and subsequent repeats at the configured interval.',
    'Initialize the sound hardware and driver state. Include the APU register definitions first.',
    'Advance music, effects and fades, normally once per frame.',
    'Start music from a bank number and song data in the driver stream format.',
    'Start a sound effect at the requested priority and record the currently visible ROM bank.',
    'Change the music/effect driver pause state. The game must separately pause its own logic.',
    'On GB, the wait function calls this callback cooperatively. The current FC implementation only stores it; it does not invoke it automatically.',
    'Allocate a free sprite slot. Check for the failure value before using the result.',
    'Initialize a free object and return its ID, or 0xFF when the pool is full.',
    'Return the object for a valid ID. Check for NULL for out-of-range or inactive IDs.',
    'Convert an integer to Q8.8. Integer 1 is represented by 256.',
    'Extract the integer part of Q8.8. Consult the implementation for rounding of negative values.',
    'Multiply two Q8.8 values and return a Q8.8 result. Keep inputs within the supported range.',
    'Divide Q8.8 values. Avoid zero divisors and values outside the representable range.',
    'Pack RGB components, each in 0–31, into the Game Boy Color 15-bit format.',
    'Select a BG palette and color slot, then set RGB components in 0–31.',
    'Select an OBJ palette and color slot, then set RGB components in 0–31.',
    'Wait for NMI-driven frame progress. Enable NMI before calling.',
    'Commit prepared VRAM updates for processing by NMI.',
    'Apply queued updates to the PPU, normally during the safe NMI interval.',
    'Disable rendering before direct PPU updates such as initial loading.',
    'Set NES scroll coordinates, including restoring scroll after PPU transfers.']))
assert len(SPECIAL) == len(g.SPECIAL)

def purpose(r):
    if r['name'] in SPECIAL: return SPECIAL[r['name']]
    verbs = [('init','Prepare initial state'),('clear','Clear contents or state'),('reset','Reset state'),
        ('get','Retrieve a value or state'),('read','Read a value'),('write','Write a value'),
        ('set','Set a value or operating condition'),('draw','Create drawing data'),('load','Load data'),
        ('save','Save data'),('update','Update state'),('step','Advance one processing step'),
        ('wait','Wait for a condition'),('enable','Enable a feature'),('disable','Disable a feature'),
        ('copy','Copy data'),('fill','Fill a region'),('flush','Apply accumulated updates'),
        ('count','Get a count'),('push','Append data'),('pop','Remove and retrieve data')]
    verb = next((v for k,v in verbs if k in r['name'].lower()),'Perform the operation specified by the arguments')
    return verb+'. Module: '+MODULES.get(r['module'],r['module'])+'. The declaration, original notes and implementation below define exact units, terminators and return conditions.'

def code(t,lang='c'):
    return '<div class="codebox"><span class="lang">'+E(lang)+'</span><button class="copy" type="button">Copy</button><pre><code>'+E(t.strip())+'</code></pre></div>'

def page(key,title,subtitle,body):
    # Assets and source files are shared; links between volumes remain in /en/.
    body = re.sub(r'(href|src)="(samples/|verification/|reference/|assets/)',r'\1="../\2',body)
    nav = '<a href="index.html">Contents</a>'+''.join('<a '+('aria-current="page" ' if key==k else '')+'href="'+k+'.html"><b>'+n+'</b> '+E(t)+'</a>' for k,n,t,s in BOOKS)
    toc = ''.join('<a href="#'+i+'">'+re.sub('<[^>]+>','',t)+'</a>' for i,t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',body))
    text = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><title>'+E(title)+' — KITAQ SERIES MANUAL</title><link rel="stylesheet" href="../assets/manual.css"></head><body><a class="skip" href="#main">Skip to content</a><header class="mast"><a href="index.html">KITAQ <span>DEVELOPMENT SYSTEM</span></a><div>USER\'S MANUAL <b>2026.09</b> · <a href="../'+key+'.html" lang="ja" hreflang="ja">日本語</a></div></header><div class="layout"><aside><nav aria-label="Select a volume">'+nav+'</nav><label class="searchlabel" for="search">Search this volume</label><input type="search" id="search" placeholder="e.g. input / __memcpy"><p id="search-status" role="status"></p><nav class="toc" aria-label="Volume contents">'+toc+'</nav><button class="print" type="button">Print this volume</button></aside><main id="main"><div class="cover"><p class="eyebrow">KITAQ SERIES • REFERENCE EDITION</p><h1>'+E(title)+'</h1><p class="subtitle">'+E(subtitle)+'</p><div class="edition">From your first line to execution, observation and retesting.<br>Source snapshot: September 12, 2026 · English edition: September 13, 2026</div></div>'+body+'<footer>Source edition 2026-09-12 • <a href="index.html">Contents</a> • <a href="verification.html">Verification</a> • <a href="../reference/inventory.json">Snapshot fingerprints</a><br>Sample builds, emulator execution and expected-result comparisons are recorded separately.</footer></main></div><script src="../assets/manual.js"></script></body></html>'
    dest=S/'en'/(key+'.html');dest.parent.mkdir(exist_ok=True);dest.write_text(text,encoding='utf-8')

def samples_section(platform,manifest):
    out=['<h2 id="samples">Complete sample programs</h2><p>Each program, the shared headers, the supplied ascii.c and its converted assets are included. Names beginning with m_ are helpers written for these manuals. Read each build command together with its expected result and verification record. Run commands from the parent of the sibling repository folders.</p><p><a href="samples/build.ps1">Batch build script</a> / <a href="verification.html">Results and screenshots</a></p>']
    titles={'font':'Supplied letters, digits and symbols','hello':'Your first display','arithmetic':'Variables, arithmetic and conversions','control':'Branches and loops','aggregate':'Functions, arrays, structures and pointers','input':'Read controller input','sprite':'Place a sprite','entity':'An object pool','fixed':'Fixed-point arithmetic','scene':'Scene management','chain':'Position history','audio':'Music and sound effects','vram':'VRAM updates','bank':'Banked data','rpg':'Text and game helpers','scroll':'Scrolling','camera':'Camera coordinates','cgb':'Game Boy Color','palette':'Palette operations','collision':'Collision tests','mapper':'Mapper operations','physics':'Motion and physics','ppu':'PPU updates','oam':'OAM operations'}
    for d in manifest:
        if d['platform']!=platform:continue
        name=d['id'].split('_',1)[1]
        title=titles.get(name,name.replace('_',' ').capitalize())
        lib=platform=='gb' and 'kitaqgb/lib' or 'kitaqfc/lib'
        exe='.\\kitaqgb\\kitaqgb.exe' if platform=='gb' else '.\\kitaqfc\\kitaqfc.exe'
        cmd=exe+' '+' '.join(lib+'/'+f for f in d['libs'])+' kitaq-docs/samples/'+d['file']+' -I '+lib+' -I kitaq-docs/samples -o out/'+d['id']+('.gb' if platform=='gb' else '.nes')
        cmd+=' --profile=dev --rst-disable --stack-bank=fixed' if platform=='gb' else ' --mapper=nrom --nes-chr=kitaq-docs/samples/font.chr'
        cmd+=' '+' '.join(d['options'])
        if d.get('known_issue'):cmd='# Known build limitation: '+d['known_issue']+'\n'+cmd
        out.append('<details class="sample searchable" id="sample-'+d['id']+'"><summary>'+E(title)+' <code>'+d['file']+'</code></summary><p>Expected result: '+E(d['expected'])+'</p><p><a href="samples/'+d['file']+'" download>Download source</a> / <a href="verification.html#'+d['id']+'">Verification status</a></p>'+code(cmd,'powershell')+code(g.read(S/'samples'/d['file']))+'</details>')
    return ''.join(out)

def api_section(platform,intrinsic):
    data=json.loads(g.read(S/'reference'/(platform+'-api.json')))
    records=[r for r in data['records'] if r['name'].startswith('__')==intrinsic]
    out=['<h2 id="api">'+('Compiler intrinsic' if intrinsic else 'Library API')+' dictionary</h2><p>'+str(len(records))+' entries. Open an entry for its syntax, arguments, source notes and usage example. Calling fragments require surrounding initialization; they are not standalone ROMs. Newly supplied argument-passing examples show how prepared values reach the API, and do not establish device-level verification.</p><p>Source excerpts and original declaration notes are reproduced verbatim, including comments in their original language. The English explanation precedes each declaration.</p>']
    for mod in sorted(set(r['module'] for r in records)):
        out.append('<h3 id="module-'+mod+'">'+mod+'.h — '+E(MODULES.get(mod,'Compiler functionality'))+'</h3>')
        for r in sorted((r for r in records if r['module']==mod),key=lambda r:r['name'].lower()):
            status={'compiler':'Compiler intrinsic','implementation':'Implementation found','declaration':'Declaration only; body not found','macro':'Macro'}[r['availability']]
            out.append('<details class="api searchable" id="api-'+r['name']+'"><summary><code>'+E(r['name'])+'</code><span class="badge">'+status+'</span></summary><p>'+E(purpose(r))+'</p>'+code(r['signature']))
            if r.get('arity_only'):out.append('<p class="note">This syntax records the argument count from code generation. Names such as arg0 are explanatory placeholders, not type declarations. Follow the usage example and implementation requirements.</p>')
            elif r['args'] and r['args']!='void':out.append('<p><b>Arguments, left to right: </b>'+E(r['args'])+'. For arrays and pointers, allocate sufficient storage and keep it valid until processing finishes.</p>')
            if r['ret'] not in ('','void','macro'):out.append('<p><b>Return type: </b><code>'+E(r['ret'])+'</code>. The original notes and return conditions in the implementation define the meaning and success or failure values.</p>')
            if r['comment']:out.append('<div class="original"><b>Original declaration notes (verbatim)</b><pre>'+E(r['comment'])+'</pre></div>')
            if r['availability']=='declaration':out.append('<p class="note">A public header declares this API, but the collected sources did not reveal its body. This is not evidence that it links or runs. Identify the providing compilation unit before use.</p>')
            ex=r.get('example')
            if ex:
                out.append('<h4>Calling example (surrounding-code fragment)</h4>'+code(ex['code'])+'<p class="source">Source: '+E(ex['path'])+':'+str(ex['line'])+'</p>')
                if 'kitaq-docs/samples/' in ex['path']:out.append('<p><a href="samples/'+ex['path'].split('/')[-1]+'">Complete program for this example</a></p>')
            else:
                out.append('<h4>New argument-passing example</h4>'+code(r.get('new_example',r['signature']))+'<p>Prepare object initialization, buffer sizes, ROM banks and device state in the calling code. This function fragment has not been executed in isolation.</p><p><a href="samples/api-fragments/'+platform+'/'+r['name']+'.c" download>Download this fragment</a></p>')
            d=r.get('definition')
            if d:out.append('<p class="source"><b>Implementation to include: </b><code>'+E(d['path'])+'</code>:'+str(d['line'])+'. Include the providers of any additional functions it calls.</p><details><summary>Read the current implementation</summary>'+code(d['body'])+'</details>')
            elif r.get('implementation_excerpt'):out.append('<details><summary>Code generator argument checks</summary>'+code(r['implementation_excerpt'],'csharp')+'</details>')
            out.append('<p class="source">Declaration or identifier source: '+E(r['path'])+':'+str(r['line'])+'</p></details>')
    return ''.join(out)

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
    body='<h2 id="scope">Verification scope</h2><p>The records below belong to the September 12 source snapshot. The two compilers and KUROSAKI CLI were built from the collected sources. KOKURA and SARAKURA used local executables fingerprinted in the inventory. These checks do not cover all features, peripherals or physical hardware.</p><p>Each entry records compilation, a 120-frame emulator run and its screenshot. Pixel comparisons are separate evidence. Exit code zero alone does not prove correct input, sound or game behavior. Publication builds and workspace tests performed later are documented in <a href="../PUBLICATION_CHECKS.md">publication checks</a>; translating the manuals did not rerun every historical observation.</p>'
    results=json.loads(g.read(S/'verification/samples.json'))
    for r in results:
        ident=r['id'];body+='<section id="'+ident+'"><h2 id="result-'+ident+'">'+ident+'</h2><p>Build exit code: '+E(str(r['build_exit']))+' / Runtime status: '+E(r['runtime'])+'</p><p>'+E(r.get('expected',''))+'</p>'
        if (S/'verification'/(ident+'.png')).exists():body+='<img class="screen" loading="lazy" src="verification/'+ident+'.png" alt="Emulator screenshot for '+ident+'">'
        body+='<p><a href="verification/'+ident+'-build.txt">Build log</a>'
        if (S/'verification'/(ident+'-runtime.txt')).exists():body+=' / <a href="verification/'+ident+'-runtime.txt">Runtime log</a>'
        body+='</p></section>'
    for f,t in [('visual_checks.json','Pixel values and font comparisons'),('workflow.json','Diagnostic workflow'),('compiler_tests.json','Compiler regression checks'),('browser_checks.json','Historical browser display checks'),('site_checks.json','HTML structure and links'),('bilingual_checks.json','Complete bilingual edition checks'),('english_browser_checks.json','English edition browser checks')]:
        if (S/'verification'/f).exists():body+='<h2 id="'+f.replace('.','-')+'">'+t+'</h2>'+code(g.read(S/'verification'/f),'json')
    page('verification','VERIFICATION','Build, execution and display records',body)

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
        if key=='index':body+='<h2 id="books">Choose a manual</h2><div class="books">'+''.join('<a class="book" href="'+k+'.html"><span>'+n+'</span><strong>'+E(t)+'</strong><small>'+E(s)+'</small></a>' for k,n,t,s in BOOKS)+'</div>'
        if key in ('kitaqgb','gb-library','kitaqfc','fc-library'):
            p='gb' if key in ('kitaqgb','gb-library') else 'fc'
            body+=samples_section(p,manifest)+api_section(p,key in ('kitaqgb','kitaqfc'))
            body+=headers_section(p) if key.endswith('library') else cli_section(key,inventory)+asm_section(p)
        elif key!='index':body+=cli_section(key,inventory)
        page(key,title,sub,body)
    verification()
    print('Generated 9 English HTML pages with shared API and sample records')

if __name__=='__main__':main()
