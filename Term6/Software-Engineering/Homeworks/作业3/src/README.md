# BUPT 智能充电桩调度计费系统

北京邮电大学 · 软件工程 · 2026 春季

## 技术栈

- 后端：FastAPI (Python) + SQLAlchemy + SQLite/MySQL
- 前端：React + TypeScript + Ant Design + Vite
- 架构：C/S 三层架构 + MVC + Strategy 模式

## 系统结构与软件工程思想

本系统采用 **C/S 三层架构 + MVC 分层思想 + Strategy 调度策略模式** 组织实现，目标是在课程项目规模内保持结构清晰、职责分明、便于扩展和测试。

### C/S 三层架构

系统整体分为客户端与服务器端：

- **客户端（Client）**：前端使用 React + TypeScript + Ant Design 实现，分为用户端与管理员端两个界面。用户端负责注册登录、提交充电请求、查看排队状态和详单；管理员端负责查看充电桩状态、管理充电桩、查看报表和切换调度策略。
- **服务器端（Server）**：后端使用 FastAPI 实现统一 API，集中处理用户管理、排队调度、充电桩管理、计费和报表生成等业务逻辑。
- **数据层（Database）**：通过 SQLAlchemy ORM 管理用户、充电请求、排队号、充电会话、充电桩状态和详单等持久化数据，可在 SQLite 与 MySQL 间切换。

这种结构体现了软件工程中的 **分层设计** 思想：前端只负责展示与交互，后端集中处理业务规则，数据库负责持久化，降低了界面、业务和数据之间的耦合。

### 后端 MVC 与 Repository 分层

后端按照类似 MVC 的方式组织：

- `routers/`：接口入口，对应 Controller 的边界层，负责接收 HTTP 请求、参数校验和返回响应。
- `services/`：业务逻辑层，负责实现充电请求、调度、充电桩控制、故障处理、计费和报表等核心流程。
- `models/`：领域实体层，描述用户、充电请求、排队号、充电会话、充电桩、账单等核心对象。
- `repositories/`：数据访问层，封装数据库查询与更新，避免业务逻辑直接依赖 SQL 细节。
- `schemas/`：接口数据结构层，使用 Pydantic 定义请求和响应模型。

这体现了 **高内聚、低耦合** 和 **关注点分离** 的思想：路由层不写复杂业务，业务层不直接暴露数据库细节，数据访问逻辑集中在 Repository 中，便于后续维护和替换存储方式。

### Strategy 调度策略模式

调度模块使用 Strategy 模式实现：

- `BaselinePolicy`：默认策略，选择“等待时间 + 自身充电时间”最短的充电桩。
- `MinSinglePolicy`：多空位场景下进行单次批量优化。
- `MinBatchPolicy`：满站场景下进行整体批量调度优化。

`Scheduler` 只依赖统一的调度策略接口，不直接绑定某一种具体算法。管理员通过 UC14 可以在运行时切换调度策略。这体现了 **开闭原则**：新增调度算法时，可以增加新的策略类，而不需要大幅修改调度器主体逻辑。

### 面向对象建模与用例驱动

系统功能围绕 14 个用例实现，从用户端的注册、登录、提交/修改/取消充电请求，到管理员端的充电桩管理、排队车辆查看、运营报表和策略切换，均与设计文档中的用例模型保持对应。

核心业务对象包括 `Customer`、`Administrator`、`ChargingRequest`、`QueueNumber`、`ChargingSession`、`ChargingPile`、`BillDetail` 等，体现了 **面向对象分析与设计** 的思想：先从业务领域抽象出对象和关系，再将其落实为后端模型、服务和接口。

### 可维护性与可扩展性

本系统在实现上重点体现以下软件工程原则：

