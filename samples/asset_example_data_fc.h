// Original triangle, outline and half-tile patterns. Descriptor bank 3 is separate from payload bank 2.
#pragma fixed_bank 1
__prg_rom u8 asset_bank_marker[1]={0xA1};
#pragma fixed_bank 2
__prg_rom u8 asset_shapes[144]={
    128,192,224,240,248,252,254,255,128,192,224,240,248,252,254,255,
    255,129,129,129,129,129,129,255,255,129,129,129,129,129,129,255,
    240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,
    128,192,224,240,248,252,254,255,128,192,224,240,248,252,254,255,
    255,129,129,129,129,129,129,255,255,129,129,129,129,129,129,255,
    240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,
    128,192,224,240,248,252,254,255,128,192,224,240,248,252,254,255,
    255,129,129,129,129,129,129,255,255,129,129,129,129,129,129,255,
    240,240,240,240,240,240,240,240,240,240,240,240,240,240,240,240
};
#pragma fixed_bank 3
__prg_rom AssetDesc asset_descriptors[4]={
    {ASSET_TYPE_TILES,2,asset_shapes,144},
    {ASSET_TYPE_RAW,2,asset_shapes,32},
    {ASSET_TYPE_MAP,2,asset_shapes,16},
    {ASSET_TYPE_RAW,0,0,0}
};
#pragma fixed_bank 0
