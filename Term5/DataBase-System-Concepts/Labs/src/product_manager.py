#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GaussDB 商品管理系统
"""

import jaydebeapi
import jpype
import os
from datetime import datetime
from typing import Optional, List, Tuple
from dotenv import load_dotenv


class DBConnection:
    """数据库连接管理模块"""

    def __init__(self, jar_path: str, jdbc_url: str, user: str, password: str):
        """
        初始化数据库连接配置
        """
        self.jar_path = jar_path
        self.driver_class = "com.huawei.gaussdb.jdbc.Driver"
        self.jdbc_url = jdbc_url
        self.user = user
        self.password = password
        self.conn = None
        self.jvm_started = False

    def connect(self):
        """
        建立数据库连接
        """
        try:
            # Step 1: 启动 JVM
            if not jpype.isJVMStarted():
                print("【Step 1】初始化 JDBC 环境...")
                jpype.startJVM(
                    jpype.getDefaultJVMPath(),
                    "-ea",
                    f"-Djava.class.path={self.jar_path}",
                    "-Djava.util.logging.config.file=logging.properties"
                )
                self.jvm_started = True
                print("✓ JVM 启动成功")

            # Step 2: 建立连接
            print("【Step 2】建立数据库连接...")
            self.conn = jaydebeapi.connect(
                self.driver_class,
                self.jdbc_url,
                [self.user, self.password],
                self.jar_path
            )
            # 关闭自动提交模式，支持手动事务管理
            self.conn.jconn.setAutoCommit(False)
            print("✓ 数据库连接成功")
            return self.conn

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            raise

    def close(self):
        """
        关闭连接并释放资源
        """
        try:
            if self.conn:
                self.conn.close()
                print("✓ 数据库连接已关闭")

            if self.jvm_started and jpype.isJVMStarted():
                jpype.shutdownJVM()
                print("✓ JVM 已关闭")

        except Exception as e:
            print(f"⚠️  关闭连接时出现警告: {e}")


class ProductCRUD:
    """商品表 CRUD 操作模块"""

    def __init__(self, connection):
        """初始化 CRUD 操作类"""
        self.conn = connection

    def _create_cursor(self):
        """
        创建游标
        """
        return self.conn.cursor()

    def query_all_products(self) -> List[Tuple]:
        """
        查询所有商品
        """
        cursor = None
        try:
            cursor = self._create_cursor()

            # 执行查询
            sql = 'SELECT "product_id", "name", "description", "price", "stock", "category_id", "create_time", "update_time" FROM "商品基本信息表" ORDER BY "product_id"'
            cursor.execute(sql)

            # 获取所有结果
            results = cursor.fetchall()
            return results

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def query_product_by_id(self, product_id: int) -> Optional[Tuple]:
        """根据 ID 查询单个商品"""
        cursor = None
        try:
            cursor = self._create_cursor()

            sql = 'SELECT "product_id", "name", "description", "price", "stock", "category_id", "create_time", "update_time" FROM "商品基本信息表" WHERE "product_id" = ?'
            cursor.execute(sql, [product_id])

            result = cursor.fetchone()
            return result

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def create_product(self, name: str, description: str, price: float, stock: int, category_id: Optional[int] = None) -> bool:
        """
        插入新商品
        """
        cursor = None
        try:
            cursor = self._create_cursor()

            sql = '''INSERT INTO "商品基本信息表"
                     ("name", "description", "price", "stock", "category_id")
                     VALUES (?, ?, ?, ?, ?)'''

            cursor.execute(sql, [name, description, price, stock, category_id])
            self.conn.commit()

            print(f"✓ 插入成功！商品名称: {name}")
            return True

        except Exception as e:
            print(f"❌ 插入失败: {e}")
            self.conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def update_product(self, product_id: int, price: Optional[float] = None, stock: Optional[int] = None) -> bool:
        """
        更新商品信息
        """
        cursor = None
        try:
            cursor = self._create_cursor()

            # 动态构建 SQL
            updates = []
            params = []

            if price is not None:
                updates.append('"price" = ?')
                params.append(price)

            if stock is not None:
                updates.append('"stock" = ?')
                params.append(stock)

            if not updates:
                print("⚠️  没有需要更新的字段")
                return False

            # 添加 update_time 更新
            updates.append('"update_time" = NOW()')

            sql = f'UPDATE "商品基本信息表" SET {", ".join(updates)} WHERE "product_id" = ?'
            params.append(product_id)

            cursor.execute(sql, params)
            self.conn.commit()

            if cursor.rowcount > 0:
                print(f"✓ 更新成功！受影响行数: {cursor.rowcount}")
                return True
            else:
                print("⚠️  未找到该商品")
                return False

        except Exception as e:
            print(f"❌ 更新失败: {e}")
            self.conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def delete_product(self, product_id: int) -> bool:
        """
        删除商品
        """
        cursor = None
        try:
            cursor = self._create_cursor()

            sql = 'DELETE FROM "商品基本信息表" WHERE "product_id" = ?'
            cursor.execute(sql, [product_id])
            self.conn.commit()

            if cursor.rowcount > 0:
                print(f"✓ 删除成功！受影响行数: {cursor.rowcount}")
                return True
            else:
                print("⚠️  未找到该商品")
                return False

        except Exception as e:
            print(f"❌ 删除失败: {e}")
            self.conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()


class MainMenu:
    """用户交互主程序"""

    def __init__(self, product_crud: ProductCRUD):
        """初始化主菜单"""
        self.product_crud = product_crud

    def print_menu(self):
        """打印操作菜单"""
        print("\n" + "=" * 50)
        print("        GaussDB 商品管理系统 v1.0")
        print("=" * 50)
        print("1. 查询所有商品")
        print("2. 根据 ID 查询商品")
        print("3. 插入新商品")
        print("4. 更新商品信息")
        print("5. 删除商品")
        print("0. 退出程序")
        print("=" * 50)

    def print_products_table(self, products: List[Tuple]):
        """以表格形式打印商品列表"""
        if not products:
            print("\n📦 当前无商品记录\n")
            return

        print("\n【查询结果】")
        print("-" * 120)
        print(f"{'ID':<6} {'商品名称':<20} {'描述':<30} {'价格':<10} {'库存':<8} {'分类ID':<8} {'创建时间':<20}")
        print("-" * 120)

        for product in products:
            product_id, name, desc, price, stock, cat_id, create_time, _ = product

            # 所有字段都需要转换为 Python 原生类型避免 Java 对象格式化错误
            pid_str = str(product_id) if product_id else ""
            name_str = (str(name)[:19]) if name and len(str(name)) > 20 else (str(name) if name else "")
            desc_str = (str(desc)[:27] + "...") if desc and len(str(desc)) > 30 else (str(desc) if desc else "")
            cat_str = str(cat_id) if cat_id else "N/A"
            create_str = str(create_time)[:19] if create_time else ""

            # 转换 price 和 stock 为 Python 原生类型
            price_val = float(str(price)) if price else 0.0
            stock_val = int(str(stock)) if stock else 0

            print(f"{pid_str:<6} {name_str:<20} {desc_str:<30} {price_val:<10.2f} {stock_val:<8} {cat_str:<8} {create_str:<20}")

        print("-" * 120)
        print(f"共 {len(products)} 条记录\n")

    def handle_query_all(self):
        """处理查询所有商品"""
        print("\n【查询所有商品】")
        products = self.product_crud.query_all_products()
        self.print_products_table(products)

    def handle_query_by_id(self):
        """处理根据 ID 查询"""
        print("\n【根据 ID 查询商品】")
        try:
            product_id = int(input("请输入商品 ID: "))
            product = self.product_crud.query_product_by_id(product_id)

            if product:
                self.print_products_table([product])
            else:
                print("⚠️  未找到该商品\n")

        except ValueError:
            print("❌ 输入无效，请输入数字\n")

    def handle_create(self):
        """处理插入新商品"""
        print("\n【插入新商品】")
        try:
            name = input("商品名称: ").strip()
            description = input("商品描述: ").strip()
            price = float(input("价格: "))
            stock = int(input("库存: "))
            category_id_str = input("分类 ID (留空表示 NULL): ").strip()

            category_id = int(category_id_str) if category_id_str else None

            if not name:
                print("❌ 商品名称不能为空\n")
                return

            self.product_crud.create_product(name, description, price, stock, category_id)

        except ValueError:
            print("❌ 输入格式错误\n")

    def handle_update(self):
        """处理更新商品"""
        print("\n【更新商品信息】")
        try:
            product_id = int(input("请输入要更新的商品 ID: "))

            price_str = input("新价格（留空不改）: ").strip()
            stock_str = input("新库存（留空不改）: ").strip()

            price = float(price_str) if price_str else None
            stock = int(stock_str) if stock_str else None

            self.product_crud.update_product(product_id, price, stock)

        except ValueError:
            print("❌ 输入格式错误\n")

    def handle_delete(self):
        """处理删除商品"""
        print("\n【删除商品】")
        try:
            product_id = int(input("请输入要删除的商品 ID: "))

            # 先查询确认
            product = self.product_crud.query_product_by_id(product_id)
            if not product:
                print("⚠️  未找到该商品\n")
                return

            print(f"\n即将删除商品: {product[1]}")
            confirm = input("确认删除？(y/n): ").strip().lower()

            if confirm == 'y':
                self.product_crud.delete_product(product_id)
            else:
                print("✓ 已取消删除\n")

        except ValueError:
            print("❌ 输入格式错误\n")

    def run(self):
        """主循环"""
        while True:
            self.print_menu()

            try:
                choice = input("请输入操作编号: ").strip()

                if choice == '1':
                    self.handle_query_all()
                elif choice == '2':
                    self.handle_query_by_id()
                elif choice == '3':
                    self.handle_create()
                elif choice == '4':
                    self.handle_update()
                elif choice == '5':
                    self.handle_delete()
                elif choice == '0':
                    print("\n【程序退出】感谢使用！")
                    break
                else:
                    print("\n❌ 无效的选项，请重新输入\n")

            except KeyboardInterrupt:
                print("\n\n【程序中断】用户取消操作")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}\n")


def main():
    """
    主函数：完整的数据库访问流程
    """
    # === 加载环境变量 ===
    load_dotenv()

    # === 从环境变量读取配置信息 ===
    jar_path = os.getenv('GAUSSDB_JAR_PATH')
    host = os.getenv('GAUSSDB_HOST')
    port = os.getenv('GAUSSDB_PORT')
    database = os.getenv('GAUSSDB_DATABASE')
    user = os.getenv('GAUSSDB_USER')
    password = os.getenv('GAUSSDB_PASSWORD')

    # 构建 JDBC URL
    jdbc_url = f"jdbc:gaussdb://{host}:{port}/{database}"

    db_conn = None

    try:
        # Step 1 & 2: 初始化并连接数据库
        db_conn = DBConnection(jar_path, jdbc_url, user, password)
        connection = db_conn.connect()

        print("\n" + "=" * 50)
        print("【Step 3】开始执行数据库操作...")
        print("=" * 50)

        # Step 3: 创建 CRUD 操作对象并启动主菜单
        product_crud = ProductCRUD(connection)
        main_menu = MainMenu(product_crud)
        main_menu.run()

    except Exception as e:
        print(f"\n❌ 程序异常: {e}")

    finally:
        # Step 4: 清理资源
        print("\n" + "=" * 50)
        print("【Step 4】释放资源...")
        print("=" * 50)

        if db_conn:
            db_conn.close()


if __name__ == "__main__":
    main()
