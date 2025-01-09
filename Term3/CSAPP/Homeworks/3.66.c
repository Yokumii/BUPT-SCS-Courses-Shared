#include <stdio.h>

#define NR(v) (3 * (v))
#define NC(v) (1 + 4 * (v))

long sum_col(long n, long A[NR(n)][NC(n)], long j)
{
    long i;
    long result = 0;
    for (i = 0; i < NR(n); i++)
    {
        result += A[i][j];
    }
    return result;
}

int main(void)
{
    return 0;
}