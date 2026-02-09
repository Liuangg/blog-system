"""
博客系统数据库模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# 注意：db 对象需要在 app.py 中初始化
db = SQLAlchemy()

# ============================================================================
# 用户模型
# ============================================================================

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='邮箱')
    password = db.Column(db.String(500), nullable=False, comment='密码（已加密）')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系定义
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """
        设置密码（自动加密）
        
        参数:
            password: 明文密码
        """
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """
        验证密码是否正确
        
        参数:
            password: 待验证的明文密码
            
        返回:
            bool: 密码正确返回 True，否则返回 False
        """
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        """将用户对象转换为字典（用于 JSON 响应）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 文章模型
# ============================================================================

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

# ============================================================================
# 评论模型
# ============================================================================

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
