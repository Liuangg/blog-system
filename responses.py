"""
统一响应工具模块

功能：
    1. 提供标准化的 API 响应格式
    2. 减少路由中的重复代码
    3. 确保所有接口返回一致的 JSON 结构

统一响应格式：
    成功: { "message": "...", "data": {...} }
    失败: { "error": "...", "detail": "..." }
"""
from flask import jsonify


def success(message, data=None, status_code=200):
    """
    返回成功响应
    
    参数:
        message:     成功提示信息
        data:        返回的数据（字典或列表）
        status_code: HTTP 状态码（默认 200）
    
    返回:
        Flask Response 对象
    
    使用示例:
        return success('获取文章成功', data={'post': post.to_dict()})
        return success('创建成功', data={'id': 1}, status_code=201)
    """
    response = {'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error(message, detail=None, status_code=400):
    """
    返回错误响应
    
    参数:
        message:     错误提示信息
        detail:      错误详情（可选）
        status_code: HTTP 状态码（默认 400）
    
    返回:
        Flask Response 对象
    
    使用示例:
        return error('文章不存在', status_code=404)
        return error('密码不正确', detail='请检查密码')
    """
    response = {'error': message}
    if detail:
        response['detail'] = detail
    return jsonify(response), status_code
