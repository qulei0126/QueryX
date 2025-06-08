#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
资源文件包
"""

import os
import sys

# 判断是否在PyInstaller环境中运行
def get_resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和PyInstaller打包环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 不在PyInstaller环境中，使用相对路径
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, "app", "resources", relative_path)

# 资源目录路径
RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))

# 图标文件路径（兼容PyInstaller）
ICON_PATH = get_resource_path("icon.ico")

# 导入帮助内容
from app.resources.help_content import HELP_TEXT, ABOUT_TEXT

__all__ = ['RESOURCES_DIR', 'ICON_PATH', 'HELP_TEXT', 'ABOUT_TEXT', 'get_resource_path'] 