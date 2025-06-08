#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
查询引擎模块
使用DuckDB执行SQL查询
"""

import time
import duckdb
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any


class QueryEngine:
    """查询引擎类，使用DuckDB执行SQL查询"""
    
    def __init__(self):
        """初始化查询引擎"""
        self.conn = duckdb.connect(database=':memory:', read_only=False)
        self.query_history = []  # 存储查询历史
        self.last_result = None  # 存储最近一次查询结果
        self.execution_time = 0  # 存储查询执行时间(毫秒)
        self.registered_tables = set()  # 存储已注册的表名
    
    def register_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """
        注册数据框到DuckDB
        
        Args:
            dataframes: {表名: DataFrame} 字典
        """
        # 获取当前要注册的表名集合
        current_tables = set(dataframes.keys())
        
        # 找出需要删除的表（已注册但不在当前dataframes中的表）
        tables_to_remove = self.registered_tables - current_tables
        
        # 删除不再需要的表
        for table_name in tables_to_remove:
            self._drop_table(table_name)
        
        # 注册或更新当前的表
        for table_name, df in dataframes.items():
            # 如果表已存在，先删除
            if table_name in self.registered_tables:
                self._drop_table(table_name)
            
            # 注册新表
            self.conn.register(table_name, df)
        
        # 更新已注册表集合
        self.registered_tables = current_tables
    
    def remove_table(self, table_name: str) -> bool:
        """
        从DuckDB中移除指定的表
        
        Args:
            table_name: 要移除的表名
            
        Returns:
            bool: 是否成功移除
        """
        if table_name in self.registered_tables:
            success = self._drop_table(table_name)
            if success:
                self.registered_tables.remove(table_name)
            return success
        return False
    
    def _drop_table(self, table_name: str) -> bool:
        """
        从DuckDB中删除表或视图
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 是否成功删除
        """
        try:
            # 尝试删除表，使用双引号包裹表名
            self.conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            return True
        except Exception:
            try:
                # 如果失败，尝试删除视图，使用双引号包裹表名
                self.conn.execute(f'DROP VIEW IF EXISTS "{table_name}"')
                return True
            except Exception:
                return False
    
    def execute_query(self, query: str) -> Tuple[bool, Any, str]:
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            
        Returns:
            Tuple[bool, Any, str]: (是否成功, 结果DataFrame或None, 成功/错误信息)
        """
        if not query.strip():
            return False, None, "查询语句不能为空"
        
        # 记录查询历史
        if query not in self.query_history:
            self.query_history.append(query)
            if len(self.query_history) > 20:  # 最多保留20条历史记录
                self.query_history.pop(0)
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 执行查询
            result = self.conn.execute(query).fetchdf()
            
            # 计算执行时间(毫秒)
            self.execution_time = (time.time() - start_time) * 1000
            
            # 存储结果
            self.last_result = result
            
            return True, result, f"查询成功，耗时: {self.execution_time:.2f}ms，返回 {len(result)} 行数据"
        
        except Exception as e:
            return False, None, f"查询执行错误: {str(e)}"
    
    def get_query_history(self) -> List[str]:
        """
        获取查询历史
        
        Returns:
            List[str]: 查询历史列表
        """
        return self.query_history
    
    def get_table_schema(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        获取表结构
        
        Args:
            table_name: 表名
            
        Returns:
            Optional[pd.DataFrame]: 表结构DataFrame
        """
        try:
            # 使用DuckDB的PRAGMA语句获取表结构
            schema = self.conn.execute(f'PRAGMA table_info("{table_name}")').fetchdf()
            return schema
        except Exception:
            return None
    
    def get_table_preview(self, table_name: str, limit: int = 5) -> Optional[pd.DataFrame]:
        """
        获取表数据预览
        
        Args:
            table_name: 表名
            limit: 返回行数，默认5行
            
        Returns:
            Optional[pd.DataFrame]: 表数据预览
        """
        try:
            preview = self.conn.execute(f'SELECT * FROM "{table_name}" LIMIT {limit}').fetchdf()
            return preview
        except Exception:
            return None 