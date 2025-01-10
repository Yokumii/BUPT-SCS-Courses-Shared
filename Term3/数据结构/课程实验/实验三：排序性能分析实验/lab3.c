#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define MAXSIZE 3019

typedef double Key_Open_Type;
typedef double Key_Close_Type;
typedef double Key_High_Type;
typedef double Key_Low_Type;
typedef long Key_Volume_Type;

typedef struct {
    int Id;
    char Date[12];
    Key_Open_Type Open;
    Key_Close_Type Close;
    Key_High_Type High;
    Key_Low_Type Low;
    Key_Volume_Type Volume;
} StockType;

typedef struct {
    StockType r[MAXSIZE + 1];  //r[0]闲置或作哨兵
    int length;
} SqList;

typedef SqList HeapType; // 完全二叉堆，也用顺序表存储

// 计数器，设置为全局变量，省去通过参数传递
long compare_count = 0;
long move_count = 0;

// 读取 CSV 文件并存入 SqList
void load_csv(const char *filename, SqList *list) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("无法打开文件");
        return;
    }

    char line[256];
    int line_count = 0;

    // 跳过表头
    fgets(line, sizeof(line), file);
    list->r[0].Close = 0;
    strcmp(list->r[0].Date, "");
    list->r[0].High = 0;
    list->r[0].Id = 0;
    list->r[0].Low = 0;
    list->r[0].Open = 0;
    list->r[0].Volume = 100;
    while (fgets(line, sizeof(line), file)) {
        if (line_count >= MAXSIZE) {
            printf("文件数据超出限制(%d)。\n", MAXSIZE);
            break;
        }

        // 解析一行数据
        StockType stock;
        char *token = strtok(line, ",");
        stock.Id = atoi(token);

        token = strtok(NULL, ",");
        strncpy(stock.Date, token, sizeof(stock.Date) - 1);
        stock.Date[sizeof(stock.Date) - 1] = '\0';

        token = strtok(NULL, ",");
        stock.Open = atof(token);

        token = strtok(NULL, ",");
        stock.High = atof(token);

        token = strtok(NULL, ",");
        stock.Low = atof(token);

        token = strtok(NULL, ",");
        stock.Close = atof(token);

        token = strtok(NULL, ",");
        stock.Volume = atol(token);

        // 将数据存入 SqList
        list->r[++line_count] = stock;
    }

    list->length = line_count;

    fclose(file);
    printf("CSV 数据加载完成，共加载 %d 条记录。\n", list->length);
}

// 打印 SqList 中的数据
void print_sq_list(const SqList *list) {
    for (int i = 1; i <= list->length; i++) {
        const StockType *stock = &list->r[i];
        printf("Id: %d, Date: %s, Open: %.2f, High: %.2f, Low: %.2f, Close: %.2f, Volume: %ld\n",
               stock->Id, stock->Date, stock->Open, stock->High, stock->Low, stock->Close, stock->Volume);
    }
}

// 比较函数
int compare_open(const StockType *a, const StockType *b) {
    return (a->Open > b->Open) - (a->Open < b->Open);
}
int compare_close(const StockType *a, const StockType *b) {
    return (a->Close > b->Close) - (a->Close < b->Close);
}
int compare_high(const StockType *a, const StockType *b) {
    return (a->High > b->High) - (a->High < b->High);
}
int compare_low(const StockType *a, const StockType *b) {
    return (a->Low > b->Low) - (a->Low < b->Low);
}
int compare_volume(const StockType *a, const StockType *b) {
    return (a->Volume > b->Volume) - (a->Volume < b->Volume);
}

// 希尔排序函数
void ShellSort(SqList *list, int (*compare)(const StockType *, const StockType *)) {
    // 给定Sedgewick's增量
    int gaps[] = {1, 5, 19, 41, 109, 209, 505, 929};
    int gap_size = 8;

    compare_count = 0;
    move_count = 0;

    for (int g = gap_size - 1; g >= 0; g--) {
        int gap = gaps[g];
        for (int i = gap + 1; i <= list->length; i++) {
            StockType temp = list->r[i];
            move_count++;

            int j;
            for (j = i - gap; j > 0; j -= gap) {
                compare_count++;
                if (compare(&temp, &list->r[j]) >= 0) break;
                list->r[j + gap] = list->r[j];
                move_count++;
            }
            list->r[j + gap] = temp;
            move_count++;
        }
    }
}

