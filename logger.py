"""
日志工具模块

功能：
    1. 控制台输出彩色日志（开发时方便查看）
    2. 文件记录日志（生产环境持久化保存）
    3. 请求日志中间件（记录每次 API 调用）

日志级别（从低到高）：
    DEBUG < INFO < WARNING < ERROR < CRITICAL
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import request, g
import time


def setup_logger(app):
    """
    配置应用日志系统
    
    参数:
        app: Flask 应用对象
    """
    # ============ 1. 创建日志目录 ============
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # ============ 2. 定义日志格式 ============
    # 详细格式（用于文件）
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 简洁格式（用于控制台）
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # ============ 3. 文件日志处理器 ============
    # 普通日志文件（记录所有 INFO 及以上级别的日志）
    info_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 单个文件最大 10MB
        backupCount=5,               # 保留 5 个备份文件
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_formatter)
    
    # 错误日志文件（只记录 ERROR 及以上级别）
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # ============ 4. 控制台日志处理器 ============
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(console_formatter)
    
    # ============ 5. 配置 Flask 应用的 logger ============
    # 设置日志级别
    app.logger.setLevel(logging.DEBUG)
    
    # 清除默认处理器（避免重复输出）
    app.logger.handlers.clear()
    
    # 添加我们自定义的处理器
    app.logger.addHandler(info_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    
    app.logger.info('日志系统初始化完成')


def register_request_logging(app):
    """
    注册请求日志中间件
    
    功能：自动记录每次 API 请求的方法、路径、状态码、耗时
    
    参数:
        app: Flask 应用对象
    """
    
    @app.before_request
    def log_request_start():
        """请求开始前：记录开始时间"""
        g.start_time = time.time()
    
    @app.after_request
    def log_request_end(response):
        """请求结束后：记录请求详情"""
        # 计算耗时
        duration = time.time() - g.get('start_time', time.time())
        duration_ms = round(duration * 1000, 2)  # 转为毫秒
        
        # 获取请求信息
        method = request.method
        path = request.path
        status = response.status_code
        ip = request.remote_addr
        
        # 根据状态码决定日志级别
        if status >= 500:
            app.logger.error(
                f'{method} {path} - {status} - {duration_ms}ms - IP:{ip}'
            )
        elif status >= 400:
            app.logger.warning(
                f'{method} {path} - {status} - {duration_ms}ms - IP:{ip}'
            )
        else:
            app.logger.info(
                f'{method} {path} - {status} - {duration_ms}ms - IP:{ip}'
            )
        
        return response
