#include <stdio.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>

typedef struct PokerCard *PtrToCard; // 指向某张牌的指针

// 记录牌堆信息的结构体节点
typedef struct PokerCard
{
    /* 
    * char Data[3]，Data[0]表示花色，Data[1]表示数值，Data[2]表示结束符'\0'，若两位前两位都为X(Y)则表示大王(小王)
    * PtrToCard Next，指向下一张牌的指针
    */
    char Data[3];
    PtrToCard Next;
}Card;

// 以链表结构储存的牌堆
typedef struct
{
    PtrToCard Head;
    PtrToCard Tail; // 仅用于当计数M = 1时，不再遍历一遍找到头节点的前面一个节点。
}Link;

// 以链栈结构储存的牌堆
typedef struct
{
    PtrToCard Top; // 栈顶元素
}Stack;

// 以队列结构储存的牌堆
typedef struct
{
    PtrToCard Front; // 队首元素
    PtrToCard Rear; // 队尾元素
}Quene;

typedef Link *LinkDeck;
typedef Stack *StackDeck;
typedef Quene *QueneDeck;

// 入队
void EnQuene(QueneDeck queneDeck, char data[3])
{
    if (queneDeck->Front == NULL)
    {
        queneDeck->Front = (PtrToCard)malloc(sizeof(Card));
        strcpy(queneDeck->Front->Data, data);
        queneDeck->Rear = queneDeck->Front;
        queneDeck->Front->Next = NULL;
    }
    else
    {
        queneDeck->Rear->Next = (PtrToCard)malloc(sizeof(Card));
        queneDeck->Rear = queneDeck->Rear->Next;
        strcpy(queneDeck->Rear->Data, data);
        queneDeck->Rear->Next = NULL;
    }
}

// 队首元素出队
void DeQuene(QueneDeck queneDeck)
{
    if (queneDeck->Front == NULL)
    {
        printf("队列为空，无法出队\n");
        return;
    }
    
    PtrToCard Ptr = queneDeck->Front;
    if (queneDeck->Front == queneDeck->Rear) // 队列只有一张牌
    {
        queneDeck->Front = queneDeck->Rear = NULL;
    }
    else
    {
        queneDeck->Front = queneDeck->Front->Next;
    }
    free(Ptr);
}

// 从队首开始打印队列元素
void PrintQuene(QueneDeck queneDeck)
{   
    PtrToCard Ptr = queneDeck->Front;
    if (Ptr == NULL)
    {
        printf("队列为空，无法打印\n");
        return;
    }
    do {
        printf("%s ", Ptr->Data);
        Ptr = Ptr->Next;
    } while (Ptr != NULL);
    printf("\n");
}

// 打印队列中最后五个元素
void PrintQuene_5(QueneDeck queneDeck)
{   
    PtrToCard Ptr = queneDeck->Front;
    int count = 0;
    if (Ptr == NULL)
    {
        printf("队列为空，无法打印\n");
        return;
    }
    do {
        count++;
        Ptr = Ptr->Next;
    } while (Ptr != NULL);
    Ptr = queneDeck->Front;
    if (count >= 5)
    {
        int i = 0;
        do {
            i++;
            Ptr = Ptr->Next;
        } while (i < count - 5);

        do {
            printf("%s ", Ptr->Data);
            Ptr = Ptr->Next;
        } while (Ptr != NULL);
    }
    else
    {
        do {
            printf("%s ", Ptr->Data);
            Ptr = Ptr->Next;
        } while (Ptr != NULL);
    }
    printf("\n");
}

// 入栈
void EnStack(StackDeck stackDeck, char data[3])
{
    if (stackDeck->Top == NULL)
    {
        stackDeck->Top = (PtrToCard)malloc(sizeof(Card));
        strcpy(stackDeck->Top->Data, data);
        stackDeck->Top->Next = NULL;
    }
    else
    {
        PtrToCard Ptr = (PtrToCard)malloc(sizeof(Card));
        strcpy(Ptr->Data, data);
        Ptr->Next = stackDeck->Top;
        stackDeck->Top = Ptr;
    }
}

// 栈顶元素出栈
void DeStack(StackDeck stackDeck)
{
    if (stackDeck->Top == NULL)
    {
        printf("栈为空，无法出栈\n");
        return;
    }

    PtrToCard Ptr = stackDeck->Top;
    stackDeck->Top = Ptr->Next;
    free(Ptr);
}


