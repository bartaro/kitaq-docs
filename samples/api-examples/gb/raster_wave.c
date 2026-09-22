// A complete original scanline-wave scene. Background letters and vertical
// pillars reveal horizontal displacement on each individual screen line.
#include "gb_common.h"
#include "scroll.c"
#include "raster.c"
#pragma bank 0
__location(0xC600) u8 wave_frames;
__location(0xC601) u8 wave_lookup;
RasterLineX wave;
__location(0xFF68) u8 Wave_BGPI;
__location(0xFF69) u8 Wave_BGPD;
// A three-pixel pillar makes the displacement of every pixel row measurable.
__prg_rom u8 wave_pillar[16] = {
    0x38,0x38, 0x38,0x38, 0x38,0x38, 0x38,0x38,
    0x38,0x38, 0x38,0x38, 0x38,0x38, 0x38,0x38
};
u8 __cgb_is_cgb();

void main() {
    u8 y;
    u8 x;
#ifdef RASTER_TITLE_ENTRY
    u8 age = 0;
#endif
    m_init();
    __wait_vblank();
    M_LCDC = 0;
    __vram_copy(0x8800, wave_pillar, 16);
    for (y = 0; y < 18; y++) {
        for (x = 0; x < 32; x += 4) m_put(x, y, 128);
    }
    // CGB uses a pale blue background and dark blue lettering/pillars.
    if (__cgb_is_cgb()) {
        Wave_BGPI=0x80;
        Wave_BGPD=0xFF; Wave_BGPD=0x7F;
        Wave_BGPD=0xD0; Wave_BGPD=0x7E;
        Wave_BGPD=0x44; Wave_BGPD=0x65;
        Wave_BGPD=0x20; Wave_BGPD=0x30;
    }
#ifdef RASTER_TITLE_ENTRY
    m_text(3, 4, "ORBIT GUARD");
    m_text(4, 8, "TITLE ARRIVAL");
    m_text(4, 12, "PRESS START");
#else
    m_text(3, 4, "SCANLINE WAVE");
    m_text(4, 8, "BOSS APPROACH");
    m_text(4, 12, "WARP CORRIDOR");
#endif
    Raster_LineXInit(&wave, KQ_RASTER_LINE_TRAVEL_GATE, 0);
    Raster_LineXSetSpeed(&wave, 1, 1);
    // A lookup predicts a row's SCX without drawing or advancing the phase.
    // Phase 8 at row zero gives +17 pixels; reset to start the animation at 0.
    Raster_LineXSetPhase(&wave, 8);
    wave_lookup = Raster_LineXGetOffset(&wave, 0);
    Raster_LineXSetPhase(&wave, 0);
    wave_frames = 0;
    M_LCDC = 0x91;
    while (1) {
#ifdef RASTER_TITLE_ENTRY
        // Scroll the title in from the right with a large wave. Then switch
        // to a small ripple, settle completely, and repeat the entrance.
        if (age == 0) Raster_LineXSetProfile(&wave, KQ_RASTER_LINE_TRAVEL_GATE);
        if (age < 48) wave.base_x = (u8)(160 + age * 2);
        if (age == 48) {
            wave.base_x = 0;
            Raster_LineXSetProfile(&wave, KQ_RASTER_LINE_X_TITLE);
        }
        if (age == 96) Raster_LineXSetProfile(&wave, KQ_RASTER_LINE_FLAT);
#endif
        Raster_LineXRunFrame(&wave);
        wave_frames++;
#ifdef RASTER_TITLE_ENTRY
        age++;
        if (age == 160) age = 0;
#endif
    }
}
