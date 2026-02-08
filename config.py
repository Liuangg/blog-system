"""
博客系统配置文件
"""
import os
from datetime import timedelta

class Config:
    """基础配置类"""
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
