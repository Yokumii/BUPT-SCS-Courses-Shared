#include <stdio.h>

int mul3div4(int x)
{
    int w = sizeof(int) << 3;
    int is_neg = x >> (w - 1);
    return ((x + (x << 1)) + (is_neg & 3)) >> 2;
}

int main(void)
{
    int x = -7;
    printf("3 * %d / 4 = %d", x, mul3div4(x));
    return 0;
}