// 初始化未打乱的牌堆
void Generate_UnshuffledCards(char (*UnshuffledCards)[3])
{
    int k = 0;
    char values[13] = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K'};
    for (int i = 0; i < 4; i++) // 遍历花色
    {
        for (int j = 0; j < 13; j++) // 遍历数值
        {
            UnshuffledCards[k][0] = (char)((int)'A' + i);
            UnshuffledCards[k][1] = values[j];
            UnshuffledCards[k][2] = '\0'; // 结束符
            k++;
        }
    }

    // 单独处理大王和小王
    strcpy(UnshuffledCards[52], "XX");
    strcpy(UnshuffledCards[53], "YY");
    return;
}

// 打印顺序表储存的牌堆
void Print_Cards(char (*UnshuffledCards)[3])
{   
    for (int i = 0; i < 54; i++)
    {
        printf("%s ", UnshuffledCards[i]);
    }
    printf("\n");
}

// Knuth-Durstenfeld Shuffle算法洗牌
void Knuth_Durstenfeld_Shuffle(char (*UnshuffledCards)[3])
{
    srand(0);
    for (int i = 54 - 1; i > 0; i--)
    {
        // 从 [0, i] 中随机选取一个索引
        int j = rand() % (i + 1);

        // 交换 UnshuffledCards[i] 和 UnshuffledCards[j]
        char temp[3];
        memcpy(temp, UnshuffledCards[i], sizeof(temp));
        memcpy(UnshuffledCards[i], UnshuffledCards[j], sizeof(temp));
        memcpy(UnshuffledCards[j], temp, sizeof(temp));
    }
}

// 将洗牌后的元素从顺序表中取出插入循环链表
LinkDeck Insert2CircularLinkedList(char (*UnshuffledCards)[3])
{
    LinkDeck linkDeck = (LinkDeck)malloc(sizeof(Link));
    linkDeck->Head = (PtrToCard)malloc(sizeof(Card));
    if (linkDeck->Head == NULL) {
        fprintf(stderr, "内存分配失败!\n");
        exit(1);
    }
    strcpy(linkDeck->Head->Data, UnshuffledCards[0]);
    linkDeck->Head->Next = NULL; 
    PtrToCard Ptr = linkDeck->Head;
    for (int i = 1; i < 54; i++) 
    {
        Ptr->Next = (PtrToCard)malloc(sizeof(Card));
        if (Ptr->Next == NULL) {
            fprintf(stderr, "内存分配失败!\n");
            exit(1);
        }
        Ptr = Ptr->Next;
        strcpy(Ptr->Data, UnshuffledCards[i]);
        Ptr->Next = NULL;
    }
    linkDeck->Tail = Ptr;
    linkDeck->Tail->Next = linkDeck->Head;
    return linkDeck;
}

// 打印循环链表
void PrintCircularLinkedList(LinkDeck linkDeck)
{
    PtrToCard Ptr = linkDeck->Head;
    do {
        printf("%s ", Ptr->Data);
        Ptr = Ptr->Next;
    } while (Ptr != linkDeck->Head);
    
    printf("\n");
}

// 在Ptr后插入新节点
void InsertToLink(LinkDeck linkDeck, PtrToCard Ptr, char data[3])
{
    PtrToCard Temp = (PtrToCard)malloc(sizeof(Card));
    strcpy(Temp->Data, data);
    Temp->Next = Ptr->Next;
    Ptr->Next = Temp;
}

// 根据牌面查找牌堆中任意一张牌的地址，未查找到则返回NULL
PtrToCard FindCardinDeck(LinkDeck linkDeck, char card[3])
{
    PtrToCard Ptr = linkDeck->Head;
    do {
        if (strcmp(Ptr->Data, card) == 0){
            return Ptr;
        }
        Ptr = Ptr->Next;
    } while (Ptr != linkDeck->Head);
    return NULL;
}

// 查找牌堆中出现的第一张大王或小王牌
void FindXYinDeck(LinkDeck linkDeck)
{
    PtrToCard PrePtr = linkDeck->Tail;
    PtrToCard Ptr = linkDeck->Head;
    int count = 1;
    do {
        if (strcmp(Ptr->Data, "XX") == 0)
        {
            printf("定位到第一张出现的大王或小王牌位于从牌堆顶开始的第%d张，此牌为大王牌\n", count);
            linkDeck->Head = Ptr;
            linkDeck->Tail = PrePtr;
            return;
        }
        else if (strcmp(Ptr->Data, "YY") == 0)
        {
            printf("定位到第一张出现的大王或小王牌位于从牌堆顶开始的第%d张，此牌为小王牌\n", count);
            linkDeck->Head = Ptr;
            linkDeck->Tail = PrePtr;
            return;
        }
        count++;
        PrePtr = Ptr;
        Ptr = Ptr->Next;
    } while (Ptr != linkDeck->Head);
    return;
}