// 划分
int Partition(SqList *list, int low, int high, int (*compare)(const StockType *, const StockType *)) {
    list->r[0] = list->r[low];
    move_count++;
    StockType pivot = list->r[low];  // 使用临时变量存储支点值
    while (low < high) {
        while (low < high && compare(&pivot, &list->r[high]) <= 0) {
            compare_count++;  // 比较次数++
            high--;
        }
        list->r[low] = list->r[high];  // 将较小值移到左侧
        move_count++;  // 移动次数++
        while (low < high && compare(&pivot, &list->r[low]) >= 0) {
            compare_count++;  // 比较次数++
            low++;
        }
        list->r[high] = list->r[low];  // 将较大值移到右侧
        move_count++;  // 移动次数++
    }
    list->r[low] = list->r[0];  // 将支点值放入最终位置
    move_count++;  // 移动次数++
    return low;
}

// 快速排序递归函数
void Qsort(SqList *list, int low, int high, int (*compare)(const StockType *, const StockType *)) {
    while (low < high) {
        int pivotloc = Partition(list, low, high, compare);
        Qsort(list, low, pivotloc - 1, compare);  // 先处理左子数组
        low = pivotloc + 1;  // 尾递归优化：右子数组的递归替换为循环
    }
}

void QuickSort(SqList *list, int (*compare)(const StockType *, const StockType *)) {
    compare_count = 0;
    move_count = 0;  // 初始化计数器
    Qsort(list, 1, list->length, compare);
}

// 检查稳定性
int check_stability(const SqList *list, int (*compare)(const StockType *, const StockType *)) {
    for (int i = 1; i < list->length; i++) {
        if (compare(&list->r[i], &list->r[i + 1]) == 0 && list->r[i].Id > list->r[i + 1].Id) {
            return 0;  // 不稳定
        }
    }
    return 1;  // 稳定
}

// 维持堆的性质
void HeapAdjust(HeapType *H, int root, int length, int (*compare)(const StockType *, const StockType *)) {
    StockType r = H->r[root];

    for (int j = 2 * root; j <= length; j *= 2) {
        if (j < length && compare(&H->r[j], &H->r[j + 1]) < 0) {  
            // 比较左右子节点
            compare_count++;
            j++;  // 选择右子节点
        }

        // 如果根节点已经大于等于子节点，则退出
        compare_count++;
        if (compare(&r, &H->r[j]) >= 0) 
            break;

        // 将子节点移动到根节点位置
        H->r[root] = H->r[j];
        move_count++;  // 移动次数计数
        root = j;  // 更新当前根节点
    }

    H->r[root] = r;  // 最后将根节点放入正确位置
    move_count++;  // 移动次数计数
}

// 堆排序
void HeapSort(HeapType *H, int (*compare)(const StockType *, const StockType *)) {
    compare_count = 0;
    move_count = 0;  // 初始化计数器

    // 构建初始大顶堆
    for (int i = H->length / 2; i > 0; i--) {
        HeapAdjust(H, i, H->length, compare);
    }

    // 进行排序操作
    for (int j = H->length; j > 1; j--) {
        // 交换堆顶和最后一个元素
        StockType temp = H->r[1];
        H->r[1] = H->r[j];
        H->r[j] = temp;
        move_count += 3;  // 一次完整的交换计为三次移动

        // 调整剩余元素使其重新满足堆性质
        HeapAdjust(H, 1, j - 1, compare);
    }
}

// 堆排序得到top100和top500
void HeapSortTopK(HeapType *H, int K, int (*compare)(const StockType *, const StockType *)) {
    compare_count = 0;
    move_count = 0;  // 初始化计数器

    // 构建初始大顶堆
    for (int i = H->length / 2; i > 0; i--) {
        HeapAdjust(H, i, H->length, compare);
    }

    // 对堆进行调整，只保留前K大元素
    for (int j = H->length; j > H->length - K; j--) {
        StockType temp = H->r[1];
        H->r[1] = H->r[j];
        H->r[j] = temp;
        move_count += 3;  // 一次交换计三次移动

        // 调整堆以维持堆性质
        HeapAdjust(H, 1, K, compare);
    }
}

// 将两张有序表归并为一张有序表
void Merge(StockType SR[], StockType TR[], int left, int mid, int right, int (*compare)(const StockType *, const StockType *)) {
    int i = left, j = mid + 1, k = left;

    while (i <= mid && j <= right) {
        compare_count++;
        if (compare(&SR[i], &SR[j]) <= 0) {
            TR[k++] = SR[i++];
        } else {
            TR[k++] = SR[j++];
        }
        move_count++;
    }

    while (i <= mid) {
        TR[k++] = SR[i++];
        move_count++;
    }
    while (j <= right) {
        TR[k++] = SR[j++];
        move_count++;
    }
}

