#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 定义二叉搜索树节点
typedef struct BstNode {
    char ID[33];                    // 商品ID
    char Name[256];                 // 商品名称
    int inventory;                  // 商品库存
    struct BstNode *left, *right;   // 左右子树指针
} BstNode;

BstNode* createNode(const char* ID, const char* Name, int inventory);
BstNode* insertBST(BstNode* root, const char* ID, const char* Name, int inventory);
BstNode* buildTreeFromFile(const char* filename);
int calculateHeight(BstNode* root);
void calculateTotalDepth(BstNode* root, int depth, int* totalDepth, int* totalNodes);
void inOrderTraversal(BstNode* root, const char* filename);
BstNode* deleteBST(BstNode* root, const char* ID, int* isFound);

typedef struct AVLNode {
    char ID[33];                    // 商品ID
    char Name[256];                 // 商品名称
    int inventory;                  // 商品库存
    int bf;                         // 平衡因子
    struct AVLNode* left;           // 左右子树指针
    struct AVLNode* right;
} AVLNode;

// 定义栈节点
typedef struct StackNode {
    BstNode* treeNode;      // 栈中存储的二叉树节点
    struct StackNode* next; // 指向下一个栈节点的指针
} StackNode;

StackNode* createStackNode(BstNode* treeNode);
void push(StackNode** top, BstNode* treeNode);
BstNode* pop(StackNode** top);
int isEmpty(StackNode* top);

// 创建一个栈节点
StackNode* createStackNode(BstNode* treeNode) {
    StackNode* newStackNode = (StackNode*)malloc(sizeof(StackNode));
    newStackNode->treeNode = treeNode;
    newStackNode->next = NULL;
    return newStackNode;
}

// 压栈
void push(StackNode** top, BstNode* treeNode) {
    StackNode* newStackNode = createStackNode(treeNode);
    newStackNode->next = *top;
    *top = newStackNode;
}

// 出栈
BstNode* pop(StackNode** top) {
    if (*top == NULL) {
        return NULL;
    }
    StackNode* temp = *top;
    BstNode* treeNode = temp->treeNode;
    *top = (*top)->next;
    free(temp);
    return treeNode;
}

// 判断栈是否为空，若为空栈则返回 1
int isEmpty(StackNode* top) {
    return top == NULL;
}

// 创建新节点
BstNode* createNode(const char* ID, const char* Name, int inventory) {
    BstNode* newNode = (BstNode*)malloc(sizeof(BstNode));
    strcpy(newNode->ID, ID);
    strcpy(newNode->Name, Name);
    newNode->inventory = inventory;
    newNode->left = newNode->right = NULL;
    return newNode;
}

// 插入节点到二叉查找树
BstNode* insertBST(BstNode* root, const char* ID, const char* Name, int inventory) {
    if (root == NULL) {
        return createNode(ID, Name, inventory);
    }
    if (strcmp(ID, root->ID) < 0) {
        root->left = insertBST(root->left, ID, Name, inventory);
    } else if (strcmp(ID, root->ID) > 0) {
        root->right = insertBST(root->right, ID, Name, inventory);
    }
    return root;
}

// 删除节点
BstNode* deleteBST(BstNode* root, const char* ID, int* isFound) {
    if (root == NULL) {
        *isFound = 0;  // 节点未找到
        return NULL; // 空树，无法进行删除操作
    }
    if (strcmp(ID, root->ID) < 0) { // 往左子树查找
        root->left = deleteBST(root->left, ID, isFound);
    } else if (strcmp(ID, root->ID) > 0) { // 往右子树查找
        root->right = deleteBST(root->right, ID, isFound);
    } else { // 找到该节点
        *isFound = 1;
        // 情况1：叶子节点
        if (root->left == NULL && root->right == NULL) {
            free(root);
            return NULL;
        }

        // 情况2：只有一个子节点
        if (root->left == NULL) {
            BstNode* temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            BstNode* temp = root->left;
            free(root);
            return temp;
        }

        // 情况3：有两个子节点
        // 找到右子树中的最小节点
        BstNode* successor = root->right;
        while (successor->left != NULL) {
            successor = successor->left;
        }
        // 用后继节点的数据替换当前节点
        strcpy(root->ID, successor->ID);
        strcpy(root->Name, successor->Name);
        root->inventory = successor->inventory;

        // 删除后继节点
        root->right = deleteBST(root->right, successor->ID, isFound);
    }
    return root;
}

// 从文件中读取数据并构建二叉查找树
BstNode* buildTreeFromFile(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        perror("文件打开失败");
        exit(EXIT_FAILURE);
    }

    BstNode* root = NULL;
    char line[300];

    // 跳过表头
    fgets(line, sizeof(line), file);

    // 读取每一行数据
    while (fgets(line, sizeof(line), file)) {
        char ID[33];
        char Name[256];
        int inventory;

        sscanf(line, "%32[^,],%255[^,],%d", ID, Name, &inventory);
        root = insertBST(root, ID, Name, inventory);
    }

    fclose(file);
    return root;
}

// 计算树的高度
int calculateHeight(BstNode* root) {
    if (root == NULL) {
        return -1;
    }
    int leftHeight = calculateHeight(root->left);
    int rightHeight = calculateHeight(root->right);
    return (leftHeight > rightHeight ? leftHeight : rightHeight) + 1;
}

