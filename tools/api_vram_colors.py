"""Classify emulator pixels against the documented VRAM example palette."""
def matches_color(rgb,name):
    red,green,blue=rgb
    if name=='black':return max(red,green,blue)<64
    if name=='white':return min(red,green,blue)>192
    if name=='red':return red>green+64 and red>blue+64
    if name=='blue':return blue>red+64 and blue>green+64
    if name=='green':return green>red+64 and green>blue+64
    raise ValueError('Unknown expected color: '+name)
