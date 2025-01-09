#include <stdio.h>

unsigned replace_byte(unsigned x, int i, unsigned char b)
{
    if (i < 0)
    {
        printf("ERROR\n");
        return x;
    }

    unsigned part1 = b << (i * 8);
    unsigned part2 = 0xFF << (i * 8);
    return x & (~part2) | part1;
}

int main(void)
{
    printf("replace_byte(0x12345678, 2, 0xAB) --> %X\n", replace_byte(0x12345678, 2, 0xAB));
    printf("replace_byte(0x12345678, 0, 0xAB) --> %X\n", replace_byte(0x12345678, 0, 0xAB));
    return 0;
}