- **单一职责原则**：认证、调度、充电桩管理、计费、报表分别由不同模块负责。
- **模块化设计**：前端按用户端/管理员端页面拆分，后端按 router/service/repository/model 拆分。
- **可扩展设计**：调度策略、数据库配置、充电桩数量、等候区容量等均可扩展或配置。
- **用例到代码的可追踪性**：README 和代码中的 API 与 UC01~UC14 一一对应，便于验收和说明。
- **异常流程建模**：支持取消充电、提前结束、充电桩故障、故障恢复等非正常流程，体现了对完整业务生命周期的考虑。

## 快速启动

### 后端

```bash
cd backend

# 安装依赖
python3 -m pip install -r requirements.txt

# 启动（默认使用 SQLite，无需安装数据库）
python3 -m uvicorn app.main:app --reload --port 8000
```

启动后访问 http://localhost:8000/docs 查看 Swagger API 文档。

默认账号：
- 管理员：admin / admin123
- 注册新用户后可作为普通客户使用

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

启动后访问 http://localhost:3000

### 切换 MySQL

编辑 `backend/.env`：
```
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/charging_station
```

## 系统功能 (14 个用例)

### 用户端 (Customer)
| 用例 | API | 功能 |
|------|-----|------|
| UC01 | POST /api/auth/register | 注册 |
| UC02 | POST /api/auth/login | 登录 |
| UC03 | POST /api/charging/submit | 提交充电请求 |
| UC04 | PUT /api/charging/modify-mode, modify-amount | 修改充电请求 |
| UC05 | POST /api/charging/cancel | 取消充电 |
| UC06 | GET /api/charging/queue-number | 查看排队号 |
| UC07 | GET /api/charging/waiting-count | 查看前车数 |
| UC08 | POST /api/pile/end-charging | 结束充电 |
| UC09 | GET /api/billing/bills | 查看充电详单 |

### 管理员端 (Administrator)
| 用例 | API | 功能 |
|------|-----|------|
| UC10 | POST /api/pile/toggle | 启动/关闭充电桩 |
| UC11 | GET /api/pile/status | 查看所有充电桩状态 |
| UC12 | GET /api/pile/queuing/{pile_id} | 查看排队车辆 |
| UC13 | GET /api/billing/report | 查看运营报表 |
| UC14 | PUT /api/pile/scheduling-policy | 切换调度策略 |

### 故障处理
| 功能 | API |
|------|-----|
| 上报故障 | POST /api/pile/fault/{pile_id} |
| 故障恢复 | POST /api/pile/recover/{pile_id} |

## 调度策略

| 模式 | 说明 |
|------|------|
| BASELINE | 默认策略，选 min(等待时间 + 自身充电时间) 的桩 |
| MIN_SINGLE | 多空位时批量叫号，min Σ(等待+充电) |
| MIN_BATCH | 全满时整批调度，不区分快慢充 |

## 计费规则

| 时段 | 时间 | 电价(元/度) |
|------|------|------------|
| 峰时 | 10:00-15:00, 18:00-21:00 | 1.0 |
| 平时 | 7:00-10:00, 15:00-18:00, 21:00-23:00 | 0.7 |
| 谷时 | 23:00-次日7:00 | 0.4 |
| 服务费 | 全时段 | 0.8 |

总费用 = (电价 × 充电度数) + (0.8 × 充电度数)

## 系统参数（可配置）

| 参数 | 默认值 |
|------|--------|
| 快充桩数 | 3 (30度/时) |
| 慢充桩数 | 2 (10度/时) |
| 等候区容量 | 6 |
| 充电桩队列长度 | 2 |

## 项目结构

```
backend/
  app/
    models/          # ORM 模型层 (Entity)
    schemas/         # Pydantic 请求/响应模型
    repositories/    # 数据访问层 (Repository)
    services/        # 业务逻辑层 (Controller/Service)
    strategies/      # 调度策略 (Strategy 模式)
    routers/         # API 路由层 (表示层接口)
    main.py          # 应用入口

frontend/
  src/
    api/             # API 调用封装
    pages/customer/  # 用户端页面
    pages/admin/     # 管理员端页面
```
