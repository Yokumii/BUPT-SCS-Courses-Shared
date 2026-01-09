import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib as mpl
import os

# 设置中文字体
mpl.rcParams['font.family'] = 'STHeiti' 
mpl.rcParams['axes.unicode_minus'] = False 

# 1. 从 Excel 文件加载数据
excel_path = os.path.join(os.path.dirname(__file__), 'data', '八年级期末考试成绩表.xlsx')
df = pd.read_excel(excel_path, sheet_name=0)

target_columns = [
    '语文分数', '数学分数', '英语分数', 
    '物理分数', '生物分数', '地理分数'
]

# 根据数据最大值（116）设置分段：每10分一个分段，从0到120
bins = np.arange(0, 121, 10)
# 自定义分段标签
bin_labels = [f'{i}-{i+9}' for i in range(0, 110, 10)] + ['110+'] 

# 2. 设置 2x3 子图布局
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten() 

# 3. 循环绘制每个子图
for i, col in enumerate(target_columns):
    ax = axes[i]
    
    # 绘制直方图
    counts, edges, patches = ax.hist(
        df[col], 
        bins=bins, 
        edgecolor='black', 
        alpha=0.7, 
        color='#1f77b4', # Matplotlib默认蓝色
        label='学生人数'
    )
    
    # 设置标题、坐标轴标签
    subject_name = col.replace('分数', '')
    ax.set_title(f'{subject_name}成绩分段统计 ({col})', fontsize=14)
    ax.set_xlabel('分数分段', fontsize=12)
    ax.set_ylabel('学生人数', fontsize=12)
    
    # 设置 X 轴刻度及标签
    ax.set_xticks(bins[:-1] + 5)
    ax.set_xticklabels(bin_labels, rotation=45, ha='right')
    
    # 设置 Y 轴刻度，确保从0开始
    max_count = counts.max()
    ax.set_ylim(0, max_count * 1.1)
    
    # 添加网格线和图例
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.legend(loc='upper right', fontsize=10)
    
    # 添加数据标签
    for rect in patches:
        height = rect.get_height()
        if height > 0:
            ax.text(rect.get_x() + rect.get_width() / 2., height + 0.5,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9)

# 4. 调整布局以防止重叠
plt.tight_layout()

# 5. 保存图形
plt.savefig('grade_histogram.png', dpi=300, bbox_inches='tight')
print('图表已保存为 grade_histogram.png')

# 6. 显示图形
plt.show()