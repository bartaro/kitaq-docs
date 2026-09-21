"""Exercise link API boundaries and packet state transitions on DMG and CGB.

State-machine fault injection is explicit here; teaching programs separately
exercise actual paired and four-machine serial links.
"""
from pathlib import Path
import hashlib,json,subprocess
from check_link_examples import command,values,compiler,emu,lib,SITE,dependencies
from api_build_cleanup import cleanup_build_outputs
OUT=SITE/'verification/api-link/state';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
def case(name,code,want,frames=30):
    folder=OUT/name;folder.mkdir(exist_ok=True);source=folder/'case.c';rom=folder/'case.gb'
    source.write_text('#include "gb_link_example.h"\nvoid main(){u8 i,v,p,c,n;u8 data[24];lesson_begin();'+code+'result[79]=0xA55A;while(1){}}',encoding='utf-8')
    command([compiler,source,'-I',lib,'-I',SITE/'samples','-o',rom,'--profile=dev','--rst-disable','--stack-bank=fixed','--cgb=cgb','--cart=mbc5','--romsize=128k','--no-cache','--no-disasm'],folder,'build.txt')
    for mode in ['dmg','cgb']:
        report=folder/(mode+'.json');args=[emu,rom,'--hardware',mode,'--run-frames',str(frames),'--dump-report',report,'--report-sections','meta,cpu,watched_memory','--watch-fields','preview']
        for off in range(0,160,16):args+=['--watch-window',f'r{off}:{0xC600+off}:16']
        command(args,folder,mode+'.txt');actual=values(json.loads(report.read_text(encoding='utf-8')));expected=want+[0]*(79-len(want))+[0xA55A]
        row={'platform':'gb','group':name,'mode':mode,'source':source.relative_to(SITE).as_posix(),'source_sha256':sha(source),'rom':rom.relative_to(SITE).as_posix(),'rom_sha256':sha(rom),'compiler_sha256':sha(compiler),'emulator_sha256':sha(emu),'input_sha256':dependencies(source,lib),'actual':actual,'expected':expected,'passed':actual==expected}
        rows.append(row);print(name,mode,'PASS' if row['passed'] else 'FAIL',[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:8],flush=True)
        (OUT.parent/'edge_checks.json').write_text(json.dumps({'script_sha256':sha(Path(__file__)),'records':rows},indent=2),encoding='utf-8')
    cleanup_build_outputs(folder)

case('topology-validation','''
result[0]=Link4_InitHost(1);result[1]=Link4_GetMode();result[2]=Link4_GetSelectedPeer();
result[3]=Link4_InitHost(2);result[4]=Link4_GetSlotCount();result[5]=Link4_SelectPeer(0);result[6]=Link4_SelectPeer(2);
result[7]=Link4_InitHost(5);result[8]=Link4_GetSlotCount();result[9]=Link4_InitPeer(0,4);result[10]=Link4_InitPeer(4,4);
result[11]=Link4_InitPeer(3,4);result[12]=Link4_SelectPeer(1);result[13]=Link4_SelectPeer(0);
Link_ClearError();v=77;p=88;c=66;n=55;result[14]=Link4_HasByteFrom(3);result[15]=Link4_TryReadByteFrom(255,&v);result[16]=Link4_TryReadByteAny(&p,&v);
result[17]=Link4_ReadPacketFrom(3,&c,&n,data);result[18]=v;result[19]=p;result[20]=c;result[21]=n;result[22]=Link_LastError();
Link_BeginTransfer(42);result[23]=Link4_SelectPeer(0);Link_Cancel();result[24]=Link4_SelectPeer(0);
''',[4,0,255,0,2,4,4,4,0,4,4,0,4,0,0,0,0,0,77,88,66,55,0,1,0])

case('send-validation-copy','''
Link_InitMaster();result[0]=Link_SendPacket(0,1,7);result[1]=Link_SendPacket(data,25,7);result[2]=Link_SendPacket(0,0,7);result[3]=Link_SendPacket(data,1,7);
Link_InitMaster();for(i=0;i<24;i++)data[i]=i;result[4]=Link_SendPacket(data,24,49);data[0]=99;data[23]=99;
result[5]=Link_CurrentPacketBuf[0];result[6]=Link_CurrentPacketBuf[23];result[7]=Link_CurrentPacketLen;result[8]=Link_CurrentPacketChecksum;
Link4_InitHost(4);result[9]=Link4_SendPacketTo(2,0,1,7);result[10]=Link4_GetSelectedPeer();result[11]=Link_LastError();
''',[4,4,0,1,0,0,23,24,41,4,2,4])

