#include <stdio.h>

int lower_one_mask(int n)
{
    unsigned part1 = -1;
    unsigned part2 = sizeof(int) * 8 - n;
    return (int)(part1 >> part2);
}

int main(void)
{
    printf("n = 6 --> %#X, n = 17 --> %#X\n", lower_one_mask(6), lower_one_mask(17));
    return 0;
}