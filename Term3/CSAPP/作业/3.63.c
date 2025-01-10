#include <stdio.h>

long switch_prob(long x, long n)
{
    long result = x;
    switch (n)
    {
        case 60: case 62:
            result *= 8;
            break;
        
        case 63:
            result >>= 3;
            break;

        case 64:
            result <<= 4;
            result -= x;
            break;
        
        case 65:
            result *= result;
            break;
        
        case 61: default:
            result += 75;
            break;
    }
    return result;
}

int main(void)
{
    printf("%ld", switch_prob(1, 64));
    return 0;
}