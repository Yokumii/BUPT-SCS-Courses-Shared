import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# 设置中文字体
mpl.rcParams['font.family'] = 'STHeiti' 
mpl.rcParams['axes.unicode_minus'] = False 

# 1. 准备数据 (所有八项支出)
categories = [
    '酒店旅游', '转账红包', '餐饮美食', '日用百货', 
    '交通出行', '充值缴费', '服饰装扮', '互助保障'
]
expenses = np.array([ # 使用 numpy array 方便后续操作
    21914.00, 19973.20, 10379.59, 9859.93, 
    8351.35, 2428.54, 950.83, 827.20
])

total_expense = expenses.sum()

# 2. 准备绘图参数
explode = [0.05] + [0] * 7 # 突出显示最大的支出项 (酒店旅游)

# 3. 创建图表和坐标轴对象
fig, ax = plt.subplots(figsize=(10, 8))

# 4. 绘制饼图
# autopct 仅显示百分比，保留一位小数
# 关键变化：labels=None，这样分类名称不会在图上重叠
wedges, texts, autotexts = ax.pie(
    expenses, 
    labels=None,  # 不在饼图上显示标签，避免重叠
    autopct='%1.1f%%', 
    startangle=90, 
    explode=explode, 
    shadow=True,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5} # 增加扇区分割线
)

# 5. 创建图例标签：包含分类名称和具体金额
legend_labels = [f'{cat} (¥{exp:.2f})' for cat, exp in zip(categories, expenses)]

# 6. 添加图例，放置在图表右侧
ax.legend(
    wedges, 
    legend_labels,
    title="支出分类 (金额)",
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1) # 放置在图表外部右侧
)

# 7. 调整百分比标签的样式，确保在较小的扇区也能看清
for text in autotexts:
    text.set_color('white')
    text.set_fontsize(8)
    text.set_fontweight('bold')

# 8. 添加标题
ax.set_title(f'2020年年度支出分类占比\n(总支出: ¥{total_expense:.2f})', 
             fontsize=16, 
             fontweight='bold')

# 9. 确保饼图是圆形
ax.axis('equal') 

# 10. 调整布局
plt.tight_layout()

# 11. 保存图形
plt.savefig('expense_pie_chart.png', dpi=300, bbox_inches='tight')
print('图表已保存为 expense_pie_chart.png')

# 12. 显示图形
plt.show()