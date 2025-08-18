#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SLTMX编辑器 - 主程序入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from config.language import load_language_config
from ui.main_window import TMXViewer

# 全局语言配置
LANG = load_language_config()

def main():
    """主程序入口"""
    # 启用高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app_name = LANG.get('app', {}).get('name', 'TMX Viewer')
    app.setApplicationName(app_name)
    
    # 设置高DPI缩放策略
    if hasattr(Qt, 'AA_DisableWindowContextHelpButton'):
        app.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
    
    # 设置应用程序图标（任务栏图标）
    try:
        icon_path = "icon.ico"
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
    except Exception as e:
        error_msg = LANG.get('icon', {}).get('icon_load_error_template', 'Failed to set icon: {}')
        print(error_msg.format(e))
    
    # 创建并显示主窗口
    viewer = TMXViewer()
    viewer.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