case('parser-checksum-length','''
/* Feed explicit wire bytes to isolate rejection and mailbox rules. */
Link_InitSlave();Link_PacketConsumeByte(0xA5);Link_PacketConsumeByte(7);Link_PacketConsumeByte(25);
result[0]=Link_LastError();result[1]=Link_PendingAck;result[2]=Link_HasPacket();
Link_InitSlave();Link_PacketConsumeByte(0xA5);Link_PacketConsumeByte(7);Link_PacketConsumeByte(1);Link_PacketConsumeByte(42);Link_PacketConsumeByte(0);
result[3]=Link_LastError();result[4]=Link_PendingAck;result[5]=Link_HasPacket();
Link_InitSlave();Link_PacketConsumeByte(0xA5);Link_PacketConsumeByte(7);Link_PacketConsumeByte(0);Link_PacketConsumeByte(7);
result[6]=Link_HasPacket();result[7]=Link_PendingAck;result[8]=Link_ReadPacket(0,0,0);result[9]=Link_HasPacket();
''',[4,31,0,4,31,0,1,121,1,0])

case('maximum-parser-mailbox','''
Link4_InitPeer(1,4);Link_PacketConsumeByte(0xA5);Link_PacketConsumeByte(49);Link_PacketConsumeByte(24);
for(i=0;i<24;i++)Link_PacketConsumeByte(i);Link_PacketConsumeByte(41);
result[0]=Link_HasPacket();result[1]=Link4_HasPacketFrom(0);result[2]=Link_ReadPacket(&c,&n,data);result[3]=c;result[4]=n;result[5]=data[23];result[6]=Link4_HasPacketFrom(0);
Link4_InitHost(4);Link4_SelectedPeer=1;Link_PacketConsumeByte(0xA5);Link_PacketConsumeByte(7);Link_PacketConsumeByte(0);Link_PacketConsumeByte(7);
Link_PendingAck=0;Link_PacketGoIdle();Link4_SelectedPeer=2;Link_PacketConsumeByte(0xA5);Link_PacketConsumeByte(8);Link_PacketConsumeByte(0);Link_PacketConsumeByte(8);
result[7]=Link4_ReadPacketFrom(1,0,0,0);result[8]=Link_HasPacket();result[9]=Link4_HasPacketFrom(2);result[10]=Link_ReadPacket(&c,&n,0);result[11]=c;result[12]=Link4_HasPacketFrom(2);
''',[1,1,1,49,24,23,0,1,1,1,1,8,0])

case('nak-retry-limit','''
Link_InitMaster();Link_SendPacket(0,0,7);Link_PacketState=LINK_PKT_STATE_WAIT_ACK;Link_PacketConsumeByte(0x1F);result[0]=Link_PacketRetryCount;
Link_PacketState=LINK_PKT_STATE_WAIT_ACK;Link_PacketConsumeByte(0x1F);result[1]=Link_PacketRetryCount;
Link_PacketState=LINK_PKT_STATE_WAIT_ACK;Link_PacketConsumeByte(0x1F);result[2]=Link_LastError();result[3]=Link_PacketState;Link_PollPacket();result[4]=Link_PacketState;
''',[1,2,4,13,0])

case('ack-deadline-90','''
/* Finish each real internal-clock exchange before the next timer tick. */
Link_InitMaster();Link_SendPacket(0,0,7);Link_PacketState=LINK_PKT_STATE_WAIT_ACK;Link_PacketTimer=90;
for(i=0;i<89;i++){Link_PollPacket();m_wait();}result[0]=Link_PacketTimer;result[1]=Link_PacketRetryCount;
Link_PollPacket();result[2]=Link_PacketRetryCount;result[3]=Link_PacketState;result[4]=Link_LastError();Link_Cancel();
''',[1,0,1,1,0],120)

case('external-clock-stall','''
Link_InitSlave();Link_SendPacket(0,0,7);for(i=0;i<100;i++)Link_PollPacket();result[0]=Link_PacketRetryCount;
for(i=0;i<200;i++)Link_PollPacket();result[1]=Link_LastError();result[2]=Link_IsBusy();Link_Cancel();result[3]=Link_IsBusy();
''',[1,2,1,0])
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
