"""
博客系统后端 API - 主应用入口
"""
from flask import Flask, jsonify, request
from config import Config
from models import db, User, Post, Comment
from auth import login_required, get_current_user, generate_token
from validators import (
    validate_username, validate_email, validate_password,
    validate_post_title, validate_post_content, validate_comment_content
)
from responses import success, error
from exceptions import APIError, BadRequestError, NotFoundError, ForbiddenError, ConflictError
from logger import setup_logger, register_request_logging
# ============================================================================
# Flask 应用初始化
# ============================================================================

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化日志系统
    setup_logger(app)
    register_request_logging(app)
    
    # 注册全局错误处理
    register_error_handlers(app)
    
    # 注册路由
    register_routes(app)
    
    app.logger.info('Flask 应用初始化完成')
    
    return app


# ============================================================================
# 全局错误处理
# ============================================================================

def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(APIError)
    def handle_api_error(e):
        """处理自定义业务异常 —— 自动返回 JSON 响应"""
        app.logger.warning(f'业务异常: {e.message} (HTTP {e.status_code})')
        return jsonify(e.to_dict()), e.status_code
    
    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning(f'400 请求错误: {e}')
        return jsonify({'error': '请求格式错误', 'detail': str(e)}), 400
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': '请求的资源不存在', 'detail': str(e)}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': '请求方法不被允许', 'detail': str(e)}), 405
    
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()  # 出错时回滚数据库
        app.logger.error(f'500 服务器错误: {e}')
        return jsonify({'error': '服务器内部错误，请稍后重试'}), 500

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
    
    # ==================== 用户注册 ====================
    @app.route('/api/users/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.get_json()
            if not data:
                raise BadRequestError('请求体不能为空')
            
            # ---- 输入验证 ----
            valid, msg = validate_username(data.get('username', ''))
            if not valid:
                raise BadRequestError(msg)
            
            valid, msg = validate_email(data.get('email', ''))
            if not valid:
                raise BadRequestError(msg)
            
            valid, msg = validate_password(data.get('password', ''))
            if not valid:
                raise BadRequestError(msg)
            
            # ---- 唯一性检查 ----
            if User.query.filter_by(username=data['username'].strip()).first():
                raise ConflictError('用户名已被注册')
            
            if User.query.filter_by(email=data['email'].strip()).first():
                raise ConflictError('邮箱已被注册')
            
            # ---- 创建用户 ----
            new_user = User(
                username=data['username'].strip(),
                email=data['email'].strip()
            )
            new_user.set_password(data['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            app.logger.info(f'新用户注册: {new_user.username} (ID:{new_user.id})')
            
            return success('注册成功', data={
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'email': new_user.email
                }
            }, status_code=201)

        except APIError:
            raise  # 自定义异常交给全局处理器
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'注册失败: {str(e)}')
            return error(f'注册失败: {str(e)}', status_code=500)

    # ==================== 用户登录 ====================
    @app.route('/api/users/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.get_json()
            if not data:
                raise BadRequestError('请求体不能为空')
            
            # 支持邮箱或用户名登录
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            
            if not password:
                raise BadRequestError('缺少必填字段: password')
            
            # 根据邮箱或用户名查找用户
            if email:
                user = User.query.filter_by(email=email).first()
            elif username:
                user = User.query.filter_by(username=username).first()
            else:
                raise BadRequestError('请提供邮箱或用户名')
            
            if not user:
                raise NotFoundError('用户不存在')
            
            # 使用哈希密码验证
            if not user.check_password(password):
                raise BadRequestError('密码不正确')
            
            # 生成 JWT Token
            token = generate_token(user.id)
            
            app.logger.info(f'用户登录: {user.username} (ID:{user.id})')
            
            return success('登录成功', data={
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })

        except APIError:
            raise
        except Exception as e:
            app.logger.error(f'登录失败: {str(e)}')
            return error(f'登录失败: {str(e)}', status_code=500)
    # ==================== 获取所有用户 ====================
    @app.route('/api/users/all', methods=['GET'])
    def get_all_users():
        """获取所有用户"""
        try:
            users = User.query.all()
            return success('获取用户成功', data={
                'count': len(users),
                'users': [user.to_dict() for user in users]
            })
        except Exception as e:
            app.logger.error(f'获取用户失败: {str(e)}')
            return error(f'获取用户失败: {str(e)}', status_code=500)

    # ==================== 获取当前用户信息 ====================
    @app.route('/api/users/me', methods=['GET'])
    @login_required
    def get_me():
        """获取当前登录用户信息"""
        try:
            current_user = request.current_user
            
            return success('获取当前用户成功', data={
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'created_at': current_user.created_at.isoformat() if current_user.created_at else None
            })

        except APIError:
            raise
        except Exception as e:
            app.logger.error(f'获取当前用户失败: {str(e)}')
            return error(f'获取当前用户失败: {str(e)}', status_code=500)

    # ==================== 修改密码 ====================
    @app.route('/api/users/password', methods=['PUT'])
    @login_required
    def update_password():
        """修改当前用户密码"""
        try:
            # 获取当前用户
            current_user = request.current_user
            
            # 获取请求数据
            data = request.get_json()
            if not data:
                raise BadRequestError('请求体不能为空')
            
            # 获取新旧密码
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            # 验证字段是否提供
            if not old_password:
                raise BadRequestError('请输入原密码')
            if not new_password:
                raise BadRequestError('请输入新密码')
            
            # 验证原密码是否正确
            if not current_user.check_password(old_password):
                raise BadRequestError('原密码错误')
            
            # 新密码不能与原密码相同
            if old_password == new_password:
                raise BadRequestError('新密码不能与原密码相同')
            
            # 复用验证器检查新密码强度
            valid, msg = validate_password(new_password)
            if not valid:
                raise BadRequestError(msg)
            
            # 更新密码
            current_user.set_password(new_password)
            db.session.commit()
            
            app.logger.info(f'用户 {current_user.username} 修改密码成功')
            
            return success('密码修改成功')
        
        except APIError:
            raise
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'修改密码失败: {str(e)}')
            return error('修改密码失败，请稍后重试', status_code=500)
    # ==================== 创建文章 ====================
    @app.route('/api/posts', methods=['POST'])
    @login_required
    def create_post():
        """创建文章 API（需要登录）"""
        try:
            current_user = request.current_user
            
            data = request.get_json()
            if not data:
                raise BadRequestError('请求体不能为空')
            
            # ---- 输入验证 ----
            valid, msg = validate_post_title(data.get('title', ''))
            if not valid:
                raise BadRequestError(msg)
            
            valid, msg = validate_post_content(data.get('content', ''))
            if not valid:
                raise BadRequestError(msg)
            
            # ---- 创建文章 ----
            new_post = Post(
                title=data['title'].strip(),
                content=data['content'].strip(),
                author_id=current_user.id
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            app.logger.info(f'文章创建: "{new_post.title}" by {current_user.username}')
            
            return success('创建文章成功', data={
                'post': new_post.to_dict()
            }, status_code=201)
            
        except APIError:
            raise
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'创建文章失败: {str(e)}')
            return error(f'创建文章失败: {str(e)}', status_code=500)
    # ==================== 获取文章详情 ====================
    @app.route('/api/posts/<int:post_id>', methods=['GET'])
    def get_post_detail(post_id):
        """获取文章详情（包含作者信息和评论）"""
        try:
            post = db.session.get(Post, post_id)
            if not post:
                raise NotFoundError('文章不存在')
            
            return success('获取文章成功', data=post.to_dict(include_author=True, include_comments=True))
        
        except APIError:
            raise
        except Exception as e:
            app.logger.error(f'获取文章详情失败: {str(e)}')
            return error(f'获取文章失败: {str(e)}', status_code=500)
    
    # ==================== 更新文章 ====================
    @app.route('/api/posts/<int:post_id>', methods=['PUT'])
    @login_required
    def update_post(post_id):
        """更新文章 API（需要登录，只能更新自己的文章）"""
        try:
            current_user = request.current_user
            
            data = request.get_json()
            if not data:
                raise BadRequestError('请求体不能为空')
            
            # ---- 输入验证 ----
            valid, msg = validate_post_title(data.get('title', ''))
            if not valid:
                raise BadRequestError(msg)
            
            valid, msg = validate_post_content(data.get('content', ''))
            if not valid:
                raise BadRequestError(msg)
            
            # ---- 查找文章 ----
            post = db.session.get(Post, post_id)
            if not post:
                raise NotFoundError('文章不存在')
            
            # ---- 权限验证 ----
            if post.author_id != current_user.id:
                raise ForbiddenError('无权修改此文章')
            
            # ---- 更新文章 ----
            post.title = data['title'].strip()
            post.content = data['content'].strip()
            db.session.commit()
            
            app.logger.info(f'文章更新: "{post.title}" (ID:{post.id}) by {current_user.username}')
            
            return success('更新文章成功', data={
                'post': post.to_dict()
            })

        except APIError:
            raise
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'更新文章失败: {str(e)}')
            return error(f'更新文章失败: {str(e)}', status_code=500)
    # ==================== 删除文章 ====================
    @app.route('/api/posts/<int:post_id>', methods=['DELETE'])
    @login_required
    def delete_post(post_id):
        """删除文章 API（需要登录，只能删除自己的文章）"""
        try:
            current_user = request.current_user
            
            post = db.session.get(Post, post_id)
            if not post:
                raise NotFoundError('文章不存在')
            
            if post.author_id != current_user.id:
                raise ForbiddenError('无权删除此文章')
            
            post_title = post.title
            db.session.delete(post)
            db.session.commit()
            
            app.logger.info(f'文章删除: "{post_title}" (ID:{post_id}) by {current_user.username}')
            
            return success('删除文章成功')

        except APIError:
            raise
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'删除文章失败: {str(e)}')
            return error(f'删除文章失败: {str(e)}', status_code=500)
    @app.route('/api/posts', methods=['GET'])
    def get_posts():
        """
        获取文章列表（支持分页 + 过滤 + 排序）
        
        查询参数：
            page     - 页码（默认 1）
            per_page - 每页数量（默认 10，最大 100）
            keyword  - 搜索关键字（搜索标题和内容）
            author_id - 按作者ID过滤
            sort     - 排序字段（created_at / updated_at / title，默认 created_at）
            order    - 排序方向（desc 降序 / asc 升序，默认 desc）
        """
        try:
            # ============ 1. 获取分页参数 ============
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # 限制 per_page 范围，防止一次查太多
            if per_page > 100:
                per_page = 100
            if per_page < 1:
                per_page = 10
            
            # ============ 2. 构建查询 ============
            query = Post.query
            
            # ---- 过滤：按关键字搜索（标题或内容包含关键字） ----
            keyword = request.args.get('keyword', '').strip()
            if keyword:
                query = query.filter(
                    db.or_(
                        Post.title.contains(keyword),
                        Post.content.contains(keyword)
                    )
                )
            
            # ---- 过滤：按作者ID ----
            author_id = request.args.get('author_id', type=int)
            if author_id:
                query = query.filter(Post.author_id == author_id)
            
            # ============ 3. 排序 ============
            sort_field = request.args.get('sort', 'created_at')
            order = request.args.get('order', 'desc')
            
            # 允许的排序字段（防止注入）
            allowed_sort = {
                'created_at': Post.created_at,
                'updated_at': Post.updated_at,
                'title': Post.title
            }
            
            sort_column = allowed_sort.get(sort_field, Post.created_at)
            
            if order == 'asc':
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())
            
            # ============ 4. 执行分页查询 ============
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # ============ 5. 返回结果 ============
            return success('获取文章成功', data={
                'posts': [post.to_dict() for post in pagination.items],
                'pagination': {
                    'total': pagination.total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
                'filters': {
                    'keyword': keyword if keyword else None,
                    'author_id': author_id,
                    'sort': sort_field,
                    'order': order
                }
            })

        except Exception as e:
            app.logger.error(f'获取文章列表失败: {str(e)}')
            return error(f'获取文章失败: {str(e)}', status_code=500)
    # ==================== 创建评论 ====================
    @app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
    @login_required
    def create_comment(post_id):
        """创建评论 API（需要登录）"""
        try:
            current_user = request.current_user
            
            data = request.get_json()
            if not data:
                raise BadRequestError('请求体不能为空')
            
            post = db.session.get(Post, post_id)
            if not post:
                raise NotFoundError('文章不存在')
            
            valid, msg = validate_comment_content(data.get('content', ''))
            if not valid:
                raise BadRequestError(msg)
            
            comment = Comment(
                content=data['content'].strip(),
                author_id=current_user.id,
                post_id=post_id
            )
            
            db.session.add(comment)
            db.session.commit()
            
            app.logger.info(f'评论创建: 文章#{post_id} by {current_user.username}')
            
            return success('创建评论成功', data={
                'comment': comment.to_dict(include_author=True)
            }, status_code=201)

        except APIError:
            raise
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'创建评论失败: {str(e)}')
            return error(f'创建评论失败: {str(e)}', status_code=500)

    # ==================== 获取文章评论 ====================
    @app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
    def get_comments_for_post(post_id):
        """获取文章的评论列表"""
        try:
            post = db.session.get(Post, post_id)
            if not post:
                raise NotFoundError('文章不存在')
            
            comments = Comment.query.filter_by(post_id=post_id)\
                .order_by(Comment.created_at.desc()).all()
            
            return success('获取评论成功', data={
                'comments': [comment.to_dict(include_author=True) for comment in comments],
                'count': len(comments),
                'post_id': post_id
            })

        except APIError:
            raise
        except Exception as e:
            app.logger.error(f'获取评论失败: {str(e)}')
            return error(f'获取评论失败: {str(e)}', status_code=500)
    # ==================== 更新评论 ====================
    @app.route('/api/posts/comments/<int:comment_id>', methods=['PUT'])
    @login_required
    def update_comment(comment_id):
        """更新评论 API（需要登录，只能更新自己的评论）"""
        try:
            current_user = request.current_user
            
            data = request.get_json()
            if not data:
                raise BadRequestError('请求体不能为空')
            
            valid, msg = validate_comment_content(data.get('content', ''))
            if not valid:
                raise BadRequestError(msg)
            
            comment = db.session.get(Comment, comment_id)
            if not comment:
                raise NotFoundError('评论不存在')
            
            if comment.author_id != current_user.id:
                raise ForbiddenError('无权修改此评论')
            
            comment.content = data['content'].strip()
            db.session.commit()
            
            app.logger.info(f'评论更新: #{comment_id} by {current_user.username}')
            
            return success('更新评论成功', data={
                'comment': comment.to_dict(include_author=True)
            })

        except APIError:
            raise
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'更新评论失败: {str(e)}')
            return error(f'更新评论失败: {str(e)}', status_code=500)
    # ==================== 删除评论 ====================
    @app.route('/api/posts/comments/<int:comment_id>', methods=['DELETE'])
    @login_required
    def delete_comment(comment_id):
        """删除评论 API（需要登录，只能删除自己的评论）"""
        try:
            current_user = request.current_user
            
            comment = db.session.get(Comment, comment_id)
            if not comment:
                raise NotFoundError('评论不存在')
            
            if comment.author_id != current_user.id:
                raise ForbiddenError('无权删除此评论')
            
            db.session.delete(comment)
            db.session.commit()
            
            app.logger.info(f'评论删除: #{comment_id} by {current_user.username}')
            
            return success('删除评论成功')

        except APIError:
            raise
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'删除评论失败: {str(e)}')
            return error(f'删除评论失败: {str(e)}', status_code=500)
