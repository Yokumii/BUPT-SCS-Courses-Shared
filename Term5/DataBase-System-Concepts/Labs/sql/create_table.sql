DROP TABLE IF EXISTS "商品分类基本信息表";
CREATE TABLE "商品分类基本信息表" (
  "category_id" SERIAL PRIMARY KEY,
  "name" VARCHAR(100) NOT NULL,
  "parent_id" INTEGER NULL,
  "create_time" TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS "用户基本信息表";
CREATE TABLE "用户基本信息表" (
  "user_id" SERIAL PRIMARY KEY,
  "username" VARCHAR(50) NOT NULL,
  "password" VARCHAR(255) NOT NULL,
  "email" VARCHAR(100) NOT NULL UNIQUE,
  "phone" VARCHAR(20) NULL,
  "age" INTEGER NULL,
  "gender" VARCHAR(10) NULL,
  "create_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  "update_time" TIMESTAMP NOT NULL DEFAULT NOW()
);

DROP TABLE IF EXISTS "商品基本信息表";
CREATE TABLE "商品基本信息表" (
  "product_id" SERIAL PRIMARY KEY,
  "name" VARCHAR(255) NOT NULL,
  "description" TEXT NULL,
  "price" DECIMAL(10, 2) NOT NULL,
  "stock" INTEGER NOT NULL DEFAULT 0,
  "category_id" INTEGER NULL,
  "create_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  "update_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT "fk_product_category" FOREIGN KEY ("category_id") REFERENCES "商品分类基本信息表" ("category_id") ON DELETE SET NULL ON UPDATE CASCADE
);


DROP TABLE IF EXISTS "地址基本信息表";
CREATE TABLE "地址基本信息表" (
  "address_id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "recipient_name" VARCHAR(100) NOT NULL,
  "phone" VARCHAR(20) NOT NULL,
  "address_line1" VARCHAR(255) NOT NULL,
  "address_line2" VARCHAR(255) NULL,
  "city" VARCHAR(100) NOT NULL,
  "state" VARCHAR(100) NOT NULL,
  "postal_code" VARCHAR(20) NOT NULL,
  "country" VARCHAR(100) NOT NULL,
  "is_default" BOOLEAN NOT NULL DEFAULT FALSE,
  "create_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT "fk_address_user" FOREIGN KEY ("user_id") REFERENCES "用户基本信息表" ("user_id") ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS "订单基本信息表";
CREATE TABLE "订单基本信息表" (
  "order_id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "total_amount" DECIMAL(10, 2) NOT NULL,
  "create_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  "update_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT "fk_order_user" FOREIGN KEY ("user_id") REFERENCES "用户基本信息表" ("user_id") ON DELETE CASCADE ON UPDATE CASCADE
);

DROP TABLE IF EXISTS "订单明细基本信息表";
CREATE TABLE "订单明细基本信息表" (
  "order_item_id" SERIAL PRIMARY KEY,
  "order_id" BIGINT NOT NULL,
  "product_id" INTEGER NOT NULL,
  "quantity" INTEGER NOT NULL,
  "price" DECIMAL(10, 2) NOT NULL,
  "create_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT "fk_item_order" FOREIGN KEY ("order_id") REFERENCES "订单基本信息表" ("order_id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_item_product" FOREIGN KEY ("product_id") REFERENCES "商品基本信息表" ("product_id") ON DELETE RESTRICT ON UPDATE CASCADE
);

DROP TABLE IF EXISTS "购物车基本信息表";
CREATE TABLE "购物车基本信息表" (
  "cart_id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "product_id" INTEGER NOT NULL,
  "quantity" INTEGER NOT NULL,
  "create_time" TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT "fk_cart_user" FOREIGN KEY ("user_id") REFERENCES "用户基本信息表" ("user_id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "fk_cart_product" FOREIGN KEY ("product_id") REFERENCES "商品基本信息表" ("product_id") ON DELETE CASCADE ON UPDATE CASCADE
);
