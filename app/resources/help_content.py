#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
帮助内容模块
存储应用程序的帮助文本内容
"""

# 帮助文本内容
HELP_TEXT = """QueryX - SQL查询工具使用帮助
        
1. 文件操作：
- 点击"添加文件"按钮选择Excel(.xlsx/.xls/.xlsm)、CSV(.csv)或JSON(.json)文件
- 支持同时加载多个文件
- 文件将显示在左侧文件面板中，包含文件名、类型、大小、行数和列数信息
- 可通过文件面板的"移除选中"或"清空所有"按钮管理文件
- 支持右键点击文件，选择"预览"查看文件内容，或选择"查询"直接查询所有记录

2. 界面操作：
- 左侧有一个类似IDEA的侧边栏，包含多个功能按钮
- "📁"按钮：显示/隐藏文件面板
- "📊"按钮：显示/隐藏表结构面板
- "📜"按钮：显示/隐藏历史面板
- 也可以通过"视图"菜单控制各面板的显示和隐藏

3. 表结构浏览：
- 点击"📊"按钮可打开表结构面板，以树形结构展示所有表及其字段
- 每个表和字段都有直观的图标标识
- 双击表名可展开/收起表字段列表
- 双击字段名可将表名.字段名插入到SQL编辑器光标处
- 可使用搜索框快速查找表或字段
- 右键点击表名可选择"显示前10行"、"查询全表"或"复制表名"
- 右键点击字段名可选择"复制字段名"

4. 编写SQL查询：
- 在中央编辑器中输入SQL查询语句
- 使用表名作为FROM子句（表名为文件名，不含扩展名）
- 例如：SELECT * FROM employees WHERE salary > 10000
- 可以使用"格式化SQL"按钮或快捷键Ctrl+F自动格式化SQL语句
- 支持SQL语法高亮显示
- 支持标准的剪切(Ctrl+X)、复制(Ctrl+C)、粘贴(Ctrl+V)操作

5. 执行查询：
- 点击"执行查询"按钮或按Ctrl+Enter执行当前查询
- 结果将显示在下方结果面板中

6. 浏览和处理结果：
- 结果以表格形式显示，支持分页浏览
- 可直接在结果面板中对数据进行筛选和排序，无需重新执行SQL查询
- 点击列标题可快速排序（支持升序和降序切换）
- 点击"显示过滤/排序"按钮可展开过滤功能区域
- 过滤和排序后的结果可以直接导出
- 点击"导出结果"按钮将结果保存为Excel、CSV或JSON格式

7. 查询历史：
- 历史查询会自动保存在历史面板中
- 双击历史记录或选中后点击"使用选中"按钮可以重新加载查询
- 可以通过"清空历史"按钮清除所有历史记录

8. 格式化设置：
- 通过"编辑"菜单中的"SQL格式化设置"可以自定义格式化选项
- 可设置关键字大小写、标识符大小写、缩进宽度等选项

9. 文件预览：
- 双击文件或右键选择"预览"可查看文件内容
- 预览区域可通过垂直分割条调整大小
- 可随时关闭预览区域，专注于文件列表
"""

# 关于文本内容
ABOUT_TEXT = """QueryX - SQL查询工具
        
版本: 1.0.0
        
一个基于Python的SQL查询工具，支持对Excel、CSV和JSON文件进行SQL查询。
        
使用技术:
- Python 3.x
- DuckDB (SQL引擎)
- Tkinter (GUI框架)
- Pandas (数据处理)

项目地址:
https://github.com/qulei0126/QueryX

欢迎访问GitHub仓库获取最新版本和提交问题反馈。
""" 