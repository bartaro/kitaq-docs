u8 __svbk_get();
u8 __svbk_set(u8 bank);
u8 result;
void main() { result=__svbk_get(); while(1) {} }
