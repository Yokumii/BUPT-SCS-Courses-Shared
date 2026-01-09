def knapsack(weights, values, capacity):
    n = len(weights)
    if n == 0 or capacity == 0:
        return 0
    
    # 初始化 DP 表
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    # 填充 DP 表
    for i in range(1, n + 1):
        w = weights[i-1] # 当前物品重量
        v = values[i-1]  # 当前物品价值
        
        for j in range(1, capacity + 1):
            if w > j:
                # 物品太重，放不进去
                dp[i][j] = dp[i-1][j]
            else:
                # 在放与不放之间取最大值
                dp[i][j] = max(dp[i-1][j], dp[i-1][j-w] + v)

    # 回溯求出解向量
    x = []
    w_idx, c_idx = n, capacity
    while w_idx > 0 and c_idx > 0:
        if dp[w_idx][c_idx] != dp[w_idx-1][c_idx]:
            item_index = w_idx - 1   # 选择了物品 w_idx - 1
            x.append(item_index)
            c_idx -= weights[item_index]
        w_idx -= 1
        
    return dp[n][capacity], x    

def knapsack_optimized(weights, values, capacity):
    n = len(weights)
    dp = [0] * (capacity + 1)

    for i in range(n):
        w = weights[i]
        v = values[i]
        
        # 逆序遍历
        for j in range(capacity, w - 1, -1):
            dp[j] = max(dp[j], dp[j - w] + v)

    return dp[capacity]

if __name__ == "__main__":
    # 题中示例
    weights = [10, 40, 55, 20]
    values = [20, 120, 55, 100]
    capacity = 100
    
    max_val, items = knapsack(weights, values, capacity)
    
    print(f"物品重量: {weights}")
    print(f"物品价值: {values}")
    print(f"背包容量: {capacity}")
    print(f"计算出的最大价值: {max_val}")
    print(f"选择的物品索引: {items}")

    max_val_2 = knapsack_optimized(weights, values, capacity)

    print(f"（空间优化版）计算出的最大价值: {max_val_2}")