// 模拟报数+出牌过程
void PlayingCards(LinkDeck linkDeck, int M, QueneDeck queneDeckA, StackDeck stackDeck)
{
    if (linkDeck->Head == NULL) 
    {
        printf("链表为空，无法进行出牌操作。\n");
        return;
    }

    int count = 1, i = 1;
    PtrToCard prePtr = linkDeck->Tail;
    PtrToCard curPtr = linkDeck->Head;

    while (curPtr->Next != NULL) // 直至只剩最后一张牌
    {
        if (count < M)
        {
            prePtr = curPtr;
            curPtr = curPtr->Next;
            count++;
        }
        else // 出牌
        {
            PtrToCard temp = curPtr;
            if (curPtr->Next == prePtr) //处理将要打出倒数第二张牌时，最后一张牌的Next指针会指向自己的特殊情况
            {
                prePtr->Next = NULL;
            }
            else
            {
                prePtr->Next = curPtr->Next;
            }
            count = 1;

            printf("第%d次打出了牌%s\n", i, curPtr->Data);
            i++;

            // 附加要求：当打出大小王时，可以取回5张，这里将这5张插入打出去牌的位置处，从弃牌堆顶摸一张插一张。
            if (strcmp(curPtr->Data, "XX") == 0 || strcmp(curPtr->Data, "YY") == 0)
            {
                int j = 0;
                printf("打出了%s，进行摸牌操作: ", curPtr->Data);
                PtrToCard Temp = prePtr;
                while (j < 5 && stackDeck->Top != NULL)
                {
                    // 该方法原先设计时是在任意位置后插入
                    InsertToLink(linkDeck, linkDeck->Tail, stackDeck->Top->Data);
                    // 如果在尾部插入，需要更新尾指针
                    if (Temp == linkDeck->Tail) {
                        linkDeck->Tail = Temp->Next;
                    }
                    printf("%s ", stackDeck->Top->Data);
                    DeStack(stackDeck);
                    // 尾插则不需要该语句
                    // Temp = Temp->Next;
                    j++;
                }
                curPtr->Next = prePtr->Next;
                printf("\n");
            }

            if (curPtr == linkDeck->Head)
            {
                linkDeck->Head = curPtr->Next;
            }

            // 将打出的牌置于弃牌堆(除了大小王)
            if (strcmp(curPtr->Data, "XX") != 0&& strcmp(curPtr->Data, "YY") != 0)
            {
                EnStack(stackDeck, curPtr->Data);
            }

            if (curPtr->Data[0] == 'A')
            {
                EnQuene(queneDeckA, curPtr->Data);
            }

            curPtr = curPtr->Next;
            free(temp);
        }
    }

    printf("仅剩最后一张牌%s，出牌阶段结束！\n", curPtr->Data);
}

int main(void){

    // 定义顺序表（二维数组）储存牌堆并进行初始化
    char UnshuffledCards[54][3];
    Generate_UnshuffledCards(UnshuffledCards);
    
    printf("洗牌前的牌堆为:\n");
    Print_Cards(UnshuffledCards);
    Knuth_Durstenfeld_Shuffle(UnshuffledCards);
    printf("使用Knuth-Durstenfeld Shuffle算法洗牌后的牌堆为:\n");
    Print_Cards(UnshuffledCards);

    // 初始化循环链表用于储存手牌
    LinkDeck linkdeck = Insert2CircularLinkedList(UnshuffledCards);
    printf("循环链表中的牌:\n");
    PrintCircularLinkedList(linkdeck);

    // 初始化链队用于储存打出的A开头的牌
    QueneDeck quenedeck_A = (QueneDeck)malloc(sizeof(Quene));

    // 初始化链栈用于储存打出的所有牌
    StackDeck stackdeck = (StackDeck)malloc(sizeof(Stack));

    // 定位：在循环链表中定位第一个出现的大王或小王牌，并将它作为牌堆顶
    FindXYinDeck(linkdeck);
    if (linkdeck->Head == NULL)
    {
        printf("未找到大王牌或小王牌\n");
    }

    // 报数+出牌
    int M;
    printf("请指定计数上限M: ");
    scanf("%d", &M);
    PlayingCards(linkdeck, M, quenedeck_A, stackdeck);

    printf("最后被打出的5张A开头的牌为:\n");
    PrintQuene_5(quenedeck_A);
    return 0;
}