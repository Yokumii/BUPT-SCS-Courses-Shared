#define _DEFAULT_SOURCE  // 启用 POSIX 扩展功能（如 usleep）
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>  // 高精度计时

// 缓冲区相关
int *buffer;           // 缓冲区数组
int buffer_size;       // 缓冲区大小
int total_products;    // 总生产数量

// 索引指针
int produce_index = 0; // 下一个生产位置
int consume_index = 0; // 下一个消费位置

// 计数器
int produced = 0;      // 已生产数量
int consumed = 0;      // 已消费数量

// 同步与互斥
sem_t mutex;           // 互斥信号量（初始值为1）
sem_t full_sem;        // 缓冲区已满的数量
sem_t empty_sem;       // 缓冲区空位的数量

// 线程信息结构
typedef struct {
    int id;            // 线程ID
    char role;         // P=生产者, C=消费者
    int delay;         // 启动延时（秒）
    int count;         // 生产/消费数量
} ThreadInfo;

// 时间基准（程序启动时间）- 高精度
struct timeval start_time;

// 获取当前相对时间（毫秒）
long get_current_time_ms() {
    struct timeval current;
    gettimeofday(&current, NULL);
    return (current.tv_sec - start_time.tv_sec) * 1000 +
           (current.tv_usec - start_time.tv_usec) / 1000;
}

// 初始化随机数种子（使用高精度计时器）
void initialize_random_seed() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    unsigned int seed = (unsigned int)(tv.tv_sec * 1000000 + tv.tv_usec + pthread_self());
    srand(seed);
}

// 生成随机数 [min, max]
int random_range(int min, int max) {
    return rand() % (max - min + 1) + min;
}

// 生产者函数
void* producer(void* arg) {
    ThreadInfo *info = (ThreadInfo*)arg;

    // 初始化随机数种子（每个线程独立）
    initialize_random_seed();

    // 延时启动
    sleep(info->delay);
    printf("[%04ldms]生产者线程%d启动，计划生产%d个产品\n",
           get_current_time_ms(), info->id, info->count);

    for (int i = 0; i < info->count; i++) {
        // 模拟随机生产耗时（500-2000ms）- 生产需要时间
        int produce_time = random_range(500, 2000);
        usleep(produce_time * 1000);

        // 等待空位
        sem_wait(&empty_sem);

        // 互斥访问缓冲区
        sem_wait(&mutex);

        // 检查是否已达到总生产量
        if (produced >= total_products) {
            sem_post(&mutex);
            sem_post(&empty_sem);
            break;
        }

        // 生产产品（放入缓冲区）
        int product = ++produced;
        buffer[produce_index] = product;
        printf("[%04ldms]生产者%d生产产品%d，放入位置[%d]（耗时%dms）\n",
               get_current_time_ms(), info->id, product, produce_index, produce_time);

        // 移动生产索引（循环队列）
        produce_index = (produce_index + 1) % buffer_size;

        sem_post(&mutex);

        // 通知消费者有新产品
        sem_post(&full_sem);
    }

    printf("[%04ldms]生产者线程%d结束\n", get_current_time_ms(), info->id);
    free(info);
    return NULL;
}

// 消费者函数
void* consumer(void* arg) {
    ThreadInfo *info = (ThreadInfo*)arg;

    // 初始化随机数种子（每个线程独立）
    initialize_random_seed();

    // 延时启动
    sleep(info->delay);
    printf("[%04ldms]消费者线程%d启动，计划消费%d个产品\n",
           get_current_time_ms(), info->id, info->count);

    for (int i = 0; i < info->count; i++) {
        // 等待产品
        sem_wait(&full_sem);

        // 互斥访问缓冲区
        sem_wait(&mutex);

        // 检查是否已消费完所有产品
        if (consumed >= total_products) {
            sem_post(&mutex);
            sem_post(&full_sem);
            break;
        }

        // 消费产品（从缓冲区取出）
        int product = buffer[consume_index];
        consumed++;
        printf("[%04ldms]消费者%d消费产品%d，从位置[%d]取出\n",
               get_current_time_ms(), info->id, product, consume_index);

        // 移动消费索引（循环队列）
        consume_index = (consume_index + 1) % buffer_size;

        sem_post(&mutex);

        // 通知生产者有空位
        sem_post(&empty_sem);

        // 模拟随机消费耗时（500-2000ms）- 消费/处理需要时间
        int consume_time = random_range(500, 2000);
        usleep(consume_time * 1000);
    }

    printf("[%04ldms]消费者线程%d结束\n", get_current_time_ms(), info->id);
    free(info);
    return NULL;
}

int main() {
    // 读取配置：缓冲区大小和总生产量
    scanf("%d %d", &buffer_size, &total_products);

    // 初始化缓冲区
    buffer = (int*)malloc(buffer_size * sizeof(int));

    // 初始化信号量
    sem_init(&mutex, 0, 1);              // 互斥信号量，初始值为1
    sem_init(&full_sem, 0, 0);           // 初始无产品
    sem_init(&empty_sem, 0, buffer_size); // 初始全空

    // 记录启动时间（高精度）
    gettimeofday(&start_time, NULL);
    printf("[0000ms]程序启动，缓冲区大小=%d，总生产量=%d\n",
           buffer_size, total_products);

    // 读取线程配置并创建线程
    char role;
    int id, delay, count;
    pthread_t threads[100];
    int thread_count = 0;

    while (scanf(" %c %d %d", &role, &delay, &count) == 3) {
        ThreadInfo *info = (ThreadInfo*)malloc(sizeof(ThreadInfo));
        info->id = id = thread_count + 1;
        info->role = role;
        info->delay = delay;
        info->count = count;

        if (role == 'P') {
            pthread_create(&threads[thread_count++], NULL, producer, info);
        } else if (role == 'C') {
            pthread_create(&threads[thread_count++], NULL, consumer, info);
        }
    }

    // 等待所有线程结束
    for (int i = 0; i < thread_count; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("[%04ldms]所有线程结束，总生产=%d，总消费=%d\n",
           get_current_time_ms(), produced, consumed);

    // 清理资源
    sem_destroy(&mutex);
    sem_destroy(&full_sem);
    sem_destroy(&empty_sem);
    free(buffer);

    return 0;
}
