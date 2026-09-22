"""Prove CH1..CH4 activation, independent stopping and stereo output in each driver.

The VBlank cases execute the installed ISR; queue cases publish complete records
with interrupts disabled. Register observations and PCM are checked separately.
"""
from pathlib import Path
import hashlib, json, subprocess
from check_sound_examples import measure, pcm, SITE, REPOS
from check_batch200 import dependencies
from api_build_cleanup import cleanup_build_outputs

OUT=SITE/'verification/api-sound/channel-routes'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def program(driver, channel):
    wave=channel==3; vb=driver.startswith('vblank'); queue=driver=='vblank-queue'
    prefix='#define SOUND_VBLANK\n' if vb else ''
    stream=f'AUDIO_STREAM_CHANNEL_CH{channel}'
    # Record positions are independently specified, not obtained from the driver.
    position=channel-1
    event=['AUDIO_VBLANK_REST']*4;event[position]='0x35' if channel==4 else '33'
    stop=['AUDIO_VBLANK_REST']*4;stop[position]='AUDIO_VBLANK_STOP'
    event=','.join(event);stop=','.join(stop)
    if vb:
        declarations=f'__prg_rom u8 route_song[]={{30,{event},90,{stop},AUDIO_VBLANK_END}};\n'
        start='Audio_NoiseEffectActive=0;AudioVBlank_Init();AudioVBlank_Ch1Envelope=0xC0;AudioVBlank_Ch2Envelope=0xC0;AudioVBlank_Ch3Level=0x20;AudioVBlank_Ch4Envelope=0xC0;AudioVBlank_PlayMusic(route_song);'
        if queue:
            start+='\n// Publish both records before enabling their ISR consumer.\nSound_SVBK=1;for(i=0;i<10;i++)AudioVBlank_QueueBuffer[i]=route_song[i];AudioVBlank_QueueReadIndex=0;AudioVBlank_QueueWriteIndex=2;AudioVBlank_QueueCount=2;AudioVBlank_QueueMode=1;'
        start+='AudioVBlank_EnableIrq();'
    elif driver=='stream':
        declarations=f'__prg_rom u8 route_song[]={{AUDIO_CMD_SET_INST,{stream},0,0xC0,AUDIO_CMD_SET_CH3_LEVEL,0x20,AUDIO_CMD_NOTE,{stream},'+('0x35' if channel==4 else '33')+f',AUDIO_CMD_WAIT,30,AUDIO_CMD_STOP_CHANNEL,{stream},AUDIO_CMD_WAIT,90,AUDIO_CMD_STOP}};\n'
        start='Audio_PlayMusic(0,route_song);\n// Starting a song resets pan; apply the test routing after that reset.\nAudio_SetPan(AUDIO_CHANNEL_CH1,AUDIO_PAN_LEFT);Audio_SetPan(AUDIO_CHANNEL_CH2,AUDIO_PAN_RIGHT);Audio_SetPan(AUDIO_CHANNEL_CH3,AUDIO_PAN_LEFT);Audio_SetPan(AUDIO_CHANNEL_CH4,AUDIO_PAN_RIGHT);'
    else:
        declarations=''; start={1:'Audio_Ch1NoteOn(33,0xC0,2);',2:'Audio_Ch2NoteOn(33,0xC0,2);',3:'Audio_Ch3NoteOn(33,0x20);',4:'Audio_Ch4NoteOn(0x35,0xC0);'}[channel]
    middle='sound_wait(25);'
    if driver=='direct': middle+=f'Audio_StopChannel(AUDIO_CHANNEL_CH{channel});'
    return prefix+'#include "gb_sound_example.h"\n__location(0xFF70) u8 Sound_SVBK;\n'+declarations+f'''void main() {{
    u8 i;
    sound_begin("CH{channel} {driver.upper()}");
    __asm {{ DI }}
    Audio_SetMasterVolume(3,3);
    // Odd physical channels go left; even physical channels go right.
    Audio_SetPan(AUDIO_CHANNEL_CH1,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH2,AUDIO_PAN_RIGHT);
    Audio_SetPan(AUDIO_CHANNEL_CH3,AUDIO_PAN_LEFT);
    Audio_SetPan(AUDIO_CHANNEL_CH4,AUDIO_PAN_RIGHT);
    {start}
    sound_wait(10);
    sound_result[0]=(u8)(NR52&15);
    sound_result[1]=NR51;
    sound_result[2]=NR32;
    sound_result[3]=NR43;
    {middle}
    sound_wait(10);
    sound_result[4]=(u8)(NR52&15);
    sound_wait(25);
''' + ('    AudioVBlank_DisableIrq();AudioVBlank_Stop();\n' if vb else '') + '    sound_end();\n}\n'

