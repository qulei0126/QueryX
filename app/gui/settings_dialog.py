#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置对话框
提供应用程序各种设置的配置界面
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable

from app.core.config import config_manager


class SqlFormatSettingsDialog(tk.Toplevel):
    """SQL格式化设置对话框"""
    
    def __init__(self, parent, on_save_callback: Optional[Callable] = None):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            on_save_callback: 保存设置后的回调函数
        """
        super().__init__(parent)
        self.parent = parent
        self.on_save_callback = on_save_callback
        
        # 设置对话框属性
        self.title("SQL格式化设置")
        self.resizable(False, False)
        self.grab_set()  # 模态对话框
        
        # 获取当前配置
        self.format_options = config_manager.get_sql_format_options()
        
        # 创建UI组件
        self._create_widgets()
        
        # 设置初始值
        self._set_initial_values()
        
        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """创建对话框组件"""
        # 主框架
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 关键字大小写
        ttk.Label(main_frame, text="关键字大小写:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keyword_case_var = tk.StringVar()
        keyword_combo = ttk.Combobox(main_frame, textvariable=self.keyword_case_var, width=15)
        keyword_combo['values'] = ('upper', 'lower', 'capitalize')
        keyword_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(main_frame, text="upper: 大写, lower: 小写, capitalize: 首字母大写").grid(row=0, column=2, sticky=tk.W, pady=5)
        
        # 标识符大小写
        ttk.Label(main_frame, text="标识符大小写:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.identifier_case_var = tk.StringVar()
        identifier_combo = ttk.Combobox(main_frame, textvariable=self.identifier_case_var, width=15)
        identifier_combo['values'] = ('upper', 'lower', 'capitalize')
        identifier_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(main_frame, text="upper: 大写, lower: 小写, capitalize: 首字母大写").grid(row=1, column=2, sticky=tk.W, pady=5)
        
        # 删除注释
        self.strip_comments_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="删除注释", variable=self.strip_comments_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 自动缩进
        self.reindent_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="自动缩进", variable=self.reindent_var).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 缩进宽度
        ttk.Label(main_frame, text="缩进宽度(空格数):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.indent_width_var = tk.IntVar()
        indent_spinbox = ttk.Spinbox(main_frame, from_=1, to=8, textvariable=self.indent_width_var, width=5)
        indent_spinbox.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 逗号位置
        self.comma_first_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="逗号放在行首", variable=self.comma_first_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 运算符周围加空格
        self.use_space_around_operators_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="运算符周围加空格", variable=self.use_space_around_operators_var).grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        # 保存按钮
        ttk.Button(btn_frame, text="保存", command=self._on_save).pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        ttk.Button(btn_frame, text="重置为默认", command=self._on_reset).pack(side=tk.LEFT, padx=5)
    
    def _set_initial_values(self):
        """设置控件初始值"""
        self.keyword_case_var.set(self.format_options.get("keyword_case", "upper"))
        self.identifier_case_var.set(self.format_options.get("identifier_case", "lower"))
        self.strip_comments_var.set(self.format_options.get("strip_comments", False))
        self.reindent_var.set(self.format_options.get("reindent", True))
        self.indent_width_var.set(self.format_options.get("indent_width", 4))
        self.comma_first_var.set(self.format_options.get("comma_first", False))
        self.use_space_around_operators_var.set(self.format_options.get("use_space_around_operators", True))
    
    def _on_save(self):
        """保存设置"""
        # 收集设置值
        options = {
            "keyword_case": self.keyword_case_var.get(),
            "identifier_case": self.identifier_case_var.get(),
            "strip_comments": self.strip_comments_var.get(),
            "reindent": self.reindent_var.get(),
            "indent_width": self.indent_width_var.get(),
            "comma_first": self.comma_first_var.get(),
            "use_space_around_operators": self.use_space_around_operators_var.get(),
        }
        
        # 更新配置
        for key, value in options.items():
            config_manager.set_config("sql_format", key, value)
        
        # 保存配置到文件
        config_manager.save_config()
        
        # 调用回调函数
        if self.on_save_callback:
            self.on_save_callback()
        
        # 关闭对话框
        self.destroy()
    
    def _on_reset(self):
        """重置为默认设置"""
        # 重置为默认设置
        default_options = config_manager.DEFAULT_CONFIG["sql_format"]
        
        # 更新UI
        self.keyword_case_var.set(default_options["keyword_case"])
        self.identifier_case_var.set(default_options["identifier_case"])
        self.strip_comments_var.set(default_options["strip_comments"])
        self.reindent_var.set(default_options["reindent"])
        self.indent_width_var.set(default_options["indent_width"])
        self.comma_first_var.set(default_options["comma_first"])
        self.use_space_around_operators_var.set(default_options["use_space_around_operators"]) 