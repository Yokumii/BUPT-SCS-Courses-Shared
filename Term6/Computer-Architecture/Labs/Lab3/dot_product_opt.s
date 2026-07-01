.text 
main:
ADDIU $r1, $r0, a
ADDIU $r2, $r0, b   
ADDIU $r3, $r0, n
BGEZAL $r0, dot_product_func
NOP
TEQ $r0,$r0

dot_product_func:
LW $r3,0($r3)
ADD $r4,$r0,$r0
ADD $r5,$r0,$r0
loop:
LW $r6,0($r1)
LW $r7,0($r2)
ADDIU $r1,$r1,4
ADDIU $r2,$r2,4
MUL $r8,$r6,$r7
ADDIU $r4,$r4,1
ADD $r5,$r5,$r8
BNE $r4,$r3,loop
JR $r31

.data 
a: .word 2, 4, 6, 8, 10, 12, 14, 16, 18, 20   
b: .word 1, 3, 5, 7, 9, 11, 13, 15, 17, 19  
n: .word 10
