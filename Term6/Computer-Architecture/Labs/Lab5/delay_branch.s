.text
main:
ADDI  $r2,$r0,1024
ADD   $r3,$r0,$r0
ADDI  $r4,$r0,8

loop:
LW    $r1,0($r2)
ADDI  $r3,$r3,4         # 提前执行 r3 += 4（填充LW延迟，不影响r1语义）
ADDI  $r1,$r1,1
SW    $r1,0($r2)        # 写回内存（保持 LW→ADD→SW 语义顺序）
SUB   $r5,$r4,$r3
BGTZ  $r5,loop
ADD   $r7,$r0,$r6       # branch delay slot
TEQ   $r0,$r0