"""
Day 20-21: 博客系统 - 单文件版本
所有代码都在一个文件里，适合学习和理解整体结构
"""

# ============================================================================
# 第一部分：导入库
# ============================================================================
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ============================================================================
# 第二部分：配置
# ============================================================================

class Config:
    """配置文件"""
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:root123@localhost:3306/blog_system'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = True
    
    # API 配置
    JSON_AS_ASCII = False  # 支持中文 JSON 响应

# ============================================================================
# 第三部分：数据库模型
# ============================================================================

# 创建 db 对象
db = SQLAlchemy()

# 用户模型
class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='邮箱')
    password = db.Column(db.String(100), nullable=False, comment='密码（实际应用中应加密）')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        """将用户对象转换为字典（用于 JSON 响应）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 文章模型
class Post(db.Model):
    """文章模型"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='文章标题')
    content = db.Column(db.Text, nullable=False, comment='文章内容')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='作者ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    def to_dict(self, include_author=False, include_comments=False):
        """将文章对象转换为字典（用于 JSON 响应）"""
        result = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 可选：包含作者信息
        if include_author and self.author:
            result['author'] = {
                'id': self.author.id,
                'username': self.author.username,
                'email': self.author.email
            }
        
        # 可选：包含评论列表
        if include_comments:
            result['comments'] = [comment.to_dict() for comment in self.comments]
            result['comments_count'] = len(self.comments)
        
        return result

# 评论模型
class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, comment='文章ID')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='评论者ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f'<Comment {self.id}>'
    
    def to_dict(self, include_author=False):
        """将评论对象转换为字典（用于 JSON 响应）"""
        result = {
            'id': self.id,
            'content': self.content,
            'post_id': self.post_id,
            'author_id': self.author_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 可选：包含作者信息
        if include_author and self.author:
            result['author'] = {
                'id': self.author.id,
                'username': self.author.username
            }
        
        return result

# ============================================================================
# 第四部分：Flask 应用
# ============================================================================

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册路由
    register_routes(app)
    
    return app

def register_routes(app):
    """注册路由"""
    
    # ==================== 健康检查 ====================
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'ok',
            'message': '博客系统 API 运行正常'
        }), 200
    
    # ==================== 占位路由（后续会实现） ====================
    @app.route('/api/users/register', methods=['POST'])
    def register():
        """用户注册（待实现）"""
        return jsonify({'message': '功能开发中...'}), 501
    
    @app.route('/api/users/login', methods=['POST'])
    def login():
        """用户登录（待实现）"""
        return jsonify({'message': '功能开发中...'}), 501

# ============================================================================
# 第五部分：数据库初始化
# ============================================================================

def init_db(app, force=False):
    """
    初始化数据库表
    
    参数:
        app: Flask 应用对象
        force: 是否强制重新创建（默认 False，只在表不存在时创建）
    """
    with app.app_context():
        from sqlalchemy import inspect
        
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        expected_tables = ['users', 'posts', 'comments']
        
        if force:
            # 强制模式：删除所有表后重新创建（仅用于开发环境）
            print("⚠️  强制模式：删除所有表...")
            db.drop_all()
            db.create_all()
            print("✅ 数据库表重新创建成功！")
        else:
            # 智能模式：只创建缺失的表
            missing_tables = [t for t in expected_tables if t not in existing_tables]
            
            if missing_tables:
                print(f"📝 发现缺失的表: {', '.join(missing_tables)}")
                db.create_all()  # 只创建缺失的表（幂等操作）
                print("✅ 数据库表创建成功！")
            else:
                print("✅ 所有表已存在，跳过创建")
        
        # 显示所有表的状态（重新检查，因为可能刚创建了表）
        final_tables = inspector.get_table_names()
        print("📊 当前数据库表：")
        for table in expected_tables:
            status = "✓" if table in final_tables else "✗"
            print(f"   {status} {table}")

# ============================================================================
# 第六部分：主程序
# ============================================================================

if __name__ == '__main__':
    # 创建应用
    app = create_app()
    
    # 初始化数据库（智能检查，不会重复创建）
    print("=" * 60)
    print("博客系统后端 API - 初始化（单文件版本）")
    print("=" * 60)
    init_db(app)  # 只在表不存在时创建，不会重复创建或删除数据
    
    print("\n✅ API 服务启动中...")
    print("📝 可用接口：")
    print("   GET    /api/health           - 健康检查")
    print("   POST   /api/users/register   - 用户注册（开发中）")
    print("   POST   /api/users/login      - 用户登录（开发中）")
    print("\n🚀 服务运行在: http://127.0.0.1:5000")
    print("=" * 60)
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5000)
