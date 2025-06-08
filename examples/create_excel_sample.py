#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建Excel示例文件
"""

import pandas as pd
import os

# 创建示例数据
data = {
    'order_id': list(range(1, 11)),
    'customer_name': ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十', '郑十一', '王十二'],
    'product': ['笔记本电脑', '智能手机', '无线耳机', '机械键盘', '显示器', '游戏鼠标', '平板电脑', '移动硬盘', '固态硬盘', '路由器'],
    'quantity': [1, 2, 3, 1, 1, 2, 1, 3, 2, 1],
    'price': [5999.99, 3999.00, 899.00, 499.00, 1299.00, 299.00, 2599.00, 399.00, 599.00, 199.00],
    'order_date': ['2023-01-05', '2023-01-10', '2023-01-15', '2023-01-20', '2023-01-25', 
                  '2023-02-01', '2023-02-05', '2023-02-10', '2023-02-15', '2023-02-20'],
    'status': ['已发货', '已完成', '已完成', '已发货', '已完成', '处理中', '已发货', '已完成', '已发货', '处理中']
}

# 创建DataFrame
df = pd.DataFrame(data)

# 计算总价
df['total'] = df['quantity'] * df['price']

# 确保examples目录存在
os.makedirs('examples', exist_ok=True)

# 保存为Excel文件
excel_path = 'examples/orders.xlsx'
df.to_excel(excel_path, index=False)

print(f"Excel示例文件已创建: {excel_path}")

# 显示数据预览
print("\n数据预览:")
print(df.head()) 