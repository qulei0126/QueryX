#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件选择面板
提供文件选择和管理功能
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Callable
import pandas as pd

from app.utils.helpers import is_supported_file, get_file_extension
from app.utils.ui_helpers import scrollbar_autohide


class FilePanel(ttk.Frame):
    """文件选择面板，提供文件选择和管理功能"""
    
    def __init__(self, parent, load_callback: Callable = None, remove_callback: Callable = None):
        """
        初始化文件选择面板
        
        Args:
            parent: 父容器
            load_callback: 加载文件的回调函数
            remove_callback: 移除文件的回调函数
        """
        super().__init__(parent)
        self.parent = parent
        self.load_callback = load_callback
        self.remove_callback = remove_callback
        self.selected_files = []  # 已选择的文件路径列表
        self.file_table_map = {}  # 文件路径到表名的映射
        self.query_callback = None  # 查询回调函数
        self.query_engine = None  # 查询引擎实例
        self.preview_visible = False  # 预览区域是否可见
        self.current_preview_file = None  # 当前预览的文件路径
        
        self._create_widgets()
        self._create_context_menu()
    
    def _create_widgets(self):
        """创建组件"""
        # 状态栏 - 在方法开头创建，确保它始终在底部显示
        self.status_label = ttk.Label(self, text="未加载文件")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # 顶部按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 添加文件按钮 - 修改左边距为0，确保左对齐
        self.add_btn = ttk.Button(
            btn_frame, 
            text="添加文件",
            command=self._on_add_files
        )
        self.add_btn.pack(side=tk.LEFT, padx=(0, 5))  # 左侧边距为0，右侧为5
        
        # 移除选中文件按钮
        self.remove_btn = ttk.Button(
            btn_frame, 
            text="移除选中",
            command=self._on_remove_selected
        )
        self.remove_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空所有按钮
        self.clear_btn = ttk.Button(
            btn_frame, 
            text="清空所有",
            command=self._on_clear_all
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 创建内容框架，将所有内容（除状态栏外）放入其中
        content_frame = ttk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建垂直分割面板
        self.main_paned = ttk.PanedWindow(content_frame, orient=tk.VERTICAL)
        self.main_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文件列表框架
        list_frame = ttk.LabelFrame(self.main_paned, text="已加载文件")
        self.main_paned.add(list_frame, weight=1)
        
        # 创建Treeview显示文件列表
        self.file_tree = ttk.Treeview(
            list_frame,
            columns=("index", "name", "type", "size", "rows", "cols"),
            show="headings",
            selectmode="extended"
        )
        
        # 设置列标题
        self.file_tree.heading("index", text="#", anchor=tk.CENTER)
        self.file_tree.heading("name", text="文件名", anchor=tk.CENTER)
        self.file_tree.heading("type", text="类型", anchor=tk.CENTER)
        self.file_tree.heading("size", text="大小", anchor=tk.CENTER)
        self.file_tree.heading("rows", text="行数", anchor=tk.CENTER)
        self.file_tree.heading("cols", text="列数", anchor=tk.CENTER)
        
        # 设置列宽和对齐方式
        self.file_tree.column("index", width=40, anchor=tk.CENTER, stretch=tk.NO)
        self.file_tree.column("name", width=200, anchor=tk.CENTER)
        self.file_tree.column("type", width=50, anchor=tk.CENTER)
        self.file_tree.column("size", width=80, anchor=tk.CENTER)
        self.file_tree.column("rows", width=80, anchor=tk.CENTER)
        self.file_tree.column("cols", width=80, anchor=tk.CENTER)
        
        # 设置序号列的样式（弱化显示）
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscroll=scrollbar_autohide(scrollbar, 'pack'))
        
        # 放置组件
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.file_tree.bind("<Double-1>", self._on_file_double_click)
        
        # 创建预览区域框架 - 初始不添加到PanedWindow
        self.preview_container = ttk.Frame(self.main_paned)
        
        # 预览区域标题栏
        self.preview_header = ttk.Frame(self.preview_container)
        self.preview_header.pack(side=tk.TOP, fill=tk.X)
        
        self.preview_title = ttk.Label(self.preview_header, text="文件预览 (显示前100行)", font=("Arial", 10, "bold"))
        self.preview_title.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 关闭预览按钮
        self.close_preview_btn = ttk.Button(
            self.preview_header,
            text="关闭预览",
            command=self._toggle_preview,
            width=10
        )
        self.close_preview_btn.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # 预览区域内容
        preview_content = ttk.Frame(self.preview_container)
        preview_content.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建文件预览的Treeview
        self.preview_tree = ttk.Treeview(
            preview_content,
            show="headings",
            selectmode="browse"
        )
        
        # 添加水平和垂直滚动条
        h_scrollbar = ttk.Scrollbar(preview_content, orient=tk.HORIZONTAL, command=self.preview_tree.xview)
        v_scrollbar = ttk.Scrollbar(preview_content, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(xscroll=scrollbar_autohide(h_scrollbar, 'grid'), yscroll=scrollbar_autohide(v_scrollbar, 'grid'))
        
        # 放置组件 - 使用grid布局确保滚动条在同一水平高度
        self.preview_tree.grid(row=0, column=0, sticky='nsew')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # 配置预览框架的行列权重，使其可以正确调整大小
        preview_content.grid_rowconfigure(0, weight=1)
        preview_content.grid_columnconfigure(0, weight=1)
    
    def _create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="预览", command=self._on_preview_selected)
        self.context_menu.add_command(label="查询", command=self._on_query_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="移除", command=self._on_remove_selected)
        
        # 绑定右键点击事件
        self.file_tree.bind("<Button-3>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """显示右键菜单"""
        # 获取点击位置的项
        item_id = self.file_tree.identify_row(event.y)
        if not item_id:
            return
        
        # 选中被点击的项
        self.file_tree.selection_set(item_id)
        
        # 显示右键菜单
        self.context_menu.post(event.x_root, event.y_root)
    
    def _on_file_double_click(self, event):
        """双击文件项预览文件内容"""
        # 获取选中项
        item_id = self.file_tree.identify_row(event.y)
        if not item_id:
            return
        
        # 获取文件路径
        values = self.file_tree.item(item_id, "values")
        file_name = values[1]
        file_path = values[-1]  # 文件路径存储在隐藏列
        
        # 调用预览切换功能，显示预览区域并加载内容
        self._toggle_preview(show_preview=True, file_path=file_path, file_name=file_name)
    
    def _on_preview_selected(self):
        """预览选中的文件"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
        
        # 获取选中项对应的文件路径
        item_id = selected_items[0]  # 只预览第一个选中的文件
        values = self.file_tree.item(item_id, "values")
        file_name = values[1]
        file_path = values[-1]  # 文件路径存储在隐藏列
        
        # 调用预览切换功能，显示预览区域并加载内容
        self._toggle_preview(show_preview=True, file_path=file_path, file_name=file_name)
    
    def _on_query_selected(self):
        """查询选中的文件"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
        
        # 获取选中项对应的文件路径
        item_id = selected_items[0]  # 只查询第一个选中的文件
        values = self.file_tree.item(item_id, "values")
        file_name = values[1]
        file_path = values[-1]  # 文件路径存储在隐藏列
        
        # 获取表名
        if file_path in self.file_table_map:
            table_name = self.file_table_map[file_path]
            
            # 如果设置了查询回调函数，则调用
            if self.query_callback:
                query = f'SELECT * FROM "{table_name}"'
                self.query_callback(query)
                self.status_label.config(text=f"正在查询: {file_name}")
            else:
                self.status_label.config(text="查询功能未初始化")
        else:
            self.status_label.config(text=f"无法获取 {file_name} 的表名")
    
    def _on_add_files(self):
        """添加文件"""
        file_paths = filedialog.askopenfilenames(
            title="选择文件",
            filetypes=[
                ("所有支持的文件", "*.xlsx *.xls *.xlsm *.csv *.json"),
                ("Excel文件", "*.xlsx *.xls *.xlsm"),
                ("CSV文件", "*.csv"),
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_paths:
            # 过滤不支持的文件格式
            valid_files = [f for f in file_paths if is_supported_file(f)]
            
            if not valid_files:
                self.status_label.config(text="未选择有效文件")
                return
            
            # 调用回调函数加载文件
            if self.load_callback:
                for file_path in valid_files:
                    self.load_callback(file_path)
    
    def _on_remove_selected(self):
        """移除选中的文件"""
        selected_items = self.file_tree.selection()
        
        if not selected_items:
            return
        
        # 获取选中项对应的文件路径
        selected_paths = []
        for item_id in selected_items:
            file_path = self.file_tree.item(item_id, "values")[-1]  # 文件路径存储在隐藏列
            selected_paths.append(file_path)
        
        # 检查是否有这些文件相关的可用表
        affected_tables = []
        for file_path in selected_paths:
            if file_path in self.file_table_map:
                affected_tables.append(self.file_table_map[file_path])
        
        # 如果有相关表，提示用户确认
        if affected_tables:
            tables_str = ", ".join(affected_tables)
            confirm = messagebox.askokcancel(
                "确认移除", 
                f"移除选中的文件将同时移除以下可用表:\n{tables_str}\n\n是否继续?"
            )
            if not confirm:
                return
        
        # 从列表中移除
        for file_path in selected_paths:
            self._remove_file(file_path)
        
        self.status_label.config(text=f"已移除 {len(selected_paths)} 个文件")
        
        # 清空预览区域
        self._clear_preview()
    
    def _on_clear_all(self):
        """清空所有文件"""
        # 获取所有文件路径
        all_paths = []
        for item_id in self.file_tree.get_children():
            file_path = self.file_tree.item(item_id, "values")[-1]
            all_paths.append(file_path)
        
        if not all_paths:
            return
        
        # 检查是否有可用表
        affected_tables = list(self.file_table_map.values())
        
        # 如果有相关表，提示用户确认
        if affected_tables:
            tables_str = ", ".join(affected_tables)
            confirm = messagebox.askokcancel(
                "确认清空", 
                f"清空所有文件将同时移除以下可用表:\n{tables_str}\n\n是否继续?"
            )
            if not confirm:
                return
        
        # 从列表中移除
        for file_path in all_paths:
            self._remove_file(file_path)
        
        self.status_label.config(text="已清空所有文件")
        
        # 隐藏预览区域
        self._toggle_preview(show_preview=False)
        
        # 清空预览区域
        self._clear_preview()
    
    def _display_dataframe(self, df: pd.DataFrame):
        """
        在预览区域显示数据框
        
        Args:
            df: 要显示的数据框
        """
        # 设置列，添加序号列
        columns = ["#"] + list(df.columns)
        self.preview_tree["columns"] = columns
        
        # 设置列标题和居中对齐
        for i, col in enumerate(columns):
            if i == 0:  # 序号列
                self.preview_tree.heading(col, text="#", anchor=tk.CENTER)
                self.preview_tree.column(col, width=40, anchor=tk.CENTER, stretch=tk.NO)
                # 设置序号列样式（弱化显示）
                style = ttk.Style()
                style.configure("Treeview.Cell", foreground="gray")
            else:
                self.preview_tree.heading(col, text=str(col), anchor=tk.CENTER)
                # 根据内容设置列宽
                max_width = max(
                    len(str(col)),
                    df[col].astype(str).str.len().max() if len(df) > 0 else 0
                )
                self.preview_tree.column(col, width=min(max_width * 10, 300), anchor=tk.CENTER)
        
        # 添加数据行
        for i, (_, row) in enumerate(df.iterrows(), 1):
            values = [i] + [str(row[col]) for col in df.columns]
            self.preview_tree.insert("", tk.END, values=values)
    
    def _clear_preview(self):
        """清空预览区域"""
        # 清空表格
        for col in self.preview_tree["columns"]:
            self.preview_tree.heading(col, text="")
        
        self.preview_tree["columns"] = []
        self.preview_tree.delete(*self.preview_tree.get_children())
    
    def _remove_file(self, file_path):
        """
        从列表中移除文件
        
        Args:
            file_path: 文件路径
        """
        # 查找对应的树项
        for item_id in self.file_tree.get_children():
            if self.file_tree.item(item_id, "values")[-1] == file_path:
                self.file_tree.delete(item_id)
                break
        
        # 从已选择列表中移除
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
        
        # 从表映射中移除
        if file_path in self.file_table_map:
            del self.file_table_map[file_path]
        
        # 如果正在预览该文件，隐藏预览区域
        if self.current_preview_file == file_path:
            self.current_preview_file = None
            self._toggle_preview(show_preview=False)
            
        # 调用回调函数通知主窗口移除文件
        if self.remove_callback:
            self.remove_callback(file_path)
    
    def add_file(self, file_path: str, file_info: Dict):
        """
        添加文件到列表
        
        Args:
            file_path: 文件路径
            file_info: 文件信息字典
        """
        # 检查文件是否已存在
        for item_id in self.file_tree.get_children():
            if self.file_tree.item(item_id, "values")[-1] == file_path:
                return
        
        # 计算序号
        row_num = len(self.file_tree.get_children()) + 1
        
        # 添加到树视图
        self.file_tree.insert(
            "",
            tk.END,
            values=(
                row_num,
                file_info["name"],
                file_info["type"],
                file_info["size"],
                file_info["rows"],
                file_info["columns"],
                file_path  # 隐藏列，存储文件路径
            )
        )
        
        # 添加到已选择列表
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
        
        # 更新状态
        self.status_label.config(text=f"已加载: {file_info['name']}")
        
        # 如果文件信息中包含表名，记录文件到表名的映射
        if 'table_name' in file_info:
            self.file_table_map[file_path] = file_info['table_name']
    
    def get_selected_files(self) -> List[str]:
        """
        获取已选择的文件路径列表
        
        Returns:
            List[str]: 文件路径列表
        """
        return self.selected_files
    
    def set_query_callback(self, callback: Callable):
        """
        设置查询回调函数
        
        Args:
            callback: 查询回调函数
        """
        self.query_callback = callback
    
    def set_query_engine(self, query_engine):
        """
        设置查询引擎
        
        Args:
            query_engine: 查询引擎实例
        """
        self.query_engine = query_engine
    
    def _toggle_preview(self, show_preview=None, file_path=None, file_name=None):
        """
        切换预览区域的显示/隐藏
        
        Args:
            show_preview: 是否显示预览，None表示切换状态
            file_path: 要预览的文件路径
            file_name: 要预览的文件名称
        """
        # 如果指定了show_preview，使用指定值，否则切换状态
        if show_preview is not None:
            will_show = show_preview
        else:
            will_show = not self.preview_visible
        
        # 更新预览状态
        if will_show:
            if file_path:
                # 如果提供了文件路径，加载并显示预览内容
                self.current_preview_file = file_path
                if not self.preview_visible:
                    # 如果预览区域当前是隐藏的，先添加到PanedWindow
                    self.main_paned.add(self.preview_container, weight=1)
                    self.preview_visible = True
                
                # 加载预览内容
                self._load_preview_content(file_path, file_name or "文件")
                
                # 更新预览标题
                if file_name:
                    self.preview_title.config(text=f"文件预览: {file_name} (显示前100行)")
            else:
                # 没有文件路径但需要显示，使用当前预览文件
                if self.current_preview_file:
                    # 如果有当前预览文件但预览区域是隐藏的，重新添加到PanedWindow
                    if not self.preview_visible:
                        self.main_paned.add(self.preview_container, weight=1)
                        self.preview_visible = True
                else:
                    # 没有当前预览文件，不做任何操作
                    return
        else:
            # 隐藏预览区域
            if self.preview_visible:
                self.main_paned.forget(self.preview_container)
                self.preview_visible = False
        
        # 更新界面
        self.update_idletasks()
        
    def _load_preview_content(self, file_path, file_name):
        """加载预览内容"""
        # 清空预览区域
        self._clear_preview()
        
        # 如果设置了查询引擎，优先使用查询引擎的预览功能
        if self.query_engine and file_path in self.file_table_map:
            table_name = self.file_table_map[file_path]
            try:
                # 使用查询引擎预览表数据（显示前100行）
                df = self.query_engine.get_table_preview(table_name, limit=100)
                if df is not None and not df.empty:
                    self._display_dataframe(df)
                    self.status_label.config(text=f"已预览 {file_name} (显示前100行)")
                    return
            except Exception as e:
                print(f"使用查询引擎预览失败: {str(e)}，将使用备用方式预览")
        
        # 备用方式：直接读取文件
        try:
            # 根据文件类型加载数据
            ext = get_file_extension(file_path)
            
            if ext in ['xlsx', 'xls', 'xlsm']:
                # 读取Excel文件，只读取前100行进行预览
                df = pd.read_excel(file_path, nrows=100)
            elif ext == 'csv':
                # 读取CSV文件，只读取前100行进行预览
                df = pd.read_csv(file_path, nrows=100)
            elif ext == 'json':
                # 读取JSON文件，只读取前100行进行预览
                df = pd.read_json(file_path)
                if len(df) > 100:
                    df = df.head(100)
            else:
                self.status_label.config(text=f"不支持预览此类型文件: {file_name}")
                return
            
            # 显示数据框
            self._display_dataframe(df)
            self.status_label.config(text=f"已预览 {file_name} (显示前100行)")
            
        except Exception as e:
            self.status_label.config(text=f"预览文件失败: {str(e)}")
            messagebox.showerror("预览失败", f"无法预览文件 {file_name}: {str(e)}") 