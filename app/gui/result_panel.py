#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
结果显示面板
显示查询结果并提供分页和导出功能
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from typing import List, Dict, Callable, Optional, Any

from app.core.exporter import Exporter
from app.utils.ui_helpers import scrollbar_autohide


class ResultPanel(ttk.Frame):
    """结果显示面板，显示查询结果并提供分页和排序筛选功能"""
    
    def __init__(self, parent):
        """
        初始化结果显示面板
        
        Args:
            parent: 父容器
        """
        super().__init__(parent)
        self.parent = parent
        
        # 结果数据
        self.result_data = None  # 完整结果数据
        self.filtered_data = None  # 过滤后的数据
        self.current_page = 1    # 当前页码
        self.page_size = 100     # 每页行数
        self.total_pages = 0     # 总页数
        
        # 排序和过滤状态
        self.sort_column = None   # 当前排序列
        self.sort_ascending = True  # 排序方向（升序/降序）
        self.filter_column = None   # 当前过滤列
        self.filter_value = ""      # 过滤值
        self.filter_frame_visible = False  # 过滤区域是否可见
        
        # 设置序号列的样式（弱化显示）
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 创建三个主要区域
        self.top_area = ttk.Frame(self)
        self.center_area = ttk.Frame(self)
        self.bottom_area = ttk.Frame(self)
        
        # 使用适当的权重放置这些区域
        self.top_area.pack(side=tk.TOP, fill=tk.X)
        self.bottom_area.pack(side=tk.BOTTOM, fill=tk.X)
        self.center_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 顶部工具栏
        toolbar = ttk.Frame(self.top_area)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 导出按钮 - 修改左侧边距为0
        self.export_btn = ttk.Button(
            toolbar, 
            text="导出结果",
            command=self._on_export,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=(0, 5))  # 左侧边距为0，右侧为5
        
        # 导出格式选择
        self.export_format = tk.StringVar(value="xlsx")
        formats = [("Excel", "xlsx"), ("CSV", "csv"), ("JSON", "json")]
        
        for text, value in formats:
            ttk.Radiobutton(
                toolbar,
                text=text,
                variable=self.export_format,
                value=value
            ).pack(side=tk.LEFT, padx=5)
        
        # 导出范围选择
        self.export_scope = tk.StringVar(value="all")
        ttk.Radiobutton(
            toolbar,
            text="当前页",
            variable=self.export_scope,
            value="current"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            toolbar,
            text="全部数据",
            variable=self.export_scope,
            value="all"
        ).pack(side=tk.LEFT, padx=5)
        
        # 切换过滤区域的按钮 - 放在顶部工具栏的右侧，设置适当的右边距
        self.toggle_filter_btn = ttk.Button(
            toolbar,
            text="显示过滤/排序 ▼",
            command=self._toggle_filter_frame,
            state=tk.DISABLED
        )
        self.toggle_filter_btn.pack(side=tk.RIGHT, padx=(5, 15))  # 增加右侧边距为15像素，避免与滚动条重合
        
        # === 中央区域 ===
        # 排序和过滤面板（默认不显示）
        self.filter_frame = ttk.LabelFrame(self.center_area, text="结果过滤与排序")
        
        # 创建过滤控件
        ttk.Label(self.filter_frame, text="选择列:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_col_var = tk.StringVar()
        self.filter_column_combo = ttk.Combobox(self.filter_frame, textvariable=self.filter_col_var, state="readonly", width=15)
        self.filter_column_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_column_combo.bind("<<ComboboxSelected>>", self._on_filter_column_change)
        
        ttk.Label(self.filter_frame, text="过滤值:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_value_var = tk.StringVar()
        self.filter_value_entry = ttk.Entry(self.filter_frame, textvariable=self.filter_value_var, width=20)
        self.filter_value_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_value_entry.bind("<KeyRelease>", self._on_filter_value_change)
        
        # 创建排序控件
        ttk.Label(self.filter_frame, text="排序列:").grid(row=1, column=0, padx=5, pady=5)
        self.sort_col_var = tk.StringVar()
        self.sort_column_combo = ttk.Combobox(self.filter_frame, textvariable=self.sort_col_var, state="readonly", width=15)
        self.sort_column_combo.grid(row=1, column=1, padx=5, pady=5)
        self.sort_column_combo.bind("<<ComboboxSelected>>", self._on_sort_column_change)
        
        self.sort_order_var = tk.StringVar(value="升序")
        sort_asc_radio = ttk.Radiobutton(self.filter_frame, text="升序", variable=self.sort_order_var, value="升序")
        sort_asc_radio.grid(row=1, column=2, padx=5, pady=5)
        sort_asc_radio.bind("<Button-1>", lambda e: self._on_sort_order_change(True))
        
        sort_desc_radio = ttk.Radiobutton(self.filter_frame, text="降序", variable=self.sort_order_var, value="降序")
        sort_desc_radio.grid(row=1, column=3, padx=5, pady=5)
        sort_desc_radio.bind("<Button-1>", lambda e: self._on_sort_order_change(False))
        
        # 重置按钮
        self.reset_btn = ttk.Button(self.filter_frame, text="重置过滤和排序", command=self._on_reset_filter_sort, state=tk.DISABLED)
        self.reset_btn.grid(row=1, column=4, padx=5, pady=5)
        
        # 创建结果表格，调整与SQL编辑器区域一致的边距
        self.table_frame = ttk.Frame(self.center_area)
        self.table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))  # 调整上部边距
        
        # 创建Treeview显示结果
        self.result_tree = ttk.Treeview(
            self.table_frame,
            show="headings",
            selectmode="extended"
        )
        
        # 添加水平和垂直滚动条，使用自定义滚动条样式
        style = ttk.Style()
        # 配置水平滚动条只在需要时显示
        style.configure("Horizontal.TScrollbar", gripcount=0)
        style.configure("Vertical.TScrollbar", gripcount=0)
        
        h_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.result_tree.xview, style="Horizontal.TScrollbar")
        v_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.result_tree.yview, style="Vertical.TScrollbar")
        
        # 修改滚动条配置，设置当不需要滚动时隐藏滚动条
        self.result_tree.configure(xscrollcommand=scrollbar_autohide(h_scrollbar, 'grid'), 
                                   yscrollcommand=scrollbar_autohide(v_scrollbar, 'grid'))
        
        # 放置组件 - 使用grid布局确保滚动条在同一水平高度
        self.result_tree.grid(row=0, column=0, sticky='nsew')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # 配置表格框架的行列权重，使其可以正确调整大小
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
        # === 底部区域 ===
        # 状态栏
        self.status_bar = ttk.Label(self.bottom_area, text="就绪", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # 分页控制区域
        pagination = ttk.Frame(self.bottom_area)
        pagination.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 页码显示
        self.page_info = ttk.Label(pagination, text="无数据")
        self.page_info.pack(side=tk.LEFT, padx=5)
        
        # 每页行数选择
        ttk.Label(pagination, text="每页行数:").pack(side=tk.LEFT, padx=5)
        self.page_size_var = tk.StringVar(value="100")
        page_size_combo = ttk.Combobox(
            pagination,
            textvariable=self.page_size_var,
            values=["50", "100", "200", "500", "1000"],
            width=5,
            state="readonly"
        )
        page_size_combo.pack(side=tk.LEFT, padx=5)
        page_size_combo.bind("<<ComboboxSelected>>", self._on_page_size_change)
        
        # 分页按钮
        self.first_btn = ttk.Button(
            pagination, 
            text="首页",
            command=self._on_first_page,
            state=tk.DISABLED
        )
        self.first_btn.pack(side=tk.LEFT, padx=5)
        
        self.prev_btn = ttk.Button(
            pagination, 
            text="上一页",
            command=self._on_prev_page,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(
            pagination, 
            text="下一页",
            command=self._on_next_page,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.last_btn = ttk.Button(
            pagination, 
            text="末页",
            command=self._on_last_page,
            state=tk.DISABLED
        )
        self.last_btn.pack(side=tk.LEFT, padx=5)
        
        # 显示全部按钮
        self.show_all_btn = ttk.Button(
            pagination, 
            text="显示全部",
            command=self._on_show_all,
            state=tk.DISABLED
        )
        self.show_all_btn.pack(side=tk.LEFT, padx=5)
        
        # 初始化后确保底部区域已经准备好布局
        self.update_idletasks()
        
        # 强制一次布局更新
        self.after(500, self.ensure_bottom_area_visible)
    
    def display_result(self, data: pd.DataFrame, query_time: float = 0):
        """
        显示查询结果
        
        Args:
            data: 结果数据框
            query_time: 查询时间(毫秒)
        """
        if data is None or data.empty:
            self.status_bar.config(text="查询返回空结果")
            self._clear_result()
            return
        
        # 存储结果数据
        self.result_data = data
        self.filtered_data = data.copy()  # 初始时过滤后的数据与原始数据相同
        
        # 计算分页信息
        total_rows = len(self.filtered_data)
        self.total_pages = (total_rows + self.page_size - 1) // self.page_size
        self.current_page = 1
        
        # 更新排序和过滤控件
        self._update_filter_sort_controls()
        
        # 更新结果表格
        self._update_table()
        
        # 更新状态栏
        self.status_bar.config(text=f"查询完成，耗时: {query_time:.2f}ms，返回 {total_rows} 行数据")
        
        # 启用导出按钮和重置按钮
        self.export_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)
        self.toggle_filter_btn.config(state=tk.NORMAL)
        
        # 更新分页按钮状态
        self._update_pagination_controls()
        
        # 延迟一点确保底部区域可见
        self.after(100, self.ensure_bottom_area_visible)
    
    def _update_table(self):
        """更新结果表格"""
        if self.result_data is None or self.filtered_data is None:
            return
        
        # 清空表格
        for col in self.result_tree["columns"]:
            self.result_tree.heading(col, text="")
        
        self.result_tree.delete(*self.result_tree.get_children())
        
        # 计算当前页数据范围
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.filtered_data))
        
        # 获取当前页数据
        page_data = self.filtered_data.iloc[start_idx:end_idx]
        
        # 设置列，添加序号列
        data_columns = list(page_data.columns)
        display_columns = ["#"] + data_columns
        self.result_tree["columns"] = display_columns
        
        # 设置列标题
        for i, col in enumerate(display_columns):
            if i == 0:  # 序号列
                self.result_tree.heading(col, text="#", anchor=tk.CENTER)
                self.result_tree.column(col, width=40, anchor=tk.CENTER, stretch=tk.NO)
            else:
                col_name = str(col)
                # 如果是排序列，添加指示箭头
                if self.sort_column == col:
                    if self.sort_ascending:
                        col_name += " ▲"  # 升序
                    else:
                        col_name += " ▼"  # 降序
                self.result_tree.heading(col, text=col_name, anchor=tk.CENTER)
                # 为列标题添加点击事件，用于排序
                self.result_tree.heading(col, command=lambda c=col: self._on_heading_click(c))
                # 根据内容设置列宽
                max_width = max(
                    len(str(col)),
                    page_data[data_columns[i-1]].astype(str).str.len().max() if len(page_data) > 0 else 0
                )
                self.result_tree.column(col, width=min(max_width * 10, 300), anchor=tk.CENTER)
        
        # 添加数据行
        for i, (_, row) in enumerate(page_data.iterrows(), 1):
            # 计算实际行号（考虑分页）
            row_num = start_idx + i
            values = [row_num] + [str(row[col]) for col in data_columns]
            self.result_tree.insert("", tk.END, values=values)
        
        # 更新页码信息
        self.page_info.config(
            text=f"第 {self.current_page} 页，共 {self.total_pages} 页，总计 {len(self.filtered_data)} 行 (原始数据: {len(self.result_data)} 行)"
        )
    
    def _update_pagination_controls(self):
        """更新分页控件状态"""
        if self.result_data is None or self.total_pages <= 1:
            # 禁用所有分页按钮
            for btn in [self.first_btn, self.prev_btn, self.next_btn, self.last_btn, self.show_all_btn]:
                btn.config(state=tk.DISABLED)
        else:
            # 启用/禁用分页按钮
            self.first_btn.config(state=tk.DISABLED if self.current_page == 1 else tk.NORMAL)
            self.prev_btn.config(state=tk.DISABLED if self.current_page == 1 else tk.NORMAL)
            self.next_btn.config(state=tk.DISABLED if self.current_page == self.total_pages else tk.NORMAL)
            self.last_btn.config(state=tk.DISABLED if self.current_page == self.total_pages else tk.NORMAL)
            self.show_all_btn.config(state=tk.NORMAL)
            
        # 更新页码信息
        if self.filtered_data is not None and not self.filtered_data.empty:
            total_rows = len(self.filtered_data)
            start_idx = (self.current_page - 1) * self.page_size + 1
            end_idx = min(self.current_page * self.page_size, total_rows)
            self.page_info.config(text=f"第 {start_idx}-{end_idx} 行 / 共 {total_rows} 行 (第 {self.current_page}/{self.total_pages} 页)")
        else:
            self.page_info.config(text="无数据")
    
    def _on_first_page(self):
        """跳转到首页"""
        if self.current_page != 1:
            self.current_page = 1
            self._update_table()
            self._update_pagination_controls()
    
    def _on_prev_page(self):
        """跳转到上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_table()
            self._update_pagination_controls()
    
    def _on_next_page(self):
        """跳转到下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_table()
            self._update_pagination_controls()
    
    def _on_last_page(self):
        """跳转到末页"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self._update_table()
            self._update_pagination_controls()
    
    def _on_show_all(self):
        """显示所有数据"""
        if self.filtered_data is None or len(self.filtered_data) <= self.page_size:
            return
        
        # 如果数据量很大，给出警告
        if len(self.filtered_data) > 1000:
            if not messagebox.askyesno(
                "警告",
                f"数据量较大({len(self.filtered_data)}行)，显示全部可能会导致界面卡顿。是否继续？"
            ):
                return
        
        # 临时设置页大小为数据总量
        old_page_size = self.page_size
        self.page_size = len(self.filtered_data)
        self.current_page = 1
        self.total_pages = 1
        
        # 更新表格
        self._update_table()
        self._update_pagination_controls()
        
        # 恢复原页大小
        self.page_size = old_page_size
        self.total_pages = (len(self.filtered_data) + self.page_size - 1) // self.page_size
    
    def _on_page_size_change(self, event):
        """页大小改变事件"""
        try:
            new_size = int(self.page_size_var.get())
            if new_size != self.page_size:
                self.page_size = new_size
                
                # 重新计算分页信息
                if self.filtered_data is not None:
                    self.total_pages = (len(self.filtered_data) + self.page_size - 1) // self.page_size
                    self.current_page = min(self.current_page, self.total_pages)
                    self._update_table()
                    self._update_pagination_controls()
        except ValueError:
            pass
    
    def _on_export(self):
        """导出结果"""
        if self.result_data is None or self.result_data.empty:
            messagebox.showinfo("提示", "没有可导出的数据")
            return
        
        # 确定导出数据源
        data_source = self.filtered_data if len(self.filtered_data) != len(self.result_data) else self.result_data
        
        # 确定导出数据范围
        if self.export_scope.get() == "current":
            # 导出当前页
            start_idx = (self.current_page - 1) * self.page_size
            end_idx = min(start_idx + self.page_size, len(data_source))
            export_data = data_source.iloc[start_idx:end_idx]
        else:
            # 导出全部数据
            export_data = data_source
        
        # 注意：导出时不包含序号列，直接使用原始数据
        
        # 获取导出格式
        export_format = self.export_format.get()
        
        # 根据选择的格式设置文件类型过滤器
        filetypes = []
        defaultextension = f".{export_format}"
        
        if export_format == "xlsx":
            filetypes = [("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        elif export_format == "csv":
            filetypes = [("CSV文件", "*.csv"), ("所有文件", "*.*")]
        elif export_format == "json":
            filetypes = [("JSON文件", "*.json"), ("所有文件", "*.*")]
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="导出结果",
            defaultextension=defaultextension,
            filetypes=filetypes
        )
        
        if not file_path:
            return
        
        # 执行导出
        success = False
        message = ""
        
        if export_format == "xlsx":
            success, message = Exporter.export_to_excel(export_data, file_path)
        elif export_format == "csv":
            success, message = Exporter.export_to_csv(export_data, file_path)
        elif export_format == "json":
            success, message = Exporter.export_to_json(export_data, file_path)
        
        # 显示结果
        if success:
            self.status_bar.config(text=message)
            messagebox.showinfo("导出成功", message)
        else:
            self.status_bar.config(text=f"导出失败: {message}")
            messagebox.showerror("导出失败", message)
    
    def _clear_result(self):
        """清空结果"""
        # 清空表格
        for col in self.result_tree["columns"]:
            self.result_tree.heading(col, text="")
        
        self.result_tree["columns"] = []
        self.result_tree.delete(*self.result_tree.get_children())
        
        # 重置分页信息
        self.result_data = None
        self.filtered_data = None
        self.current_page = 1
        self.total_pages = 0
        self.page_info.config(text="无数据")
        
        # 重置过滤和排序状态
        self.filter_column = None
        self.filter_value = ""
        self.filter_col_var.set("")
        self.filter_value_var.set("")
        
        self.sort_column = None
        self.sort_ascending = True
        self.sort_col_var.set("")
        self.sort_order_var.set("升序")
        
        # 禁用按钮
        self.export_btn.config(state=tk.DISABLED)
        self.reset_btn.config(state=tk.DISABLED)
        self.toggle_filter_btn.config(state=tk.DISABLED)
        for btn in [self.first_btn, self.prev_btn, self.next_btn, self.last_btn, self.show_all_btn]:
            btn.config(state=tk.DISABLED)
            
        # 如果过滤区域是可见的，隐藏它
        if self.filter_frame_visible:
            self._toggle_filter_frame()
    
    def set_status(self, message: str):
        """
        设置状态栏消息
        
        Args:
            message: 状态消息
        """
        self.status_bar.config(text=message)
    
    def _update_filter_sort_controls(self):
        """更新过滤和排序控件"""
        if self.result_data is None or self.result_data.empty:
            return
        
        # 获取所有列名（不包括序号列）
        columns = list(self.result_data.columns)
        
        # 更新列下拉框的值
        self.filter_column_combo['values'] = columns
        self.sort_column_combo['values'] = columns
        
        # 如果之前选择的列不在新的结果中，则重置选择
        if self.filter_column not in columns:
            self.filter_column = None
            self.filter_col_var.set('')
            self.filter_value_var.set('')
        else:
            self.filter_col_var.set(self.filter_column)
        
        if self.sort_column not in columns:
            self.sort_column = None
            self.sort_col_var.set('')
        else:
            self.sort_col_var.set(self.sort_column)
    
    def _on_filter_column_change(self, event):
        """过滤列改变事件"""
        new_column = self.filter_col_var.get()
        if new_column != self.filter_column:
            self.filter_column = new_column
            # 重置过滤值
            self.filter_value = ""
            self.filter_value_var.set("")
            # 应用过滤
            self._apply_filter_and_sort()
    
    def _on_filter_value_change(self, event):
        """过滤值改变事件"""
        new_value = self.filter_value_var.get()
        if new_value != self.filter_value:
            self.filter_value = new_value
            # 应用过滤（延迟500ms应用，避免频繁刷新）
            if hasattr(self, '_filter_after_id'):
                self.after_cancel(self._filter_after_id)
            self._filter_after_id = self.after(500, self._apply_filter_and_sort)
    
    def _on_sort_column_change(self, event):
        """排序列改变事件"""
        new_column = self.sort_col_var.get()
        if new_column != self.sort_column:
            self.sort_column = new_column
            # 恢复为默认升序
            self.sort_ascending = True
            self.sort_order_var.set("升序")
            # 应用排序
            self._apply_filter_and_sort()
    
    def _on_sort_order_change(self, ascending):
        """排序顺序改变事件"""
        if self.sort_ascending != ascending:
            self.sort_ascending = ascending
            # 应用排序
            self._apply_filter_and_sort()
    
    def _on_heading_click(self, column):
        """列标题点击事件，用于快速排序"""
        if column == "#":  # 忽略序号列
            return
        
        # 如果点击的是当前排序列，则切换升序/降序
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
            self.sort_order_var.set("升序" if self.sort_ascending else "降序")
        else:
            # 否则设置为新的排序列，默认升序
            self.sort_column = column
            self.sort_ascending = True
            self.sort_order_var.set("升序")
            self.sort_col_var.set(column)
        
        # 应用排序
        self._apply_filter_and_sort()
    
    def _on_reset_filter_sort(self):
        """重置过滤和排序"""
        # 重置过滤
        self.filter_column = None
        self.filter_value = ""
        self.filter_col_var.set("")
        self.filter_value_var.set("")
        
        # 重置排序
        self.sort_column = None
        self.sort_ascending = True
        self.sort_col_var.set("")
        self.sort_order_var.set("升序")
        
        # 恢复原始数据
        if self.result_data is not None:
            self.filtered_data = self.result_data.copy()
            self.total_pages = (len(self.filtered_data) + self.page_size - 1) // self.page_size
            self.current_page = 1
            self._update_table()
            self._update_pagination_controls()
    
    def _apply_filter_and_sort(self):
        """应用过滤和排序"""
        if self.result_data is None or self.result_data.empty:
            return
        
        # 先复制原始数据
        filtered_df = self.result_data.copy()
        
        # 应用过滤
        if self.filter_column and self.filter_value:
            try:
                # 将列值转为字符串，然后进行不区分大小写的模糊匹配
                mask = filtered_df[self.filter_column].astype(str).str.contains(
                    self.filter_value, case=False, na=False
                )
                filtered_df = filtered_df[mask]
            except Exception as e:
                self.status_bar.config(text=f"过滤错误: {str(e)}")
        
        # 应用排序
        if self.sort_column:
            try:
                filtered_df = filtered_df.sort_values(
                    by=self.sort_column, 
                    ascending=self.sort_ascending,
                    na_position='last'
                )
            except Exception as e:
                self.status_bar.config(text=f"排序错误: {str(e)}")
        
        # 更新过滤后的数据
        self.filtered_data = filtered_df
        
        # 重新计算分页
        self.total_pages = (len(self.filtered_data) + self.page_size - 1) // self.page_size
        self.current_page = min(self.current_page, max(1, self.total_pages))
        
        # 更新表格和分页控制
        self._update_table()
        self._update_pagination_controls()
        
        # 更新状态栏
        filter_status = "已过滤" if len(self.filtered_data) != len(self.result_data) else "全部"
        sort_status = f"已排序({self.sort_column})" if self.sort_column else "未排序"
        self.status_bar.config(
            text=f"显示: {filter_status} {len(self.filtered_data)}/{len(self.result_data)} 行, {sort_status}"
        )

    def _toggle_filter_frame(self):
        """切换过滤区域的可见性"""
        self.filter_frame_visible = not self.filter_frame_visible
        if self.filter_frame_visible:
            # 显示过滤框架，确保它位于table_frame之前
            self.filter_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5, before=self.table_frame)
            self.toggle_filter_btn.config(text="隐藏过滤/排序 ▲")
        else:
            # 隐藏过滤框架
            self.filter_frame.pack_forget()
            self.toggle_filter_btn.config(text="显示过滤/排序 ▼")
        
        # 强制调整布局
        self.update_idletasks()
        
        # 确保滚动视图以显示所有内容
        self.master.update_idletasks()
        
        # 确保底部区域可见
        self.after(100, self.ensure_bottom_area_visible)

    def ensure_bottom_area_visible(self):
        """确保底部区域始终可见"""
        # 获取底部区域的高度
        self.bottom_area.update_idletasks()
        bottom_height = self.bottom_area.winfo_reqheight()
        
        # 确保父容器有足够大的最小高度
        if hasattr(self.master, 'configure'):
            self.master.update_idletasks()
            master_height = self.master.winfo_height()
            
            # 设置最小高度为底部区域高度加上一些额外空间
            min_height = bottom_height + 50  # 额外空间，确保完全可见
            
            # 如果分割窗口过小，调整它
            if master_height < min_height:
                if hasattr(self.master, 'sash_coord') and hasattr(self.master, 'sash_place'):
                    try:
                        # 假设这是一个PanedWindow，尝试调整分隔条位置
                        sash_pos = self.master.sash_coord(0)[1]  # 获取第一个分隔条的Y坐标
                        new_pos = sash_pos - (min_height - master_height) - 10
                        if new_pos > 100:  # 防止将分隔条拉得太高
                            self.master.sash_place(0, 0, new_pos)
                    except:
                        pass
