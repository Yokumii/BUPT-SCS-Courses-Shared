#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <pthread.h>
#include <semaphore.h>
#include <stdbool.h>
#include <string.h>

sem_t sig_trac;
sem_t sig_alloc;
bool finished = false;
size_t pagesize;

void show_memory_usage()
{
    FILE * fp;
    char filename[32];
    sprintf(filename, "/proc/%d/status", getpid());
    fp = fopen (filename, "r");
    char line[100];
    while (fgets(line, sizeof line, fp) != NULL) {
        // 使用字符串匹配查找VmSize和VmRSS（当前值指标）
        if (strncmp(line, "VmSize:", 7) == 0 ||
            strncmp(line, "VmRSS:", 6) == 0) {
            printf("%s", line);
        }
    }
    printf("----------\n");
    fclose(fp);
}

void show_meminfo()
{
    printf("PageSize = %ld B\n", pagesize);
    FILE * fp;
    char filename[32];
    sprintf(filename, "/proc/meminfo");
    fp = fopen (filename, "r");
    char result[300] = "";
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

void* tracker(void *argPtr)
{
    show_meminfo();
    while (!finished) {
        sem_wait(&sig_trac);
        show_memory_usage();
        sem_post(&sig_alloc);
    }
    return NULL;
}

void* allocater(void *argPtr)
{
    int oper, start, block, protection;
    int base = 1 << 20;
    FILE * fp;
    fp = fopen ("input.txt", "r");    
    char* region;
    while (fscanf(fp, "%d%d%d%d\n", &oper, &start, &block, &protection) != EOF) {
        sem_wait(&sig_alloc);
        if (oper == 0) {
            region = mmap(
                (void*) (pagesize * (base + start)),
                pagesize * block,
                PROT_READ|PROT_WRITE|PROT_EXEC,
                MAP_ANON|MAP_PRIVATE,
                0,
                0
            );
            if (region == MAP_FAILED) {
                perror("Could not mmap\n");
                return NULL;
            }            
            printf("mmap:    addr = %p, pages = %d\n", region, block);

        } else if (oper == 1) {
            void* pos = (void*) (pagesize * (base + start));
            for (int i = 0; i < pagesize * block; i++)
                memcpy((void*) ((pagesize * (base + start) + i)), "a", 1);
            printf("write:   addr = %p, pages = %d\n", region, block);
        } else if (oper == 2) {
            mlock((void*) (pagesize * (base + start)), block * pagesize);
            printf("mlock:   addr = %p, pages = %d\n", region, block);
        } else if (oper == 3) {
            munlock((void*) (pagesize * (base + start)), block * pagesize);
            printf("munlock: addr = %p, pages = %d\n", region, block);
        } else if (oper == 4) {
            munmap((void*) (pagesize * (base + start)), block * pagesize);
            printf("munmap:  addr = %p, pages = %d\n", region, block);
        }

        sem_post(&sig_trac);
    }
    finished = true;
    return NULL;
}

int main(int argc, char const *argv[])
{
    pagesize = getpagesize();
    pthread_t id_trac, id_alloc;
    sem_init(&sig_trac, 0, 1);
    sem_init(&sig_alloc, 0, 0);
    pthread_create(&id_trac, NULL, tracker, NULL);
    pthread_create(&id_alloc, NULL, allocater, NULL);
    pthread_join(id_trac, NULL);
    pthread_join(id_alloc, NULL);

    sem_destroy(&sig_trac);
    sem_destroy(&sig_alloc);

    return 0;
}
