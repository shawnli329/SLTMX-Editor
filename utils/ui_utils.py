# -*- coding: utf-8 -*-
"""
UI工具函数
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from config.settings import *

class UIUtils:
    """UI工具类"""
    
    def __init__(self):
        """初始化UI工具"""
        self.dpi_scale = self.get_dpi_scale()
    
    def get_dpi_scale(self):
        """
        获取DPI缩放比例
        
        Returns:
            float: DPI缩放比例
        """
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        # 标准DPI为96，计算缩放比例
        scale = dpi / STANDARD_DPI
        
        # 对于常见的高DPI场景进行优化
        if scale >= 2.0:  # 200%缩放或更高
            return 2.0
        elif scale >= 1.5:  # 150%缩放
            return 1.5
        elif scale >= 1.25:  # 125%缩放
            return 1.25
        else:
            return max(MIN_SCALE, scale)  # 最小缩放比例为1.0
    
    def scale_size(self, size):
        """
        根据DPI缩放调整尺寸
        
        Args:
            size (int): 原始尺寸
            
        Returns:
            int: 缩放后的尺寸
        """
        return int(size * self.dpi_scale)
    
    def get_scaled_font(self, base_size=DEFAULT_FONT_SIZE):
        """
        获取缩放后的字体
        
        Args:
            base_size (int): 基础字体大小
            
        Returns:
            QFont: 缩放后的字体
        """
        font = QFont()
        font.setFamily(DEFAULT_FONT_FAMILY)
        font.setPointSize(max(MIN_FONT_SIZE, int(base_size * self.dpi_scale)))
        return font
    
    def setup_main_window_styles(self, main_window):
        """
        设置主窗口样式
        
        Args:
            main_window: 主窗口对象
        """
        # 根据DPI缩放调整字体大小和间距
        scaled_font_size = max(10, int(DEFAULT_FONT_SIZE * self.dpi_scale))
        
        # 调整padding和margin
        padding_small = max(4, int(4 * self.dpi_scale))
        padding_medium = max(8, int(8 * self.dpi_scale))
        padding_large = max(16, int(16 * self.dpi_scale))
        border_radius = max(4, int(4 * self.dpi_scale))
        border_width = max(1, int(1 * self.dpi_scale))
        min_height = max(20, int(20 * self.dpi_scale))
        
        main_window.setStyleSheet(f"""
            QMainWindow {{
                background-color: #f5f5f5;
            }}
            QTableWidget {{
                background-color: white;
                border: {border_width}px solid #ddd;
                border-radius: {border_radius}px;
            }}
            QTableWidget::item {{
                padding: {padding_small}px;
                border-bottom: {border_width}px solid #eee;
                font-size: {scaled_font_size}px;
                font-family: "{DEFAULT_FONT_FAMILY}", "SimHei", Arial, sans-serif;
            }}
            QTableWidget::item:selected {{
                background-color: {PRIMARY_COLOR};
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: {padding_medium}px {padding_large}px;
                border-radius: {border_radius}px;
                font-weight: bold;
                font-size: {scaled_font_size}px;
                min-height: {min_height}px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};
            }}
            QPushButton:pressed {{
                background-color: {PRESSED_COLOR};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
            QGroupBox {{
                font-weight: bold;
                border: {border_width}px solid #ddd;
                border-radius: {border_radius}px;
                margin: {padding_small}px 0;
                padding-top: {padding_medium}px;
                font-size: {scaled_font_size}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {padding_medium}px;
                padding: 0 {padding_small}px 0 {padding_small}px;
            }}
            QLineEdit {{
                padding: {padding_small}px;
                border: {border_width}px solid #ddd;
                border-radius: {border_radius}px;
                font-size: {scaled_font_size}px;
                min-height: {min_height}px;
            }}
            QTextEdit {{
                border: {border_width}px solid #ddd;
                border-radius: {border_radius}px;
                font-size: {scaled_font_size}px;
            }}
            QLabel {{
                font-size: {scaled_font_size}px;
            }}
            QStatusBar {{
                font-size: {scaled_font_size}px;
            }}
        """)
