import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# 设置中文字体，确保图表中的中文正常显示
mpl.rcParams['font.family'] = 'STHeiti' 
mpl.rcParams['axes.unicode_minus'] = False

# 1. 准备数据
years = ['1953', '1964', '1982', '1990', '2000', '2010', '2020']
population = [58260, 69458, 100818, 113368, 126583, 133972, 141178]

# 2. 创建图表和坐标轴对象
fig, ax = plt.subplots(figsize=(10, 6))

# 3. 绘制柱状图
bars = ax.bar(years, population, color='#4682B4', label='全国人口数量') # 使用蓝色系的颜色

# 4. 添加标题
ax.set_title('历次普查全国人口\nNational Population from Population Censuses', 
             fontsize=16, 
             fontweight='bold', 
             color='#336699')

# 5. 添加坐标轴标签
ax.set_xlabel('年份 (years)', fontsize=12)
ax.set_ylabel('人口数量 (万人 10000 persons)', fontsize=12)

# 6. 添加数据标签
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2., height + 1000,
            f'{height}',
            ha='center', va='bottom', fontsize=10)

# 7. 设置Y轴刻度
max_pop = max(population)
ax.set_ylim(0, 160000)
ax.set_yticks(np.arange(0, 160001, 40000))

# 8. 添加图例
ax.legend(loc='upper left', fontsize=10)

# 9. 调整布局，防止标签重叠
plt.tight_layout()

# 10. 保存图形
plt.savefig('population_census.png', dpi=300, bbox_inches='tight')
print('图表已保存为 population_census.png')

# 11. 显示图形
plt.show()