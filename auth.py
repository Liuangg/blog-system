"""
认证工具模块 - JWT Token 生成和验证
"""
import jwt
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from models import User


def generate_token(user_id):
    """
    生成 JWT Token
    
    参数:
        user_id: 用户ID
        
    返回:
        str: JWT Token 字符串
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token 7天后过期
        'iat': datetime.utcnow()  # 签发时间
    }
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return token


def verify_token(token):
    """
    验证 JWT Token
    
    参数:
        token: JWT Token 字符串
        
    返回:
        dict: Token 载荷（包含 user_id），验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token 已过期
    except jwt.InvalidTokenError:
        return None  # Token 无效


def get_current_user():
    """
    从请求头中获取当前登录用户
    
    返回:
        User: 用户对象，未登录返回 None
    """
    # 从请求头获取 Token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    # 支持 "Bearer <token>" 格式
    try:
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
    except IndexError:
        return None
    
    # 验证 Token
    payload = verify_token(token)
    if not payload:
        return None
    
    # 获取用户
    user_id = payload.get('user_id')
    if not user_id:
        return None
    
    user = User.query.get(user_id)
    return user


def login_required(f):
    """
    登录验证装饰器
    
    使用示例:
        @app.route('/api/posts', methods=['POST'])
        @login_required
        def create_post():
            current_user = get_current_user()
            # ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取当前用户
        current_user = get_current_user()
        
        if not current_user:
            return jsonify({
                'error': '需要登录',
                'message': '请先登录后再进行操作'
            }), 401
        
        # 将当前用户传递给路由函数
        # 可以通过 request.current_user 访问
        request.current_user = current_user
        
        return f(*args, **kwargs)
    
    return decorated_function
