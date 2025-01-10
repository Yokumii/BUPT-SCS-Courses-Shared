#include <stdio.h>

int main(void)
{
    int x = 100;
    printf("%d * 17 = %d\n",x, (x << 4) + x);
    printf("%d * -7 = %d\n",x, x - (x << 3));
    printf("%d * 60 = %d\n",x, (x << 6) - (x << 2));
    printf("%d * -112 = %d\n",x, (x << 4) - (x << 7));
    return 0;
}