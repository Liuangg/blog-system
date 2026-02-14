"""
博客系统后端 API - 主应用入口
"""
from flask import Flask, jsonify, request
from config import Config
from models import db, User, Post, Comment
from werkzeug.security import check_password_hash
from auth import login_required, get_current_user, generate_token
from validators import (
    validate_username, validate_email, validate_password,
    validate_post_title, validate_post_content, validate_comment_content
)
# ============================================================================
# Flask 应用初始化
# ============================================================================

def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册全局错误处理
    register_error_handlers(app)
    
    # 注册路由（后续会分离到 routes 模块）
    register_routes(app)
    
    return app


# ============================================================================
# 全局错误处理
# ============================================================================

def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(e):
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
    
    # ==================== 占位路由（后续会实现） ====================
    @app.route('/api/users/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体不能为空'}), 400
            
            # ---- 输入验证 ----
            valid, msg = validate_username(data.get('username', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            valid, msg = validate_email(data.get('email', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            valid, msg = validate_password(data.get('password', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            # ---- 唯一性检查 ----
            if User.query.filter_by(username=data['username'].strip()).first():
                return jsonify({'error': '用户名已被注册'}), 400
            
            if User.query.filter_by(email=data['email'].strip()).first():
                return jsonify({'error': '邮箱已被注册'}), 400
            
            # ---- 创建用户 ----
            new_user = User(
                username=data['username'].strip(),
                email=data['email'].strip()
            )
            new_user.set_password(data['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': '注册成功',
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'email': new_user.email
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'注册失败: {str(e)}'}), 500

    @app.route('/api/users/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体不能为空'}), 400
            
            # 支持邮箱或用户名登录
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            
            if not password:
                return jsonify({'error': '缺少必填字段: password'}), 400
            
            # 根据邮箱或用户名查找用户
            if email:
                user = User.query.filter_by(email=email).first()
            elif username:
                user = User.query.filter_by(username=username).first()
            else:
                return jsonify({'error': '请提供邮箱或用户名'}), 400
            
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            
            # 使用哈希密码验证
            if not user.check_password(password):
                return jsonify({'error': '密码不正确'}), 400
            
            # 生成 JWT Token
            token = generate_token(user.id)
            
            return jsonify({
                'message': '登录成功',
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'登录失败: {str(e)}'}), 500
    @app.route('/api/users/all', methods=['GET'])
    def get_all_users():
        try:
            users = User.query.all()
            return jsonify({
                'message': '获取用户成功',
                'count': len(users),
                'users': [user.to_dict() for user in users]
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取用户失败: {str(e)}'}), 500
    @app.route('/api/posts', methods=['POST'])
    @login_required
    def create_post():
        """创建文章 API（需要登录）"""
        try:
            current_user = get_current_user()
            
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体不能为空'}), 400
            
            # ---- 输入验证 ----
            valid, msg = validate_post_title(data.get('title', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            valid, msg = validate_post_content(data.get('content', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            # ---- 创建文章 ----
            new_post = Post(
                title=data['title'].strip(),
                content=data['content'].strip(),
                author_id=current_user.id
            )
            
            db.session.add(new_post)
            db.session.commit()
            
            return jsonify({
                'message': '创建文章成功',
                'post': new_post.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'创建文章失败: {str(e)}'}), 500
    @app.route('/api/posts/<int:post_id>', methods=['GET'])
    def get_post_detail(post_id):
        """获取文章详情（包含作者信息和评论）"""
        try:
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'error': '文章不存在'}), 404
            
            return jsonify({
                'message': '获取文章成功',
                'data': post.to_dict(include_author=True, include_comments=True)
            }), 200
        
        except Exception as e:
            return jsonify({'error': f'获取文章失败: {str(e)}'}), 500
    
    @app.route('/api/posts/<int:post_id>', methods=['PUT'])
    @login_required
    def update_post(post_id):
        """更新文章 API（需要登录，只能更新自己的文章）"""
        try:
            current_user = get_current_user()
            
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体不能为空'}), 400
            
            # ---- 输入验证 ----
            valid, msg = validate_post_title(data.get('title', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            valid, msg = validate_post_content(data.get('content', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            # ---- 查找文章 ----
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'error': '文章不存在'}), 404
            
            # ---- 权限验证 ----
            if post.author_id != current_user.id:
                return jsonify({'error': '无权修改此文章'}), 403
            
            # ---- 更新文章 ----
            post.title = data['title'].strip()
            post.content = data['content'].strip()
            db.session.commit()
            
            return jsonify({
                'message': '更新文章成功',
                'post': post.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'更新文章失败: {str(e)}'}), 500
    @app.route('/api/posts/<int:post_id>', methods=['DELETE'])
    @login_required
    def delete_post(post_id):
        """删除文章 API（需要登录，只能删除自己的文章）"""
        try:
            # 1. 获取当前登录用户
            current_user = get_current_user()
            
            # 2. 查找文章
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'error': '文章不存在'}), 404
            
            # 3. 验证权限：只能删除自己的文章
            if post.author_id != current_user.id:
                return jsonify({'error': '无权删除此文章'}), 403
            
            # 4. 删除文章
            db.session.delete(post)
            db.session.commit()
            
            return jsonify({
                'message': '删除文章成功'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'删除文章失败: {str(e)}'}), 500
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
            return jsonify({
                'message': '获取文章成功',
                'data': {
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
                }
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取文章失败: {str(e)}'}), 500
    @app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
    @login_required
    def create_comment(post_id):
        """创建评论 API（需要登录）"""
        try:
            current_user = get_current_user()
            
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体不能为空'}), 400
            
            # ---- 验证文章是否存在 ----
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'error': '文章不存在'}), 404
            
            # ---- 输入验证 ----
            valid, msg = validate_comment_content(data.get('content', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            # ---- 创建评论 ----
            comment = Comment(
                content=data['content'].strip(),
                author_id=current_user.id,
                post_id=post_id
            )
            
            db.session.add(comment)
            db.session.commit()
            
            return jsonify({
                'message': '创建评论成功',
                'comment': comment.to_dict(include_author=True)
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'创建评论失败: {str(e)}'}), 500

    @app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
    def get_comments_for_post(post_id):
        """获取文章的评论列表"""
        try:
            # 验证文章是否存在
            post = Post.query.get(post_id)
            if not post:
                return jsonify({'error': '文章不存在'}), 404
            
            comments = Comment.query.filter_by(post_id=post_id)\
                .order_by(Comment.created_at.desc()).all()
            
            return jsonify({
                'message': '获取评论成功',
                'data': {
                    'comments': [comment.to_dict(include_author=True) for comment in comments],
                    'count': len(comments),
                    'post_id': post_id
                }
            }), 200
        except Exception as e:
            return jsonify({'error': f'获取评论失败: {str(e)}'}), 500
    @app.route('/api/posts/comments/<int:comment_id>', methods=['PUT'])
    @login_required
    def update_comment(comment_id):
        """更新评论 API（需要登录，只能更新自己的评论）"""
        try:
            current_user = get_current_user()
            
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体不能为空'}), 400
            
            # ---- 输入验证 ----
            valid, msg = validate_comment_content(data.get('content', ''))
            if not valid:
                return jsonify({'error': msg}), 400
            
            # ---- 查找评论 ----
            comment = Comment.query.get(comment_id)
            if not comment:
                return jsonify({'error': '评论不存在'}), 404
            
            # ---- 权限验证 ----
            if comment.author_id != current_user.id:
                return jsonify({'error': '无权修改此评论'}), 403
            
            # ---- 更新评论 ----
            comment.content = data['content'].strip()
            db.session.commit()
            
            return jsonify({
                'message': '更新评论成功',
                'comment': comment.to_dict(include_author=True)
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'更新评论失败: {str(e)}'}), 500
    @app.route('/api/posts/comments/<int:comment_id>', methods=['DELETE'])
    @login_required
    def delete_comment(comment_id):
        """删除评论 API（需要登录，只能删除自己的评论）"""
        try:
            # 1. 获取当前登录用户
            current_user = get_current_user()
            
            # 2. 查找评论
            comment = Comment.query.get(comment_id)
            if not comment:
                return jsonify({'error': '评论不存在'}), 404
            
            # 3. 验证权限：只能删除自己的评论
            if comment.author_id != current_user.id:
                return jsonify({'error': '无权删除此评论'}), 403
            
            # 4. 删除评论
            db.session.delete(comment)
            db.session.commit()
            
            return jsonify({
                'message': '删除评论成功'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'删除评论失败: {str(e)}'}), 500
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
    print("   POST   /api/users/register   - 用户注册（开发中）")
    print("   POST   /api/users/login      - 用户登录（开发中）")
    print("\n🚀 服务运行在: http://127.0.0.1:5000")
    print("=" * 60)
    
    # 启动 Flask 应用
    app.run(debug=True, host='0.0.0.0', port=5000)
