#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
表结构面板
显示可用表及其字段信息
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Callable, Optional

from app.utils.ui_helpers import scrollbar_autohide


class SchemaPanel(ttk.Frame):
    """表结构面板，显示可用表及其字段的树形结构"""
    
    def __init__(self, parent, on_table_select: Callable = None):
        """
        初始化表结构面板
        
        Args:
            parent: 父容器
            on_table_select: 选择表时的回调函数
        """
        super().__init__(parent)
        self.parent = parent
        self.on_table_select = on_table_select
        self.tables_info = {}  # {表名: [字段列表]}
        
        # 创建图标
        self._create_icons()
        
        self._create_widgets()
    
    def _create_icons(self):
        """创建表和字段图标"""
        try:
            # 使用更简单、更容易与文字对齐的图标
            self.table_icon = "■ "  # 方块图标，更容易与文字对齐
            
            # 字段图标也使用更容易对齐的图标
            self.col_icon = "○ "  # 圆形图标，容易与文字对齐
            
            # 保留这些变量但设为相同值，以防其他代码引用
            self.pk_icon = self.col_icon
            self.fk_icon = self.col_icon
            self.num_icon = self.col_icon
            self.date_icon = self.col_icon
        except:
            # 如果无法创建图标，使用文本替代
            self.table_icon = "[表] "
            self.col_icon = "[字段] "
            self.pk_icon = self.col_icon
            self.fk_icon = self.col_icon
            self.num_icon = self.col_icon
            self.date_icon = self.col_icon
    
    def _create_widgets(self):
        """创建界面组件"""
        # 状态栏 - 在方法开头创建，确保它始终在底部显示
        self.status_label = ttk.Label(self, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # 创建内容框架，将所有内容（除状态栏外）放入其中
        content_frame = ttk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建工具栏
        toolbar = ttk.Frame(content_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(
            toolbar,
            text="刷新",
            command=self._on_refresh
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 搜索框
        ttk.Label(toolbar, text="搜索:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # 创建树形结构
        self.tree_frame = ttk.Frame(content_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建树状视图
        self.schema_tree = ttk.Treeview(self.tree_frame, show="tree")
        
        # 滚动条
        yscrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.schema_tree.yview)
        self.schema_tree.configure(yscrollcommand=scrollbar_autohide(yscrollbar, 'pack'))
        
        # 放置组件
        self.schema_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定事件
        self.schema_tree.bind("<Double-1>", self._on_double_click)
        self.schema_tree.bind("<Button-3>", self._show_context_menu)
        
        # 创建右键菜单
        self._create_context_menu()
    
    def _create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="显示前10行", command=lambda: self._on_preview())
        self.context_menu.add_command(label="查询全表", command=lambda: self._on_query_all())
        self.context_menu.add_command(label="复制表名", command=lambda: self._on_copy_name("table"))
        self.context_menu.add_command(label="复制字段名", command=lambda: self._on_copy_name("column"))
    
    def _show_context_menu(self, event):
        """显示右键菜单"""
        # 获取点击的项目
        item = self.schema_tree.identify_row(event.y)
        if not item:
            return
        
        # 选中该项
        self.schema_tree.selection_set(item)
        
        # 根据选中项类型决定显示哪些菜单项
        item_type = self._get_item_type(item)
        
        # 更新菜单状态
        if item_type == "table":
            self.context_menu.entryconfig("显示前10行", state=tk.NORMAL)
            self.context_menu.entryconfig("查询全表", state=tk.NORMAL)
            self.context_menu.entryconfig("复制表名", state=tk.NORMAL)
            self.context_menu.entryconfig("复制字段名", state=tk.DISABLED)
        elif item_type == "column":
            self.context_menu.entryconfig("显示前10行", state=tk.DISABLED)
            self.context_menu.entryconfig("查询全表", state=tk.DISABLED)
            self.context_menu.entryconfig("复制表名", state=tk.DISABLED)
            self.context_menu.entryconfig("复制字段名", state=tk.NORMAL)
        else:
            return
            
        # 显示菜单
        self.context_menu.post(event.x_root, event.y_root)
    
    def _get_item_type(self, item):
        """获取树节点类型"""
        parent_item = self.schema_tree.parent(item)
        if parent_item == '':  # 根节点，表示表
            return "table"
        else:
            return "column"  # 子节点，表示列
    
    def _get_clean_text(self, item):
        """
        获取树节点文本，移除前缀图标
        
        Args:
            item: 树节点ID
            
        Returns:
            str: 清理后的节点文本
        """
        text = self.schema_tree.item(item, "text")
        
        # 移除所有可能的图标前缀
        icons = [self.table_icon, self.pk_icon, self.fk_icon, self.col_icon, self.num_icon, self.date_icon]
        for icon in icons:
            if text.startswith(icon):
                text = text[len(icon):]
                break
                
        return text
    
    def _on_double_click(self, event):
        """双击处理"""
        item = self.schema_tree.identify_row(event.y)
        if not item:
            return
            
        # 如果是表，则展开/折叠
        if self._get_item_type(item) == "table":
            if self.schema_tree.item(item, "open"):
                self.schema_tree.item(item, open=False)
            else:
                self.schema_tree.item(item, open=True)
        
        # 如果是字段，则插入字段名到查询编辑器
        else:
            column_name = self._get_clean_text(item)
            parent_item = self.schema_tree.parent(item)
            table_name = self._get_clean_text(parent_item)
            
            # 复制字段名到剪贴板或插入到编辑器
            if self.on_table_select:
                self.on_table_select(table_name, column_name)
    
    def _on_preview(self):
        """预览表数据"""
        item = self.schema_tree.selection()[0]
        if self._get_item_type(item) != "table":
            return
            
        table_name = self._get_clean_text(item)
        if self.on_table_select:
            query = f"SELECT * FROM {table_name} LIMIT 10"
            self.on_table_select(table_name, query=query)
    
    def _on_query_all(self):
        """查询整个表"""
        item = self.schema_tree.selection()[0]
        if self._get_item_type(item) != "table":
            return
            
        table_name = self._get_clean_text(item)
        if self.on_table_select:
            query = f"SELECT * FROM {table_name}"
            self.on_table_select(table_name, query=query)
    
    def _on_copy_name(self, item_type):
        """复制名称到剪贴板"""
        import pyperclip
        
        item = self.schema_tree.selection()[0]
        if self._get_item_type(item) != item_type:
            return
            
        name = self._get_clean_text(item)
        pyperclip.copy(name)
        self.status_label.config(text=f"已复制: {name}")
    
    def _on_refresh(self):
        """刷新表结构"""
        self.update_schema_info(self.tables_info)
    
    def _on_search(self, event=None):
        """搜索表或字段"""
        search_text = self.search_var.get().lower()
        
        if not search_text:
            # 显示所有项
            self._populate_tree(self.tables_info)
            return
            
        # 过滤表和字段
        filtered_tables = {}
        for table, columns in self.tables_info.items():
            if search_text in table.lower():
                # 表名匹配
                filtered_tables[table] = columns
            else:
                # 检查字段是否匹配
                matching_columns = [col for col in columns if search_text in col.lower()]
                if matching_columns:
                    filtered_tables[table] = matching_columns
        
        # 更新树形结构
        self._populate_tree(filtered_tables)
    
    def update_schema_info(self, tables_info: Dict[str, List[str]]):
        """
        更新表结构信息
        
        Args:
            tables_info: {表名: [字段列表]}
        """
        self.tables_info = tables_info
        self._populate_tree(tables_info)
    
    def _populate_tree(self, tables_info: Dict[str, List[str]]):
        """
        填充树形结构
        
        Args:
            tables_info: {表名: [字段列表]}
        """
        # 清空树
        self.schema_tree.delete(*self.schema_tree.get_children())
        
        # 添加表和字段
        for table_name, columns in tables_info.items():
            # 添加表节点
            table_node = self.schema_tree.insert(
                "", "end", 
                text=f"{self.table_icon}{table_name}", 
                open=False, 
                tags=("table",)
            )
            
            # 添加字段节点
            for column in columns:
                # 所有字段统一使用同一图标
                self.schema_tree.insert(
                    table_node, "end", 
                    text=f"{self.col_icon}{column}", 
                    tags=("column",)
                )
        
        # 设置样式 - 调整字体大小保持一致
        self.schema_tree.tag_configure("table", font=("Arial", 10))
        self.schema_tree.tag_configure("column", font=("Arial", 10))
        
        # 更新状态
        table_count = len(tables_info)
        self.status_label.config(text=f"共 {table_count} 张表")
    
    def clear(self):
        """清空面板"""
        self.tables_info = {}
        self.schema_tree.delete(*self.schema_tree.get_children())
        self.status_label.config(text="无可用表") 