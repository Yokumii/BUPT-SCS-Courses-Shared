#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os

# 步骤1：抽取2015年数据
print("=" * 80)
print("步骤1：抽取2015年数据")
print("=" * 80)

# 读取原始数据
df = pd.read_csv('data/BeijingPM20100101_20151231.csv')
print(f"原始数据集形状: {df.shape}")

# 抽取2015年数据
df_2015 = df[df['year'] == 2015].copy()
print(f"2015年数据形状: {df_2015.shape}")

# 保存2015年原始数据
os.makedirs('data/processed', exist_ok=True)
df_2015.to_csv('data/processed/Beijing_PM2.5_2015_raw.csv', index=False, encoding='utf-8-sig')
print(f"✓ 2015年原始数据已保存到: data/processed/Beijing_PM2.5_2015_raw.csv")

# 步骤2：分析空值情况
print("\n" + "=" * 80)
print("步骤2：分析2015年数据空值情况")
print("=" * 80)

null_counts = df_2015.isnull().sum()
null_counts = null_counts[null_counts > 0].sort_values(ascending=False)

print("\n空值统计：")
print("-" * 80)
for col, count in null_counts.items():
    percent = (count / len(df_2015)) * 100
    print(f"{col:20s}: {count:5d} 个空值 ({percent:5.2f}%)")

print(f"\n总计：{len(null_counts)} 列存在空值")

# 步骤3：实施空值处理
print("\n" + "=" * 80)
print("步骤3：执行空值处理")
print("=" * 80)

# 创建副本用于处理
df_processed = df_2015.copy()

# PM2.5相关列 - 线性插值
pm_columns = ['PM_Dongsi', 'PM_Dongsihuan', 'PM_Nongzhanguan', 'PM_US Post']
for col in pm_columns:
    if col in df_processed.columns:
        before = df_processed[col].isnull().sum()
        df_processed[col] = df_processed[col].interpolate(method='linear', limit_direction='both')
        after = df_processed[col].isnull().sum()
        print(f"✓ {col:20s}: {before} → {after} 个空值")

# 气象数据 - 线性插值
weather_columns = ['DEWP', 'TEMP', 'HUMI', 'PRES', 'Iws']
for col in weather_columns:
    if col in df_processed.columns:
        before = df_processed[col].isnull().sum()
        df_processed[col] = df_processed[col].interpolate(method='linear', limit_direction='both')
        after = df_processed[col].isnull().sum()
        print(f"✓ {col:20s}: {before} → {after} 个空值")

# 风向 - 前向填充
if 'cbwd' in df_processed.columns:
    before = df_processed['cbwd'].isnull().sum()
    df_processed['cbwd'] = df_processed['cbwd'].ffill()
    # 如果开头还有空值，用后向填充
    df_processed['cbwd'] = df_processed['cbwd'].bfill()
    after = df_processed['cbwd'].isnull().sum()
    print(f"✓ {'cbwd':20s}: {before} → {after} 个空值")

# 降水量 - 填充为0
precipitation_columns = ['precipitation', 'Iprec']
for col in precipitation_columns:
    if col in df_processed.columns:
        before = df_processed[col].isnull().sum()
        df_processed[col] = df_processed[col].fillna(0)
        after = df_processed[col].isnull().sum()
        print(f"✓ {col:20s}: {before} → {after} 个空值")

# 步骤4：验证处理结果
print("\n" + "=" * 80)
print("步骤4：验证处理结果")
print("=" * 80)

# 检查剩余空值
remaining_nulls = df_processed.isnull().sum()
remaining_nulls = remaining_nulls[remaining_nulls > 0]

if len(remaining_nulls) == 0:
    print("✓ 所有空值已成功处理")
else:
    print(f"⚠️ 仍有 {len(remaining_nulls)} 列存在空值：")
    print(remaining_nulls)

# 数据质量检查
print("\n数据质量检查：")
print("-" * 80)
print(f"处理后数据形状: {df_processed.shape}")
print(f"数据完整性: {(1 - df_processed.isnull().sum().sum() / (df_processed.shape[0] * df_processed.shape[1])) * 100:.2f}%")

# 步骤5：保存处理后的数据
print("\n" + "=" * 80)
print("步骤5：保存处理后的数据")
print("=" * 80)

# 保存处理后的数据
output_file = 'data/processed/Beijing_PM2.5_2015_processed.csv'
df_processed.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"✓ 处理后数据已保存到: {output_file}")
