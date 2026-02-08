# 博客系统后端 API

## 📋 项目概述

这是一个基于 Flask + SQLAlchemy 的博客系统后端 API 项目，提供用户管理、文章管理和评论管理功能。

## 🎯 项目需求分析

### 核心功能

1. **用户管理**
   - 用户注册
   - 用户登录
   - 用户信息查询
   - 用户信息更新

2. **文章管理**
   - 创建文章
   - 查看文章列表（支持分页）
   - 查看单篇文章详情
   - 更新文章
   - 删除文章

3. **评论管理**
   - 对文章添加评论
   - 查看文章的所有评论
   - 更新评论
   - 删除评论

### 技术栈

- **Web框架**: Flask
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **数据库**: MySQL
- **API风格**: RESTful API

## 📊 数据库设计

### 表结构

#### 1. users（用户表）
- `id`: 主键，自增
- `username`: 用户名，唯一，非空
- `email`: 邮箱，唯一，非空
- `password`: 密码，非空（实际应用中应加密）
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### 2. posts（文章表）
- `id`: 主键，自增
- `title`: 文章标题，非空
- `content`: 文章内容，非空
- `author_id`: 作者ID，外键关联users表
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### 3. comments（评论表）
- `id`: 主键，自增
- `content`: 评论内容，非空
- `post_id`: 文章ID，外键关联posts表
- `author_id`: 评论者ID，外键关联users表
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 关系说明

- **User 和 Post**: 一对多关系（一个用户可以有多篇文章）
- **Post 和 Comment**: 一对多关系（一篇文章可以有多个评论）
- **User 和 Comment**: 一对多关系（一个用户可以发表多个评论）

## 📁 项目结构

```
blog_system/
├── README.md                 # 项目说明文档
├── requirements.txt          # 依赖包列表
├── config.py                # 配置文件
├── app.py                   # 主应用入口
├── models.py                # 数据库模型
├── routes/                   # 路由模块
│   ├── __init__.py
│   ├── users.py             # 用户相关路由
│   ├── posts.py             # 文章相关路由
│   └── comments.py          # 评论相关路由
└── utils/                    # 工具函数
    ├── __init__.py
    └── validators.py        # 数据验证函数
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `config.py`，修改数据库连接信息。

### 3. 初始化数据库

```bash
python app.py
```

首次运行会自动创建数据库表。

### 4. 启动服务

```bash
python app.py
```

服务将在 `http://127.0.0.1:5000` 启动。

## 📝 API 接口列表

### 用户相关
- `POST /api/users/register` - 用户注册
- `POST /api/users/login` - 用户登录
- `GET /api/users/<id>` - 获取用户信息
- `PUT /api/users/<id>` - 更新用户信息

### 文章相关
- `POST /api/posts` - 创建文章
- `GET /api/posts` - 获取文章列表（支持分页）
- `GET /api/posts/<id>` - 获取文章详情
- `PUT /api/posts/<id>` - 更新文章
- `DELETE /api/posts/<id>` - 删除文章

### 评论相关
- `POST /api/posts/<post_id>/comments` - 添加评论
- `GET /api/posts/<post_id>/comments` - 获取文章的所有评论
- `PUT /api/comments/<id>` - 更新评论
- `DELETE /api/comments/<id>` - 删除评论

## 📅 开发计划

- **Day 20-21**: 项目规划 + 数据库设计 ✅
- **Day 22-24**: 核心功能开发
- **Day 25-26**: 项目完善 + Git 管理
