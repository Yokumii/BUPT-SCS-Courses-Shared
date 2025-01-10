#include <stdio.h>

long A[7][5][13];

long store_ele(long i, long j, long k, long *dest)
{
    *dest = A[i][j][k];
    return sizeof(A);
}

int main(void)
{
    return 0;
}