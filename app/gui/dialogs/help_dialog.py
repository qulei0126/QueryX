#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
帮助对话框模块
提供一个可滚动的帮助信息对话框
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# 导入项目资源和路径处理函数
from app.resources import ICON_PATH, get_resource_path


class HelpDialog:
    """帮助对话框类，提供可滚动的帮助信息显示"""

    def __init__(self, parent, title="使用帮助", help_text=""):
        """
        初始化帮助对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            help_text: 帮助文本内容
        """
        # 获取父窗口中心位置 - 直接使用屏幕中心计算，避免偏移
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        parent_x = screen_width // 2
        parent_y = screen_height // 2
        
        # 创建对话框窗口，但先不显示
        self.dialog = tk.Toplevel(parent)
        self.dialog.withdraw()  # 先隐藏窗口，避免闪烁
        self.dialog.title(title)
        
        # 设置对话框图标
        if os.path.exists(ICON_PATH):
            self.dialog.iconbitmap(ICON_PATH)
        
        # 设置为父窗口的临时窗口和模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建对话框内容
        self._create_widgets(help_text)
        
        # 设置窗口大小
        width, height = 800, 600
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.minsize(600, 400)
        
        # 计算居中位置 - 使用更直接的方法
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 确保窗口不会超出屏幕边界
        x = max(0, min(x, screen_width - width))
        y = max(0, min(y, screen_height - height))
        
        # 设置窗口位置
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # 强制更新几何信息，确保位置正确
        self.dialog.update()
        
        # 设置关闭按钮作为默认按钮
        self.close_button.focus_set()
        
        # 绑定Escape键关闭对话框
        self.dialog.bind("<Escape>", lambda event: self.dialog.destroy())
        
        # 最后再显示窗口
        self.dialog.deiconify()
        
    def _create_widgets(self, help_text):
        """创建对话框控件"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文本区域
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本控件
        text_font = tkfont.Font(family="TkDefaultFont", size=10)
        self.text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, 
                          font=text_font, padx=5, pady=5)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        scrollbar.config(command=self.text.yview)
        
        # 插入帮助文本
        self.text.insert(tk.END, help_text)
        self.text.config(state=tk.DISABLED)  # 设为只读
        
        # 创建底部按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 创建关闭按钮
        self.close_button = ttk.Button(button_frame, text="关闭", 
                                     command=self.dialog.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)
