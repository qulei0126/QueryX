#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI辅助函数
提供界面相关的实用函数
"""

from tkinter import ttk


def scrollbar_autohide(scrollbar, geometry_manager='pack'):
    """
    创建一个包装函数，用于自动隐藏/显示滚动条
    
    Args:
        scrollbar: 要控制的滚动条组件
        geometry_manager: 使用的几何管理器，可以是'pack'或'grid'
            
    Returns:
        滚动条设置函数，在滚动位置变化时自动判断是否需要显示滚动条
    """
    def set_scrollbar(*args):
        # 如果滚动范围小于等于1，则隐藏滚动条，否则显示
        if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
            scrollbar.pack_forget() if geometry_manager == 'pack' else scrollbar.grid_remove()
        else:
            if not scrollbar.winfo_ismapped():
                if geometry_manager == 'pack':
                    scrollbar.pack(side='right', fill='y')
                else:
                    scrollbar.grid()
        scrollbar.set(*args)  # 正常设置滚动条位置
    return set_scrollbar 