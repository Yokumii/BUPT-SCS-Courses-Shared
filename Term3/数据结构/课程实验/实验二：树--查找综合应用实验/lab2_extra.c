#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct AVLNode {
    char ID[33];                    // 商品ID
    char Name[256];                 // 商品名称
    int inventory;                  // 商品库存
    int height;                     // 节点高度
    struct AVLNode* left;           // 左右子树指针
    struct AVLNode* right;
} AVLNode;

AVLNode* createNode(const char* ID, const char* Name, int inventory);
int height(AVLNode* node);
void updateHeight(AVLNode *node);
int balanceFactor(AVLNode *node);
AVLNode* rightRotate(AVLNode *node);
AVLNode* leftRotate(AVLNode *node);
AVLNode* Rotate(AVLNode *node);
void insert(AVLNode** root, const char* ID, const char* Name, int inventory);
AVLNode *insertHelper(AVLNode* node, const char* ID, const char* Name, int inventory);
void inOrderTraversal(AVLNode* root, const char* filename);
void freeTree(AVLNode* root);

// 定义栈节点
typedef struct StackNode {
    AVLNode* treeNode;      // 栈中存储的二叉树节点
    struct StackNode* next; // 指向下一个栈节点的指针
} StackNode;

StackNode* createStackNode(AVLNode* treeNode);
void push(StackNode** top, AVLNode* treeNode);
AVLNode* pop(StackNode** top);
int isEmpty(StackNode* top);

// 创建一个栈节点
StackNode* createStackNode(AVLNode* treeNode) {
    StackNode* newStackNode = (StackNode*)malloc(sizeof(StackNode));
    newStackNode->treeNode = treeNode;
    newStackNode->next = NULL;
    return newStackNode;
}

// 压栈
void push(StackNode** top, AVLNode* treeNode) {
    StackNode* newStackNode = createStackNode(treeNode);
    newStackNode->next = *top;
    *top = newStackNode;
}

// 出栈
AVLNode* pop(StackNode** top) {
    if (*top == NULL) {
        return NULL;
    }
    StackNode* temp = *top;
    AVLNode* treeNode = temp->treeNode;
    *top = (*top)->next;
    free(temp);
    return treeNode;
}

// 判断栈是否为空，若为空栈则返回 1
int isEmpty(StackNode* top) {
    return top == NULL;
}

// 创建新节点
AVLNode* createNode(const char* ID, const char* Name, int inventory) {
    AVLNode* node = (AVLNode*)malloc(sizeof(AVLNode));
    strcpy(node->ID, ID);
    strcpy(node->Name, Name);
    node->inventory = inventory;
    node->height = 0;
    node->left = node->right = NULL;
    return node;
}

// 获取节点高度
int height(AVLNode* node) {
    // 空节点高度为 -1 ，叶节点高度为 0
    if (node != NULL) {
        return node->height;
    }
    return -1;
}

// 更新节点高度
void updateHeight(AVLNode *node) {
    int lh = height(node->left);
    int rh = height(node->right);
    // 节点高度等于最高子树高度 + 1
    if (lh > rh) {
        node->height = lh + 1;
    } else {
        node->height = rh + 1;
    }
}

// 计算平衡因子
int balanceFactor(AVLNode *node) {
    // 空节点平衡因子为 0
    if (node == NULL) {
        return 0;
    }
    // 节点平衡因子 = 左子树高度 - 右子树高度
    return height(node->left) - height(node->right);
}

// 右旋操作
AVLNode *rightRotate(AVLNode *node) {
    AVLNode *child, *grandChild;
    child = node->left;
    grandChild = child->right;
    // 以 child 为原点，将 node 向右旋转
    child->right = node;
    node->left = grandChild;
    // 更新节点高度
    updateHeight(node);
    updateHeight(child);
    // 返回旋转后子树的根节点
    return child;
}

// 左旋操作
AVLNode* leftRotate(AVLNode *node) {
    AVLNode *child, *grandChild;
    child = node->right;
    grandChild = child->left;
    // 以 child 为原点，将 node 向左旋转
    child->left = node;
    node->right = grandChild;
    // 更新节点高度
    updateHeight(node);
    updateHeight(child);
    // 返回旋转后子树的根节点
    return child;
}

