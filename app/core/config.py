#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
管理应用程序的各种配置信息
"""

import os
import json
from typing import Dict, Any, Optional

# 应用程序配置默认值
DEFAULT_CONFIG = {
    # 通用配置
    "general": {
        "max_history_size": 20,  # 历史记录最大数量
        "default_page_size": 100,  # 默认分页大小
    },
    
    # SQL格式化配置
    "sql_format": {
        "keyword_case": "upper",       # 关键字大小写：'upper', 'lower', 'capitalize'
        "identifier_case": "lower",     # 标识符大小写：'upper', 'lower', 'capitalize'
        "strip_comments": False,        # 是否删除注释
        "reindent": True,               # 是否重新缩进
        "indent_width": 4,              # 缩进宽度(空格数)
        "comma_first": False,           # 逗号是否放在行首
        "use_space_around_operators": True,  # 运算符周围是否加空格
    }
}

class ConfigManager:
    """配置管理类，负责加载、保存和访问配置"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.config_path = os.path.expanduser("~/.queryx/config.json")
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """从配置文件加载配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 更新配置，保留默认值
                    for section, values in loaded_config.items():
                        if section in self.config:
                            self.config[section].update(values)
                        else:
                            self.config[section] = values
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False
    
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置项值
        
        Args:
            section: 配置节名称
            key: 配置项键名
            default: 默认值，当配置不存在时返回
            
        Returns:
            配置项的值
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception:
            return default
    
    def set_config(self, section: str, key: str, value: Any) -> None:
        """
        设置配置项值
        
        Args:
            section: 配置节名称
            key: 配置项键名
            value: 配置项值
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_sql_format_options(self) -> Dict[str, Any]:
        """
        获取SQL格式化配置选项
        
        Returns:
            Dict[str, Any]: SQL格式化配置选项字典
        """
        return self.config.get("sql_format", DEFAULT_CONFIG["sql_format"])

# 创建全局配置管理器实例
config_manager = ConfigManager() 