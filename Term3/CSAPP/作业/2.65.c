#include <stdio.h>

int odd_ones(unsigned x)
{
    x = x ^ (x >> 16);
    x = x ^ (x >> 8);
    x = x ^ (x >> 4);
    x = x ^ (x >> 2);
    x = x ^ (x >> 1);
    x= x & 1;
    return x;
}

int main(void)
{
    printf("odd_ones(0xF1) = %d\n", odd_ones(0xF1));
    return 0;
}