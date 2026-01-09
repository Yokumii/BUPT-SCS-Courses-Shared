# Labs of Database System Concepts

基于华为云的 GaussDB 数据库的实验仓库。

### 项目结构

```
Labs-of-DataBase-System-Concepts/
├── src/
│   ├── product_manager.py     # 交互式商品管理系统（菜单驱动）
│   ├── demo_crud.py           # 自动演示完整 CRUD 流程
│   └── test_gaussdb.py        # 数据库连接测试脚本
├── driver/
│   └── gaussdbjdbc.jar        # 华为 GaussDB JDBC 驱动
├── sql/
│   └── create_table.sql       # 实验二 数据库表的创建与维护
├── docs/
│   ├── lab-1/report-1.md      # 实验一 GaussDB 数据库创建与维护
│   ├── lab-2/report-2.md      # 实验二 数据库表的创建与维护
│   ├── lab-3/report-3.md      # 实验三 数据查询
│   ├── lab-4/report-4.md      # 实验四 创建与管理用户
│   ├── lab-5/report-5.md      # 实验五 索引与视图
│   ├── lab-6/report-6.md      # 实验六 创建和管理存储过程/触发器
│   └── lab-7/report-7.md      # 实验七 Python + JDBC GaussDB 应用
└── README.md                  # 本文件
```

---

## 实验七运行方法

### 前提条件

1. 已安装 Python 3.8+ 和 uv 包管理器
2. 已安装 Java JRE（用于运行 JDBC 驱动）
3. 数据库连接信息正确配置

### 方法一：运行自动演示脚本（推荐）

自动按顺序执行完整的 CRUD 操作流程（查询→插入→修改→删除）：

```bash
uv run python src/demo_crud.py
```

**预期输出**：
- ✓ Step 1: 初始化 JVM
- ✓ Step 2: 建立数据库连接
- ✓ Step 3: 执行 7 次操作（查询→插入→查询→修改→查询→删除→查询）
- ✓ Step 4: 释放资源

### 方法二：运行交互式菜单程序

提供用户友好的菜单界面，手动选择操作：

```bash
uv run python src/product_manager.py
```

**菜单选项**：
```
1. 查询所有商品
2. 根据 ID 查询商品
3. 插入新商品
4. 更新商品信息
5. 删除商品
0. 退出程序
```

---

## 常见问题

### Q1: 报错 "Class com.huawei.gaussdb.jdbc.Driver is not found"

**解决方案**：检查 `gaussdbjdbc.jar` 的路径是否正确。修改 `product_manager.py` 和 `demo_crud.py` 中的 `jar_path` 变量为绝对路径。

### Q2: 报错 "Cannot commit when autoCommit is enabled"

**解决方案**：程序已在连接后关闭自动提交模式（`conn.jconn.setAutoCommit(False)`）。如果仍报错，请检查代码版本。

### Q3: 格式化输出报错 "unsupported format string"

**解决方案**：程序已处理 Java 对象与 Python 类型的转换。如果自行修改代码，请确保将 `java.math.BigDecimal` 等对象转换为 Python 原生类型。

---

## License

See the [LICENSE](LICENSE) file for more details.