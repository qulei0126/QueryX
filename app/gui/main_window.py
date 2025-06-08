#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块
整合所有GUI组件，实现主界面功能
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

from app.core.file_handler import FileHandler
from app.core.query_engine import QueryEngine
from app.gui.file_panel import FilePanel
from app.gui.sql_editor import SQLEditor
from app.gui.result_panel import ResultPanel
from app.gui.history_panel import HistoryPanel
from app.gui.schema_panel import SchemaPanel
from app.gui.settings_dialog import SqlFormatSettingsDialog

# 导入项目资源
from app.resources import ICON_PATH

class MainWindow:
    """主窗口类，整合所有GUI组件"""
    
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.root.title("QueryX - SQL查询工具")
        self.root.geometry("1280x800")  # 增加默认窗口宽度
        self.root.minsize(900, 600)     # 增加最小窗口宽度
        
        # 设置应用程序图标
        import os
        if os.path.exists(ICON_PATH):
            self.root.iconbitmap(ICON_PATH)
        
        # 初始化核心组件
        self.file_handler = FileHandler()
        self.query_engine = QueryEngine()
        
        # 面板状态，默认收缩
        self.file_panel_visible = True
        self.history_panel_visible = False
        self.schema_panel_visible = False  # 表结构面板默认隐藏
        
        # 表结构信息缓存
        self.tables_info = {}  # {表名: [字段列表]}
        
        # 创建界面
        self._create_widgets()
        self._create_menu()
        
        # 应用面板初始可见性设置
        self._update_panels_visibility()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 定期更新表结构信息
        self.root.after(500, self._update_schema_info)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 状态栏 - 先创建状态栏，确保它始终位于底部
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建主分隔面板
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧边栏容器
        self.sidebar_container = ttk.Frame(self.main_paned, width=40)
        self.main_paned.add(self.sidebar_container, weight=0)
        
        # 创建侧边栏按钮区域
        self.sidebar_buttons = ttk.Frame(self.sidebar_container)
        self.sidebar_buttons.pack(side=tk.TOP, fill=tk.Y, expand=True)
        
        # 文件面板按钮
        self.file_panel_btn = ttk.Button(
            self.sidebar_buttons,
            text="📁",
            width=2,
            command=self._toggle_file_panel
        )
        self.file_panel_btn.pack(side=tk.TOP, pady=5)
        # 添加鼠标悬停提示
        self._create_tooltip(self.file_panel_btn, "文件面板")
        
        # 表结构面板按钮
        self.schema_panel_btn = ttk.Button(
            self.sidebar_buttons,
            text="📊",
            width=2,
            command=self._toggle_schema_panel
        )
        self.schema_panel_btn.pack(side=tk.TOP, pady=5)
        # 添加鼠标悬停提示
        self._create_tooltip(self.schema_panel_btn, "表结构")
        
        # 历史面板按钮
        self.history_panel_btn = ttk.Button(
            self.sidebar_buttons,
            text="📜",
            width=2,
            command=self._toggle_history_panel
        )
        self.history_panel_btn.pack(side=tk.TOP, pady=5)
        # 添加鼠标悬停提示
        self._create_tooltip(self.history_panel_btn, "查询历史")
        
        # 左侧面板（文件选择、表结构和历史记录）
        self.left_panel_container = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_panel_container, weight=1)
        
        # 右侧面板（SQL编辑器和结果显示）
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.right_paned, weight=4)  # 增加右侧面板权重，从3到4
        
        # 左侧分隔：文件面板、表结构和历史记录
        self.left_paned = ttk.PanedWindow(self.left_panel_container, orient=tk.VERTICAL)
        self.left_paned.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择面板容器
        self.file_panel_container = ttk.Frame(self.left_paned)
        self.left_paned.add(self.file_panel_container, weight=2)
        
        # 文件面板标题栏
        self.file_panel_header = ttk.Frame(self.file_panel_container)
        self.file_panel_header.pack(fill=tk.X)
        
        self.file_panel_title = ttk.Label(self.file_panel_header, text="文件面板", font=("Arial", 10, "bold"))
        self.file_panel_title.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 文件选择面板
        self.file_panel = FilePanel(self.file_panel_container, self._on_load_file, self.remove_file)
        self.file_panel.pack(fill=tk.BOTH, expand=True)
        # 设置查询回调函数
        self.file_panel.set_query_callback(self._on_execute_query)
        # 设置查询引擎实例
        self.file_panel.set_query_engine(self.query_engine)
        
        # 表结构面板容器
        self.schema_panel_container = ttk.Frame(self.left_paned)
        self.left_paned.add(self.schema_panel_container, weight=2)
        
        # 表结构面板标题栏
        self.schema_panel_header = ttk.Frame(self.schema_panel_container)
        self.schema_panel_header.pack(fill=tk.X)
        
        self.schema_panel_title = ttk.Label(self.schema_panel_header, text="表结构", font=("Arial", 10, "bold"))
        self.schema_panel_title.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 表结构面板
        self.schema_panel = SchemaPanel(self.schema_panel_container, self._on_schema_select)
        self.schema_panel.pack(fill=tk.BOTH, expand=True)
        
        # 历史记录面板容器
        self.history_panel_container = ttk.Frame(self.left_paned)
        self.left_paned.add(self.history_panel_container, weight=1)
        
        # 历史面板标题栏
        self.history_panel_header = ttk.Frame(self.history_panel_container)
        self.history_panel_header.pack(fill=tk.X)
        
        self.history_panel_title = ttk.Label(self.history_panel_header, text="查询历史", font=("Arial", 10, "bold"))
        self.history_panel_title.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 历史记录面板
        self.history_panel = HistoryPanel(self.history_panel_container, self._on_history_select)
        self.history_panel.pack(fill=tk.BOTH, expand=True)
        
        # SQL编辑器
        self.sql_editor = SQLEditor(self.right_paned, self._on_execute_query)
        self.right_paned.add(self.sql_editor, weight=3)  # 增加SQL编辑器权重，从2到3
        
        # 结果显示面板
        self.result_panel = ResultPanel(self.right_paned)
        self.right_paned.add(self.result_panel, weight=2)  # 减少结果面板权重，从3到2
    
    def _create_tooltip(self, widget, text):
        """为控件创建鼠标悬停提示"""
        def enter(event):
            # 创建提示窗口
            tooltip = tk.Toplevel(self.root)
            tooltip.wm_overrideredirect(True)  # 去掉窗口边框
            tooltip.wm_attributes("-topmost", True)  # 保持在最上层
            
            # 存储tooltip引用，以便在leave事件中销毁
            widget.tooltip = tooltip
            
            # 创建提示内容标签
            label = tk.Label(tooltip, text=text, background="#FFFFCC", relief="solid", borderwidth=1,
                            padx=5, pady=2, wraplength=200, justify="left")
            label.pack()
            
            # 计算提示窗口位置
            x = widget.winfo_rootx() + widget.winfo_width() + 5
            y = widget.winfo_rooty() + (widget.winfo_height() // 2) - 10
            
            # 更新窗口大小以适应内容
            tooltip.update_idletasks()
            
            # 设置提示窗口位置
            tooltip.wm_geometry(f"+{x}+{y}")
            
        def leave(event):
            # 销毁提示窗口
            if hasattr(widget, "tooltip") and widget.tooltip:
                widget.tooltip.destroy()
                widget.tooltip = None
            
        # 绑定鼠标事件
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def _toggle_file_panel(self):
        """切换文件面板的显示/隐藏状态"""
        try:
            self.file_panel_visible = not self.file_panel_visible
            self._update_panels_visibility()
            
            # 高亮按钮显示选中状态
            if self.file_panel_visible:
                self.file_panel_btn.config(style='Selected.TButton')
            else:
                self.file_panel_btn.config(style='TButton')
                
            # 调整主窗口布局
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"切换文件面板时出错: {str(e)}")
    
    def _toggle_schema_panel(self):
        """切换表结构面板的显示/隐藏状态"""
        try:
            self.schema_panel_visible = not self.schema_panel_visible
            self._update_panels_visibility()
            
            # 高亮按钮显示选中状态
            if self.schema_panel_visible:
                self.schema_panel_btn.config(style='Selected.TButton')
            else:
                self.schema_panel_btn.config(style='TButton')
                
            # 调整主窗口布局
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"切换表结构面板时出错: {str(e)}")
    
    def _toggle_history_panel(self):
        """切换历史面板的显示/隐藏状态"""
        try:
            self.history_panel_visible = not self.history_panel_visible
            self._update_panels_visibility()
            
            # 高亮按钮显示选中状态
            if self.history_panel_visible:
                self.history_panel_btn.config(style='Selected.TButton')
            else:
                self.history_panel_btn.config(style='TButton')
                
            # 调整主窗口布局
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"切换历史面板时出错: {str(e)}")
    
    def _on_schema_select(self, table_name: str, column_name: str = None, query: str = None):
        """
        从表结构面板选择表或字段时的回调函数
        
        Args:
            table_name: 选中的表名
            column_name: 选中的列名，可选
            query: 直接执行的SQL查询，可选
        """
        if query:
            # 直接执行特定的查询
            self.sql_editor.set_query(query)
            self._on_execute_query(query)
        elif column_name:
            # 将表名.列名插入到SQL编辑器当前位置
            self.sql_editor.editor.insert(tk.INSERT, f"{table_name}.{column_name}")
        else:
            # 仅选中表名，不执行操作
            pass
            
    def _update_schema_info(self):
        """更新表结构信息，用于SQL编辑器自动补全和表结构面板"""
        try:
            # 更新所有已加载表的结构信息
            updated = False
            
            # 获取所有表名
            table_names = list(self.file_handler.get_table_names().keys())
            
            # 检查是否有新增的表
            for table_name in table_names:
                if table_name not in self.tables_info:
                    # 获取表结构
                    schema_df = self.query_engine.get_table_schema(table_name)
                    if schema_df is not None:
                        # 提取列名列表
                        columns = schema_df['name'].tolist()
                        self.tables_info[table_name] = columns
                        updated = True
            
            # 检查是否有表被删除
            for table_name in list(self.tables_info.keys()):
                if table_name not in table_names:
                    del self.tables_info[table_name]
                    updated = True
            
            # 如果有更新，则更新表结构面板的表结构信息
            if updated or not hasattr(self.schema_panel, 'tables_info') or not self.schema_panel.tables_info:
                self.schema_panel.update_schema_info(self.tables_info)
        
        except Exception as e:
            print(f"更新表结构信息时出错: {str(e)}")
        
        # 每5秒检查一次更新
        self.root.after(5000, self._update_schema_info)
    
    def _update_panels_visibility(self):
        """根据各面板的可见状态更新显示"""
        try:
            # 1. 先处理左侧分隔面板（文件面板、表结构和历史面板）
            # 清空左侧分隔面板中的所有面板
            for pane in list(self.left_paned.panes()):
                self.left_paned.forget(pane)
            
            # 检查是否有任何面板应该可见
            panels_visible = False
            
            # 按顺序添加需要显示的面板到左侧分隔面板
            if self.file_panel_visible:
                self.left_paned.add(self.file_panel_container, weight=2)
                panels_visible = True
            
            if self.schema_panel_visible:
                self.left_paned.add(self.schema_panel_container, weight=2)
                panels_visible = True
                
            if self.history_panel_visible:
                self.left_paned.add(self.history_panel_container, weight=1)
                panels_visible = True
            
            # 2. 然后处理主分隔面板
            # 获取当前主分隔面板中的所有组件
            main_panes = list(self.main_paned.panes())
            
            # 清空主分隔面板
            for pane in main_panes:
                self.main_paned.forget(pane)
            
            # 重新添加组件到主分隔面板
            # 始终添加侧边栏
            self.main_paned.add(self.sidebar_container, weight=0)
            
            # 根据面板可见性决定是否添加左侧面板容器
            if panels_visible:
                self.main_paned.add(self.left_panel_container, weight=1)
            
            # 始终添加右侧面板
            if panels_visible:
                self.main_paned.add(self.right_paned, weight=4)
            else:
                # 当没有左侧面板可见时，右侧面板占据更多空间
                self.main_paned.add(self.right_paned, weight=1)
            
            # 强制更新布局
            self.root.update_idletasks()
                
        except Exception as e:
            print(f"更新面板可见性时出错: {str(e)}")
    
    def _create_menu(self):
        """创建菜单栏"""
        # 创建自定义按钮样式
        style = ttk.Style()
        style.configure('Selected.TButton', background='lightblue')
        
        menu_bar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="添加文件", command=self._menu_add_files)
        file_menu.add_command(label="清空所有文件", command=self._menu_clear_files)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 查询菜单
        query_menu = tk.Menu(menu_bar, tearoff=0)
        query_menu.add_command(label="执行查询", command=self._on_execute_query)
        query_menu.add_command(label="格式化SQL", command=self._menu_format_sql)
        query_menu.add_command(label="SQL格式化设置", command=self._show_sql_format_settings)
        query_menu.add_separator()
        query_menu.add_command(label="清空编辑器", command=self._menu_clear_editor)
        query_menu.add_separator()
        query_menu.add_command(label="清空历史记录", command=self._menu_clear_history)
        menu_bar.add_cascade(label="查询", menu=query_menu)
        
        # 视图菜单
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="显示/隐藏文件面板", command=self._toggle_file_panel)
        view_menu.add_command(label="显示/隐藏表结构面板", command=self._toggle_schema_panel)
        view_menu.add_command(label="显示/隐藏历史面板", command=self._toggle_history_panel)
        menu_bar.add_cascade(label="视图", menu=view_menu)
        
        # 结果菜单
        result_menu = tk.Menu(menu_bar, tearoff=0)
        result_menu.add_command(label="导出结果", command=self._menu_export_result)
        result_menu.add_separator()
        result_menu.add_command(label="清空结果", command=self._menu_clear_result)
        menu_bar.add_cascade(label="结果", menu=result_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="使用帮助", command=self._menu_show_help)
        help_menu.add_command(label="关于", command=self._menu_show_about)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menu_bar)
        
        # 设置初始按钮状态
        if self.file_panel_visible:
            self.file_panel_btn.config(style='Selected.TButton')
        if self.schema_panel_visible:
            self.schema_panel_btn.config(style='Selected.TButton')
        if self.history_panel_visible:
            self.history_panel_btn.config(style='Selected.TButton')
    
    def _on_load_file(self, file_path: str):
        """
        加载文件回调函数
        
        Args:
            file_path: 文件路径
        """
        # 更新状态
        self.status_bar.config(text=f"正在加载文件: {os.path.basename(file_path)}...")
        self.root.update()
        
        # 加载文件
        success, message = self.file_handler.load_file(file_path)
        
        if success:
            # 获取文件信息
            file_info = self.file_handler.get_loaded_files()[file_path]
            
            # 获取表名信息，并添加到file_info中
            table_names = self.file_handler.get_table_names()
            for table_name, path in table_names.items():
                if path == file_path:
                    file_info['table_name'] = table_name
                    break
            
            # 添加到文件面板
            self.file_panel.add_file(file_path, file_info)
            
            # 更新状态
            self.status_bar.config(text=message)
            
            # 更新查询引擎中的数据
            dataframes = self.file_handler.get_dataframes()
            self.query_engine.register_dataframes(dataframes)
            
            # 更新SQL编辑器状态
            table_names = list(dataframes.keys())
            if table_names:
                example_query = f"SELECT * FROM {table_names[0]}"
                self.sql_editor.set_status(f"可用表: {', '.join(table_names)}")
                
                # 如果编辑器是默认内容，则更新为实际表名
                current_query = self.sql_editor.get_query()
                if "table_name" in current_query:
                    self.sql_editor.set_query(example_query)
        else:
            # 显示错误消息
            self.status_bar.config(text=message)
            messagebox.showerror("加载失败", message)
    
    def _on_execute_query(self, query: str = None):
        """
        执行查询回调函数
        
        Args:
            query: SQL查询语句，如果为None则从编辑器获取
        """

        # 获取查询语句
        if query is None:
            query = self.sql_editor.get_query()
        
        if not query.strip():
            messagebox.showinfo("提示", "请输入SQL查询语句")
            return
        
        # 更新状态
        self.status_bar.config(text="正在执行查询...")
        self.root.update()
        
        # 执行查询
        success, result, message = self.query_engine.execute_query(query)
        
        if success:
            # 显示结果
            self.result_panel.display_result(result, self.query_engine.execution_time)
            
            # 添加到历史记录
            self.history_panel.add_history(query)
            
            # 更新状态
            self.status_bar.config(text=message)
        else:
            # 显示错误消息
            self.status_bar.config(text=message)
            messagebox.showerror("查询失败", message)
            self.result_panel.set_status(f"查询失败: {message}")
    
    def _on_history_select(self, query: str):
        """
        选择历史记录回调函数
        
        Args:
            query: 选中的SQL查询语句
        """
        # 设置编辑器内容
        self.sql_editor.set_query(query)
        
        # 更新状态
        self.status_bar.config(text="已加载历史查询")
    
    def _menu_add_files(self):
        """菜单：添加文件"""
        self.file_panel._on_add_files()
    
    def _menu_clear_files(self):
        """菜单：清空所有文件"""
        self.file_panel._on_clear_all()
    
    def remove_file(self, file_path: str):
        """
        从文件处理器中移除文件
        
        Args:
            file_path: 要移除的文件路径
        """
        # 获取要移除的表名
        table_to_remove = None
        table_names = self.file_handler.get_table_names()
        for table_name, path in table_names.items():
            if path == file_path:
                table_to_remove = table_name
                break
        
        # 从文件处理器中移除
        self.file_handler.remove_file(file_path)
        
        # 从查询引擎中移除表
        if table_to_remove:
            self.query_engine.remove_table(table_to_remove)
            
            # 从表结构信息缓存中移除
            if table_to_remove in self.tables_info:
                del self.tables_info[table_to_remove]
                # 更新表结构面板
                self.schema_panel.update_schema_info(self.tables_info)
        
        # 更新SQL编辑器状态
        remaining_tables = list(self.file_handler.get_table_names().keys())
        if remaining_tables:
            self.sql_editor.set_status(f"可用表: {', '.join(remaining_tables)}")
        else:
            self.sql_editor.set_status("无可用表")
    
    def _menu_clear_editor(self):
        """菜单：清空编辑器"""
        self.sql_editor._on_clear()
    
    def _menu_format_sql(self):
        """菜单：格式化SQL"""
        self.sql_editor._on_format_sql()
    
    def _show_sql_format_settings(self):
        """菜单：显示SQL格式化设置对话框"""
        # 创建设置对话框
        SqlFormatSettingsDialog(self.root, on_save_callback=self._on_sql_format_settings_saved)
    
    def _on_sql_format_settings_saved(self):
        """SQL格式化设置保存后的回调函数"""
        # 更新状态栏
        self.status_bar.config(text="SQL格式化设置已更新")
    
    def _menu_clear_history(self):
        """菜单：清空历史记录"""
        self.history_panel._on_clear_history()
    
    def _menu_export_result(self):
        """菜单：导出结果"""
        self.result_panel._on_export()
    
    def _menu_clear_result(self):
        """菜单：清空结果"""
        self.result_panel._clear_result()
    
    def _menu_show_help(self):
        """菜单：显示帮助"""
        # 导入帮助内容
        from app.resources.help_content import HELP_TEXT
        # 使用可滚动的帮助对话框
        from app.gui.dialogs.help_dialog import HelpDialog
        HelpDialog(self.root, title="使用帮助", help_text=HELP_TEXT)
    
    def _menu_show_about(self):
        """菜单：显示关于"""
        # 导入关于内容和对话框
        from app.resources.help_content import ABOUT_TEXT
        from app.gui.dialogs.about_dialog import AboutDialog
        # 显示关于对话框
        AboutDialog(self.root, title="关于", about_text=ABOUT_TEXT)
    
    def _on_close(self):
        """关闭窗口"""
        if messagebox.askyesno("确认退出", "确定要退出程序吗？"):
            self.root.destroy()
    
    def start(self):
        """启动应用程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.start() 