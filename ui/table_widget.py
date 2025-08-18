# -*- coding: utf-8 -*-
"""
主表格组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QLineEdit,
                             QGroupBox, QGridLayout, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from config.language import load_language_config
from config.settings import *
from utils.ui_utils import UIUtils
from .table_delegate import MultiLineTextDelegate
from .table_pagination import TablePagination

# 加载语言配置
LANG = load_language_config()

class TMXTableWidget(QWidget):
    """TMX表格组件 - 支持完整文本显示和多行编辑"""
    
    # 信号定义
    selection_changed = pyqtSignal(dict)  # 选择变化信号
    item_modified = pyqtSignal(int, int, str)  # 项目修改信号
    filter_changed = pyqtSignal(list)  # 过滤变化信号
    page_changed = pyqtSignal(int)  # 页面变化信号
    
    def __init__(self, parent=None):
        """
        初始化表格组件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 数据属性
        self.tmx_data = None
        self.filtered_units = []
        self.current_page = 0
        self.page_size = DEFAULT_PAGE_SIZE
        self.source_lang = ""
        self.target_lang = ""
        self.modified_rows = set()
        
        # UI工具
        self.ui_utils = UIUtils()
        
        # 语言配置
        self.lang_config = LANG
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建工具栏
        self.create_toolbar(layout)
        
        # 创建搜索栏
        self.create_search_bar(layout)
        
        # 创建表格
        self.create_table(layout)
        
        # 创建分页控件
        self.create_pagination_widget(layout)
    
    def create_toolbar(self, layout):
        """创建工具栏"""
        toolbar_layout = QHBoxLayout()
        
        # 文件标签
        file_not_selected_text = self.lang_config.get('toolbar', {}).get('file_not_selected_label', 'No file selected')
        self.file_label = QLabel(file_not_selected_text)
        toolbar_layout.addWidget(self.file_label)
        
        toolbar_layout.addStretch()
        
        # 添加编辑提示标签
        edit_hint_text = self.lang_config.get('edit_hints', {}).get('edit_instruction', 'Tip: Double-click to edit, Ctrl+Enter to confirm, Ctrl+S to save, Esc to cancel')
        self.edit_hint = QLabel(edit_hint_text)
        self.edit_hint.setStyleSheet("color: #666; font-size: 10px;")
        toolbar_layout.addWidget(self.edit_hint)
        
        layout.addLayout(toolbar_layout)
    
    def create_search_bar(self, layout):
        """创建搜索栏"""
        search_group_title = self.lang_config.get('search_section', {}).get('group_title', 'Search')
        self.search_group = QGroupBox(search_group_title)
        search_layout = QGridLayout(self.search_group)
        
        # 原文搜索
        source_search_label = self.lang_config.get('search_section', {}).get('source_search_label', 'Source Search:')
        self.source_search_label = QLabel(source_search_label)
        search_layout.addWidget(self.source_search_label, 0, 0)
        
        self.source_search = QLineEdit()
        source_placeholder = self.lang_config.get('search_section', {}).get('source_search_placeholder', 'Enter source text to search...')
        self.source_search.setPlaceholderText(source_placeholder)
        self.source_search.textChanged.connect(self.filter_units)
        search_layout.addWidget(self.source_search, 0, 1)
        
        # 译文搜索
        target_search_label = self.lang_config.get('search_section', {}).get('target_search_label', 'Target Search:')
        self.target_search_label = QLabel(target_search_label)
        search_layout.addWidget(self.target_search_label, 1, 0)
        
        self.target_search = QLineEdit()
        target_placeholder = self.lang_config.get('search_section', {}).get('target_search_placeholder', 'Enter target text to search...')
        self.target_search.setPlaceholderText(target_placeholder)
        self.target_search.textChanged.connect(self.filter_units)
        search_layout.addWidget(self.target_search, 1, 1)
        
        # 清除搜索按钮
        clear_button_text = self.lang_config.get('search_section', {}).get('clear_search_button', 'Clear Search')
        self.clear_button = QPushButton(clear_button_text)
        self.clear_button.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_button, 0, 2, 2, 1)
        
        layout.addWidget(self.search_group)
    
    def create_table(self, layout):
        """创建表格"""
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        
        # 设置表格标题
        default_headers = self.lang_config.get('table', {}).get('default_headers', ['Source', 'Target'])
        self.table.setHorizontalHeaderLabels(default_headers)
        
        # 设置表格属性
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 启用编辑功能
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        
        # 设置多行文本编辑器委托
        self.text_delegate = MultiLineTextDelegate(self.table)
        self.table.setItemDelegate(self.text_delegate)
        
        # 关键设置：支持完整文本显示
        self.setup_text_display()
        
        # 连接信号
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.table)
    
    def create_pagination_widget(self, layout):
        """创建分页控件"""
        self.pagination = TablePagination(self)
        self.pagination.page_changed.connect(self.on_page_changed)
        layout.addWidget(self.pagination)
    
    def setup_text_display(self):
        """设置文本显示模式，支持完整内容显示"""
        # 1. 启用文本换行
        self.table.setWordWrap(True)
        
        # 2. 设置垂直表头可调整大小
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # 3. 设置最小行高，确保至少能显示一行文本
        min_row_height = self.ui_utils.scale_size(50)  # 最小50px
        self.table.verticalHeader().setMinimumSectionSize(min_row_height)
        
        # 4. 设置默认行高，适合多行文本
        default_row_height = self.ui_utils.scale_size(120)  # 120px
        self.table.verticalHeader().setDefaultSectionSize(default_row_height)
        
        # 5. 设置字体
        table_font = self.ui_utils.get_scaled_font(DEFAULT_FONT_SIZE)
        self.table.setFont(table_font)
        
        # 6. 设置表格项的文本对齐方式
        self.table.setTextElideMode(Qt.ElideNone)  # 禁用省略号显示
    
    def update_language(self, new_lang_config):
        """
        更新语言配置
        
        Args:
            new_lang_config (dict): 新的语言配置
        """
        self.lang_config = new_lang_config
        
        # 更新文件标签
        file_not_selected_text = self.lang_config.get('toolbar', {}).get('file_not_selected_label', 'No file selected')
        self.file_label.setText(file_not_selected_text)
        
        # 更新编辑提示
        edit_hint_text = self.lang_config.get('edit_hints', {}).get('edit_instruction', 'Tip: Double-click to edit, Ctrl+Enter to confirm, Ctrl+S to save, Esc to cancel')
        self.edit_hint.setText(edit_hint_text)
        
        # 更新搜索栏文本
        search_group_title = self.lang_config.get('search_section', {}).get('group_title', 'Search')
        self.search_group.setTitle(search_group_title)
        
        source_search_label = self.lang_config.get('search_section', {}).get('source_search_label', 'Source Search:')
        self.source_search_label.setText(source_search_label)
        
        target_search_label = self.lang_config.get('search_section', {}).get('target_search_label', 'Target Search:')
        self.target_search_label.setText(target_search_label)
        
        source_placeholder = self.lang_config.get('search_section', {}).get('source_search_placeholder', 'Enter source text to search...')
        self.source_search.setPlaceholderText(source_placeholder)
        
        target_placeholder = self.lang_config.get('search_section', {}).get('target_search_placeholder', 'Enter target text to search...')
        self.target_search.setPlaceholderText(target_placeholder)
        
        clear_button_text = self.lang_config.get('search_section', {}).get('clear_search_button', 'Clear Search')
        self.clear_button.setText(clear_button_text)
        
        # 更新表格标题
        if self.source_lang and self.target_lang:
            source_header_template = self.lang_config.get('table', {}).get('source_header_template', 'Source ({})')
            target_header_template = self.lang_config.get('table', {}).get('target_header_template', 'Target ({})')
            self.table.setHorizontalHeaderLabels([
                source_header_template.format(self.source_lang),
                target_header_template.format(self.target_lang)
            ])
        else:
            default_headers = self.lang_config.get('table', {}).get('default_headers', ['Source', 'Target'])
            self.table.setHorizontalHeaderLabels(default_headers)
        
        # 更新分页控件
        self.pagination.update_language(new_lang_config)
    
    def set_data(self, tmx_data, source_lang, target_lang):
        """
        设置TMX数据
        
        Args:
            tmx_data (dict): TMX数据
            source_lang (str): 源语言
            target_lang (str): 目标语言
        """
        self.tmx_data = tmx_data
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # 更新表格标题
        if source_lang and target_lang:
            source_header_template = self.lang_config.get('table', {}).get('source_header_template', 'Source ({})')
            target_header_template = self.lang_config.get('table', {}).get('target_header_template', 'Target ({})')
            self.table.setHorizontalHeaderLabels([
                source_header_template.format(source_lang),
                target_header_template.format(target_lang)
            ])
        
        # 过滤单元
        self.filter_units()
    
    def clear_data(self):
        """清空数据"""
        self.tmx_data = None
        self.filtered_units = []
        self.current_page = 0
        self.modified_rows.clear()
        self.table.setRowCount(0)
        
        # 清空搜索
        self.source_search.clear()
        self.target_search.clear()
        
        # 重置标题
        default_headers = self.lang_config.get('table', {}).get('default_headers', ['Source', 'Target'])
        self.table.setHorizontalHeaderLabels(default_headers)
        
        # 更新分页
        self.pagination.set_pagination_info(0, 0, self.page_size)
    
    def filter_units(self):
        """过滤翻译单元"""
        if not self.tmx_data:
            return
        
        source_text = self.source_search.text().lower()
        target_text = self.target_search.text().lower()
        
        self.filtered_units = []
        
        for unit in self.tmx_data['translation_units']:
            # 获取源文本和目标文本
            source_variant = unit['variants'].get(self.source_lang, {})
            target_variant = unit['variants'].get(self.target_lang, {})
            
            source_content = source_variant.get('text', '').lower()
            target_content = target_variant.get('text', '').lower()
            
            # 检查是否匹配搜索条件
            source_match = not source_text or source_text in source_content
            target_match = not target_text or target_text in target_content
            
            if source_match and target_match:
                self.filtered_units.append(unit)
        
        # 重置到第一页
        self.current_page = 0
        self.update_table()
        self.update_pagination()
        
        # 发送过滤变化信号
        self.filter_changed.emit(self.filtered_units)
    
    def clear_search(self):
        """清除搜索条件"""
        self.source_search.clear()
        self.target_search.clear()
    
    def update_table(self):
        """更新表格显示"""
        if not self.filtered_units:
            self.table.setRowCount(0)
            return
        
        # 计算当前页的数据范围
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.filtered_units))
        page_units = self.filtered_units[start_idx:end_idx]
        
        # 设置表格行数
        self.table.setRowCount(len(page_units))
        
        # 填充表格数据
        for row, unit in enumerate(page_units):
            # 获取源文本和目标文本
            source_variant = unit['variants'].get(self.source_lang, {})
            target_variant = unit['variants'].get(self.target_lang, {})
            
            source_text = source_variant.get('text', '')
            target_text = target_variant.get('text', '')
            
            # 创建自定义表格项，支持完整文本显示
            source_item = self.create_text_item(source_text)
            target_item = self.create_text_item(target_text)
            
            # 如果单元被修改过，设置背景色
            if unit.get('modified', False):
                source_item.setBackground(QColor(MODIFIED_COLOR))
                target_item.setBackground(QColor(MODIFIED_COLOR))
                self.modified_rows.add(row)
            
            # 添加到表格
            self.table.setItem(row, 0, source_item)
            self.table.setItem(row, 1, target_item)
        
        # 确保行高自适应内容
        self.table.resizeRowsToContents()
    
    def update_pagination(self):
        """更新分页信息"""
        total_records = len(self.filtered_units)
        self.pagination.set_pagination_info(self.current_page, total_records, self.page_size)
    
    def create_text_item(self, text):
        """
        创建支持完整文本显示的表格项
        
        Args:
            text (str): 文本内容
            
        Returns:
            QTableWidgetItem: 表格项
        """
        item = QTableWidgetItem(text)
        
        # 设置为可编辑
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        
        # 设置文本对齐方式（顶部对齐，左对齐）
        item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # 设置工具提示，鼠标悬停时显示完整内容
        item.setToolTip(text)
        
        return item
    
    def clear_modified_rows(self):
        """清除修改行的背景色"""
        for row in self.modified_rows:
            if row < self.table.rowCount():
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor())  # 恢复默认背景色
        self.modified_rows.clear()
    
    # 事件处理方法
    def on_selection_changed(self):
        """表格选择变化处理"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            actual_index = current_row + self.current_page * self.page_size
            if actual_index < len(self.filtered_units):
                unit = self.filtered_units[actual_index]
                self.selection_changed.emit(unit)
                return
        
        self.selection_changed.emit({})
    
    def on_item_changed(self, item):
        """表格项目改变事件"""
        if not self.tmx_data:
            return
        
        row = item.row()
        col = item.column()
        new_text = item.text()
        
        # 计算在原始数据中的索引
        actual_index = row + self.current_page * self.page_size
        if actual_index >= len(self.filtered_units):
            return
        
        # 获取对应的翻译单元
        unit = self.filtered_units[actual_index]
        
        # 立即更新数据模型
        if col == 0:  # 源文本
            if self.source_lang in unit['variants']:
                unit['variants'][self.source_lang]['text'] = new_text
                print(f"Updated source text: {new_text[:50]}...")  # 调试信息
        elif col == 1:  # 目标文本
            if self.target_lang in unit['variants']:
                unit['variants'][self.target_lang]['text'] = new_text
                print(f"Updated target text: {new_text[:50]}...")  # 调试信息
        
        # 标记为已修改
        unit['modified'] = True
        
        # 设置背景色
        item.setBackground(QColor(MODIFIED_COLOR))
        # 同一行的其他单元格也设置相同背景色
        for c in range(self.table.columnCount()):
            other_item = self.table.item(row, c)
            if other_item:
                other_item.setBackground(QColor(MODIFIED_COLOR))
        
        self.modified_rows.add(row)
        
        # 更新工具提示
        item.setToolTip(new_text)
        
        # 调整行高以适应新内容
        self.table.resizeRowToContents(row)
        
        # 发送修改信号
        self.item_modified.emit(row, col, new_text)
    
    def on_page_changed(self, page):
        """页面变化处理"""
        self.current_page = page
        self.update_table()
        self.page_changed.emit(page)