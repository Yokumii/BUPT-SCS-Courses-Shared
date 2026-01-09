CC = gcc
CFLAGS = -pthread -std=c99 -Wall
TARGET = producer-consumer.out

all: $(TARGET)

$(TARGET): producer-consumer.c
	$(CC) $(CFLAGS) producer-consumer.c -o $(TARGET)

clean:
	rm -f $(TARGET)

# 测试场景
test1: $(TARGET)
	@echo "=== 测试1：单生产者单消费者 ==="
	./$(TARGET) < ../../test/producer-consumer/test1

test2: $(TARGET)
	@echo "=== 测试2：单生产者多消费者 ==="
	./$(TARGET) < ../../test/producer-consumer/test2

test3: $(TARGET)
	@echo "=== 测试3：多生产者单消费者 ==="
	./$(TARGET) < ../../test/producer-consumer/test3

test4: $(TARGET)
	@echo "=== 测试4：多生产者多消费者 ==="
	./$(TARGET) < ../../test/producer-consumer/test4

test-all: test1 test2 test3 test4

.PHONY: all clean test1 test2 test3 test4 test-all