# ============================================================================
# 数据库初始化
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
# 主程序
# ============================================================================

if __name__ == '__main__':
    # 创建应用
    app = create_app()
    
    # 初始化数据库（智能检查，不会重复创建）
    print("=" * 60)
    print("博客系统后端 API - 初始化")
    print("=" * 60)
    init_db(app)  # 只在表不存在时创建，不会重复创建或删除数据
    
    print("\n✅ API 服务启动中...")
    print("📝 可用接口：")
    print("   GET    /api/health           - 健康检查")
    print("   POST   /api/users/register   - 用户注册")
    print("   POST   /api/users/login      - 用户登录")
    print("   GET    /api/users/all        - 获取所有用户")
    print("   GET    /api/users/me         - 获取当前用户信息（需登录）")
    print("   PUT    /api/users/password   - 修改密码（需登录）")
    print("   GET    /api/posts            - 获取文章列表（分页+过滤+排序）")
    print("   POST   /api/posts            - 创建文章（需登录）")
    print("   GET    /api/posts/<id>       - 获取文章详情")
    print("   PUT    /api/posts/<id>       - 更新文章（需登录）")
    print("   DELETE /api/posts/<id>       - 删除文章（需登录）")
    print("   POST   /api/posts/<id>/comments  - 创建评论（需登录）")
    print("   GET    /api/posts/<id>/comments  - 获取文章评论")
    print("   PUT    /api/posts/comments/<id>  - 更新评论（需登录）")
    print("   DELETE /api/posts/comments/<id>  - 删除评论（需登录）")
    print("\n📋 日志文件: logs/app.log, logs/error.log")
    print("\n🚀 服务运行在: http://127.0.0.1:5000")
    print("=" * 60)
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5000)
