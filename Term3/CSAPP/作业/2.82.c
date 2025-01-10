#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {  
    srand(time(NULL));
    int x = rand();
    int y = rand();
    unsigned ux = (unsigned) x;
    unsigned uy = (unsigned) y;

    printf("A: %d\n", (INT_MIN < y) == (-INT_MIN > -y));

    printf("B: %d\n", ((x + y) << 4) + y - x == 17 * y + 15 * x);

    printf("C: %d\n", ~x + ~y + 1 == ~(x + y));

    printf("D: %d\n", (ux - uy) == -(unsigned)(y - x));

    printf("E: %d\n", ((x >> 2) << 2) <= x);
    return 0;
}