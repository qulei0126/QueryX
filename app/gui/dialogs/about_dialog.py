#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
关于对话框模块
提供一个简洁的关于信息对话框
"""

import os
import webbrowser
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# 导入项目资源和路径处理函数
from app.resources import ICON_PATH, get_resource_path


class AboutDialog:
    """关于对话框类，提供应用信息显示"""

    def __init__(self, parent, title="关于", about_text=""):
        """
        初始化关于对话框
        
        Args:
            parent: 父窗口
            title: 对话框标题
            about_text: 关于文本内容
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
        self._create_widgets(about_text)
        
        # 设置窗口大小
        width, height = 500, 300
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.minsize(400, 250)
        
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
        
    def _create_widgets(self, about_text):
        """创建对话框控件"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        title_label = ttk.Label(main_frame, text="QueryX - SQL查询工具", font=title_font)
        title_label.pack(pady=(0, 10))
        
        # 创建文本区域
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建文本控件
        text_font = tkfont.Font(family="TkDefaultFont", size=10)
        self.text = tk.Text(text_frame, wrap=tk.WORD, font=text_font, padx=5, pady=5,
                           height=12, width=50)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 插入关于文本
        self.text.insert(tk.END, about_text)
        
        # 设置链接样式
        self.text.tag_configure("link", foreground="blue", underline=1)
        
        # 查找GitHub链接并添加样式和点击事件
        start_idx = "1.0"
        while True:
            github_pos = self.text.search("https://github.com", start_idx, tk.END)
            if not github_pos:
                break
                
            line_end = self.text.search("\n", github_pos, tk.END)
            if not line_end:
                line_end = tk.END
                
            # 为链接添加样式
            self.text.tag_add("link", github_pos, line_end)
            
            # 存储链接URL
            url = self.text.get(github_pos, line_end).strip()
            
            # 绑定点击事件
            self.text.tag_bind("link", "<Button-1>", lambda e, url=url: self._open_url(url))
            self.text.tag_bind("link", "<Enter>", lambda e: self.dialog.config(cursor="hand2"))
            self.text.tag_bind("link", "<Leave>", lambda e: self.dialog.config(cursor=""))
            
            start_idx = line_end
        
        self.text.config(state=tk.DISABLED)  # 设为只读
        
        # 创建底部按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 创建访问GitHub按钮
        self.github_button = ttk.Button(button_frame, text="访问GitHub", 
                                     command=lambda: self._open_url("https://github.com/qulei0126/QueryX"))
        self.github_button.pack(side=tk.LEFT, padx=5)
        
        # 创建关闭按钮
        self.close_button = ttk.Button(button_frame, text="关闭", 
                                     command=self.dialog.destroy)
        self.close_button.pack(side=tk.RIGHT, padx=5)
    
    def _open_url(self, url):
        """打开URL链接"""
        webbrowser.open_new_tab(url) 