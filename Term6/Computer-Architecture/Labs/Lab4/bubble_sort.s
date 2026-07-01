.text 
main:
ADDIU $r1, $r0, arr
ADDIU $r2, $r0, len
LW $r2, 0($r2)
BGEZAL $r0, bubble_sort_func
NOP
TEQ $r0,$r0

bubble_sort_func:
ADDIU $r3, $r2, -1
BLEZ $r3, exit

SLL $r2, $r2, 2
ADDIU $r4, $r1, 4
ADDU $r5, $r1, $r2

outer_loop:
ADDIU $r6, $r4, 0

inner_loop:
LW $r7, -4($r6)
LW $r8, 0($r6)
SLT $r9, $r8, $r7
BEQ $r9, $r0, end

swap:
SW $r8, -4($r6)
SW $r7, 0($r6)

end:
ADDIU $r6, $r6, 4
BNE $r5, $r6, inner_loop
ADDIU $r3, $r3, -1
ADDIU $r5, $r5, -4
BNE $r3, $r0, outer_loop

exit:
JR $r31

.data
arr: .word 23, 5, 91, 12, 47, 3, 68, 29, 74, 16, 8, 55, 39, 2, 60
len: .word 15
