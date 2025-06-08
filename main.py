#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
QueryX - SQL查询工具
主程序入口
"""

import sys
from app.gui.main_window import MainWindow

def main():
    """主程序入口"""
    app = MainWindow()
    app.start()

if __name__ == "__main__":
    main() 