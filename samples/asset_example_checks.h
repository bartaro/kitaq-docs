#pragma once
// Shared source-backed checks for asset.h; include exactly once after banked data.
u8 failures;
u8 first_failure;
u8 buffer[146];
AssetDesc descriptor;
u8 i;
u8 loaded;
u8 payload_bank;
const u8* payload_pointer;

void expect(u8 condition,u8 id) {
    if (!condition) {
        if (failures==0) first_failure=id;
        if (failures!=255) failures++;
    }
}

// The two bitplanes contain the same masks; only their byte layout differs.
u8 expected_shape_byte(u8 offset) {
    u8 row;
    u8 kind;
#ifdef MANUAL_ASSET_FC
    row=(u8)(offset&7);
#else
    row=(u8)((offset&15)>>1);
#endif
    kind=(u8)((offset>>4)%3);
    if(kind==0) return (u8)(255<<(7-row));
    if(kind==1) { if(row==0 || row==7) return 255; return 129; }
    return 240;
}

void asset_checks() {
    // example:asset_set_table:start
    asset_set_table(3,asset_descriptors,4); // Four descriptors in bank 3, payloads in bank 2.
    // example:asset_set_table:end
    // example:asset_get:start
    loaded=asset_get(0,&descriptor);
    expect(loaded==1,1);
    expect(descriptor.type==ASSET_TYPE_TILES && descriptor.bank==2,2);
    expect(descriptor.ptr==asset_shapes && descriptor.len==144,3);
    // example:asset_get:end
    expect(*asset_bank_marker==0xA1,4); // Far lookup must restore bank 1 before returning.
    descriptor.len=777;
    expect(asset_get(4,&descriptor)==0 && descriptor.len==777,5);
    expect(asset_get(0,0)==0,6);
    for(i=0;i<146;i++) buffer[(__safe_index u8)i]=0x55;
    // example:asset_load_raw:start
    loaded=asset_load_raw(0,buffer,7); // Success with truncation: copy seven of 144 bytes.
    expect(loaded==1 && buffer[7]==0x55,7);
    for(i=0;i<7;i++) expect(buffer[(__safe_index u8)i]==expected_shape_byte(i),8);
    // example:asset_load_raw:end
    expect(*asset_bank_marker==0xA1,9);
    expect(asset_load_raw(0,buffer,0)==1 && buffer[7]==0x55,10);
    expect(asset_load_raw(4,buffer,32)==0 && buffer[7]==0x55,11);
    expect(asset_load_raw(3,buffer,32)==1 && buffer[7]==0x55,12); // Valid empty asset.
    expect(asset_load_raw(0,buffer,146)==1,13);
    for(i=0;i<144;i++) expect(buffer[(__safe_index u8)i]==expected_shape_byte(i),14);
    expect(buffer[144]==0x55 && buffer[145]==0x55,15);
    expect(asset_load_raw(2,buffer,16)==1,16); // Raw copy does not reject the MAP tag.
    // example:asset_get_bank:start
    payload_bank=asset_get_bank(0);
    expect(payload_bank==2,17); // Payload bank, not descriptor-table bank 3.
    expect(asset_get_bank(4)==0,18); // Failure sentinel; a valid descriptor may also use bank 0.
    // example:asset_get_bank:end
    // example:asset_get_ptr:start
    payload_pointer=asset_get_ptr(0);
    expect(payload_pointer==asset_shapes,19);
    expect(*asset_bank_marker==0xA1,20); // Getting the pointer leaves bank 1 selected.
    // Use payload_bank together with payload_pointer for a far copy; do not dereference it here.
    // example:asset_get_ptr:end
    // example:asset_get_len:start
    expect(asset_get_len(0)==144,21); // Bytes, not tiles.
    expect(asset_get_len(3)==0 && asset_get_len(4)==0,22); // Empty asset and invalid ID both yield zero.
    // example:asset_get_len:end
    asset_set_table(0,0,0); // Empty registration disables lookups without dereferencing null.
    expect(asset_get(0,&descriptor)==0,23);
    asset_set_table(3,asset_descriptors,4);
}
