"""Byte-level fault injection through the public Poll API, separate from real linked runs."""
from pathlib import Path
import hashlib,json
from check_link_examples import command,values,compiler,emu,lib,SITE,dependencies
from api_build_cleanup import cleanup_build_outputs
OUT=SITE/'verification/api-dmg07/state';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
support='''// Test-only port shim: feed exact bytes without claiming cable timing.
#include "link_dmg07.c"
#pragma bank 0
__location(0xC600) u16 result[80];
u8 sb;u8 sc;u8 irq;u8 ie;
u8 LinkHw_ReadSB(){return sb;}u8 LinkHw_ReadSC(){return sc;}
u8 LinkHw_ReadIF(){return irq;}u8 LinkHw_ReadIE(){return ie;}
void LinkHw_WriteSB(u8 v){sb=v;}void LinkHw_WriteSC(u8 v){sc=v;}
void LinkHw_WriteIF(u8 v){irq=v;}void LinkHw_WriteIE(u8 v){ie=v;}
void feed(u8 value){sb=value;sc=0;LinkDmg07_Poll();}
void ping(u8 status){feed(0xFE);feed(status);feed(status);feed(status);}
void confirm(){feed(0xCC);feed(0xCC);feed(0xCC);feed(0xCC);}
void packet(u8 a,u8 b,u8 c,u8 d){feed(a);feed(b);feed(c);feed(d);}
'''
def case(name,code,want):
    folder=OUT/name;folder.mkdir(exist_ok=True);source=folder/'case.c';rom=folder/'case.gb'
    source.write_text(support+'void main(){u16 i;u8 data[4];'+code+'result[79]=0xA55A;while(1){}}',encoding='utf-8')
    command([compiler,source,'-I',lib,'-o',rom,'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k','--no-cache','--no-disasm'],folder,'build.txt')
    for mode in ['dmg','cgb']:
        report=folder/(mode+'.json');cmd=[emu,rom,'--hardware',mode,'--run-frames','120','--dump-report',report,'--report-sections','meta,cpu,watched_memory','--watch-fields','preview']
        for n in range(0,160,16):cmd+=['--watch-window',f'r{n}:{0xC600+n}:16']
        command(cmd,folder,mode+'.txt');actual=values(json.loads(report.read_text(encoding='utf-8')));expected=want+[0]*(79-len(want))+[0xA55A]
        row={'platform':'gb','mode':mode,'group':name,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emu),'input_sha256':dependencies(source,lib),'actual':actual,'expected':expected,'passed':actual==expected}
        rows.append(row);print(name,mode,'PASS' if row['passed'] else 'FAIL',[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:12],flush=True)
        (OUT.parent/'edge_checks.json').write_text(json.dumps({'script_sha256':sha(Path(__file__)),'records':rows},indent=2),encoding='utf-8')
    cleanup_build_outputs(folder)

case('initialization-and-start','''
ie=255;irq=255;LinkDmg07_Init(0);result[0]=ie;result[1]=irq;result[2]=sb;result[3]=sc;
result[4]=LinkDmg07_RequestTransmission();result[5]=LinkDmg07_RequestRestart();result[6]=LinkDmg07_GetErrorCount();
feed(0xFE);feed(0xF1);result[7]=sb;feed(0xF1);result[8]=sb;feed(0xF1);result[9]=sb;
result[10]=LinkDmg07_GetLocalSlot();result[11]=LinkDmg07_GetConnectedMask();result[12]=LinkDmg07_ConsumePingStatus();result[13]=LinkDmg07_ConsumePingStatus();
result[14]=LinkDmg07_RequestTransmission();result[15]=LinkDmg07_RequestTransmission();result[16]=LinkDmg07_GetPhase();
ping(0xF1);result[17]=sb;result[18]=LinkDmg07_GetPhase();
''',[247,247,136,128,2,1,0,16,1,136,1,15,1,0,0,0,0,170,1])

case('invalid-status-and-saturation','''
LinkDmg07_Init(0);ping(0xF0);result[0]=LinkDmg07_GetErrorCount();result[1]=LinkDmg07_GetLocalSlot();result[2]=LinkDmg07_HasPingStatus();
ping(0xF9);result[3]=LinkDmg07_GetErrorCount();ping(0xF1);ping(0xF2);result[4]=LinkDmg07_GetErrorCount();result[5]=LinkDmg07_GetLastStatus();result[6]=LinkDmg07_LastError();
for(i=0;i<100;i++)ping(0xF0);result[7]=LinkDmg07_GetErrorCount();LinkDmg07_ClearError();result[8]=LinkDmg07_LastError();result[9]=LinkDmg07_GetErrorCount();
''',[3,0,1,6,9,241,5,255,0,255])

case('membership-loss-count','''
LinkDmg07_Init(0);ping(0xF1);ping(0x31);result[0]=LinkDmg07_GetDisconnectCount();result[1]=LinkDmg07_GetConnectedMask();
ping(0x31);result[2]=LinkDmg07_GetDisconnectCount();ping(0x11);result[3]=LinkDmg07_GetDisconnectCount();result[4]=LinkDmg07_GetErrorCount();
''',[1,3,1,2,0])