// 归并排序
void MergeSort(SqList *list, int (*compare)(const StockType *, const StockType *)) {
    compare_count = 0;
    move_count = 0;  // 初始化计数器
    
    int len = list->length;
    StockType *TR = (StockType *)malloc((len + 1) * sizeof(StockType));
    if (TR == NULL) {
        perror("内存分配失败");
        exit(EXIT_FAILURE);
    }
    
    for (int step = 1; step < len; step *= 2) {  // 每次子序列长度加倍
        for (int left = 1; left <= len - step; left += 2 * step) {
            int mid = left + step;                // 左子序列的结束位置
            int right = (left + 2 * step > len)  // 防止越界
                           ? len
                           : (left + 2 * step);

            Merge(list->r, TR, left, mid, right, compare);
        }

        // 每轮完成后将结果复制回原数组
        for (int i = 1; i <= len; i++) {
            list->r[i] = TR[i];
        }
    }

    free(TR);  // 释放辅助数组
    TR = NULL;
}

// 保存排序结果到文件
void save_to_file(const char *filename, int start, const SqList *list) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("无法创建文件");
        return;
    }

    // 写入表头
    fprintf(file, "Id,Date,Open,High,Low,Close,Volume,Name\n");

    // 写入数据
    for (int i = start; i <= list->length; i++) {
        const StockType *stock = &list->r[i];
        fprintf(file, "%d,%s,%.2f,%.2f,%.2f,%.2f,%ld,%s\n",
                stock->Id, stock->Date, stock->Open, stock->High, stock->Low, stock->Close, stock->Volume, "AABA");
    }

    fclose(file);
}

// 保存排序结果到文件
void save_to_file_reverse(const char *filename, int start, const SqList *list) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("无法创建文件");
        return;
    }

    // 写入表头
    fprintf(file, "Id,Date,Open,High,Low,Close,Volume,Name\n");

    // 写入数据
    for (int i = list->length; i >= start; i--) {
        const StockType *stock = &list->r[i];
        fprintf(file, "%d,%s,%.2f,%.2f,%.2f,%.2f,%ld,%s\n",
                stock->Id, stock->Date, stock->Open, stock->High, stock->Low, stock->Close, stock->Volume, "AABA");
    }

    fclose(file);
}

// 执行排序并输出统计信息
void execute_shell_sort(SqList *list, const char *output_filename, int (*compare)(const StockType *, const StockType *)) {

    SqList sorted_list = *list;

    clock_t start = clock();
    ShellSort(&sorted_list, compare);
    clock_t end = clock();

    int is_stable = check_stability(&sorted_list, compare);

    save_to_file(output_filename, 1, &sorted_list);

    printf("排序结果保存至: %s\n", output_filename);
    printf("关键字比较次数: %ld\n", compare_count);
    printf("关键字移动次数: %ld\n", move_count);
    printf("排序时间: %.4f 秒\n", (double)(end - start) / CLOCKS_PER_SEC);
    printf("稳定性: %s\n\n", is_stable ? "稳定" : "不稳定");
}

void execute_quick_sort(SqList *list, const char *output_filename, int (*compare)(const StockType *, const StockType *)) {

    SqList sorted_list = *list;

    clock_t start = clock();
    QuickSort(&sorted_list, compare);
    clock_t end = clock();

    int is_stable = check_stability(&sorted_list, compare);

    save_to_file(output_filename, 1, &sorted_list);

    printf("排序结果保存至: %s\n", output_filename);
    printf("关键字比较次数: %ld\n", compare_count);
    printf("关键字移动次数: %ld\n", move_count);
    printf("排序时间: %.4f 秒\n", (double)(end - start) / CLOCKS_PER_SEC);
    printf("稳定性: %s\n\n", is_stable ? "稳定" : "不稳定");
}

void execute_heap_sort(SqList *list, const char *output_filename, int (*compare)(const StockType *, const StockType *)) {

    SqList sorted_list = *list;

    clock_t start = clock();
    HeapSort(&sorted_list, compare);
    clock_t end = clock();

    int is_stable = check_stability(&sorted_list, compare);

    save_to_file(output_filename, 1, &sorted_list);

    printf("排序结果保存至: %s\n", output_filename);
    printf("关键字比较次数: %ld\n", compare_count);
    printf("关键字移动次数: %ld\n", move_count);
    printf("排序时间: %.4f 秒\n", (double)(end - start) / CLOCKS_PER_SEC);
    printf("稳定性: %s\n\n", is_stable ? "稳定" : "不稳定");
}

void execute_merge_sort(SqList *list, const char *output_filename, int (*compare)(const StockType *, const StockType *)) {

    SqList sorted_list = *list;

    clock_t start = clock();
    MergeSort(&sorted_list, compare);
    clock_t end = clock();

    int is_stable = check_stability(&sorted_list, compare);

    save_to_file(output_filename, 1, &sorted_list);

    printf("排序结果保存至: %s\n", output_filename);
    printf("关键字比较次数: %ld\n", compare_count);
    printf("关键字移动次数: %ld\n", move_count);
    printf("排序时间: %.4f 秒\n", (double)(end - start) / CLOCKS_PER_SEC);
    printf("稳定性: %s\n\n", is_stable ? "稳定" : "不稳定");
}

