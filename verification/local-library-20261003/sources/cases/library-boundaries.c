#include "sprite.c"
#include "vram.c"
#include "cgb_palette.c"
#pragma bank 0
__location(0xC700) u16 result[16];
MetaSpritePart parts[2];
void main(){
 u8 i;for(i=0;i<16;i++)result[i]=0;
 sprite_init();parts[0].dx=0;parts[0].dy=0;parts[0].tile=7;parts[0].flags=0;parts[1]=parts[0];
 result[0]=metasprite_draw(5,20,30,parts,2);result[1]=kq_sprite_used;
 sprite_init();result[2]=metasprite_draw(39,20,30,parts,2);result[3]=kq_sprite_used;result[4]=kq_sprite_active[39];
 vram_init();result[5]=vram_get_queue_free();vram_queue_bg_tile(1,2,3);result[6]=vram_get_queue_used();result[7]=vram_get_queue_free();
 *(u8*)0xFF40=0;cgb_bg_color(0,0,0x1234);cgb_obj_color(0,0,0x1234);
 result[8]=*(u8*)0xFF68;result[9]=*(u8*)0xFF69;result[10]=*(u8*)0xFF6A;result[11]=*(u8*)0xFF6B;result[15]=0xA55A;
 while(1){}
}