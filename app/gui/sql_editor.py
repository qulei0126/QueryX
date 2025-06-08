#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQL编辑器组件
提供SQL查询输入和语法高亮功能
"""

import re
import tkinter as tk
from tkinter import ttk
from typing import List, Callable
import pyperclip  # 确保在requirements.txt中添加

# 导入Pygments库用于语法高亮
from pygments import lex
from pygments.lexers import SqlLexer
from pygments.token import Token, Keyword, Name, String, Number, Operator, Comment

from app.utils.helpers import get_sql_keywords, format_sql
from app.utils.ui_helpers import scrollbar_autohide


class SQLEditor(ttk.Frame):
    """SQL编辑器组件，提供SQL查询输入和语法高亮功能"""
    
    def __init__(self, parent, execute_callback: Callable = None):
        """
        初始化SQL编辑器
        
        Args:
            parent: 父容器
            execute_callback: 执行查询的回调函数
        """
        super().__init__(parent)
        self.parent = parent
        self.execute_callback = execute_callback
        self.keywords = get_sql_keywords()
        
        # 定义语法高亮颜色
        self.token_colors = {
            Token.Keyword: "#0000FF",           # 关键字：蓝色
            Token.Literal.String: "#008000",    # 字符串：绿色
            Token.Literal.Number: "#FF8000",    # 数字：橙色
            Token.Operator: "#800080",          # 运算符：紫色
            Token.Comment: "#808080",           # 注释：灰色
            Token.Name: "#000000",              # 标识符：黑色
            Token.Name.Function: "#800000",     # 函数名：棕色
            "default": "#000000"                # 默认：黑色
        }
        
        # 创建界面组件
        self._create_widgets()
        
        # 绑定事件
        self._bind_events()
        
        # 初始化高亮
        self.after(100, self._apply_syntax_highlighting)
    
    def _create_widgets(self):
        """创建组件"""
        # 状态栏 - 移到最开始创建，确保它始终在底部显示
        self.status_bar = ttk.Label(self, text="就绪", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # 创建顶部工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # 执行按钮 - 修改左侧边距为0
        self.execute_btn = ttk.Button(
            toolbar, 
            text="执行查询",
            command=self._on_execute
        )
        self.execute_btn.pack(side=tk.LEFT, padx=(0, 5), pady=5)  # 左侧边距为0
        
        # 清空按钮
        self.clear_btn = ttk.Button(
            toolbar, 
            text="清空",
            command=self._on_clear
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 格式化按钮
        self.format_btn = ttk.Button(
            toolbar,
            text="格式化SQL",
            command=self._on_format_sql
        )
        self.format_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 创建主编辑器框架，使用普通Frame但添加清晰的边框
        editor_frame = ttk.Frame(self, borderwidth=1, relief=tk.SOLID)  # 使用普通Frame并添加边框
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建内部框架用于容纳编辑器和行号
        inner_frame = ttk.Frame(editor_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # 创建行号显示，调整背景色更协调
        self.line_numbers = tk.Canvas(inner_frame, width=40, bg="#F8F8F8", highlightthickness=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # 添加一个垂直分隔线在行号区域和编辑区域之间
        separator = ttk.Separator(inner_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y)
        
        # 创建SQL文本编辑器
        self.editor = tk.Text(
            inner_frame,
            wrap=tk.WORD,
            width=80,  # 增加默认宽度
            height=20,  # 进一步增加默认高度
            font=("Consolas", 11),
            undo=True,
            bg="#FFFFFF",
            fg="#000000",
            insertbackground="#000000",
            selectbackground="#C0C0C0",
            selectforeground="#000000",
            padx=5,
            pady=5,
            relief=tk.FLAT,  # 使用平面效果，没有凹陷感
            borderwidth=0     # 移除内部边框
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建垂直滚动条
        yscrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL, command=self.editor.yview)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=scrollbar_autohide(yscrollbar, 'pack'))
        
        # 设置默认查询示例
        self.editor.insert(tk.END, "-- 输入SQL查询\nSELECT * FROM table_name")
    
    def _bind_events(self):
        """绑定事件"""
        # 按键绑定
        self.editor.bind("<Control-Return>", self._on_execute)  # Ctrl+Enter执行查询
        self.editor.bind("<KeyRelease>", self._on_key_release)  # 按键释放时更新高亮
        self.editor.bind("<<Modified>>", self._on_modified)     # 内容修改时更新行号
        self.editor.bind("<Configure>", self._update_line_numbers)  # 窗口大小改变时更新行号
        
        # 快捷键
        self.editor.bind("<Control-f>", lambda e: self._on_format_sql())
        
        # 右键菜单
        self._create_context_menu()
    
    def _create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="剪切", command=self._on_cut)
        self.context_menu.add_command(label="复制", command=self._on_copy)
        self.context_menu.add_command(label="粘贴", command=self._on_paste)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="全选", command=self._select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="格式化SQL", command=self._on_format_sql)
        
        # 绑定右键菜单
        self.editor.bind("<Button-3>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """显示右键菜单"""
        self.context_menu.post(event.x_root, event.y_root)
    
    def _select_all(self, event=None):
        """全选文本"""
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.mark_set(tk.INSERT, "1.0")
        self.editor.see(tk.INSERT)
        return "break"
    
    def _on_cut(self, event=None):
        """剪切选中的文本"""
        if self.editor.tag_ranges(tk.SEL):
            self._on_copy()
            self.editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
        return "break"
    
    def _on_copy(self, event=None):
        """复制选中的文本"""
        if self.editor.tag_ranges(tk.SEL):
            selected_text = self.editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            pyperclip.copy(selected_text)
        return "break"
    
    def _on_paste(self, event=None):
        """粘贴文本"""
        try:
            text = pyperclip.paste()
            if text:
                # 如果有选中的文本，先删除
                if self.editor.tag_ranges(tk.SEL):
                    self.editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.editor.insert(tk.INSERT, text)
                self._apply_syntax_highlighting()
        except Exception as e:
            self.status_bar.config(text=f"粘贴失败: {str(e)}")
        return "break"
    
    def _on_format_sql(self, event=None):
        """格式化SQL语句"""
        try:
            # 获取当前SQL
            current_sql = self.get_query()
            if not current_sql.strip():
                return "break"
            
            # 格式化SQL
            formatted_sql = format_sql(current_sql)
            
            # 更新编辑器内容
            self.set_query(formatted_sql)
            self.status_bar.config(text="SQL格式化成功")
        except Exception as e:
            self.status_bar.config(text=f"格式化失败: {str(e)}")
        return "break"
    
    def _on_execute(self, event=None):
        """执行查询"""
        if self.execute_callback:
            query = self.get_query()
            self.execute_callback(query)
    
    def _on_clear(self):
        """清空编辑器"""
        self.editor.delete("1.0", tk.END)
        self._update_line_numbers()
    
    def _on_key_release(self, event=None):
        """按键释放时更新高亮"""
        # 避免频繁更新，使用after延迟执行
        self.after_cancel(self._apply_syntax_highlighting) if hasattr(self, '_apply_syntax_highlighting_id') else None
        self._apply_syntax_highlighting_id = self.after(100, self._apply_syntax_highlighting)
    
    def _on_modified(self, event=None):
        """内容修改时更新行号"""
        self._update_line_numbers()
        self.editor.edit_modified(False)  # 重置修改标志
    
    def _update_line_numbers(self, event=None):
        """更新行号"""
        # 清除现有内容
        self.line_numbers.delete("all")
        
        # 获取总行数
        total_lines = int(self.editor.index(tk.END).split('.')[0]) - 1
        
        # 如果没有内容，直接返回
        if total_lines < 1:
            return
        
        # 获取可见区域的第一行和最后一行
        try:
            first_line = int(self.editor.index("@0,0").split('.')[0])
            last_line = int(self.editor.index(f"@0,{self.editor.winfo_height()}").split('.')[0])
        except:
            first_line = 1
            last_line = total_lines
        
        # 确保至少显示所有行
        first_line = max(1, first_line)
        last_line = min(total_lines, max(last_line, first_line + 20))
        
        # 绘制行号，调整样式和位置
        for line_num in range(first_line, last_line + 1):
            try:
                y_coord = self.editor.dlineinfo(f"{line_num}.0")
                if y_coord:
                    self.line_numbers.create_text(
                        25,  # 调整水平位置，使行号居中显示
                        y_coord[1] + y_coord[3]//2,  # 垂直居中对齐
                        text=str(line_num), 
                        anchor="e",  # 右对齐
                        font=("Consolas", 9),
                        fill="#606060"
                    )
            except:
                continue
    
    def _apply_syntax_highlighting(self):
        """应用语法高亮"""
        # 保存当前光标位置
        current_pos = self.editor.index(tk.INSERT)
        
        # 清除所有标签（除了选择标签）
        for tag in self.editor.tag_names():
            if tag != "sel":
                self.editor.tag_remove(tag, "1.0", tk.END)
        
        # 配置标签样式
        self.editor.tag_configure("keyword", foreground="#0000FF", font=("Consolas", 11, "bold"))
        self.editor.tag_configure("function", foreground="#800000", font=("Consolas", 11))
        self.editor.tag_configure("string", foreground="#008000")
        self.editor.tag_configure("number", foreground="#FF8000")
        self.editor.tag_configure("operator", foreground="#800080")
        self.editor.tag_configure("comment", foreground="#808080", font=("Consolas", 11, "italic"))
        
        # 获取文本内容
        content = self.editor.get("1.0", tk.END)
        
        try:
            # 使用Pygments进行词法分析
            tokens = list(lex(content, SqlLexer()))
            
            # 应用高亮
            pos = "1.0"
            for token_type, value in tokens:
                # 计算结束位置
                end_pos = self.editor.index(f"{pos}+{len(value)}c")
                
                # 根据token类型应用不同的标签
                if token_type in Token.Keyword:
                    self.editor.tag_add("keyword", pos, end_pos)
                elif token_type in Token.Name.Function:
                    self.editor.tag_add("function", pos, end_pos)
                elif token_type in Token.Literal.String:
                    self.editor.tag_add("string", pos, end_pos)
                elif token_type in Token.Literal.Number:
                    self.editor.tag_add("number", pos, end_pos)
                elif token_type in Token.Operator:
                    self.editor.tag_add("operator", pos, end_pos)
                elif token_type in Token.Comment:
                    self.editor.tag_add("comment", pos, end_pos)
                
                # 更新位置
                pos = end_pos
        except Exception as e:
            # 如果Pygments失败，使用基本高亮
            self._apply_basic_highlighting()
        
        # 恢复光标位置
        self.editor.mark_set(tk.INSERT, current_pos)
    
    def _apply_basic_highlighting(self):
        """应用基本的语法高亮（备用方案）"""
        content = self.editor.get("1.0", tk.END)
        
        # 高亮SQL关键字
        for keyword in self.keywords:
            start_pos = "1.0"
            keyword_pattern = r'\b' + re.escape(keyword) + r'\b'
            
            while True:
                start_pos = self.editor.search(keyword_pattern, start_pos, tk.END, regexp=True, nocase=True)
                if not start_pos:
                    break
                
                end_pos = f"{start_pos}+{len(keyword)}c"
                self.editor.tag_add("keyword", start_pos, end_pos)
                start_pos = end_pos
        
        # 高亮字符串 (单引号和双引号)
        for quote in ["'", '"']:
            start_pos = "1.0"
            while True:
                start_pos = self.editor.search(quote, start_pos, tk.END)
                if not start_pos:
                    break
                
                end_pos = self.editor.search(quote, f"{start_pos}+1c", tk.END)
                if not end_pos:
                    break
                
                end_pos = f"{end_pos}+1c"
                self.editor.tag_add("string", start_pos, end_pos)
                start_pos = end_pos
        
        # 高亮注释 (--开头的行)
        start_pos = "1.0"
        while True:
            start_pos = self.editor.search(r'--', start_pos, tk.END, regexp=True)
            if not start_pos:
                break
            
            line = start_pos.split('.')[0]
            end_pos = f"{line}.end"
            self.editor.tag_add("comment", start_pos, end_pos)
            start_pos = f"{int(line) + 1}.0"
    
    def get_query(self) -> str:
        """
        获取当前查询文本
        
        Returns:
            str: 查询文本
        """
        return self.editor.get("1.0", tk.END).strip()
    
    def set_query(self, query: str):
        """
        设置查询文本
        
        Args:
            query: 查询文本
        """
        self.editor.delete("1.0", tk.END)
        self.editor.insert(tk.END, query)
        self._apply_syntax_highlighting()
        self._update_line_numbers()
    
    def set_status(self, message: str):
        """
        设置状态栏消息
        
        Args:
            message: 状态消息
        """
        self.status_bar.config(text=message) 