#include <stdio.h>

long decode2(long x, long y, long z)
{
    y -= z;
    x *= y;
    int temp = y;
    temp <<= 63;
    temp >>= 63;
    temp ^= x;
    return temp;
}

int main(void)
{
    printf("%ld", decode2(0xff0123, 0xff1234, 0xff2345));
    return 0;
}