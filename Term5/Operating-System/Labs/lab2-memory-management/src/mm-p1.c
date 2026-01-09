#define _POSIX_C_SOURCE 200809L
#define _DEFAULT_SOURCE

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <semaphore.h>
#include <stdbool.h>
#include <string.h>

// 共享内存结构体
typedef struct {
    sem_t sem1;  // 控制p2读取
    sem_t sem2;  // 控制p1执行
    pid_t p1_pid;  // p1的进程ID
    int oper;      // 操作类型
    void* addr;    // 操作地址
    int pages;     // 页数
    bool finished; // 完成标志
} SharedData;

size_t pagesize;

int main(int argc, char const *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "使用方法: %s <共享内存名称>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    const char* shm_name = argv[1];
    pagesize = getpagesize();

    // 打开共享内存对象（由p2创建）
    int shm_fd = shm_open(shm_name, O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("shm_open");
        fprintf(stderr, "请先运行 mm-p2\n");
        exit(EXIT_FAILURE);
    }

    // 将共享内存映射到进程地址空间
    SharedData* shared_data = mmap(NULL, sizeof(SharedData),
                                    PROT_READ | PROT_WRITE,
                                    MAP_SHARED, shm_fd, 0);
    if (shared_data == MAP_FAILED) {
        perror("mmap");
        exit(EXIT_FAILURE);
    }

    // 向共享内存写入本进程PID
    shared_data->p1_pid = getpid();
    sem_post(&shared_data->sem1);

    // 等待p2打印初始信息
    sem_wait(&shared_data->sem2);

    // 读取input.txt并执行内存操作
    FILE * fp;
    fp = fopen ("input.txt", "r");
    if (fp == NULL) {
        perror("无法打开input.txt");
        exit(EXIT_FAILURE);
    }

    int oper, start, block, protection;
    int base = 1 << 20;
    char* region = NULL;

    while (fscanf(fp, "%d%d%d%d\n", &oper, &start, &block, &protection) != EOF) {
        if (oper == 0) {  // mmap
            region = mmap(
                (void*) (pagesize * (base + start)),
                pagesize * block,
                PROT_READ|PROT_WRITE|PROT_EXEC,
                MAP_ANON|MAP_PRIVATE,
                0,
                0
            );
            if (region == MAP_FAILED) {
                perror("Could not mmap");
                continue;
            }
            shared_data->addr = region;
            shared_data->pages = block;
            shared_data->oper = 0;

        } else if (oper == 1) {  // write
            void* pos = (void*) (pagesize * (base + start));
            for (int i = 0; i < pagesize * block; i++)
                memcpy((void*) ((pagesize * (base + start) + i)), "a", 1);
            shared_data->addr = pos;
            shared_data->pages = block;
            shared_data->oper = 1;

        } else if (oper == 2) {  // mlock
            mlock((void*) (pagesize * (base + start)), block * pagesize);
            shared_data->addr = (void*) (pagesize * (base + start));
            shared_data->pages = block;
            shared_data->oper = 2;

        } else if (oper == 3) {  // munlock
            munlock((void*) (pagesize * (base + start)), block * pagesize);
            shared_data->addr = (void*) (pagesize * (base + start));
            shared_data->pages = block;
            shared_data->oper = 3;

        } else if (oper == 4) {  // munmap
            munmap((void*) (pagesize * (base + start)), block * pagesize);
            shared_data->addr = (void*) (pagesize * (base + start));
            shared_data->pages = block;
            shared_data->oper = 4;
        }

        // 通知p2打印内存信息
        sem_post(&shared_data->sem1);

        // 等待p2打印完成
        sem_wait(&shared_data->sem2);
    }

    fclose(fp);

    sleep(10);

    // 标记完成
    shared_data->finished = true;
    sem_post(&shared_data->sem1);

    // 清理资源
    munmap(shared_data, sizeof(SharedData));

    return 0;
}
