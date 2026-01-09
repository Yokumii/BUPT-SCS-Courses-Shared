#include <assert.h>
#include <pthread.h>
#include <unistd.h>
#include <semaphore.h>
#include <stdio.h>

//the struct of thread
typedef struct _Thread{
  int tid;//thread id
  int delay;// the begin time of read and write operation
  int last;//time that read and write operation lasts
} Thread;

enum {
  s_waiting,
  s_reading,
  s_writing
} state = s_waiting;

static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
sem_t Sig_read;
sem_t Sig_wrt;
int reader_count = 0;
int writer_count = 0;

time_t start_time;

// 读者进程
void* Reader(void* argPtr) {
  Thread thread = *(Thread*)argPtr;
  sleep(thread.delay);
  printf("[%02.0lf秒]读者进程%d等待读取\n", 
    difftime(time(NULL), start_time), thread.tid
  );

  pthread_mutex_lock(&mutex);
    ++reader_count;
    if(state == s_waiting 
    || (state == s_reading && writer_count == 0)) {
      sem_post(&Sig_read);
      state = s_reading;
    }
  pthread_mutex_unlock(&mutex);
  sem_wait(&Sig_read);

  printf("[%02.0lf秒]读者进程%d开始读取\n", 
    difftime(time(NULL), start_time), thread.tid
  );

  // read
  sleep(thread.last);

  pthread_mutex_lock(&mutex);
    --reader_count;
    if(writer_count != 0) {
      // 有读者在等待
      sem_post(&Sig_wrt);
      state = s_writing;
    } else if(reader_count == 0) {
      // 等待队列为空
      state = s_waiting;
    }
  pthread_mutex_unlock(&mutex);

  printf("[%02.0lf秒]读者进程%d读取结束\n", 
    difftime(time(NULL), start_time), thread.tid
  );
  return NULL;
}

// 写者进程
void* Writer(void* argPtr) {
  Thread thread = *(Thread*)argPtr;
  sleep(thread.delay);
  printf("[%02.0lf秒]写者进程%d等待写入\n", 
    difftime(time(NULL), start_time), thread.tid
  );
  pthread_mutex_lock(&mutex);
  ++writer_count;
  if(state == s_waiting) {
    sem_post(&Sig_wrt);
    state = s_writing;
  }
  pthread_mutex_unlock(&mutex);

  sem_wait(&Sig_wrt);
  printf("[%02.0lf秒]写者进程%d开始写入\n", 
    difftime(time(NULL), start_time), thread.tid
  );
  // write
  sleep(thread.last);

  pthread_mutex_lock(&mutex);
    --writer_count;
    if(writer_count != 0) {
      sem_post(&Sig_wrt);
      state = s_writing;
    } else if(reader_count != 0) {
      for(int i=0; i!=reader_count; ++i) {
        sem_post(&Sig_read);
      }
      state = s_reading;
    } else {
      state = s_waiting;
    }
  pthread_mutex_unlock(&mutex);

  printf("[%02.0lf秒]写者进程%d写入结束\n", 
    difftime(time(NULL), start_time), thread.tid
  );
  return NULL;
}

int main() {
  const int MAX_THREAD = 100;
  // 读写进程队列
  pthread_t tid[MAX_THREAD];
  Thread thread[MAX_THREAD];
  int tidEnd = 0;

  // 初始化信号量
  sem_init(&Sig_read, 0, 0);
  sem_init(&Sig_wrt, 0, 0);

  start_time = time(NULL);

  int arg_tid;
  int arg_delay;
  int arg_last;
  char arg_type;
  while(scanf("%d %c%d%d", &arg_tid, &arg_type, &arg_delay, &arg_last) == 4) {
    assert(tidEnd < MAX_THREAD);
    if(arg_type == 'R') {
      thread[tidEnd].tid = arg_tid;
      thread[tidEnd].delay = arg_delay;
      thread[tidEnd].last = arg_last;
      pthread_create(tid + tidEnd, NULL, Reader, thread + tidEnd);
    } else {
      thread[tidEnd].tid = arg_tid;
      thread[tidEnd].delay = arg_delay;
      thread[tidEnd].last = arg_last;
      pthread_create(tid + tidEnd, NULL, Writer, thread + tidEnd);
    }
    printf("[%02.0lf秒]创建进程%d\n", difftime(time(NULL), start_time), arg_tid);
    ++tidEnd;
  }

  for(int i = 0; i != tidEnd; i++) {
    pthread_join(tid[i], NULL);
  }

  // 销毁信号量
  pthread_mutex_destroy(&mutex);
  sem_destroy(&Sig_read);
  sem_destroy(&Sig_wrt);
}