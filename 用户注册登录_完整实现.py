"""
用户注册和登录的完整实现代码
可以直接复制到 Day20-21_单文件版本.py 中替换占位代码
"""

# ============================================================================
# 用户注册 API
# ============================================================================

@app.route('/api/users/register', methods=['POST'])
def register():
    """
    用户注册 API
    
    请求体（JSON）：
    {
        "username": "张三",
        "email": "zhangsan@example.com",
        "password": "123456"
    }
    
    响应：
    {
        "message": "注册成功",
        "user": {
            "id": 1,
            "username": "张三",
            "email": "zhangsan@example.com",
            "created_at": "2024-01-01T10:30:00",
            "updated_at": "2024-01-01T10:30:00"
        }
    }
    """
    try:
        # 1. 获取请求数据
        data = request.get_json()
        
        # 2. 验证必填字段
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        if not data.get('username'):
            return jsonify({'error': '缺少必填字段: username'}), 400
        
        if not data.get('email'):
            return jsonify({'error': '缺少必填字段: email'}), 400
        
        if not data.get('password'):
            return jsonify({'error': '缺少必填字段: password'}), 400
        
        # 3. 验证邮箱格式（简单验证）
        if '@' not in data['email']:
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 4. 检查邮箱是否已存在
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 5. 检查用户名是否已存在
        existing_username = User.query.filter_by(username=data['username']).first()
        if existing_username:
            return jsonify({'error': '用户名已被使用'}), 400
        
        # 6. 创建新用户
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password']  # 实际应用中应该使用加密
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # 7. 返回成功响应
        return jsonify({
            'message': '注册成功',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

# ============================================================================
# 用户登录 API
# ============================================================================

@app.route('/api/users/login', methods=['POST'])
def login():
    """
    用户登录 API
    
    请求体（JSON）：
    {
        "email": "zhangsan@example.com",
        "password": "123456"
    }
    
    响应：
    {
        "message": "登录成功",
        "user": {
            "id": 1,
            "username": "张三",
            "email": "zhangsan@example.com",
            "created_at": "2024-01-01T10:30:00",
            "updated_at": "2024-01-01T10:30:00"
        }
    }
    """
    try:
        # 1. 获取请求数据
        data = request.get_json()
        
        # 2. 验证必填字段
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        if not data.get('email'):
            return jsonify({'error': '缺少邮箱'}), 400
        
        if not data.get('password'):
            return jsonify({'error': '缺少密码'}), 400
        
        # 3. 查找用户
        user = User.query.filter_by(email=data['email']).first()
        
        # 4. 验证用户是否存在
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 5. 验证密码
        if user.password != data['password']:  # 实际应用中应该使用加密比较
            return jsonify({'error': '密码错误'}), 401
        
        # 6. 登录成功
        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500