case('pipeline-and-cached-read','''
LinkDmg07_Init(0);ping(0xF1);LinkDmg07_SetLocalByte(42);confirm();result[0]=sb;packet(0,0,0,0);result[1]=LinkDmg07_IsPipelinePrimed();result[2]=LinkDmg07_HasPacket();result[3]=LinkDmg07_GetSentSequence();
LinkDmg07_SetLocalByte(99);result[4]=sb;packet(11,22,33,44);result[5]=sb;result[6]=LinkDmg07_GetPacketSequence();result[7]=LinkDmg07_ReadPacket(0);result[8]=LinkDmg07_GetPacketSlot(1);result[9]=LinkDmg07_GetPacketSlot(4);
data[0]=77;result[10]=LinkDmg07_ReadPacket(data);result[11]=data[0];result[12]=LinkDmg07_GetPacketSlot(0);result[13]=LinkDmg07_GetPacketSlot(5);
packet(55,66,77,88);packet(99,100,101,102);result[14]=LinkDmg07_GetErrorCount();result[15]=LinkDmg07_LastError();result[16]=LinkDmg07_ReadPacket(data);result[17]=data[0];result[18]=data[3];
''',[42,1,0,1,42,99,1,1,11,44,0,77,0,0,1,6,1,99,102])

case('aligned-restart-control','''
LinkDmg07_Init(0);ping(0xF1);LinkDmg07_SetLocalByte(9);confirm();feed(12);
result[0]=LinkDmg07_RequestRestart();result[1]=LinkDmg07_GetRestartState();result[2]=LinkDmg07_DataIndex;
feed(13);feed(14);feed(15);result[3]=LinkDmg07_GetRestartState();result[4]=sb;result[5]=LinkDmg07_RequestRestart();
packet(1,2,3,4);result[6]=LinkDmg07_HasPacket();result[7]=sb;packet(255,255,255,255);
result[8]=LinkDmg07_GetPhase();result[9]=LinkDmg07_GetLocalSlot();result[10]=LinkDmg07_GetConnectedMask();result[11]=LinkDmg07_IsPipelinePrimed();result[12]=LinkDmg07_GetRestartState();result[13]=sb;result[14]=LinkDmg07_GetErrorCount();
''',[0,1,1,2,255,0,0,255,0,0,0,0,0,136,0])

case('silence-preserves-inflight-byte','''
LinkDmg07_Init(0);ping(0xF1);confirm();feed(10);for(i=0;i<11;i++)LinkDmg07_TickFrame();result[0]=LinkDmg07_GetSilenceFrames();result[1]=LinkDmg07_GetTimeoutCount();
LinkDmg07_TickFrame();result[2]=LinkDmg07_GetTimeoutCount();result[3]=LinkDmg07_GetDisconnectCount();result[4]=LinkDmg07_GetRestartState();result[5]=LinkDmg07_GetPhase();result[6]=LinkDmg07_DataIndex;result[7]=sc;result[8]=sb;
for(i=0;i<100;i++)LinkDmg07_TickFrame();result[9]=LinkDmg07_GetTimeoutCount();LinkDmg07_ClearError();result[10]=LinkDmg07_LastError();feed(11);result[11]=LinkDmg07_GetSilenceFrames();feed(12);feed(13);result[12]=LinkDmg07_GetRestartState();result[13]=sb;
''',[11,0,1,1,1,3,1,128,0,1,0,0,2,255])

case('handshake-watchdog-and-readiness','''
LinkDmg07_Init(17);ping(0xE1);result[0]=LinkDmg07_RequestTransmission();result[1]=LinkDmg07_GetErrorCount();ping(0xF1);LinkDmg07_RequestTransmission();ping(0xF1);
for(i=0;i<20;i++){feed(0);LinkDmg07_TickFrame();}result[2]=LinkDmg07_GetTimeoutCount();result[3]=LinkDmg07_GetDisconnectCount();result[4]=LinkDmg07_GetPhase();result[5]=LinkDmg07_LastError();
''',[3,0,1,0,0,4])

case('sequence-wrap-and-invalid-phase','''
LinkDmg07_Init(0);ping(0xF1);confirm();for(i=0;i<256;i++){packet(1,2,3,4);LinkDmg07_ReadPacket(0);}
result[0]=LinkDmg07_GetSentSequence();result[1]=LinkDmg07_GetPacketSequence();result[2]=LinkDmg07_GetPacketSlot(4);result[3]=LinkDmg07_GetErrorCount();
/* Inject an impossible phase to check the explicit recovery guard. */
LinkDmg07_Phase=99;feed(0);result[4]=LinkDmg07_GetPhase();result[5]=LinkDmg07_LastError();result[6]=LinkDmg07_GetErrorCount();
''',[0,255,4,0,0,5,1])
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
