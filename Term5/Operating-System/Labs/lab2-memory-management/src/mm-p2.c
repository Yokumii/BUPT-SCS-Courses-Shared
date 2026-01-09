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

// 显示系统内存信息
void show_meminfo()
{
    printf("PageSize = %ld B\n", pagesize);
    FILE * fp;
    char filename[32];
    sprintf(filename, "/proc/meminfo");
    fp = fopen (filename, "r");
    char line[100];
    int index = 0;
    while (fgets(line, sizeof line, fp) != NULL) {
        if (index < 3) {
            printf("%s", line);
        }
        index += 1;
    }
    printf("----------\n");
    fclose(fp);
}

// 显示进程内存使用情况
void show_process_memory(pid_t pid)
{
    FILE * fp;
    char filename[32];
    sprintf(filename, "/proc/%d/status", pid);
    fp = fopen (filename, "r");
    if (fp == NULL) {
        perror("无法打开进程状态文件");
        return;
    }
    char line[100];
    while (fgets(line, sizeof line, fp) != NULL) {
        if (strncmp(line, "VmSize:", 7) == 0 ||
            strncmp(line, "VmRSS:", 6) == 0) {
            printf("%s", line);
        }
    }
    printf("----------\n");
    fclose(fp);
}

int main(int argc, char const *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "使用方法: %s <共享内存名称>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    const char* shm_name = argv[1];
    pagesize = getpagesize();

    // 创建并打开共享内存对象
    int shm_fd = shm_open(shm_name, O_CREAT | O_RDWR, 0666);
    if (shm_fd == -1) {
        perror("shm_open");
        exit(EXIT_FAILURE);
    }

    // 设置共享内存大小
    if (ftruncate(shm_fd, sizeof(SharedData)) == -1) {
        perror("ftruncate");
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

    // 初始化共享内存中的信号量
    sem_init(&shared_data->sem1, 1, 0);  // pshared=1表示进程间共享
    sem_init(&shared_data->sem2, 1, 0);
    shared_data->finished = false;
    shared_data->p1_pid = 0;

    // 打印操作系统内存信息
    show_meminfo();

    // 等待p1写入PID
    sem_wait(&shared_data->sem1);

    // 读取p1的PID
    pid_t p1_pid = shared_data->p1_pid;
    printf("P1 PID: %d\n", p1_pid);
    show_process_memory(p1_pid);

    // 通知p1可以继续
    sem_post(&shared_data->sem2);

    // 循环处理内存操作
    while (1) {
        sem_wait(&shared_data->sem1);

        if (shared_data->finished) {
            break;
        }

        // 打印内存操作信息
        const char* oper_name[] = {"mmap", "write", "mlock", "munlock", "munmap"};
        printf("%s:    addr = %p, pages = %d\n",
               oper_name[shared_data->oper],
               shared_data->addr,
               shared_data->pages);

        // 打印p1的内存使用情况
        show_process_memory(p1_pid);

        // 通知p1继续下一步操作
        sem_post(&shared_data->sem2);
    }

    // 清理资源
    sem_destroy(&shared_data->sem1);
    sem_destroy(&shared_data->sem2);
    munmap(shared_data, sizeof(SharedData));
    shm_unlink(shm_name);

    return 0;
}