def main():
    OUT.mkdir(parents=True,exist_ok=True);rows=[]
    compiler=REPOS/'kitaqgb/kitaqgb.exe';emulator=REPOS/'kokura/kokura-cli.exe'
    for driver in ['direct','stream','vblank-direct','vblank-queue']:
        for ch in [1,2,3,4]:
            folder=OUT/(driver+'-ch'+str(ch));folder.mkdir(exist_ok=True)
            source=folder/'case.c';source.write_text(program(driver,ch),encoding='utf-8');rom=folder/'case.gb'
            cmd=[str(compiler),str(source),'-I',str(REPOS/'kitaqgb/lib'),'-I',str(SITE/'samples'),'-o',str(rom),'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k','--no-cache','--no-disasm']
            build=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);(folder/'build.txt').write_bytes(build.stdout+build.stderr)
            if build.returncode:raise RuntimeError(str(folder)+': build failed')
            for mode in ['dmg','cgb']:
                audio=folder/(mode+'.wav');state=folder/(mode+'.json');image=folder/(mode+'.png')
                cmd=[str(emulator),str(rom),'--hardware',mode,'--run-frames','160','--record-wav',str(audio),'--png',str(image),'--dump-report',str(state),'--report-sections','meta,watched_memory','--watch-fields','preview','--watch-window','data:50688:16','--watch-window','done:50815:1']
                run=subprocess.run(cmd,cwd=folder,capture_output=True,timeout=120);assert run.returncode==0
                watches={x['name']:x['preview_bytes'] for x in json.loads(state.read_text(encoding='utf-8'))['watched_memory']}
                active=measure(audio,0.75,0.95);silent=measure(audio,1.8,2.1)
                side=0 if ch%2 else 1;other=1-side
                # A muted DMG output may retain a monotonic high-pass capacitor tail.
                # Inspect every sample: it must approach zero without renewed oscillation.
                rate,channels=pcm(audio);tail=channels[other][int(.75*rate):int(.95*rate)]
                dc_tail=all(abs(b)<=abs(a) and abs(b-a)<=1 for a,b in zip(tail,tail[1:]))
                off_silent=active[other]['ac_rms']<5 or (dc_tail and active[other]['positive_crossings']==0)
                passed=(watches['data'][0]==(1<<(ch-1)) and watches['data'][1]==0x5A and watches['data'][4]==0 and watches['done']==[0xA5] and active[side]['ac_rms']>100 and off_silent and all(x['ac_rms']<5 for x in silent))
                row=dict(driver=driver,channel=ch,mode=mode,source=source.relative_to(SITE).as_posix(),source_sha256=sha(source),rom=rom.relative_to(SITE).as_posix(),rom_sha256=sha(rom),image=image.relative_to(SITE).as_posix(),image_sha256=sha(image),audio=audio.relative_to(SITE).as_posix(),audio_sha256=sha(audio),input_sha256=dependencies(source,REPOS/'kitaqgb/lib'),compiler_sha256=sha(compiler),emulator_sha256=sha(emulator),registers=watches['data'][:5],done=watches['done'],active=active,silent=silent,off_side_monotonic_dc_tail=dc_tail,passed=passed)
                rows.append(row);print(driver,ch,mode,'PASS' if passed else 'FAIL',row['registers'],[round(x['ac_rms'],2) for x in active],flush=True)
                (OUT/'results.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),records=rows,passed=all(r['passed'] for r in rows)),indent=2),encoding='utf-8')
            cleanup_build_outputs(folder)
    raise SystemExit(0 if len(rows)==32 and all(r['passed'] for r in rows) else 1)

if __name__=='__main__':main()
