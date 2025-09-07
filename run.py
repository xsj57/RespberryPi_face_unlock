#!/usr/bin/env python3
"""
人脸识别解锁系统 - 启动器
"""
import sys
import os

# 添加core目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    sys.exit(main())
