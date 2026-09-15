// Controller-port byte encoding. This does not synthesize sound inside the FC.
#define SOUND_PORT_ONLY
#include "fc_sound_example.h"
void main(void) {
    sound_begin("MIDI PORT BYTES");
    // sound_begin has disabled DMC DMA and all internal APU voices. A compatible external circuit is required.
    // Stop NMI and mask IRQ so neither can split a software-timed serial frame.
    __ppu_ctrl_set(0); __irq_disable();
    __midi_out_byte(0x7E);
    __midi_program_change(2,5);
    __midi_control_change(2,7,100);
    __midi_note_on(2,69,96);
    __midi_note_off(2,69,0);
    __midi_clock(); __midi_start(); __midi_continue(); __midi_stop();
    // The emulator's unconnected input bit is low. Reading returns zero here.
    // A real input held high would block waiting for its start bit, without timeout.
    sound_result[0]=__midi_in_byte();
    sound_result[1]=1;
    __ppu_ctrl_set(0x80); __irq_enable();
    sound_end();
}
