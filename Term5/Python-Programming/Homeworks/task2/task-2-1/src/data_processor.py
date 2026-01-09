# -*- coding: utf-8 -*-
"""
数据预处理和统计分析程序
"""

import pandas as pd
import os
from config import OUTPUT_FILE, PROCESSED_FILE


def process_data(input_file: str, output_file: str) -> pd.DataFrame:
    """
    对原始数据进行预处理

    Args:
        input_file: 原始数据文件路径
        output_file: 处理后数据文件路径

    Returns:
        处理后的DataFrame
    """
    print("\n开始数据预处理...")

    # 读取原始数据
    df = pd.read_csv(input_file)
    print(f"原始数据: {len(df)} 条记录")

    # 1. 去除所有字符串字段的前后空格
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].str.strip()

    # 2. 删除面积缺失的数据
    before_drop = len(df)
    df = df[df['面积'].notna() & (df['面积'] != '')]
    after_drop = len(df)
    dropped = before_drop - after_drop
    print(f"删除面积缺失的数据: {dropped} 条")

    # 3. 转换数据类型
    # 面积转为整数
    df['面积'] = pd.to_numeric(df['面积'], errors='coerce').astype('Int64')

    # 均价转为整数（元）
    df['均价'] = pd.to_numeric(df['均价'], errors='coerce').astype('Int64')

    # 总价转为整数（万元）
    df['总价'] = pd.to_numeric(df['总价'], errors='coerce').astype('Int64')

    print(f"预处理后数据: {len(df)} 条记录")

    # 保存处理后的数据
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✓ 处理后数据已保存到: {output_file}")

    return df


def analyze_statistics(df: pd.DataFrame):
    """
    进行统计分析

    Args:
        df: 处理后的DataFrame
    """
    print("\n" + "=" * 50)
    print("数据统计分析")
    print("=" * 50)

    # 过滤掉总价和均价为空的数据
    df_valid = df[df['总价'].notna() & df['均价'].notna()].copy()

    if len(df_valid) == 0:
        print("⚠️ 没有有效的价格数据")
        return

    # 总价统计
    print("\n【总价统计】")
    print("-" * 50)

    # 最贵的房子
    max_total_idx = df_valid['总价'].idxmax()
    max_total_row = df_valid.loc[max_total_idx]
    print(f"最贵的房子:")
    print(f"  名称: {max_total_row['名称']}")
    print(f"  位置: {max_total_row['地理位置-区']} - {max_total_row['地理位置-板块']}")
    print(f"  总价: {max_total_row['总价']} 万元")
    print(f"  均价: {max_total_row['均价']} 元/平")
    print(f"  面积: {max_total_row['面积']} 平米")

    # 最便宜的房子
    min_total_idx = df_valid['总价'].idxmin()
    min_total_row = df_valid.loc[min_total_idx]
    print(f"\n最便宜的房子:")
    print(f"  名称: {min_total_row['名称']}")
    print(f"  位置: {min_total_row['地理位置-区']} - {min_total_row['地理位置-板块']}")
    print(f"  总价: {min_total_row['总价']} 万元")
    print(f"  均价: {min_total_row['均价']} 元/平")
    print(f"  面积: {min_total_row['面积']} 平米")

    # 总价中位数
    median_total = df_valid['总价'].median()
    print(f"\n总价中位数: {median_total} 万元")

    # 均价统计
    print("\n【均价统计】")
    print("-" * 50)

    # 均价最贵的房子
    max_unit_idx = df_valid['均价'].idxmax()
    max_unit_row = df_valid.loc[max_unit_idx]
    print(f"均价最贵的房子:")
    print(f"  名称: {max_unit_row['名称']}")
    print(f"  位置: {max_unit_row['地理位置-区']} - {max_unit_row['地理位置-板块']}")
    print(f"  均价: {max_unit_row['均价']} 元/平")
    print(f"  总价: {max_unit_row['总价']} 万元")
    print(f"  面积: {max_unit_row['面积']} 平米")

    # 均价最便宜的房子
    min_unit_idx = df_valid['均价'].idxmin()
    min_unit_row = df_valid.loc[min_unit_idx]
    print(f"\n均价最便宜的房子:")
    print(f"  名称: {min_unit_row['名称']}")
    print(f"  位置: {min_unit_row['地理位置-区']} - {min_unit_row['地理位置-板块']}")
    print(f"  均价: {min_unit_row['均价']} 元/平")
    print(f"  总价: {min_unit_row['总价']} 万元")
    print(f"  面积: {min_unit_row['面积']} 平米")

    # 均价中位数
    median_unit = df_valid['均价'].median()
    print(f"\n均价中位数: {median_unit} 元/平")

    print("\n" + "=" * 50)


def main():
    """主函数"""
    if not os.path.exists(OUTPUT_FILE):
        print(f"错误: 原始数据文件不存在: {OUTPUT_FILE}")
        print("请先运行爬虫程序获取数据")
        return

    # 数据预处理
    df = process_data(OUTPUT_FILE, PROCESSED_FILE)

    # 统计分析
    analyze_statistics(df)


if __name__ == "__main__":
    main()
