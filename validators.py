"""
输入验证工具模块
"""
import re


def validate_username(username):
    """
    验证用户名
    
    规则：
    - 不能为空
    - 长度 2~50 字符
    - 只能包含字母、数字、下划线、中文
    
    返回:
        (bool, str): (是否合法, 错误信息)
    """
    if not username or not username.strip():
        return False, '用户名不能为空'
    
    username = username.strip()
    
    if len(username) < 2:
        return False, '用户名至少需要2个字符'
    
    if len(username) > 50:
        return False, '用户名不能超过50个字符'
    
    # 只允许字母、数字、下划线、中文
    if not re.match(r'^[\w\u4e00-\u9fff]+$', username):
        return False, '用户名只能包含字母、数字、下划线和中文'
    
    return True, ''


def validate_email(email):
    """
    验证邮箱格式
    
    返回:
        (bool, str): (是否合法, 错误信息)
    """
    if not email or not email.strip():
        return False, '邮箱不能为空'
    
    email = email.strip()
    
    if len(email) > 100:
        return False, '邮箱不能超过100个字符'
    
    # 简单但实用的邮箱正则验证
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, '邮箱格式不正确'
    
    return True, ''


def validate_password(password):
    """
    验证密码强度
    
    规则：
    - 不能为空
    - 长度 6~128 字符
    
    返回:
        (bool, str): (是否合法, 错误信息)
    """
    if not password:
        return False, '密码不能为空'
    
    if len(password) < 6:
        return False, '密码至少需要6个字符'
    
    if len(password) > 128:
        return False, '密码不能超过128个字符'
    
    return True, ''


def validate_post_title(title):
    """
    验证文章标题
    
    规则：
    - 不能为空
    - 长度 1~200 字符
    
    返回:
        (bool, str): (是否合法, 错误信息)
    """
    if not title or not title.strip():
        return False, '文章标题不能为空'
    
    title = title.strip()
    
    if len(title) > 200:
        return False, '文章标题不能超过200个字符'
    
    return True, ''


def validate_post_content(content):
    """
    验证文章内容
    
    规则：
    - 不能为空
    - 长度至少1个字符
    
    返回:
        (bool, str): (是否合法, 错误信息)
    """
    if not content or not content.strip():
        return False, '文章内容不能为空'
    
    return True, ''


def validate_comment_content(content):
    """
    验证评论内容
    
    规则：
    - 不能为空
    - 长度 1~1000 字符
    
    返回:
        (bool, str): (是否合法, 错误信息)
    """
    if not content or not content.strip():
        return False, '评论内容不能为空'
    
    if len(content.strip()) > 1000:
        return False, '评论内容不能超过1000个字符'
    
    return True, ''
