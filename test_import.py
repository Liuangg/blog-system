"""
测试导入是否正常
运行这个文件来检查导入问题
"""
import sys
import os

print("=" * 60)
print("导入测试")
print("=" * 60)

print(f"\n当前工作目录: {os.getcwd()}")
print(f"Python 路径: {sys.path[:3]}")

print("\n" + "-" * 60)
print("测试 1: 导入 config")
print("-" * 60)
try:
    from config import Config
    print("✅ config 导入成功")
    print(f"   Config.SQLALCHEMY_DATABASE_URI = {Config.SQLALCHEMY_DATABASE_URI}")
except ImportError as e:
    print(f"❌ config 导入失败: {e}")
    print(f"   错误类型: {type(e).__name__}")
    print("\n💡 解决方法:")
    print("   1. 确保在 blog_system 目录下运行此文件")
    print("   2. 检查 config.py 文件是否存在")
    print("   3. 检查 config.py 中是否有 Config 类")

print("\n" + "-" * 60)
print("测试 2: 导入 models")
print("-" * 60)
try:
    from models import db, User, Post, Comment
    print("✅ models 导入成功")
    print(f"   db 对象: {db}")
    print(f"   User 类: {User}")
except ImportError as e:
    print(f"❌ models 导入失败: {e}")
    print(f"   错误类型: {type(e).__name__}")

print("\n" + "-" * 60)
print("测试 3: 导入 Flask")
print("-" * 60)
try:
    from flask import Flask, jsonify
    print("✅ Flask 导入成功")
except ImportError as e:
    print(f"❌ Flask 导入失败: {e}")
    print("   💡 解决方法: pip install flask")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
