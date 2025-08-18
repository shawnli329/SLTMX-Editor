# -*- coding: utf-8 -*-
"""
主窗口
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QProgressBar, QStatusBar, QMessageBox,
                             QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from config.language import load_language_config
from config.settings import *
from core.tmx_parser import TMXParser
from core.tmx_writer import TMXWriter
from utils.ui_utils import UIUtils
from .menu_bar import MenuBarManager
from .table_widget import TMXTableWidget
from .info_panel import InfoPanel

# 加载语言配置
LANG = load_language_config()

class TMXViewer(QMainWindow):
    """TMX查看器主窗口"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 数据属性
        self.tmx_data = None
        self.current_page = 0
        self.page_size = DEFAULT_PAGE_SIZE
        self.filtered_units = []
        self.source_lang = ""
        self.target_lang = ""
        self.current_file_path = ""
        self.modified_rows = set()
        self.current_language = 'zh-cn'  # 当前语言
        
        # UI工具
        self.ui_utils = UIUtils()
        self.dpi_scale = self.ui_utils.get_dpi_scale()
        
        # 初始化界面
        self.init_ui()
        self.setup_styles()
        self.set_window_icon()
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        window_title = LANG.get('window', {}).get('title', 'SLTMX Editor')
        self.setWindowTitle(window_title)
        
        scaled_width = int(DEFAULT_WINDOW_WIDTH * self.dpi_scale)
        scaled_height = int(DEFAULT_WINDOW_HEIGHT * self.dpi_scale)
        self.setGeometry(100, 100, scaled_width, scaled_height)
        self.showMaximized()
        
        # 创建菜单栏
        self.menu_manager = MenuBarManager(self)
        self.menu_manager.create_menu_bar()
        
        # 创建中央部件
        self.create_central_widget()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def create_central_widget(self):
        """创建中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧表格区域
        self.table_widget = TMXTableWidget(self)
        
        # 右侧信息面板
        self.info_panel = InfoPanel(self)
        
        # 添加到分割器
        splitter.addWidget(self.table_widget)
        splitter.addWidget(self.info_panel)
        
        # 设置分割器大小
        left_size = self.ui_utils.scale_size(1000)
        right_size = self.ui_utils.scale_size(400)
        splitter.setSizes([left_size, right_size])
        
        # 连接信号
        self.table_widget.selection_changed.connect(self.on_selection_changed)
        self.table_widget.item_modified.connect(self.on_item_modified)
        self.table_widget.filter_changed.connect(self.on_filter_changed)
        self.table_widget.page_changed.connect(self.on_page_changed)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        ready_status = LANG.get('status_messages', {}).get('ready_status', 'Ready')
        self.status_bar.showMessage(ready_status)
    
    def setup_styles(self):
        """设置样式"""
        self.ui_utils.setup_main_window_styles(self)
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = "icon.ico"
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            error_msg = LANG.get('icon', {}).get('icon_load_error_template', 'Failed to set icon: {}')
            print(error_msg.format(e))
    
    def switch_language(self, language_code):
        """
        切换语言
        
        Args:
            language_code (str): 语言代码 ('zh-cn' 或 'en-us')
        """
        if language_code == self.current_language:
            return
        
        self.current_language = language_code
        
        # 重新加载语言配置
        global LANG
        LANG = load_language_config(language_code)
        
        # 更新菜单文本
        self.menu_manager.update_menu_texts(LANG)
        
        # 更新窗口标题
        window_title = LANG.get('window', {}).get('title', 'SLTMX Editor')
        self.setWindowTitle(window_title)
        
        # 更新状态栏
        if not self.tmx_data:
            ready_status = LANG.get('status_messages', {}).get('ready_status', 'Ready')
            self.status_bar.showMessage(ready_status)
        else:
            success_template = LANG.get('status_messages', {}).get('success_status_template', 'Successfully loaded {} translation units')
            self.status_bar.showMessage(success_template.format(self.tmx_data['total_units']))
        
        # 更新所有子组件的语言
        self.table_widget.update_language(LANG)
        self.info_panel.update_language(LANG)
        
        # 如果有数据，重新设置以更新语言相关的显示
        if self.tmx_data:
            self.info_panel.update_file_info(self.tmx_data, self.source_lang, self.target_lang)
            self.table_widget.set_data(self.tmx_data, self.source_lang, self.target_lang)
    
    def show_about_dialog(self):
        """显示关于对话框"""
        about_title = LANG.get('about', {}).get('dialog_title', '关于')
        about_text = LANG.get('about', {}).get('dialog_text', 
            'SLTMX编辑器 V1.1\n\nTMX翻译记忆库文件编辑器\n支持查看、编辑和保存TMX文件\n\n作者: https://github.com/shawnli329/SLTMX-Editor\n版本: 1.1')
        
        QMessageBox.about(self, about_title, about_text)
    
    # 文件操作方法
    def open_file(self):
        """打开TMX文件"""
        dialog_title = LANG.get('dialogs', {}).get('file_dialog_title', 'Select TMX File')
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, dialog_title, "", TMX_FILE_FILTER
        )
        
        if file_path:
            self.current_file_path = file_path
            self.start_parsing(file_path)
    
    def start_parsing(self, file_path):
        """开始解析文件"""
        # 更新状态
        loading_prefix = LANG.get('toolbar', {}).get('loading_label_prefix', 'Loading: ')
        file_name = os.path.basename(file_path)
        
        parsing_status = LANG.get('status_messages', {}).get('parsing_status', 'Parsing TMX file...')
        self.status_bar.showMessage(parsing_status)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 创建解析线程
        self.parser_thread = TMXParser(file_path)
        self.parser_thread.progress_updated.connect(self.update_progress)
        self.parser_thread.parsing_finished.connect(self.on_parsing_finished)
        self.parser_thread.error_occurred.connect(self.on_parsing_error)
        self.parser_thread.start()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def on_parsing_finished(self, data):
        """解析完成处理"""
        self.tmx_data = data
        self.progress_bar.setVisible(False)
        
        # 确定源语言和目标语言
        self.determine_languages()
        
        # 更新界面
        self.info_panel.update_file_info(data, self.source_lang, self.target_lang)
        self.table_widget.set_data(data, self.source_lang, self.target_lang)
        
        # 更新状态
        file_name = os.path.basename(self.parser_thread.file_path)
        loaded_prefix = LANG.get('toolbar', {}).get('loaded_label_prefix', 'Loaded: ')
        
        success_template = LANG.get('status_messages', {}).get('success_status_template', 'Successfully loaded {} translation units')
        self.status_bar.showMessage(success_template.format(data['total_units']))
        
        # 启用菜单
        self.menu_manager.set_file_loaded(True)
    
    def on_parsing_error(self, error_msg):
        """解析错误处理"""
        self.progress_bar.setVisible(False)
        error_title = LANG.get('dialogs', {}).get('error_dialog_title', 'Error')
        QMessageBox.critical(self, error_title, error_msg)
        
        load_failed_status = LANG.get('status_messages', {}).get('load_failed_status', 'Load failed')
        self.status_bar.showMessage(load_failed_status)
    
    def determine_languages(self):
        """确定源语言和目标语言"""
        if not self.tmx_data or not self.tmx_data['translation_units']:
            return
        
        # 从header获取源语言
        header = self.tmx_data['header']
        self.source_lang = header.get('srclang', '')
        
        # 从第一个翻译单元获取所有语言
        first_unit = self.tmx_data['translation_units'][0]
        languages = list(first_unit['variants'].keys())
        
        # 如果源语言不在variants中，使用第一个语言作为源语言
        if self.source_lang not in languages and languages:
            self.source_lang = languages[0]
        
        # 选择目标语言（非源语言的第一个）
        for lang in languages:
            if lang != self.source_lang:
                self.target_lang = lang
                break
        
        # 如果只有一种语言，目标语言设为相同
        if not self.target_lang and languages:
            self.target_lang = languages[0]
    
    def save_file(self):
        """保存文件"""
        if not self.tmx_data:
            return
        
        if not self.current_file_path:
            self.save_as_file()
            return
        
        self.save_tmx_file(self.current_file_path)
        self.clear_modified_rows()
    
    def save_as_file(self):
        """另存为文件"""
        if not self.tmx_data:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            LANG.get('menu', {}).get('save_as_dialog_title', '另存为TMX文件'), 
            "", 
            TMX_FILE_FILTER
        )
        
        if file_path:
            self.save_tmx_file(file_path)
    
    def save_tmx_file(self, file_path):
        """保存TMX文件"""
        try:
            writer = TMXWriter(self.tmx_data)
            writer.save_to_file(file_path)
            
            # 保存成功后清除所有修改标记
            for unit in self.tmx_data['translation_units']:
                if unit.get('modified', False):
                    unit['modified'] = False
                    print(f"清除修改标记: tuid={unit.get('tuid', 'N/A')}")
            
            save_success_msg = LANG.get('menu', {}).get('save_success', '文件保存成功')
            self.status_bar.showMessage(save_success_msg)
            QMessageBox.information(self, LANG.get('menu', {}).get('save_title', '保存'), save_success_msg)
            
        except Exception as e:
            error_msg = str(e)
            QMessageBox.critical(self, LANG.get('dialogs', {}).get('error_dialog_title', 'Error'), error_msg)
    
    def close_file(self):
        """关闭文件"""
        self.tmx_data = None
        self.filtered_units = []
        self.current_file_path = ""
        self.modified_rows.clear()
        
        # 清空界面
        self.table_widget.clear_data()
        self.info_panel.clear_info()
        
        # 更新状态
        file_not_selected_text = LANG.get('toolbar', {}).get('file_not_selected_label', 'No file selected')
        self.status_bar.showMessage(file_not_selected_text)
        
        # 禁用菜单
        self.menu_manager.set_file_loaded(False)
    
    def export_file(self):
        """导出文件 - 暂时留空"""
        QMessageBox.information(
            self, 
            LANG.get('menu', {}).get('function_not_implemented', '功能未实现'), 
            LANG.get('menu', {}).get('export_not_implemented', '导出功能暂未实现')
        )
    
    def import_file(self):
        """导入文件 - 暂时留空"""
        QMessageBox.information(
            self, 
            LANG.get('menu', {}).get('function_not_implemented', '功能未实现'), 
            LANG.get('menu', {}).get('import_not_implemented', '导入功能暂未实现')
        )
    
    def clear_modified_rows(self):
        """清除修改行的背景色"""
        self.table_widget.clear_modified_rows()
        self.modified_rows.clear()
        self.menu_manager.set_has_modifications(False)
    
    # 事件处理方法
    def on_selection_changed(self, unit):
        """表格选择变化处理"""
        self.info_panel.show_unit_details(unit)
    
    def on_item_modified(self, row, col, new_text):
        """表格项目修改处理"""
        if not self.tmx_data:
            return
        
        # 计算在原始数据中的索引
        actual_index = row + self.current_page * self.page_size
        if actual_index >= len(self.filtered_units):
            return
        
        unit = self.filtered_units[actual_index]
        
        # 确保数据已经更新（表格组件已经更新了，这里主要是确认）
        print(f"Main window confirming update - Row: {row}, Col: {col}, Text: {new_text[:50]}...")
        
        # 双重确认数据更新
        if col == 0:  # 源文本
            if self.source_lang in unit['variants']:
                unit['variants'][self.source_lang]['text'] = new_text
        elif col == 1:  # 目标文本
            if self.target_lang in unit['variants']:
                unit['variants'][self.target_lang]['text'] = new_text
        
        # 标记为已修改
        unit['modified'] = True
        self.modified_rows.add(row)
        
        # 启用保存菜单
        self.menu_manager.set_has_modifications(True)
        
        # 调试信息：打印当前单元的数据
        print(f"Unit modified flag: {unit.get('modified', False)}")
        if self.source_lang in unit['variants']:
            print(f"Current source: {unit['variants'][self.source_lang]['text'][:50]}...")
        if self.target_lang in unit['variants']:
            print(f"Current target: {unit['variants'][self.target_lang]['text'][:50]}...")
    
    def on_filter_changed(self, filtered_units):
        """过滤变化处理"""
        self.filtered_units = filtered_units
        self.current_page = 0
    
    def on_page_changed(self, page):
        """页面变化处理"""
        self.current_page = page