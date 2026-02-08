"""
db 绑定机制示例
演示 db.init_app(app) 的绑定过程
"""

print("=" * 60)
print("db 绑定机制演示")
print("=" * 60)

print("\n【步骤1】在 models.py 中创建 db 对象")
print("-" * 60)
print("""
# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # ← 创建 db 对象
# 此时状态：
# ✅ db 对象已创建
# ❌ 还没有绑定到 Flask 应用
# ❌ 还不能连接数据库
""")

print("\n【步骤2】在 app.py 中绑定 db 到 Flask 应用")
print("-" * 60)
print("""
# app.py
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # ← 加载配置（包含数据库连接信息）
    
    db.init_app(app)  # ← 🔑 关键！绑定发生在这里
    # db.init_app(app) 做了什么：
    # 1. 从 app.config 读取 SQLALCHEMY_DATABASE_URI
    # 2. 根据配置创建数据库连接
    # 3. 将 db 对象与 Flask 应用关联
    # 4. 注册所有使用 db.Model 定义的模型
    
    return app
""")

print("\n【步骤3】绑定后的效果")
print("-" * 60)
print("""
绑定后，db 对象可以：

✅ 创建表
   db.create_all()

✅ 查询数据
   users = User.query.all()

✅ 保存数据
   new_user = User(username='test')
   db.session.add(new_user)
   db.session.commit()
""")

print("\n【问题】需要执行 init_db.py 吗？")
print("-" * 60)
print("""
答案：❌ 不需要！但可以选择使用。

两种方式：

方式1：使用 app.py（推荐）
  python app.py
  → 绑定 + 初始化 + 启动服务（一步到位）

方式2：使用 init_db.py（可选）
  python init_db.py
  → 绑定 + 初始化（不启动服务）
  → 适合生产环境：先初始化数据库，再启动服务
""")

print("\n【关键点】绑定发生在哪里？")
print("-" * 60)
print("""
绑定发生在 create_app() 函数中：

无论是：
  - app.py 中调用 create_app()
  - init_db.py 中调用 create_app()
  - 测试代码中调用 create_app()

只要调用 create_app()，绑定就会发生！
""")

print("\n【执行流程对比】")
print("-" * 60)

print("\n运行 python app.py：")
print("""
1. 导入 models.py → 创建 db 对象（未绑定）
2. 执行 create_app()
   └─> db.init_app(app)  ← 🔑 绑定发生在这里
3. 执行 init_db(app)
   └─> db.create_all()  ← 创建表（需要绑定后才能执行）
4. 启动 Flask 服务
""")

print("\n运行 python init_db.py：")
print("""
1. 导入 app.py → 触发 create_app()
   └─> db.init_app(app)  ← 🔑 绑定发生在这里
2. 执行 db.create_all()
   └─> 创建表（需要绑定后才能执行）
3. 退出（不启动服务）
""")

print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("""
1. ✅ 绑定发生在 create_app() 中（自动）
2. ✅ 不需要单独执行 init_db.py（但可以选择使用）
3. ✅ 绑定后才能使用数据库功能
4. ✅ 只要调用 create_app()，绑定就会发生
""")

print("\n" + "=" * 60)
