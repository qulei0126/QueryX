#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
查询历史记录面板
显示和管理SQL查询历史记录
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable

from app.utils.ui_helpers import scrollbar_autohide


class HistoryPanel(ttk.Frame):
    """查询历史记录面板，显示和管理SQL查询历史记录"""
    
    def __init__(self, parent, select_callback: Callable = None):
        """
        初始化历史记录面板
        
        Args:
            parent: 父容器
            select_callback: 选择历史记录的回调函数
        """
        super().__init__(parent)
        self.parent = parent
        self.select_callback = select_callback
        self.history_list = []  # 历史记录列表
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 状态栏 - 在方法开头创建，确保它始终在底部显示
        self.status_label = ttk.Label(self, text="共 0 条历史记录", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # 创建内容框架，将所有内容（除状态栏外）放入其中
        content_frame = ttk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建历史记录列表框
        self.history_listbox = tk.Listbox(
            content_frame,
            selectmode=tk.SINGLE,
            font=("Consolas", 9)
        )
        self.history_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.history_listbox, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscroll=scrollbar_autohide(scrollbar, 'pack'))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.history_listbox.bind("<Double-1>", self._on_history_select)
        
        # 底部按钮区域
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # 清空历史按钮
        self.clear_btn = ttk.Button(
            btn_frame,
            text="清空历史",
            command=self._on_clear_history
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 使用选中按钮
        self.use_btn = ttk.Button(
            btn_frame,
            text="使用选中",
            command=self._on_use_selected
        )
        self.use_btn.pack(side=tk.LEFT, padx=5)
    
    def _on_history_select(self, event):
        """双击选择历史记录"""
        # 获取选中的索引
        selected_idx = self.history_listbox.curselection()
        if not selected_idx:
            return
        
        # 获取选中的查询
        selected_query = self.history_list[selected_idx[0]]
        
        # 调用回调函数
        if self.select_callback:
            self.select_callback(selected_query)
    
    def _on_use_selected(self):
        """使用选中的历史记录"""
        # 获取选中的索引
        selected_idx = self.history_listbox.curselection()
        if not selected_idx:
            return
        
        # 获取选中的查询
        selected_query = self.history_list[selected_idx[0]]
        
        # 调用回调函数
        if self.select_callback:
            self.select_callback(selected_query)
    
    def _on_clear_history(self):
        """清空历史记录"""
        self.history_list.clear()
        self.history_listbox.delete(0, tk.END)
        # 更新状态栏
        self.status_label.config(text="共 0 条历史记录")
    
    def add_history(self, query: str):
        """
        添加查询历史记录
        
        Args:
            query: SQL查询语句
        """
        # 避免重复添加
        if query in self.history_list:
            # 如果已存在，先删除旧的
            idx = self.history_list.index(query)
            self.history_list.pop(idx)
            self.history_listbox.delete(idx)
        
        # 添加到列表头部
        self.history_list.insert(0, query)
        
        # 添加到列表框
        # 截断显示，保持可读性
        display_query = query.replace('\n', ' ').strip()
        if len(display_query) > 50:
            display_query = display_query[:47] + "..."
        
        self.history_listbox.insert(0, display_query)
        
        # 更新状态栏
        self.status_label.config(text=f"共 {len(self.history_list)} 条历史记录")
        
        # 限制历史记录数量
        if len(self.history_list) > 20:
            self.history_list.pop()
            self.history_listbox.delete(20)
    
    def set_history_list(self, history_list: List[str]):
        """
        设置历史记录列表
        
        Args:
            history_list: 历史记录列表
        """
        # 清空当前列表
        self.history_list.clear()
        self.history_listbox.delete(0, tk.END)
        
        # 添加新的历史记录
        for query in history_list:
            self.add_history(query)
        
        # 更新状态栏
        self.status_label.config(text=f"共 {len(self.history_list)} 条历史记录") 