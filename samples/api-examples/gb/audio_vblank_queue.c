// Stream 48 notes through a 16-record queue while the VBlank ISR plays music.
// The original eight-note phrase repeats six times; no commercial song is used.
#define SOUND_VBLANK
#include "gb_sound_example.h"
__location(0xFF70) u8 queue_svbk;
// Test-only address in the selected bank; accessed only after detecting CGB.
__location(0xD400) u8 queue_bank_source[5];
__wram u8 queue_hook_count;
// Records: delay, CH1, CH2, CH3, CH4. The phrase uses CH2.
__prg_rom u8 queue_song[] = {
    2,255,24,255,255, 2,255,28,255,255, 2,255,31,255,255, 2,255,36,255,255,
    2,255,31,255,255, 2,255,28,255,255, 2,255,26,255,255, 2,255,24,255,255,
    2,255,24,255,255, 2,255,28,255,255, 2,255,31,255,255, 2,255,36,255,255,
    2,255,31,255,255, 2,255,28,255,255, 2,255,26,255,255, 2,255,24,255,255,
    2,255,24,255,255, 2,255,28,255,255, 2,255,31,255,255, 2,255,36,255,255,
    2,255,31,255,255, 2,255,28,255,255, 2,255,26,255,255, 2,255,24,255,255,
    2,255,24,255,255, 2,255,28,255,255, 2,255,31,255,255, 2,255,36,255,255,
    2,255,31,255,255, 2,255,28,255,255, 2,255,26,255,255, 2,255,24,255,255,
    2,255,24,255,255, 2,255,28,255,255, 2,255,31,255,255, 2,255,36,255,255,
    2,255,31,255,255, 2,255,28,255,255, 2,255,26,255,255, 2,255,24,255,255,
    2,255,24,255,255, 2,255,28,255,255, 2,255,31,255,255, 2,255,36,255,255,
    2,255,31,255,255, 2,255,28,255,255, 2,255,26,255,255, 2,255,24,255,255,
    AUDIO_VBLANK_END,255,255,255,255
};

void queue_frame_hook() { queue_hook_count++; }

void main() {
    u8 i;
    u8 accepted;
    u8 next;
    u8 saved_bank;
    sound_begin("VBLANK QUEUE REFILL");
    __asm { DI }
    AudioVBlank_Init();
    // Empty, null and wrong-mode calls are safe and do not start playback.
    if (AudioVBlank_QueueRefill(queue_song,1) != 0) sound_result[0]++;
    AudioVBlank_QueueReset();
    if (AudioVBlank_QueuePlay() != 0) sound_result[0]++;
    if (AudioVBlank_QueueRefill(0,1) != 0) sound_result[0]++;
    if (AudioVBlank_QueueRefill(queue_song,0) != 0) sound_result[0]++;
    if (AudioVBlank_QueueRefill(queue_song,255) != 16) sound_result[0]++;
    if (AudioVBlank_QueueCount != 16 || AudioVBlank_QueueWriteIndex != 0) sound_result[0]++;
    if (AudioVBlank_QueueRefill(queue_song,1) != 0) sound_result[0]++;
    // CGB: copy a source in WRAM bank 2 into the queue in bank 1 and restore SVBK.
    if (__cgb_is_cgb()) {
        AudioVBlank_QueueReset();
        saved_bank=queue_svbk;
        queue_svbk=2;
        for(i=0;i<5;i++)queue_bank_source[i]=queue_song[i];
        if(AudioVBlank_QueueRefill(queue_bank_source,1)!=1) sound_result[0]++;
        if((queue_svbk&7)!=2) sound_result[0]++;
        queue_svbk=1;
        for(i=0;i<5;i++)if(AudioVBlank_QueueBuffer[i]!=queue_song[i])sound_result[0]++;
        queue_svbk=saved_bank;
    }
    // IE may be enabled while IME is disabled: producer calls must not execute EI.
    AudioVBlank_FrameHook=queue_frame_hook;queue_hook_count=0;
    AudioVBlank_IE=1;
    AudioVBlank_QueueReset();
    // example:AudioVBlank_QueueRefill:start
    next=AudioVBlank_QueueRefill(queue_song,16);
    // next counts records; each record occupies five source bytes.
    // example:AudioVBlank_QueueRefill:end
    if(AudioVBlank_IE!=1) sound_result[0]++;
    sound_wait(2);
    if(queue_hook_count!=0) sound_result[0]++;
    // example:AudioVBlank_QueuePlay:start
    if(AudioVBlank_QueuePlay()==0) sound_result[0]++;
    AudioVBlank_EnableIrq();
    // example:AudioVBlank_QueuePlay:end
    while(AudioVBlank_MusicPlaying!=0) {
        if(next<49) {
            accepted=AudioVBlank_QueueRefill(queue_song+(u16)next*5,(u8)(49-next));
            next=(u8)(next+accepted);
        }
        sound_wait(1);
    }
    AudioVBlank_DisableIrq();
    sound_result[1]=next;
    sound_result[2]=AudioVBlank_QueueUnderruns;
    sound_result[3]=AudioVBlank_QueueCount;
    sound_result[4]=AudioVBlank_QueueReadIndex;
    sound_result[5]=AudioVBlank_QueueWriteIndex;
    sound_result[6]=AudioVBlank_MusicPlaying;
    // example:AudioVBlank_QueueReset:start
    AudioVBlank_QueueReset(); // Silence playback and discard any queued records.
    // example:AudioVBlank_QueueReset:end
    sound_end();
}
