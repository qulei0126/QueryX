#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导出模块
负责将查询结果导出为不同格式(Excel, CSV, JSON)
"""

import os
import json
import pandas as pd
from typing import Dict, List, Tuple, Optional


class Exporter:
    """导出类，用于将查询结果导出为不同格式"""
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame, file_path: str) -> Tuple[bool, str]:
        """
        导出为Excel格式
        
        Args:
            df: 数据框
            file_path: 导出文件路径
            
        Returns:
            Tuple[bool, str]: (是否成功, 成功/错误信息)
        """
        try:
            # 确保文件扩展名为.xlsx
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'
                
            # 导出到Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            return True, f"成功导出到Excel文件: {os.path.basename(file_path)}"
        
        except Exception as e:
            return False, f"导出Excel失败: {str(e)}"
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame, file_path: str, encoding: str = 'utf-8') -> Tuple[bool, str]:
        """
        导出为CSV格式
        
        Args:
            df: 数据框
            file_path: 导出文件路径
            encoding: 文件编码，默认utf-8
            
        Returns:
            Tuple[bool, str]: (是否成功, 成功/错误信息)
        """
        try:
            # 确保文件扩展名为.csv
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
                
            # 导出到CSV
            df.to_csv(file_path, index=False, encoding=encoding)
            
            return True, f"成功导出到CSV文件: {os.path.basename(file_path)}"
        
        except Exception as e:
            return False, f"导出CSV失败: {str(e)}"
    
    @staticmethod
    def export_to_json(df: pd.DataFrame, file_path: str, orient: str = 'records') -> Tuple[bool, str]:
        """
        导出为JSON格式
        
        Args:
            df: 数据框
            file_path: 导出文件路径
            orient: JSON格式，默认'records'
            
        Returns:
            Tuple[bool, str]: (是否成功, 成功/错误信息)
        """
        try:
            # 确保文件扩展名为.json
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
                
            # 导出到JSON
            df.to_json(file_path, orient=orient, force_ascii=False, indent=4)
            
            return True, f"成功导出到JSON文件: {os.path.basename(file_path)}"
        
        except Exception as e:
            return False, f"导出JSON失败: {str(e)}" 