// 旋转操作，使该子树重新恢复平衡
AVLNode* Rotate(AVLNode *node) {
    // 获取节点 node 的平衡因子
    int bf = balanceFactor(node);
    // 左偏树
    if (bf > 1) {
        if (balanceFactor(node->left) >= 0) {
            // 右旋
            return rightRotate(node);
        } else {
            // 先左旋后右旋
            node->left = leftRotate(node->left);
            return rightRotate(node);
        }
    }
    // 右偏树
    if (bf < -1) {
        if (balanceFactor(node->right) <= 0) {
            // 左旋
            return leftRotate(node);
        } else {
            // 先右旋后左旋
            node->right = rightRotate(node->right);
            return leftRotate(node);
        }
    }
    // 平衡树，无须旋转，直接返回
    return node;
}

// 插入节点
void insertAVL(AVLNode** root, const char* ID, const char* Name, int inventory) {
    *root = insertHelper(*root, ID, Name, inventory);
}

// 递归插入节点（辅助函数)
AVLNode* insertHelper(AVLNode* node, const char* ID, const char* Name, int inventory) {
    if (node == NULL) {
        return createNode(ID, Name, inventory);
    }
    /* 1. 查找插入位置并插入节点 */
    if (strcmp(ID, node->ID) < 0) {
    node->left = insertHelper(node->left, ID, Name, inventory);
    } else if (strcmp(ID, node->ID) > 0) {
        node->right = insertHelper(node->right, ID, Name, inventory);
    } else {
        // 重复节点不插入，直接返回
        return node;
    }
    // 更新节点高度
    updateHeight(node);
    /* 2. 执行旋转操作，使该子树重新恢复平衡 */
    node = Rotate(node);
    // 返回子树的根节点
    return node;
}

// 释放 AVL 树
void freeTree(AVLNode* root) {
    if (!root) {
        return;
    }
    freeTree(root->left);
    freeTree(root->right);
    free(root);
}

// 从文件读取数据并构建 AVL 树
AVLNode* buildTreeFromFile(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        perror("文件打开失败");
        exit(EXIT_FAILURE);
    }

    AVLNode* root = NULL;
    char line[300];

    // 跳过表头
    fgets(line, sizeof(line), file);

    // 读取每一行数据
    while (fgets(line, sizeof(line), file)) {
        char ID[33];
        char Name[256];
        int inventory;

        sscanf(line, "%32[^,],%255[^,],%d", ID, Name, &inventory);
        insertAVL(&root, ID, Name, inventory);
    }

    fclose(file);
    return root;
}

// 非递归中序遍历
void inOrderTraversal(AVLNode* root, const char* filename) {
    StackNode* stack = NULL; // 初始化空栈
    AVLNode* cPtr = root;    // 初始指向根节点

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

void exportToDOT(AVLNode* root, FILE* file) {
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

void generateGraph(AVLNode* root) {
    FILE* file = fopen("avl_graph.dot", "w");
    if (!file) {
        perror("无法创建 DOT 文件");
        return;
    }

    fprintf(file, "digraph AVL {\n");
    fprintf(file, "    node [fontname=\"Arial\"];\n");

    // 导出节点和边
    exportToDOT(root, file);

    fprintf(file, "}\n");
    fclose(file);

    printf("DOT 文件生成成功！\n");
}

// 计算所有节点深度的总和和节点总数
void calculateTotalDepth(AVLNode* root, int depth, int* totalDepth, int* totalNodes) {
    if (root == NULL) {
        return;
    }

    // 从根节点开始遍历，根节点的深度为 0

    *totalDepth += depth; // 总查找长度 += 该节点的深度
    (*totalNodes)++; // 节点数量++

    calculateTotalDepth(root->left, depth + 1, totalDepth, totalNodes); // 递归左子树，其中左孩子的深度 = 该节点的深度 + 1
    calculateTotalDepth(root->right, depth + 1, totalDepth, totalNodes); // 递归左子树，其中右孩子的深度 = 该节点的深度 + 1
}

int main() {
    AVLNode* root = NULL;
    // 从文件加载数据并构建 AVL 树
    root = buildTreeFromFile("marketing_sample_10k_data.csv");

    // 打印 AVL 树高度
    printf("AVL树的高度: %d\n", height(root));
    printf("AVL树的高度 = %.2flogN\n", height(root) / (log2(10000)));
    inOrderTraversal(root, "中序遍历结果_AVL.txt");

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

    // generateGraph(root);
    // 释放内存
    freeTree(root);
    return 0;
}