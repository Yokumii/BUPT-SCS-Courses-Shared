#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import jaydebeapi
import jpype
import os
from datetime import datetime
from dotenv import load_dotenv


def demo_crud_operations():
    """演示数据库 CRUD 操作的完整流程"""
    # === 配置信息 ===
    # 从环境变量读取配置
    load_dotenv()

    # JAR 路径
    jar_path = os.getenv(
        'GAUSSDB_JAR_PATH',
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'driver', 'gaussdbjdbc.jar'))
    )

    driver_class = "com.huawei.gaussdb.jdbc.Driver"

    # JDBC URL
    jdbc_url = os.getenv('GAUSSDB_JDBC_URL')
    if not jdbc_url:
        host = os.getenv('GAUSSDB_HOST')
        port = os.getenv('GAUSSDB_PORT')
        database = os.getenv('GAUSSDB_DATABASE')
        if host and port and database:
            jdbc_url = f"jdbc:gaussdb://{host}:{port}/{database}"
        else:
            raise RuntimeError("数据库连接信息不完整：请设置 GAUSSDB_JDBC_URL 或 GAUSSDB_HOST/GAUSSDB_PORT/GAUSSDB_DATABASE")

    user = os.getenv('GAUSSDB_USER')
    password = os.getenv('GAUSSDB_PASSWORD')
    if not user or not password:
        raise RuntimeError("缺少数据库用户名或密码，请设置 GAUSSDB_USER 和 GAUSSDB_PASSWORD")

    conn = None

    try:
        # === Step 1: 初始化 JDBC 环境 ===
        print("\n" + "=" * 80)
        print("【Step 1】初始化 JDBC 环境")
        print("=" * 80)

        if not jpype.isJVMStarted():
            jpype.startJVM(
                jpype.getDefaultJVMPath(),
                "-ea",
                f"-Djava.class.path={jar_path}",
                "-Djava.util.logging.config.file=logging.properties"
            )
        print("✓ JVM 启动成功")

        # === Step 2: 建立数据库连接 ===
        print("\n" + "=" * 80)
        print("【Step 2】建立数据库连接")
        print("=" * 80)

        conn = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            [user, password],
            jar_path
        )
        print("✓ 数据库连接成功")

        # 关闭自动提交模式，支持手动事务管理
        conn.jconn.setAutoCommit(False)
        print("✓ 已切换为手动事务模式")

        # === Step 3: 执行 CRUD 操作 ===
        print("\n" + "=" * 80)
        print("【Step 3】执行数据库 CRUD 操作")
        print("=" * 80)

        # 3.1 第一次查询：打印所有记录
        print("\n[操作 1] 查询所有商品（初始状态）")
        print("-" * 80)
        query_all(conn)

        # 3.2 插入新商品
        print("\n[操作 2] 插入测试商品")
        print("-" * 80)
        test_product_name = f"测试商品_{datetime.now().strftime('%H%M%S')}"
        insert_product(conn, test_product_name, "这是一个测试商品", 999.99, 100, 1)

        # 3.3 第二次查询：验证插入
        print("\n[操作 3] 再次查询（验证插入成功）")
        print("-" * 80)
        query_all(conn)

        # 获取刚插入的商品 ID
        product_id = get_product_id_by_name(conn, test_product_name)

        if product_id:
            # 3.4 修改商品
            print(f"\n[操作 4] 修改商品 ID={product_id}（价格改为 1999.99，库存改为 50）")
            print("-" * 80)
            update_product(conn, product_id, 1999.99, 50)

            # 3.5 第三次查询：验证修改
            print("\n[操作 5] 再次查询（验证修改成功）")
            print("-" * 80)
            query_all(conn)

            # 3.6 删除商品
            print(f"\n[操作 6] 删除商品 ID={product_id}")
            print("-" * 80)
            delete_product(conn, product_id)

            # 3.7 第四次查询：验证删除
            print("\n[操作 7] 最终查询（验证删除成功）")
            print("-" * 80)
            query_all(conn)

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # === Step 4: 释放资源 ===
        print("\n" + "=" * 80)
        print("【Step 4】释放资源")
        print("=" * 80)

        if conn:
            conn.close()
            print("✓ 数据库连接已关闭")

        if jpype.isJVMStarted():
            jpype.shutdownJVM()
            print("✓ JVM 已关闭")

        print("\n" + "=" * 80)
        print("【演示完成】")
        print("=" * 80)


def query_all(conn):
    """查询所有商品"""
    cursor = None
    try:
        cursor = conn.cursor()
        sql = 'SELECT "product_id", "name", "description", "price", "stock", "category_id" FROM "商品基本信息表" ORDER BY "product_id"'
        cursor.execute(sql)

        results = cursor.fetchall()

        if not results:
            print("📦 当前无商品记录")
            return

        print(f"\n{'ID':<6} {'商品名称':<25} {'描述':<35} {'价格':<10} {'库存':<8} {'分类ID':<8}")
        print("-" * 100)

        for row in results:
            pid = row[0]
            name = str(row[1])[:24]
            desc = str(row[2])[:34] if row[2] else ""
            price = float(str(row[3]))
            stock = int(str(row[4]))
            cat = str(row[5]) if row[5] else "N/A"

            print(f"{pid:<6} {name:<25} {desc:<35} {price:<10.2f} {stock:<8} {cat:<8}")

        print("-" * 100)
        print(f"共 {len(results)} 条记录\n")

    finally:
        if cursor:
            cursor.close()


def insert_product(conn, name, desc, price, stock, category_id):
    """插入商品"""
    cursor = None
    try:
        cursor = conn.cursor()
        sql = '''INSERT INTO "商品基本信息表"
                 ("name", "description", "price", "stock", "category_id")
                 VALUES (?, ?, ?, ?, ?)'''

        cursor.execute(sql, [name, desc, price, stock, category_id])
        conn.commit()

        print(f"✓ 插入成功！商品名称: {name}, 价格: {price}, 库存: {stock}")

    except Exception as e:
        print(f"❌ 插入失败: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()


def get_product_id_by_name(conn, name):
    """根据名称获取商品 ID"""
    cursor = None
    try:
        cursor = conn.cursor()
        sql = 'SELECT "product_id" FROM "商品基本信息表" WHERE "name" = ?'
        cursor.execute(sql, [name])

        result = cursor.fetchone()
        return result[0] if result else None

    finally:
        if cursor:
            cursor.close()


def update_product(conn, product_id, price, stock):
    """更新商品"""
    cursor = None
    try:
        cursor = conn.cursor()
        sql = 'UPDATE "商品基本信息表" SET "price" = ?, "stock" = ?, "update_time" = NOW() WHERE "product_id" = ?'

        cursor.execute(sql, [price, stock, product_id])
        conn.commit()

        print(f"✓ 更新成功！商品 ID: {product_id}, 新价格: {price}, 新库存: {stock}")

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()


def delete_product(conn, product_id):
    """删除商品"""
    cursor = None
    try:
        cursor = conn.cursor()
        sql = 'DELETE FROM "商品基本信息表" WHERE "product_id" = ?'

        cursor.execute(sql, [product_id])
        conn.commit()

        if cursor.rowcount > 0:
            print(f"✓ 删除成功！商品 ID: {product_id}")
        else:
            print(f"⚠️  未找到商品 ID: {product_id}")

    except Exception as e:
        print(f"❌ 删除失败: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()


if __name__ == "__main__":
    demo_crud_operations()
