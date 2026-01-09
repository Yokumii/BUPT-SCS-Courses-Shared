class Item:
    # 物品结构体
    def __init__(self, id, weight, value):
        self.id = id                  # 物品编号
        self.weight = weight          # 物品总重量
        self.value = value            # 物品价值
        self.ratio = value / weight   # 物品单位价值

def initialize_items(weights, values):
    """
    初始化物品列表函数
    输入: weights (重量列表), values (价值列表)
    输出: items_list (Item对象列表)
    """
    items_list = []
    if len(weights) != len(values):
        raise ValueError("Error: 重量和价值列表长度不一致")

    for i in range(len(weights)):
        # i + 1 作为物品 ID，从 1 开始编号
        items_list.append(Item(i + 1, weights[i], values[i]))
    
    return items_list

def knapsack(items, capacity):
    total_value = 0.0
    current_capacity = capacity
    solution = {}

    # 对原物品按照单位价值进行降序排序
    items.sort(key=lambda x: x.ratio, reverse=True)
    
    for item in items:
        if (item.weight < current_capacity):
            # 可以全部装入
            current_capacity -= item.weight
            total_value += item.value
            solution[item.id] = item.weight
        else:
            # 只能部分装入
            fraction = current_capacity / item.weight
            solution[item.id] = current_capacity
            current_capacity = 0
            total_value += (fraction * item.value)
            break
    return total_value, solution
            
if __name__ == "__main__":
    # 实验数据
    w = [10, 40, 55, 20]
    v = [20, 120, 55, 100]
    capacity = 100
    
    items_list = initialize_items(w, v)

    max_val, weight_distribution = knapsack(items_list, capacity)
    
    print(f"背包最大总价值: {max_val:.2f}")
    print("各物品放入重量:")
    for i in range(1, len(items_list) + 1):
        # 如果字典里没有该物品，说明没放，重量为0
        weight_taken = weight_distribution.get(i, 0)
        print(f"物品 {i}: {weight_taken} ")