CC = gcc
CFLAGS = -pthread -std=c99 -Wall
TARGET_READ = readFirst.out
TARGET_WRITE = writeFirst.out

all: $(TARGET_READ) $(TARGET_WRITE)

$(TARGET_READ): readFirst.c
	$(CC) $(CFLAGS) readFirst.c -o $(TARGET_READ)

$(TARGET_WRITE): writeFirst.c
	$(CC) $(CFLAGS) writeFirst.c -o $(TARGET_WRITE)

clean:
	rm -f $(TARGET_READ) $(TARGET_WRITE)

# 测试场景 - 读者优先
test-read-1: $(TARGET_READ)
	@echo "=== 测试1：读者优先 - 基础场景 ==="
	./$(TARGET_READ) < ../../test/reader-and-writer/test

test-read-2: $(TARGET_READ)
	@echo "=== 测试2：读者优先 - 多读者场景 ==="
	./$(TARGET_READ) < ../../test/reader-and-writer/test2

test-read-3: $(TARGET_READ)
	@echo "=== 测试3：读者优先 - 读写交替场景 ==="
	./$(TARGET_READ) < ../../test/reader-and-writer/test3

test-read-4: $(TARGET_READ)
	@echo "=== 测试4：读者优先 - 多写者场景 ==="
	./$(TARGET_READ) < ../../test/reader-and-writer/test4

test-read-5: $(TARGET_READ)
	@echo "=== 测试5：读者优先 - 复杂并发场景 ==="
	./$(TARGET_READ) < ../../test/reader-and-writer/test5

# 测试场景 - 写者优先
test-write-1: $(TARGET_WRITE)
	@echo "=== 测试1：写者优先 - 基础场景 ==="
	./$(TARGET_WRITE) < ../../test/reader-and-writer/test

test-write-2: $(TARGET_WRITE)
	@echo "=== 测试2：写者优先 - 多读者场景 ==="
	./$(TARGET_WRITE) < ../../test/reader-and-writer/test2

test-write-3: $(TARGET_WRITE)
	@echo "=== 测试3：写者优先 - 读写交替场景 ==="
	./$(TARGET_WRITE) < ../../test/reader-and-writer/test3

test-write-4: $(TARGET_WRITE)
	@echo "=== 测试4：写者优先 - 多写者场景 ==="
	./$(TARGET_WRITE) < ../../test/reader-and-writer/test4

test-write-5: $(TARGET_WRITE)
	@echo "=== 测试5：写者优先 - 复杂并发场景 ==="
	./$(TARGET_WRITE) < ../../test/reader-and-writer/test5

# 全部测试
test-read-all: test-read-1 test-read-2 test-read-3 test-read-4 test-read-5

test-write-all: test-write-1 test-write-2 test-write-3 test-write-4 test-write-5

test-all: test-read-all test-write-all

.PHONY: all clean test-read-1 test-read-2 test-read-3 test-read-4 test-read-5 \
        test-write-1 test-write-2 test-write-3 test-write-4 test-write-5 \
        test-read-all test-write-all test-all