// 计算所有节点深度的总和和节点总数
void calculateTotalDepth(BstNode* root, int depth, int* totalDepth, int* totalNodes) {
    if (root == NULL) {
        return;
    }

    // 从根节点开始遍历，根节点的深度为 0

    *totalDepth += depth; // 总查找长度 += 该节点的深度
    (*totalNodes)++; // 节点数量++

    calculateTotalDepth(root->left, depth + 1, totalDepth, totalNodes); // 递归左子树，其中左孩子的深度 = 该节点的深度 + 1
    calculateTotalDepth(root->right, depth + 1, totalDepth, totalNodes); // 递归左子树，其中右孩子的深度 = 该节点的深度 + 1
}

// 非递归中序遍历
void inOrderTraversal(BstNode* root, const char* filename) {
    StackNode* stack = NULL; // 初始化空栈
    BstNode* cPtr = root;    // 初始指向根节点

    FILE* file = fopen(filename, "w");
    if (!file) {
        perror("无法打开文件");
        return;
    }

    while (cPtr != NULL || !isEmpty(stack)) { // 当前节点不为空或栈非空
        while (cPtr != NULL) { // 当前节点不为空，则将当前节点入栈，然后继续往左直至走到底
            push(&stack, cPtr);
            cPtr = cPtr->left;
        }

        cPtr = pop(&stack); // 已经走到左下角，出栈，将栈顶节点赋给p
        fprintf(file, "%s\n", cPtr->ID);
        // printf("%s\n", cPtr->ID); // 输出该节点

        cPtr = cPtr->right; // 该节点作为根节点，位于整棵树的左下角，无左子树，检查右子树
    }

    fclose(file);
    printf("中序遍历结果已保存到文件：%s\n", filename);
}

// 搜索节点
BstNode* searchNode(BstNode* root, const char* ID) {
    // 如果节点为空或找到目标节点
    if (root == NULL || strcmp(root->ID, ID) == 0) {
        return root;
    }
    // 根据目标值选择查找方向
    if (strcmp(ID, root->ID) < 0) {
        return searchNode(root->left, ID);
    } else {
        return searchNode(root->right, ID);
    }
}

// 释放树的内存
void freeTree(BstNode* root) {
    if (root == NULL) {
        return;
    }
    freeTree(root->left);
    freeTree(root->right);
    free(root);
}

// 删除文件中的商品 ID
void deleteFromFile(BstNode** root, const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        perror("文件打开失败");
        exit(EXIT_FAILURE);
    }

    char ID[33];
    int isFound;
    // 跳过表头
    while (fscanf(file, "%32s", ID) != EOF) {
        isFound = 0;
        *root = deleteBST(*root, ID, &isFound);
        if (!isFound) {
            printf("%s 节点未找到，无法删除！\n", ID);
        }
    }

    fclose(file);
}

void exportToDOT(BstNode* root, FILE* file) {
    if (!root) return;

    fprintf(file, "    \"%s\" [label=\"%s\"];\n", root->ID, root->ID);

    if (root->left) {
        fprintf(file, "    \"%s\" -> \"%s\";\n", root->ID, root->left->ID);
        exportToDOT(root->left, file);
    }
    if (root->right) {
        fprintf(file, "    \"%s\" -> \"%s\";\n", root->ID, root->right->ID);
        exportToDOT(root->right, file);
    }
}

void generateGraph(BstNode* root) {
    FILE* file = fopen("bst_graph.dot", "w");
    if (!file) {
        perror("无法创建 DOT 文件");
        return;
    }

    fprintf(file, "digraph BST {\n");
    fprintf(file, "    node [fontname=\"Arial\"];\n");

    // 导出节点和边
    exportToDOT(root, file);

    fprintf(file, "}\n");
    fclose(file);

    printf("DOT 文件生成成功！请使用 Graphviz 或其他工具打开 bst_graph.dot 文件。\n");
}

// 主函数
int main() {
    BstNode* root = NULL;

    // 从文件构建二叉查找树
    root = buildTreeFromFile("marketing_sample_10k_data.csv");

    int height = calculateHeight(root);
    printf("二叉查找树的高度: %d\n", height);

    // 计算平均查找长度
    int totalDepth = 0;
    int totalNodes = 0;
    calculateTotalDepth(root, 0, &totalDepth, &totalNodes);

    if (totalNodes > 0) {
        double averageSearchLength = (double)totalDepth / totalNodes;
        printf("二叉查找树的平均查找长度: %.3f\n", averageSearchLength);
    } else {
        printf("树为空，无法计算平均查找长度。\n");
    }

    inOrderTraversal(root, "中序遍历结果.txt");

    deleteFromFile(&root, "drop sample_1k_data.csv");

    inOrderTraversal(root, "中序遍历结果_删除后.txt");

    int height_2 = calculateHeight(root);
    printf("删除商品后，二叉平衡树的高度: %d\n", height_2);

    // 计算平均查找长度
    totalDepth = 0;
    totalNodes = 0;
    calculateTotalDepth(root, 0, &totalDepth, &totalNodes);

    if (totalNodes > 0) {
        double averageSearchLength = (double)totalDepth / totalNodes;
        printf("删除后的二叉查找树的平均查找长度: %.3f\n", averageSearchLength);
    } else {
        printf("树为空，无法计算平均查找长度。\n");
    }

    freeTree(root);
    // generateGraph(root);

    return 0;
}