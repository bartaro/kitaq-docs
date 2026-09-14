// This sample compares allocation results before displaying actual sprite pixels.
u8 sprite_example_failures;
SpriteAnim sprite_example_animation;
__prg_rom MetaSpritePart sprite_example_pair[2]={{0,0,128,0},{8,0,128,SPRITE_FLAG_XFLIP}};
__prg_rom MetaSpritePart sprite_example_line[11]={
    {0,0,128,0},{8,0,128,0},{16,0,128,0},{24,0,128,0},{32,0,128,0},{40,0,128,0},
    {48,0,128,0},{56,0,128,0},{64,0,128,0},{72,0,128,0},{80,0,128,0}};

void sprite_example_expect(u8 condition) {
    if(condition==0) sprite_example_failures++;
}

// FC passes the OAM Y byte directly; its visible top is one pixel lower.
#ifdef MANUAL_SPRITE_FC
#define SPRITE_EXAMPLE_Y(y) ((u8)((y)-1))
#define SPRITE_EXAMPLE_LINE_COUNT 9
#else
#define SPRITE_EXAMPLE_Y(y) (y)
#define SPRITE_EXAMPLE_LINE_COUNT 11
#endif

void sprite_example_place(u8 id,u8 x,u8 y,u8 tile,u8 flags) {
    sprite_set_pos(id,x,SPRITE_EXAMPLE_Y(y));
    sprite_set_tile(id,tile);
    sprite_set_flags(id,flags);
}

void sprite_example_draw() {
    u8 i;u8 tile;
    sprite_example_failures=0;
    // example:sprite_init:start
    sprite_init();
    sprite_example_expect(sprite_count_used()==0);
    // example:sprite_init:end
    // example:sprite_alloc:start
    for(i=0;i<8;i++) sprite_example_expect(sprite_alloc()==i);
    sprite_example_expect(sprite_count_used()==8);
    // example:sprite_alloc:end
    // Visible arrows demonstrate positioning, tile selection and whole-byte attributes.
    sprite_example_place(0,88,16,128,0);
    sprite_example_place(1,88,32,128,SPRITE_FLAG_XFLIP);
    sprite_example_place(2,88,48,128,SPRITE_FLAG_YFLIP);
    sprite_example_place(3,88,80,128,0);
    sprite_example_place(4,92,80,129,0);
    sprite_example_place(5,88,96,128,0);
    sprite_example_place(6,120,16,128,0);
    sprite_example_place(7,120,32,128,0);
    // example:sprite_hide:start
    sprite_hide(6);
    sprite_example_expect(sprite_count_used()==8); // Hiding retains allocation.
    // example:sprite_hide:end
    // example:sprite_free:start
    sprite_free(7);sprite_free(7);
    sprite_example_expect(sprite_count_used()==7); // Repeated release is ignored.
    // example:sprite_free:end
    // example:metasprite_draw:start
    sprite_example_expect(metasprite_draw(10,88,SPRITE_EXAMPLE_Y(64),sprite_example_pair,2)==2);
    sprite_example_expect(sprite_count_used()==9); // Sparse IDs count actual active slots.
    // example:metasprite_draw:end
    // example:anim_update:start
    sprite_example_animation.first_tile=128;sprite_example_animation.frame_count=2;
    sprite_example_animation.frame=0;sprite_example_animation.ticks=0;
    sprite_example_animation.ticks_per_frame=2;
    sprite_example_expect(anim_update(&sprite_example_animation)==128);
    tile=anim_update(&sprite_example_animation);
    sprite_example_expect(tile==129);sprite_set_tile(5,tile);
    // example:anim_update:end
    // The last row intentionally exceeds the hardware's per-line selection limit by one.
    sprite_example_expect(metasprite_draw(16,8,SPRITE_EXAMPLE_Y(128),sprite_example_line,SPRITE_EXAMPLE_LINE_COUNT)==SPRITE_EXAMPLE_LINE_COUNT);
    // example:sprite_max_scanline_count:start
    sprite_example_expect(sprite_max_scanline_count()==SPRITE_EXAMPLE_LINE_COUNT);
    // example:sprite_max_scanline_count:end
    // example:sprite_warn_scanline_overflow:start
    sprite_example_expect(sprite_warn_scanline_overflow()==1);
    // example:sprite_warn_scanline_overflow:end
    sprite_example_expect(sprite_count_used()==(u8)(9+SPRITE_EXAMPLE_LINE_COUNT));
}

// Keep each FC text batch within the intrinsic VRAM queue's capacity.
void sprite_example_flush_text() {
#ifdef MANUAL_SPRITE_FC
    m_wait();
#endif
}

void sprite_example_labels() {
    m_text(1,0,"SPRITE EXAMPLE");
    m_put(17,0,(u8)('0'+sprite_example_failures/10));
    m_put(18,0,(u8)('0'+sprite_example_failures%10));
    sprite_example_flush_text();
    m_text(1,2,"NORMAL");sprite_example_flush_text();
    m_text(1,4,"FLIP X");sprite_example_flush_text();
    m_text(1,6,"FLIP Y");sprite_example_flush_text();
    m_text(1,8,"META");sprite_example_flush_text();
    m_text(1,10,"OVERLAP");sprite_example_flush_text();
    m_text(1,12,"ANIMATION");sprite_example_flush_text();
    m_text(1,14,"SCAN LIMIT");sprite_example_flush_text();
}
