# -*- coding: utf-8 -*-
"""
分页控件组件
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal

from config.language import load_language_config

# 加载语言配置
LANG = load_language_config()

class TablePagination(QWidget):
    """表格分页控件"""
    
    # 信号定义
    page_changed = pyqtSignal(int)  # 页面变化信号
    
    def __init__(self, parent=None):
        """
        初始化分页控件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 分页属性
        self.current_page = 0
        self.total_records = 0
        self.page_size = 100
        
        # 语言配置
        self.lang_config = LANG
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        
        # 分页按钮
        first_button_text = self.lang_config.get('pagination', {}).get('first_page_button', 'First')
        self.first_button = QPushButton(first_button_text)
        self.first_button.clicked.connect(lambda: self.go_to_page(0))
        layout.addWidget(self.first_button)
        
        prev_button_text = self.lang_config.get('pagination', {}).get('prev_page_button', 'Previous')
        self.prev_button = QPushButton(prev_button_text)
        self.prev_button.clicked.connect(self.prev_page)
        layout.addWidget(self.prev_button)
        
        page_label_default = self.lang_config.get('pagination', {}).get('page_label_default', 'Page 0 of 0')
        self.page_label = QLabel(page_label_default)
        layout.addWidget(self.page_label)
        
        next_button_text = self.lang_config.get('pagination', {}).get('next_page_button', 'Next')
        self.next_button = QPushButton(next_button_text)
        self.next_button.clicked.connect(self.next_page)
        layout.addWidget(self.next_button)
        
        last_button_text = self.lang_config.get('pagination', {}).get('last_page_button', 'Last')
        self.last_button = QPushButton(last_button_text)
        self.last_button.clicked.connect(self.last_page)
        layout.addWidget(self.last_button)
        
        layout.addStretch()
        
        # 记录信息
        record_label_default = self.lang_config.get('pagination', {}).get('record_label_default', '0 records total')
        self.record_label = QLabel(record_label_default)
        layout.addWidget(self.record_label)
        
        # 初始化按钮状态
        self.update_buttons()
    
    def update_language(self, new_lang_config):
        """
        更新语言配置
        
        Args:
            new_lang_config (dict): 新的语言配置
        """
        self.lang_config = new_lang_config
        
        # 更新按钮文本
        first_button_text = self.lang_config.get('pagination', {}).get('first_page_button', 'First')
        self.first_button.setText(first_button_text)
        
        prev_button_text = self.lang_config.get('pagination', {}).get('prev_page_button', 'Previous')
        self.prev_button.setText(prev_button_text)
        
        next_button_text = self.lang_config.get('pagination', {}).get('next_page_button', 'Next')
        self.next_button.setText(next_button_text)
        
        last_button_text = self.lang_config.get('pagination', {}).get('last_page_button', 'Last')
        self.last_button.setText(last_button_text)
        
        # 更新显示信息
        self.update_display()
    
    def set_pagination_info(self, current_page, total_records, page_size):
        """
        设置分页信息
        
        Args:
            current_page (int): 当前页码（从0开始）
            total_records (int): 总记录数
            page_size (int): 每页大小
        """
        self.current_page = current_page
        self.total_records = total_records
        self.page_size = page_size
        
        self.update_display()
        self.update_buttons()
    
    def update_display(self):
        """更新显示信息"""
        if self.total_records == 0:
            page_label_default = self.lang_config.get('pagination', {}).get('page_label_default', 'Page 0 of 0')
            self.page_label.setText(page_label_default)
            record_label_default = self.lang_config.get('pagination', {}).get('record_label_default', '0 records total')
            self.record_label.setText(record_label_default)
        else:
            total_pages = (self.total_records + self.page_size - 1) // self.page_size
            page_label_template = self.lang_config.get('pagination', {}).get('page_label_template', 'Page {} of {}')
            self.page_label.setText(page_label_template.format(self.current_page + 1, total_pages))
            
            record_label_template = self.lang_config.get('pagination', {}).get('record_label_template', '{} records total')
            self.record_label.setText(record_label_template.format(self.total_records))
    
    def update_buttons(self):
        """更新按钮状态"""
        if self.total_records == 0:
            self.first_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.last_button.setEnabled(False)
            return
        
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        
        self.first_button.setEnabled(self.current_page > 0)
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        self.last_button.setEnabled(self.current_page < total_pages - 1)
    
    def go_to_page(self, page):
        """
        跳转到指定页
        
        Args:
            page (int): 页码（从0开始）
        """
        if self.total_records == 0:
            return
        
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        new_page = max(0, min(page, total_pages - 1))
        
        if new_page != self.current_page:
            self.current_page = new_page
            self.update_display()
            self.update_buttons()
            self.page_changed.emit(self.current_page)
    
    def prev_page(self):
        """上一页"""
        self.go_to_page(self.current_page - 1)
    
    def next_page(self):
        """下一页"""
        self.go_to_page(self.current_page + 1)
    
    def last_page(self):
        """最后一页"""
        if self.total_records > 0:
            total_pages = (self.total_records + self.page_size - 1) // self.page_size
            self.go_to_page(total_pages - 1)
    
    def get_current_page(self):
        """
        获取当前页码
        
        Returns:
            int: 当前页码（从0开始）
        """
        return self.current_page