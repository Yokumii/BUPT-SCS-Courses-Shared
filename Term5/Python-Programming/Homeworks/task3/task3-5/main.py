import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib as mpl
import os

# 设置中文字体
mpl.rcParams['font.family'] = 'STHeiti' 
mpl.rcParams['axes.unicode_minus'] = False 

# 1. 读取数据
csv_path = os.path.join(os.path.dirname(__file__), 'data', 'BeijingPM20100101_20151231.csv')
df = pd.read_csv(csv_path)

# 2. 按照 process_pm25.py 的逻辑处理缺失值
df_processed = df.copy()

# PM2.5相关列 - 线性插值
pm_columns = ['PM_Dongsi', 'PM_Dongsihuan', 'PM_Nongzhanguan', 'PM_US Post']
for col in pm_columns:
    if col in df_processed.columns:
        df_processed[col] = df_processed[col].interpolate(method='linear', limit_direction='both')

# 气象数据 - 线性插值
weather_columns = ['DEWP', 'TEMP', 'HUMI', 'PRES', 'Iws']
for col in weather_columns:
    if col in df_processed.columns:
        df_processed[col] = df_processed[col].interpolate(method='linear', limit_direction='both')

# 风向 - 前向填充
if 'cbwd' in df_processed.columns:
    df_processed['cbwd'] = df_processed['cbwd'].ffill()
    df_processed['cbwd'] = df_processed['cbwd'].bfill()

# 降水量 - 填充为0
precipitation_columns = ['precipitation', 'Iprec']
for col in precipitation_columns:
    if col in df_processed.columns:
        df_processed[col] = df_processed[col].fillna(0)

# 3. 选择四个PM2.5站点并求平均
# 使用四个站点：PM_Dongsi, PM_Dongsihuan, PM_Nongzhanguan, PM_US Post
selected_pm_columns = ['PM_Dongsi', 'PM_Dongsihuan', 'PM_Nongzhanguan', 'PM_US Post']
# 检查哪些列存在
available_pm_columns = [col for col in selected_pm_columns if col in df_processed.columns]

# 使用所有可用的PM2.5站点
pm_columns_to_use = available_pm_columns

# 计算四个站点的平均值
df_processed['PM_avg'] = df_processed[pm_columns_to_use].mean(axis=1)

# 4. 筛选 2010-2015 年数据并计算月平均值
df_filtered = df_processed[(df_processed['year'] >= 2010) & (df_processed['year'] <= 2015)].copy()
monthly_avg = df_filtered.groupby(['year', 'month'])['PM_avg'].mean().reset_index()

# 5. 数据重塑：将年份作为列，月份作为索引
pm_pivot = monthly_avg.pivot_table(
    index='month', 
    columns='year', 
    values='PM_avg'
)

# 6. 绘图
fig, ax = plt.subplots(figsize=(12, 7))

# 绘制每年的折线图
colors = plt.cm.viridis(np.linspace(0, 1, len(pm_pivot.columns)))
for i, year in enumerate(pm_pivot.columns):
    ax.plot(
        pm_pivot.index, 
        pm_pivot[year], 
        label=str(year), 
        marker='o', 
        linestyle='-',
        color=colors[i],
        linewidth=2,
        markersize=6
    )

# 7. 添加标题、坐标轴标签和图例
site_names = ', '.join(pm_columns_to_use)
ax.set_title('北京市2010-2015年PM2.5指数月平均数据变化', fontsize=16, fontweight='bold')
ax.set_xlabel('月份', fontsize=12)
ax.set_ylabel(f'PM2.5指数月平均值 (四个站点平均)', fontsize=12)

# 设置 X 轴刻度标签为 '1月', '2月' ...
ax.set_xticks(pm_pivot.index)
ax.set_xticklabels([f'{m}月' for m in pm_pivot.index])

# 添加网格线和图例
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend(title='年份', loc='upper right')

# 设置 Y 轴从 0 开始
ax.set_ylim(bottom=0)

# 8. 调整布局
plt.tight_layout()

# 9. 保存图形
plt.savefig('pm25_monthly_avg.png', dpi=300, bbox_inches='tight')
print(f'图表已保存为 pm25_monthly_avg.png')
print(f'使用的PM2.5站点: {", ".join(pm_columns_to_use)}')

# 10. 显示图形
plt.show()