void execute_select_top(SqList *list, int K, const char *output_filename, int (*compare)(const StockType *, const StockType *)) {

    SqList sorted_list = *list;

    clock_t start = clock();
    HeapSortTopK(&sorted_list, K, compare);
    clock_t end = clock();

    save_to_file_reverse(output_filename, list->length - K + 1, &sorted_list);

    printf("排序结果保存至: %s\n", output_filename);
    printf("关键字比较次数: %ld\n", compare_count);
    printf("关键字移动次数: %ld\n", move_count);
    printf("排序时间: %.4f 秒\n", (double)(end - start) / CLOCKS_PER_SEC);
}


int main() {
    SqList stock_list = {.length = 0};

    const char *filename = "stock_data.csv";
    load_csv(filename, &stock_list);

    // printf("读取的数据如下：\n");
    // print_sq_list(&stock_list);

    // // 希尔排序
    // // 对 Open 排序
    // SqList open_sorted = stock_list;
    // execute_shell_sort(&open_sorted, "Open_shell_sort.csv", compare_open);

    // // 对 Close 排序
    // SqList close_sorted = stock_list;
    // execute_shell_sort(&close_sorted, "Close_shell_sort.csv", compare_close);

    // // 对 High 排序
    // SqList high_sorted = stock_list;
    // execute_shell_sort(&high_sorted, "High_shell_sort.csv", compare_high);

    // // 对 Low 排序
    // SqList low_sorted = stock_list;
    // execute_shell_sort(&low_sorted, "Low_shell_sort.csv", compare_low);

    // // 对 Volume 排序
    // SqList volume_sorted = stock_list;
    // execute_shell_sort(&volume_sorted, "Volume_shell_sort.csv", compare_volume);

    // printf("希尔排序完成，结果已保存到文件。\n");

    // // 快速排序
    // // 对 Open 排序
    // SqList open_sorted = stock_list;
    // execute_quick_sort(&open_sorted, "Open_quick_sort.csv", compare_open);

    // // 对 Close 排序
    // SqList close_sorted = stock_list;
    // execute_quick_sort(&close_sorted, "Close_quick_sort.csv", compare_close);

    // // 对 High 排序
    // SqList high_sorted = stock_list;
    // execute_quick_sort(&high_sorted, "High_quick_sort.csv", compare_high);

    // // 对 Low 排序
    // SqList low_sorted = stock_list;
    // execute_quick_sort(&low_sorted, "Low_quick_sort.csv", compare_low);

    // // 对 Volume 排序
    // SqList volume_sorted = stock_list;
    // execute_quick_sort(&volume_sorted, "Volume_quick_sort.csv", compare_volume);

    // printf("快速排序完成，结果已保存到文件。\n");

    // // 堆排序
    // // 对 Open 排序
    // SqList open_sorted = stock_list;
    // execute_heap_sort(&open_sorted, "Open_heap_sort.csv", compare_open);

    // // 对 Close 排序
    // SqList close_sorted = stock_list;
    // execute_heap_sort(&close_sorted, "Close_heap_sort.csv", compare_close);

    // // 对 High 排序
    // SqList high_sorted = stock_list;
    // execute_heap_sort(&high_sorted, "High_heap_sort.csv", compare_high);

    // // 对 Low 排序
    // SqList low_sorted = stock_list;
    // execute_heap_sort(&low_sorted, "Low_heap_sort.csv", compare_low);

    // // 对 Volume 排序
    // SqList volume_sorted = stock_list;
    // execute_heap_sort(&volume_sorted, "Volume_heap_sort.csv", compare_volume);

    // printf("堆排序完成，结果已保存到文件。\n");

    // 归并排序
    // 对 Open 排序
    SqList open_sorted = stock_list;
    execute_merge_sort(&open_sorted, "Open_merge_sort.csv", compare_open);

    // 对 Close 排序
    SqList close_sorted = stock_list;
    execute_merge_sort(&close_sorted, "Close_merge_sort.csv", compare_close);

    // 对 High 排序
    SqList high_sorted = stock_list;
    execute_merge_sort(&high_sorted, "High_merge_sort.csv", compare_high);

    // 对 Low 排序
    SqList low_sorted = stock_list;
    execute_merge_sort(&low_sorted, "Low_merge_sort.csv", compare_low);

    // 对 Volume 排序
    SqList volume_sorted = stock_list;
    execute_merge_sort(&volume_sorted, "Volume_merge_sort.csv", compare_volume);

    printf("归并排序完成，结果已保存到文件。\n");

    // SqList volume_sorted = stock_list;
    // execute_select_top(&volume_sorted, 100, "volume_top100.csv", compare_volume);
    
    return 0;
}