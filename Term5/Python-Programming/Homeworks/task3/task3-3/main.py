import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl
import os

# 设置中文字体
mpl.rcParams['font.family'] = 'STHeiti' 
mpl.rcParams['axes.unicode_minus'] = False 

# 1. 从 CSV 文件加载 IRIS 数据集
csv_path = os.path.join(os.path.dirname(__file__), 'data', 'iris.csv')
df = pd.read_csv(csv_path)

# 将列名转换为小写，并映射到标准特征名称
df.columns = df.columns.str.lower()
# 重命名列以匹配标准格式
df = df.rename(columns={
    'sepal.length': 'sepal_length',
    'sepal.width': 'sepal_width',
    'petal.length': 'petal_length',
    'petal.width': 'petal_width',
    'species': 'species_name'
})

# 2. 定义特征名称和物种信息
features = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
# 特征列名映射（用于从 DataFrame 中读取数据）
feature_columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
feature_map = {feat: col for feat, col in zip(features, feature_columns)}

species_names = df['species_name'].unique()
colors = ['tab:blue', 'tab:orange', 'tab:green'] # 对应 setosa, versicolor, virginica
species_map = {name: color for name, color in zip(species_names, colors)}

# 3. 创建 4x4 子图矩阵
fig, axes = plt.subplots(4, 4, figsize=(10, 10))
plt.subplots_adjust(hspace=0.1, wspace=0.1) # 减小子图间的间距

# 4. 循环绘制每个子图
for i, feature_y in enumerate(features): # y轴特征 (行)
    for j, feature_x in enumerate(features): # x轴特征 (列)
        ax = axes[i, j]
        
        # 4.1. 绘制散点图
        if i == j:
            # 主对角线：绘制 x=y 的散点图 (即特征自身与自身的散点图)
            # 保持与原图一致，绘制一条直线上的散点
            # 使用一个特征作为X和Y，并按物种着色
            feature_col = feature_map[feature_x]
            for k, species_name in enumerate(species_names):
                subset = df[df['species_name'] == species_name]
                ax.plot(subset[feature_col], subset[feature_col], 
                        'o', 
                        markersize=3, 
                        color=species_map[species_name],
                        label=species_name)
        else:
            # 非主对角线：绘制特征 feature_x vs feature_y 的散点图
            feature_x_col = feature_map[feature_x]
            feature_y_col = feature_map[feature_y]
            for k, species_name in enumerate(species_names):
                subset = df[df['species_name'] == species_name]
                ax.scatter(subset[feature_x_col], subset[feature_y_col], 
                           s=10, # 调整点的大小
                           color=species_map[species_name], 
                           label=species_name)
        
        # 4.2. 隐藏刻度标签
        if i < 3:
            ax.set_xticklabels([])
        if j > 0:
            ax.set_yticklabels([])
            
        # 4.3. 设置轴标签（仅在最外层设置）
        # X轴标签：只在最底行设置
        if i == 3:
            ax.set_xlabel(feature_x.split(' (cm)')[0].replace(' ', '.'), fontsize=10)
            ax.tick_params(axis='x', rotation=90)
        # Y轴标签：只在最左列设置
        if j == 0:
            ax.set_ylabel(feature_y.split(' (cm)')[0].replace(' ', '.'), fontsize=10)
        
        # 4.4. 添加网格线
        ax.grid(True, linestyle='--', alpha=0.6)
        
# 5. 添加图例（仅在右上角子图添加）
# 提取一个子图的 handles 和 labels
handles, labels = axes[0, 1].get_legend_handles_labels()
# 在右上角的空白区域添加图例 (原图是在右侧空白区域)
fig.legend(handles, labels, 
           loc='center right', 
           title="物种", 
           bbox_to_anchor=(1.05, 0.5),
           fontsize=10)

# 6. 添加总标题
plt.suptitle('IRIS Dataset Pairwise Scatter Matrix', y=1.02, fontsize=16)
plt.tight_layout(rect=[0, 0, 1.0, 1]) # 调整布局，为图例留出空间

# 7. 保存图形
plt.savefig('iris_scatter_matrix.png', dpi=300, bbox_inches='tight')
print('图表已保存为 iris_scatter_matrix.png')

# 8. 显示图形
plt.show()
