"""
数据库初始化脚本
用于单独初始化数据库，不启动 Flask 服务
"""
from app import create_app, db
from models import User, Post, Comment

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("博客系统 - 数据库初始化")
        print("=" * 60)
        
        # 删除所有表（仅用于开发环境，生产环境不要使用）
        # 取消注释下面的行可以重置数据库
        # print("⚠️  警告：正在删除所有表...")
        db.drop_all()
        
        # 创建所有表
        print("\n📝 正在创建数据库表...")
        db.create_all()
        
        print("\n✅ 数据库表创建成功！")
        print("   ✓ users 表")
        print("   ✓ posts 表")
        print("   ✓ comments 表")
        
        # 验证表是否创建成功
        print("\n🔍 验证表结构...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'posts', 'comments']
        for table in expected_tables:
            if table in tables:
                print(f"   ✓ {table} 表存在")
            else:
                print(f"   ✗ {table} 表不存在")
        
        print("\n" + "=" * 60)
        print("数据库初始化完成！")
        print("=" * 60)

if __name__ == '__main__':
    init_database()
