#include <stdio.h>

long loop(long x, long n) {
    long result = 0;
    long mask;
    for (mask = 1; mask; mask = mask >> n) {
        result |= x & mask;
    }
    return result;
}

int main(void)
{
    long x, n;
    scanf("%ld %ld", &x, &n);
    printf("%ld", loop(x, n));
}