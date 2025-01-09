#include <stdio.h>

int bad_int_size_is_32()
{
    int set_msb = 1 << 31;
    int beyond_msb = set_msb << 1;
    return set_msb && !beyond_msb;
}

int main(void)
{
    printf("%d\n", bad_int_size_is_32());
    return 0;
}