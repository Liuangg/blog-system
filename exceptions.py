"""
自定义异常模块

功能：
    1. 定义业务相关的异常类
    2. 配合全局错误处理器，自动返回标准化错误响应
    3. 让代码更清晰：用 raise 抛异常代替到处写 return error

使用方式：
    from exceptions import NotFoundError, ForbiddenError
    
    # 在路由中直接抛出异常
    raise NotFoundError('文章不存在')
    raise ForbiddenError('无权修改此文章')
    
    # 全局错误处理器会自动捕获并返回 JSON 响应
"""


class APIError(Exception):
    """
    API 错误基类
    
    所有自定义异常都继承自这个类
    """
    status_code = 400  # 默认 HTTP 状态码
    
    def __init__(self, message, detail=None):
        """
        参数:
            message: 错误提示信息（给前端看的）
            detail:  错误详情（可选，调试用）
        """
        super().__init__(message)
        self.message = message
        self.detail = detail
    
    def to_dict(self):
        """将异常转为字典（用于 JSON 响应）"""
        result = {'error': self.message}
        if self.detail:
            result['detail'] = self.detail
        return result


class BadRequestError(APIError):
    """400 - 请求参数错误"""
    status_code = 400


class UnauthorizedError(APIError):
    """401 - 未登录/Token无效"""
    status_code = 401


class ForbiddenError(APIError):
    """403 - 无权操作"""
    status_code = 403


class NotFoundError(APIError):
    """404 - 资源不存在"""
    status_code = 404


class ConflictError(APIError):
    """409 - 资源冲突（如用户名已存在）"""
    status_code = 409
