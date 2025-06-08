# QueryX - SQL查询工具

基于Python的SQL查询工具，支持对Excel、CSV和JSON文件进行SQL查询，并提供友好的GUI界面。

## 功能特点

- **多格式支持**：支持Excel(.xlsx/.xls/.xlsm)、CSV(.csv)和JSON(.json)文件
- **SQL查询**：使用DuckDB作为SQL引擎，支持标准SQL语法
- **可视化界面**：基于Tkinter构建的简洁直观的图形界面，统一的应用图标风格
- **表结构浏览**：可通过侧边栏图标打开表结构面板，以树形展示表和字段，支持表字段搜索
- **文件预览**：按需加载文件预览内容，支持拖动调整预览区域大小
- **结果分页**：大数据集结果自动分页显示
- **结果过滤和排序**：在结果面板中可以直接对数据进行筛选和排序
- **多格式导出**：支持将查询结果导出为Excel、CSV或JSON格式
- **查询历史**：自动保存查询历史，方便重复使用
- **智能侧边栏**：类似IDEA的侧边栏设计，可以灵活控制面板的显示和隐藏
- **SQL编辑增强**：语法高亮、自动补全、剪切/复制/粘贴操作和一键格式化SQL语句
- **右键菜单功能**：文件列表支持右键菜单，可快速预览和查询文件
- **优化帮助系统**：提供可滚动的帮助对话框和美观的关于界面

## 安装方法

### 环境要求

- Python 3.6+
- 依赖库：duckdb, pandas, openpyxl, pillow, pyperclip, pygments, sqlparse

### 安装步骤

1. 克隆或下载本仓库

```bash
git clone https://github.com/qulei0126/QueryX.git
cd QueryX
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

### 打包为可执行文件

如果希望将应用打包为独立的Windows可执行文件，可以使用以下方法：

#### 方法一：使用命令行直接打包

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包应用（带有应用图标和资源文件）
pyinstaller --onefile --windowed --add-data "app/resources/*.ico;app/resources" --add-data "app/resources/*.py;app/resources" --icon="app/resources/icon.ico" --name="QueryX" main.py
```

#### 方法二：使用spec文件（推荐）

这种方法提供更精细的控制，确保窗口图标在打包后正确显示：

```bash
# 使用项目中提供的spec文件打包
pyinstaller QueryX.spec
```

打包后的可执行文件将位于`dist`目录中，双击即可运行，无需安装Python环境。

#### 常见问题解决

如果打包后的程序窗口图标不正确：
1. 确保使用了spec文件打包或正确包含了所有资源文件
2. 检查是否正确处理了PyInstaller打包环境下的资源路径
3. 对于Windows，可以尝试使用`--win-private-assemblies`参数

## 使用方法

### 启动应用

```bash
python main.py
```

### 基本操作流程

1. **加载数据文件**
   - 点击"添加文件"按钮选择Excel、CSV或JSON文件
   - 支持同时加载多个文件
   - 文件将显示在左侧文件面板中
   - 支持右键点击文件，选择"预览"查看文件内容，或选择"查询"直接查询所有记录

2. **界面操作**
   - 左侧有一个类似IDEA的侧边栏，包含多个功能按钮
   - "📁"按钮：显示/隐藏文件面板
   - "📊"按钮：显示/隐藏表结构面板
   - "📜"按钮：显示/隐藏历史面板
   - 也可以通过"视图"菜单控制各面板的显示和隐藏

3. **表结构浏览**
   - 点击"📊"按钮可打开表结构面板，以树形结构展示所有表及其字段
   - 每个表和字段都有直观的图标标识：表(📊)、主键(🔑)、外键(🔗)、普通字段(📝)、数字字段(🔢)、日期字段(📅)
   - 双击表名可展开/收起表字段列表
   - 双击字段名可将表名.字段名插入到SQL编辑器光标处
   - 可使用搜索框快速查找表或字段
   - 右键点击表名可选择"显示前10行"、"查询全表"或"复制表名"
   - 右键点击字段名可选择"复制字段名"

4. **编写SQL查询**
   - 在中央编辑器中输入SQL查询语句
   - 使用表名作为FROM子句（表名为文件名，不含扩展名）
   - 例如：`SELECT * FROM employees WHERE salary > 10000`
   - 可以使用"格式化SQL"按钮或快捷键Ctrl+F自动格式化SQL语句
   - 支持标准的剪切(Ctrl+X)、复制(Ctrl+C)、粘贴(Ctrl+V)操作

5. **执行查询**
   - 点击"执行查询"按钮或按Ctrl+Enter
   - 结果将显示在下方结果面板中

6. **浏览和导出结果**
   - 使用分页控制浏览大数据集
   - 点击"导出结果"按钮将结果保存为Excel、CSV或JSON格式

7. **查询历史**
   - 历史查询会自动保存在历史面板中
   - 双击历史记录或选中后点击"使用选中"按钮可以重新加载查询

## 示例查询

假设加载了一个名为"employees.csv"的文件：

```sql
-- 查询所有员工
SELECT * FROM employees

-- 查询高薪员工
SELECT name, salary FROM employees WHERE salary > 10000

-- 按部门统计平均薪资
SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department

-- 连接多个表
SELECT e.name, e.salary, d.department_name 
FROM employees e JOIN departments d ON e.dept_id = d.id
```

## 项目结构

```
QueryX/
├── app/                  # 应用主目录
│   ├── __init__.py          # 应用包初始化，包含版本和作者信息
│   ├── core/             # 核心功能模块
│   │   ├── __init__.py      # 核心模块初始化，导出核心类
│   │   ├── file_handler.py  # 文件处理
│   │   ├── query_engine.py  # 查询引擎
│   │   └── exporter.py      # 导出功能
│   ├── gui/              # GUI界面模块
│   │   ├── __init__.py      # GUI模块初始化，导出界面组件
│   │   ├── main_window.py   # 主窗口
│   │   ├── file_panel.py    # 文件面板
│   │   ├── sql_editor.py    # SQL编辑器
│   │   ├── result_panel.py  # 结果面板
│   │   ├── history_panel.py # 历史记录面板
│   │   ├── schema_panel.py  # 表结构面板
│   │   ├── settings_dialog.py # 设置对话框
│   │   └── dialogs/         # 对话框组件
│   │       ├── __init__.py    # 对话框模块初始化，导出对话框类
│   │       ├── help_dialog.py # 帮助对话框
│   │       └── about_dialog.py # 关于对话框
│   ├── resources/        # 资源文件
│   │   ├── __init__.py      # 资源路径管理，导出资源常量
│   │   ├── icon.ico         # 应用图标
│   │   └── help_content.py  # 帮助内容文本
│   └── utils/            # 工具函数
│       ├── __init__.py      # 工具模块初始化，导出工具函数
│       └── helpers.py       # 辅助功能
├── examples/             # 示例文件
├── main.py               # 主程序入口
└── requirements.txt      # 依赖列表
```

## 许可证

MIT License

## 更新日志