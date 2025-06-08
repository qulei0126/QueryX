#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
辅助工具模块
提供各种辅助功能
"""

import os
import re
import pyperclip
from typing import Dict, List, Tuple, Optional, Any
import sqlparse

# 导入配置管理器
from app.core.config import config_manager


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小(字节)
        
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def validate_sql_query(query: str) -> Tuple[bool, str]:
    """
    简单验证SQL查询语法
    
    Args:
        query: SQL查询语句
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    # 检查基本语法
    if not query.strip():
        return False, "查询不能为空"
    
    # 检查是否有SELECT语句
    if not re.search(r'SELECT\s+', query, re.IGNORECASE):
        return False, "查询必须包含SELECT语句"
    
    # 检查括号是否匹配
    if query.count('(') != query.count(')'):
        return False, "括号不匹配"
    
    # 检查引号是否匹配
    single_quotes = len(re.findall(r"(?<!')'(?!')|^'|'$", query))
    if single_quotes % 2 != 0:
        return False, "单引号不匹配"
    
    double_quotes = len(re.findall(r'(?<!")"(?!")|^"|"$', query))
    if double_quotes % 2 != 0:
        return False, "双引号不匹配"
    
    return True, ""


def format_sql(sql: str) -> str:
    """
    格式化SQL查询语句
    
    Args:
        sql: 原始SQL查询语句
        
    Returns:
        str: 格式化后的SQL查询语句
    """
    # 使用sqlparse库进行格式化
    
    # 从配置管理器获取格式化选项
    options = config_manager.get_sql_format_options()
    
    # 执行格式化
    formatted_sql = sqlparse.format(sql, **options)
    
    return formatted_sql


def get_sql_keywords() -> List[str]:
    """
    获取SQL关键字列表，用于语法高亮
    
    Returns:
        List[str]: SQL关键字列表
    """
    return [
        "SELECT", "FROM", "WHERE", "GROUP BY", "HAVING", "ORDER BY",
        "LIMIT", "OFFSET", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
        "FULL JOIN", "ON", "AS", "AND", "OR", "NOT", "IN", "BETWEEN",
        "LIKE", "IS NULL", "IS NOT NULL", "COUNT", "SUM", "AVG", "MIN",
        "MAX", "DISTINCT", "UNION", "INTERSECT", "EXCEPT", "CASE", "WHEN",
        "THEN", "ELSE", "END", "WITH", "INSERT", "UPDATE", "DELETE"
    ]


def copy_to_clipboard(text: str) -> None:
    """
    复制文本到剪贴板
    
    Args:
        text: 要复制的文本
    """
    pyperclip.copy(text)


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件扩展名(不包含点号)
    """
    return os.path.splitext(file_path)[1][1:].lower()


def is_supported_file(file_path: str) -> bool:
    """
    检查文件是否为支持的格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否支持
    """
    supported_extensions = ['xlsx', 'xls', 'xlsm', 'csv', 'json']
    ext = get_file_extension(file_path)
    return ext in supported_extensions 