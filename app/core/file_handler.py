#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件处理模块
负责加载和处理不同格式的文件(Excel, CSV, JSON)
"""

import os
import json
import pandas as pd
from typing import Dict, List, Tuple, Optional


class FileHandler:
    """文件处理类，用于加载和处理不同格式的文件"""
    
    def __init__(self):
        """初始化文件处理器"""
        self.loaded_files = {}  # 存储已加载的文件 {文件路径: DataFrame}
        self.file_info = {}     # 存储文件信息 {文件路径: {"name": 文件名, "type": 文件类型, "size": 文件大小}}
    
    def load_file(self, file_path: str) -> Tuple[bool, str]:
        """
        加载文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[bool, str]: (是否成功, 成功/错误信息)
        """
        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}"
        
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        base_name = os.path.splitext(file_name)[0]
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        # 检查是否存在同名但不同后缀的文件
        for existing_path in self.loaded_files.keys():
            existing_file_name = os.path.basename(existing_path)
            existing_base_name = os.path.splitext(existing_file_name)[0]
            existing_ext = os.path.splitext(existing_file_name)[1].lower()
            
            # 如果基本名称相同但扩展名不同，则报错
            if existing_base_name == base_name and existing_ext != file_ext:
                return False, f"已存在同名但不同格式的文件: {existing_file_name}。不允许添加同名不同格式的文件。"
        
        try:
            # 根据文件扩展名选择加载方法
            if file_ext in ['.xlsx', '.xls', '.xlsm']:
                df = pd.read_excel(file_path)
            elif file_ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
                # 尝试不同编码
                if df.empty or len(df.columns) <= 1:
                    df = pd.read_csv(file_path, encoding='gbk')
            elif file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 如果是列表数据，直接转为DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                # 如果是字典，需要处理嵌套结构
                else:
                    df = pd.json_normalize(data)
            else:
                return False, f"不支持的文件格式: {file_ext}"
            
            # 存储加载的文件
            table_name = os.path.splitext(file_name)[0]
            # 替换表名中的特殊字符
            table_name = ''.join(c if c.isalnum() else '_' for c in table_name)
            
            self.loaded_files[file_path] = {
                'dataframe': df,
                'table_name': table_name
            }
            
            # 存储文件信息
            self.file_info[file_path] = {
                'name': file_name,
                'type': file_ext[1:].upper(),  # 去掉点号
                'size': f"{file_size:.2f} KB",
                'rows': len(df),
                'columns': len(df.columns)
            }
            
            return True, f"成功加载文件: {file_name}"
        
        except Exception as e:
            return False, f"加载文件出错: {str(e)}"
    
    def remove_file(self, file_path: str) -> None:
        """
        从已加载列表中移除文件
        
        Args:
            file_path: 文件路径
        """
        if file_path in self.loaded_files:
            del self.loaded_files[file_path]
        
        if file_path in self.file_info:
            del self.file_info[file_path]
    
    def get_loaded_files(self) -> Dict:
        """
        获取已加载的文件信息
        
        Returns:
            Dict: 文件信息字典
        """
        return self.file_info
    
    def get_table_names(self) -> Dict[str, str]:
        """
        获取所有表名和对应的文件路径
        
        Returns:
            Dict[str, str]: {表名: 文件路径}
        """
        return {info['table_name']: path for path, info in self.loaded_files.items()}
    
    def get_dataframes(self) -> Dict[str, pd.DataFrame]:
        """
        获取所有数据框和对应的表名
        
        Returns:
            Dict[str, pd.DataFrame]: {表名: DataFrame}
        """
        return {info['table_name']: info['dataframe'] for path, info in self.loaded_files.items()} 