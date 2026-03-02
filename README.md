# 博客系统后端 API

这是我做的第一个完整后端项目，核心目标是把“用户-文章-评论”这条链路跑通，同时把登录鉴权、权限控制、统一异常处理这些工程化能力一起练起来。

## 技术栈

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- MySQL（PyMySQL）
- JWT（PyJWT）
- Werkzeug（密码哈希）

## 已实现功能

- 用户：注册、登录、获取当前用户、修改密码
- 文章：发布、列表（分页 + 过滤 + 排序）、详情、更新、删除
- 评论：创建、列表、更新、删除
- 鉴权：JWT + `@login_required`
- 工程化：统一响应格式、统一异常处理、请求日志

## 项目结构

```text
blog_system/
├── app.py            # 主应用入口（路由、错误处理、初始化）
├── models.py         # User/Post/Comment 模型定义
├── auth.py           # JWT 生成/校验、登录装饰器
├── validators.py     # 输入参数校验
├── responses.py      # 统一响应
├── exceptions.py     # 自定义业务异常
├── logger.py         # 日志系统
├── config.py         # 配置项
├── requirements.txt  # 依赖
└── logs/             # 运行日志目录
```

## 快速启动

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 配置数据库

`config.py` 默认连接：

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root123@localhost:3306/blog_system"
```

按你的本机账号密码修改即可，也可以用 `DATABASE_URL` 覆盖。

### 3) 启动项目

```bash
python app.py
```

启动后默认地址：

```text
http://127.0.0.1:5000
```

## 鉴权说明

需要登录的接口，在请求头携带：

```text
Authorization: Bearer <token>
```

Token 通过 `POST /api/users/login` 获取。

## 主要接口

| 方法 | 路径 | 说明 | 需登录 |
|---|---|---|---|
| GET | `/api/health` | 健康检查 | 否 |
| POST | `/api/users/register` | 用户注册 | 否 |
| POST | `/api/users/login` | 用户登录 | 否 |
| GET | `/api/users/all` | 用户列表 | 否 |
| GET | `/api/users/me` | 当前用户信息 | 是 |
| PUT | `/api/users/password` | 修改密码 | 是 |
| POST | `/api/posts` | 发布文章 | 是 |
| GET | `/api/posts` | 文章列表 | 否 |
| GET | `/api/posts/<post_id>` | 文章详情 | 否 |
| PUT | `/api/posts/<post_id>` | 更新文章（仅作者） | 是 |
| DELETE | `/api/posts/<post_id>` | 删除文章（仅作者） | 是 |
| POST | `/api/posts/<post_id>/comments` | 发表评论 | 是 |
| GET | `/api/posts/<post_id>/comments` | 评论列表 | 否 |
| PUT | `/api/posts/comments/<comment_id>` | 更新评论（仅作者） | 是 |
| DELETE | `/api/posts/comments/<comment_id>` | 删除评论（仅作者） | 是 |

## 统一响应格式

成功：

```json
{
  "message": "操作成功",
  "data": {}
}
```

失败：

```json
{
  "error": "错误信息",
  "detail": "可选错误详情"
}
```

## 数据模型

- `users`：用户信息
- `posts`：文章信息
- `comments`：评论信息

三张表通过外键串起来，覆盖了最常见的一对多关系练习场景。

## 日志

- 应用日志：`logs/app.log`
- 错误日志：`logs/error.log`
