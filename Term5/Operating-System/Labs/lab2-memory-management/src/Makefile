.PHONY: all clean thread process

# 编译所有程序
all: thread process

# 双线程实验
thread: memory_op

memory_op: memory_op.c
	gcc memory_op.c -o memory_op -lpthread -std=c99

# 双进程实验
process: mm-p1 mm-p2

mm-p1: mm-p1.c
	gcc mm-p1.c -o mm-p1 -lrt -lpthread -std=c99

mm-p2: mm-p2.c
	gcc mm-p2.c -o mm-p2 -lrt -lpthread -std=c99

# 清理编译产物
clean:
	rm -f memory_op mm-p1 mm-p2

# 运行双线程实验
run-thread: memory_op
	./memory_op

# 测试说明
help:
	@echo "编译命令:"
	@echo "  make all       - 编译所有程序"
	@echo "  make thread    - 只编译双线程程序"
	@echo "  make process   - 只编译双进程程序"
	@echo ""
	@echo "运行命令:"
	@echo "  双线程实验:"
	@echo "    ./memory_op < input.txt"
	@echo ""
	@echo "  双进程实验:"
	@echo "    # 终端1："
	@echo "    ./mm-p2 /myshm"
	@echo "    # 终端2："
	@echo "    ./mm-p1 /myshm"
	@echo ""
	@echo "清理:"
	@echo "  make clean     - 删除所有编译产物"
