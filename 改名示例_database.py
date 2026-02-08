"""
改名示例：将 db 改成 database
这个文件展示了如何改名，但不会实际修改项目文件
"""

# ============================================================================
# 原始代码（使用 db）
# ============================================================================

print("=" * 60)
print("原始代码（使用 db）")
print("=" * 60)

print("""
# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # ← 使用 db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    posts = db.relationship('Post', backref='author')
""")

print("\n" + "=" * 60)
print("改名后（使用 database）")
print("=" * 60)

print("""
# models.py
from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()  # ← 改成 database

class User(database.Model):  # ← 改成 database
    id = database.Column(database.Integer, primary_key=True)  # ← 改成 database
    username = database.Column(database.String(50))  # ← 改成 database
    posts = database.relationship('Post', backref='author')  # ← 改成 database
""")

print("\n" + "=" * 60)
print("app.py 中的改动")
print("=" * 60)

print("""
# 原始代码
from models import db, User, Post, Comment
db.init_app(app)

# 改名后
from models import database, User, Post, Comment  # ← 改成 database
database.init_app(app)  # ← 改成 database
""")

print("\n" + "=" * 60)
print("关键点总结")
print("=" * 60)

points = [
    "1. 名字不固定，可以用任何合法的 Python 变量名",
    "2. 但必须保持一致性：所有地方用同一个名字",
    "3. 推荐使用 'db'，这是约定俗成的做法",
    "4. 改名需要修改所有使用该对象的地方",
]

for point in points:
    print(f"   {point}")

print("\n" + "=" * 60)
