"""
文件链接关系示例
这个文件展示了各个文件是如何链接在一起的
"""

# ============================================================================
# 模拟 config.py 的内容
# ============================================================================
print("=" * 60)
print("1. config.py 的内容（独立文件）")
print("=" * 60)

class Config:
    """配置文件 - 不依赖其他文件"""
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root123@localhost:3306/blog_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

print("✅ Config 类定义完成（独立，不导入其他文件）")
print()

# ============================================================================
# 模拟 models.py 的内容
# ============================================================================
print("=" * 60)
print("2. models.py 的内容")
print("=" * 60)

# 注意：这里只是模拟，实际需要导入 flask_sqlalchemy
print("from flask_sqlalchemy import SQLAlchemy")
print("db = SQLAlchemy()  # 创建 db 对象，但还没绑定到 Flask")
print()

class User:
    """用户模型 - 使用 db.Model"""
    def __init__(self):
        print("  User 类定义（使用 db.Model）")

class Post:
    """文章模型 - 使用 db.Model"""
    def __init__(self):
        print("  Post 类定义（使用 db.Model）")

print("✅ 模型类定义完成（使用 db 对象，但 db 还未初始化）")
print()

# ============================================================================
# 模拟 app.py 的内容
# ============================================================================
print("=" * 60)
print("3. app.py 的内容（主程序）")
print("=" * 60)

print("步骤1: 导入配置")
print("  from config import Config  # ← 导入 config.py")
print()

print("步骤2: 导入模型")
print("  from models import db, User, Post, Comment  # ← 导入 models.py")
print()

print("步骤3: 创建 Flask 应用")
print("  app = Flask(__name__)")
print()

print("步骤4: 加载配置")
print("  app.config.from_object(Config)  # ← 使用 config.py 的配置")
print()

print("步骤5: 初始化数据库（关键步骤！）")
print("  db.init_app(app)  # ← 将 models.py 中的 db 绑定到 Flask 应用")
print("  ✅ 现在 db 对象已经连接到 Flask 应用了！")
print()

print("步骤6: 注册路由")
print("  @app.route('/api/health')")
print("  def health_check(): ...")
print()

print("步骤7: 初始化数据库表")
print("  with app.app_context():")
print("      db.create_all()  # ← 创建所有在 models.py 中定义的表")
print()

# ============================================================================
# 模拟 init_db.py 的内容
# ============================================================================
print("=" * 60)
print("4. init_db.py 的内容（初始化脚本）")
print("=" * 60)

print("步骤1: 导入主程序")
print("  from app import create_app, db  # ← 导入 app.py")
print("  # 这会触发 app.py 的所有导入和初始化")
print()

print("步骤2: 导入模型类（确保模型被注册）")
print("  from models import User, Post, Comment  # ← 导入模型")
print("  # 虽然不直接使用，但导入后模型会被注册到 db")
print()

print("步骤3: 创建应用并初始化数据库")
print("  app = create_app()  # ← 这会执行 app.py 中的所有初始化")
print("  with app.app_context():")
print("      db.create_all()  # ← 创建表")
print()

# ============================================================================
# 完整的执行流程
# ============================================================================
print("=" * 60)
print("5. 完整执行流程（当你运行 python app.py 时）")
print("=" * 60)

steps = [
    ("1. Python 开始执行 app.py", ""),
    ("2. 导入 config.py", "  └─> 加载 Config 类"),
    ("3. 导入 models.py", "  └─> 创建 db 对象"),
    ("   ", "  └─> 定义 User, Post, Comment 类"),
    ("4. 执行 create_app()", "  ├─> 创建 Flask 应用"),
    ("   ", "  ├─> 加载配置（使用 Config）"),
    ("   ", "  ├─> 初始化数据库（db.init_app(app)）"),
    ("   ", "  └─> 注册路由"),
    ("5. 执行 init_db(app)", "  └─> 在应用上下文中创建表"),
    ("6. 启动 Flask 服务", "  └─> app.run(port=5000)"),
]

for step, detail in steps:
    print(step)
    if detail:
        print(detail)

print()
print("=" * 60)
print("关键链接点总结")
print("=" * 60)
print()
print("1. config.py → app.py")
print("   通过: from config import Config")
print()
print("2. models.py → app.py")
print("   通过: from models import db, User, Post, Comment")
print()
print("3. db 对象绑定")
print("   通过: db.init_app(app)  # 在 app.py 中执行")
print()
print("4. app.py → init_db.py")
print("   通过: from app import create_app, db")
print()
print("=" * 60)
