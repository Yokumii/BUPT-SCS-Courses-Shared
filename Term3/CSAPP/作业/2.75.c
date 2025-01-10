#include <stdio.h>  
#include <stdint.h>

int signed_high_prod(int x, int y) {
    return (int64_t) x * y >> 32;
}

unsigned unsigned_high_prod(int x, int y)
{
    int w = sizeof(unsigned) << 3;
    int xw = (unsigned) x >> w - 1, yw = (unsigned) y >> w - 1;
    return signed_high_prod(x, y) + xw * y + yw * x;
}

int main(){
    unsigned x = 0x12345678;
	unsigned y = 0xFFFFFFFF;
    printf("%x\n", unsigned_high_prod(x,y));
    return 0;
}