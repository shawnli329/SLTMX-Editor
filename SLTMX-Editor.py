import sys
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QFileDialog, QLabel, QLineEdit,
                             QTextEdit, QSplitter, QHeaderView, QMessageBox,
                             QProgressBar, QStatusBar, QFrame, QGridLayout,
                             QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import os
import json
from datetime import datetime

# 加载语言配置
def load_language_config(language='en-us'):
    """加载语言配置文件"""
    try:
        config_path = f"{language}.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Language config file {config_path} not found, using default texts")
        return {}
    except json.JSONDecodeError:
        print(f"Error parsing {config_path}, using default texts")
        return {}

# 全局语言配置
LANG = load_language_config()

class TMXParser(QThread):
    """TMX文件解析线程"""
    progress_updated = pyqtSignal(int)
    parsing_finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            self.parse_tmx_file()
        except Exception as e:
            error_msg = LANG.get('dialogs', {}).get('parse_error_prefix', 'Error while prasing tmx file: ') + str(e)
            self.error_occurred.emit(error_msg)

    def parse_tmx_file(self):
        """解析TMX文件"""
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        
        # 解析header信息
        header = root.find('header')
        header_info = {}
        if header is not None:
            header_info = dict(header.attrib)
            # 查找header中的note和prop元素
            notes = [note.text for note in header.findall('note') if note.text]
            props = {prop.get('type', 'unknown'): prop.text for prop in header.findall('prop') if prop.text}
            if notes:
                header_info['notes'] = notes
            if props:
                header_info['properties'] = props
        
        # 解析translation units
        body = root.find('body')
        translation_units = []
        
        if body is not None:
            tu_elements = body.findall('tu')
            total_units = len(tu_elements)
            
            for i, tu in enumerate(tu_elements):
                # 更新进度
                progress = int((i + 1) / total_units * 100)
                self.progress_updated.emit(progress)
                
                unit_data = {
                    'tuid': tu.get('tuid', ''),
                    'attributes': dict(tu.attrib),
                    'notes': [],
                    'properties': {},
                    'variants': {}
                }
                
                # 解析tu级别的note和prop
                for note in tu.findall('note'):
                    if note.text:
                        unit_data['notes'].append(note.text)
                
                for prop in tu.findall('prop'):
                    prop_type = prop.get('type', 'unknown')
                    if prop.text:
                        unit_data['properties'][prop_type] = prop.text
                
                # 解析tuv元素（翻译变体）
                for tuv in tu.findall('tuv'):
                    lang = tuv.get('{http://www.w3.org/XML/1998/namespace}lang') or tuv.get('xml:lang', 'unknown')
                    seg = tuv.find('seg')
                    
                    if seg is not None:
                        # 处理seg内容，包括内联标记
                        seg_text = self.extract_text_from_seg(seg)
                        
                        unit_data['variants'][lang] = {
                            'text': seg_text,
                            'attributes': dict(tuv.attrib),
                            'notes': [note.text for note in tuv.findall('note') if note.text],
                            'properties': {prop.get('type', 'unknown'): prop.text 
                                         for prop in tuv.findall('prop') if prop.text}
                        }
                
                translation_units.append(unit_data)
        
        result = {
            'header': header_info,
            'translation_units': translation_units,
            'total_units': len(translation_units)
        }
        
        self.parsing_finished.emit(result)
    
    def extract_text_from_seg(self, seg_element):
        """从seg元素中提取文本内容，处理内联标记"""
        if seg_element.text:
            text = seg_element.text
        else:
            text = ""
        
        for child in seg_element:
            if child.tag in ['bpt', 'ept', 'ph', 'it', 'hi']:
                # 保留标记信息但简化显示
                text += f"[{child.tag}]"
            if child.text:
                text += child.text
            if child.tail:
                text += child.tail
        
        return text.strip()

class TMXViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tmx_data = None
        self.current_page = 0
        self.page_size = 100
        self.filtered_units = []
        self.source_lang = ""
        self.target_lang = ""
        
        # 获取DPI缩放比例
        self.dpi_scale = self.get_dpi_scale()
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.init_ui()
        self.setup_styles()
    
    def get_dpi_scale(self):
        """获取DPI缩放比例"""
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        # 标准DPI为96，计算缩放比例
        scale = dpi / 96.0
        
        # 对于常见的高DPI场景进行优化
        if scale >= 2.0:  # 200%缩放或更高
            return 2.0
        elif scale >= 1.5:  # 150%缩放
            return 1.5
        elif scale >= 1.25:  # 125%缩放
            return 1.25
        else:
            return max(1.0, scale)  # 最小缩放比例为1.0
    
    def scale_size(self, size):
        """根据DPI缩放调整尺寸"""
        return int(size * self.dpi_scale)
    
    def get_scaled_font(self, base_size=12):
        """获取缩放后的字体"""
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(max(9, int(base_size * self.dpi_scale)))
        return font
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = "icon.ico"
            # 图标设置代码
        except Exception as e:
            error_msg = LANG.get('icon', {}).get('icon_load_error_template', 'Failed to set icon: {}').format(e)
            print(error_msg)
    
    def init_ui(self):
        """初始化用户界面"""
        window_title = LANG.get('window', {}).get('title', 'SLTMX Editor')
        self.setWindowTitle(window_title)
        
        # 根据DPI缩放调整窗口大小
        base_width = 1400
        base_height = 800
        scaled_width = int(base_width * self.dpi_scale)
        scaled_height = int(base_height * self.dpi_scale)
        
        self.setGeometry(100, 100, scaled_width, scaled_height)
        self.showMaximized()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧主要内容区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 工具栏
        self.create_toolbar(left_layout)
        
        # 搜索栏
        self.create_search_bar(left_layout)
        
        # 翻译单元表格
        self.create_translation_table(left_layout)
        
        # 分页控件
        self.create_pagination(left_layout)
        
        # 右侧信息面板
        right_widget = self.create_info_panel()
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        # 根据DPI缩放调整分割器大小
        left_size = self.scale_size(1000)
        right_size = self.scale_size(400)
        splitter.setSizes([left_size, right_size])
        
        # 状态栏
        self.create_status_bar()
        
        # 进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def create_toolbar(self, layout):
        """创建工具栏"""
        toolbar_layout = QHBoxLayout()
        
        open_button_text = LANG.get('toolbar', {}).get('open_file_button', 'Open TMX File')
        self.open_button = QPushButton(open_button_text)
        self.open_button.clicked.connect(self.open_file)
        toolbar_layout.addWidget(self.open_button)
        
        file_not_selected_text = LANG.get('toolbar', {}).get('file_not_selected_label', 'No file selected')
        self.file_label = QLabel(file_not_selected_text)
        toolbar_layout.addWidget(self.file_label)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
    
    def create_search_bar(self, layout):
        """创建搜索栏"""
        search_group_title = LANG.get('search_section', {}).get('group_title', 'Search')
        search_group = QGroupBox(search_group_title)
        search_layout = QGridLayout(search_group)
        
        # 原文搜索
        source_search_label = LANG.get('search_section', {}).get('source_search_label', 'Source Search:')
        search_layout.addWidget(QLabel(source_search_label), 0, 0)
        
        self.source_search = QLineEdit()
        source_placeholder = LANG.get('search_section', {}).get('source_search_placeholder', 'Enter source text to search...')
        self.source_search.setPlaceholderText(source_placeholder)
        self.source_search.textChanged.connect(self.filter_units)
        search_layout.addWidget(self.source_search, 0, 1)
        
        # 译文搜索
        target_search_label = LANG.get('search_section', {}).get('target_search_label', 'Target Search:')
        search_layout.addWidget(QLabel(target_search_label), 1, 0)
        
        self.target_search = QLineEdit()
        target_placeholder = LANG.get('search_section', {}).get('target_search_placeholder', 'Enter target text to search...')
        self.target_search.setPlaceholderText(target_placeholder)
        self.target_search.textChanged.connect(self.filter_units)
        search_layout.addWidget(self.target_search, 1, 1)
        
        # 清除搜索按钮
        clear_button_text = LANG.get('search_section', {}).get('clear_search_button', 'Clear Search')
        clear_button = QPushButton(clear_button_text)
        clear_button.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_button, 0, 2, 2, 1)
        
        layout.addWidget(search_group)
    
    def create_translation_table(self, layout):
        """创建翻译单元表格"""
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        
        # 设置表格标题
        default_headers = LANG.get('table', {}).get('default_headers', ['Source', 'Target'])
        self.table.setHorizontalHeaderLabels(default_headers)
        
        # 设置表格属性
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 根据DPI缩放调整行高
        row_height = int(60 * self.dpi_scale)
        self.table.verticalHeader().setDefaultSectionSize(row_height)
        self.table.setWordWrap(True)
        
        # 设置表格字体
        table_font = self.get_scaled_font(12)
        self.table.setFont(table_font)
        
        # 连接选择信号
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
    
    def create_pagination(self, layout):
        """创建分页控件"""
        pagination_layout = QHBoxLayout()
        
        # 分页按钮
        first_button_text = LANG.get('pagination', {}).get('first_page_button', 'First')
        self.first_button = QPushButton(first_button_text)
        self.first_button.clicked.connect(lambda: self.go_to_page(0))
        pagination_layout.addWidget(self.first_button)
        
        prev_button_text = LANG.get('pagination', {}).get('prev_page_button', 'Previous')
        self.prev_button = QPushButton(prev_button_text)
        self.prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_button)
        
        page_label_default = LANG.get('pagination', {}).get('page_label_default', 'Page 0 of 0')
        self.page_label = QLabel(page_label_default)
        pagination_layout.addWidget(self.page_label)
        
        next_button_text = LANG.get('pagination', {}).get('next_page_button', 'Next')
        self.next_button = QPushButton(next_button_text)
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)
        
        last_button_text = LANG.get('pagination', {}).get('last_page_button', 'Last')
        self.last_button = QPushButton(last_button_text)
        self.last_button.clicked.connect(self.last_page)
        pagination_layout.addWidget(self.last_button)
        
        pagination_layout.addStretch()
        
        # 记录信息
        record_label_default = LANG.get('pagination', {}).get('record_label_default', '0 records total')
        self.record_label = QLabel(record_label_default)
        pagination_layout.addWidget(self.record_label)
        
        layout.addLayout(pagination_layout)
        self.update_pagination_buttons()
    
    def create_info_panel(self):
        """创建右侧信息面板"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # 文件信息
        file_group = QGroupBox(LANG.get('info_panel', {}).get('file_info_group_title', 'File Information'))
        file_layout = QVBoxLayout(file_group)
        
        self.file_info = QTextEdit()
        # 根据DPI缩放调整高度
        max_height = int(200 * self.dpi_scale)
        self.file_info.setMaximumHeight(max_height)
        self.file_info.setReadOnly(True)
        file_layout.addWidget(self.file_info)
        
        info_layout.addWidget(file_group)
        
        # 当前条目详细信息
        detail_group = QGroupBox(LANG.get('info_panel', {}).get('detail_info_group_title', 'Entry Details'))
        detail_layout = QVBoxLayout(detail_group)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.detail_layout = QVBoxLayout(scroll_widget)
        
        self.detail_info = QTextEdit()
        self.detail_info.setReadOnly(True)
        self.detail_layout.addWidget(self.detail_info)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        detail_layout.addWidget(scroll_area)
        
        info_layout.addWidget(detail_group)
        
        return info_widget
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        ready_status = LANG.get('status_messages', {}).get('ready_status', 'Ready')
        self.status_bar.showMessage(ready_status)
    
    def setup_styles(self):
        """设置样式"""
        # 根据DPI缩放调整字体大小和间距
        base_font_size = 12
        scaled_font_size = max(10, int(base_font_size * self.dpi_scale))
        
        # 调整padding和margin
        padding_small = max(4, int(4 * self.dpi_scale))
        padding_medium = max(8, int(8 * self.dpi_scale))
        padding_large = max(16, int(16 * self.dpi_scale))
        border_radius = max(4, int(4 * self.dpi_scale))
        border_width = max(1, int(1 * self.dpi_scale))
        
        self.setStyleSheet(f"""
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
                font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
            }}
            QTableWidget::item:selected {{
                background-color: #04b84c;
            }}
            QPushButton {{
                background-color: #04b84c;
                color: white;
                border: none;
                padding: {padding_medium}px {padding_large}px;
                border-radius: {border_radius}px;
                font-weight: bold;
                font-size: {scaled_font_size}px;
                min-height: {max(20, int(20 * self.dpi_scale))}px;
            }}
            QPushButton:hover {{
                background-color: #01dd6d;
            }}
            QPushButton:pressed {{
                background-color: #03db6c;
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
                min-height: {max(20, int(20 * self.dpi_scale))}px;
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
    
    def open_file(self):
        """打开TMX文件"""
        dialog_title = LANG.get('dialogs', {}).get('file_dialog_title', 'Select TMX File')
        dialog_filter = LANG.get('dialogs', {}).get('file_dialog_filter', 'TMX Files (*.tmx);;All Files (*)')
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, dialog_title, "", dialog_filter
        )
        
        if file_path:
            loading_prefix = LANG.get('toolbar', {}).get('loading_label_prefix', 'Loading: ')
            self.file_label.setText(f"{loading_prefix}{os.path.basename(file_path)}")
            
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
        self.update_file_info()
        self.filter_units()  # 初始显示所有单元
        
        file_name = os.path.basename(self.parser_thread.file_path)
        loaded_prefix = LANG.get('toolbar', {}).get('loaded_label_prefix', 'Loaded: ')
        self.file_label.setText(f"{loaded_prefix}{file_name}")
        
        success_template = LANG.get('status_messages', {}).get('success_status_template', 'Successfully loaded {} translation units')
        self.status_bar.showMessage(success_template.format(data['total_units']))
    
    def on_parsing_error(self, error_msg):
        """解析错误处理"""
        self.progress_bar.setVisible(False)
        error_title = LANG.get('dialogs', {}).get('error_dialog_title', 'Error')
        QMessageBox.critical(self, error_title, error_msg)
        
        load_failed_label = LANG.get('toolbar', {}).get('load_failed_label', 'Load failed')
        self.file_label.setText(load_failed_label)
        
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
        
        # 更新表格标题
        if self.source_lang and self.target_lang:
            source_header_template = LANG.get('table', {}).get('source_header_template', 'Source ({})')
            target_header_template = LANG.get('table', {}).get('target_header_template', 'Target ({})')
            self.table.setHorizontalHeaderLabels([
                source_header_template.format(self.source_lang), 
                target_header_template.format(self.target_lang)
            ])
    
    def update_file_info(self):
        """更新文件信息显示"""
        if not self.tmx_data:
            return
        
        header = self.tmx_data['header']
        info_text = []
        
        # 基本信息
        file_info_title = LANG.get('file_info_content', {}).get('file_info_title', '=== TMX File Information ===')
        info_text.append(file_info_title)
        total_units_label = LANG.get('file_info_content', {}).get('total_units_label', 'Total Translation Units: {}')
        info_text.append(total_units_label.format(self.tmx_data['total_units']))
        source_lang_label = LANG.get('file_info_content', {}).get('source_lang_label', 'Source Language: {}')
        info_text.append(source_lang_label.format(self.source_lang))
        target_lang_label = LANG.get('file_info_content', {}).get('target_lang_label', 'Target Language: {}')
        info_text.append(target_lang_label.format(self.target_lang))
        info_text.append("")
        
        # Header属性
        header_info_title = LANG.get('file_info_content', {}).get('header_info_title', '=== Header Information ===')
        info_text.append(header_info_title)
        for key, value in header.items():
            if key not in ['notes', 'properties']:
                info_text.append(f"{key}: {value}")
        
        # Notes
        if 'notes' in header:
            notes_title = LANG.get('file_info_content', {}).get('notes_title', '=== Notes ===')
            info_text.append(f"\n{notes_title}")
            for note in header['notes']:
                info_text.append(f"• {note}")
        
        # Properties
        if 'properties' in header:
            properties_title = LANG.get('file_info_content', {}).get('properties_title', '=== Properties ===')
            info_text.append(f"\n{properties_title}")
            for prop_type, prop_value in header['properties'].items():
                info_text.append(f"{prop_type}: {prop_value}")
        
        self.file_info.setPlainText("\n".join(info_text))

    def show_unit_details(self, unit):
        """显示翻译单元详细信息"""
        if not unit:
            return
        
        details = []
        
        # 基本信息
        unit_detail_title = LANG.get('detail_info_content', {}).get('unit_detail_title', '=== Translation Unit Details ===')
        details.append(unit_detail_title)
        if unit['tuid']:
            tuid_label = LANG.get('detail_info_content', {}).get('tuid_label', 'Unit ID: {}')
            details.append(tuid_label.format(unit['tuid']))
        
        # 属性
        if unit['attributes']:
            attributes_title = LANG.get('detail_info_content', {}).get('attributes_title', '=== Unit Attributes ===')
            details.append(f"\n{attributes_title}")
            for key, value in unit['attributes'].items():
                if key != 'tuid':  # tuid已经显示过了
                    details.append(f"{key}: {value}")
        
        # 备注
        if unit['notes']:
            notes_title = LANG.get('detail_info_content', {}).get('notes_title', '=== Notes ===')
            details.append(f"\n{notes_title}")
            for note in unit['notes']:
                details.append(f"• {note}")
        
        # 属性
        if unit['properties']:
            properties_title = LANG.get('detail_info_content', {}).get('properties_title', '=== Properties ===')
            details.append(f"\n{properties_title}")
            for prop_type, prop_value in unit['properties'].items():
                details.append(f"{prop_type}: {prop_value}")
        
        # 所有语言变体
        variants_title = LANG.get('detail_info_content', {}).get('variants_title', '=== All Language Variants ===')
        details.append(f"\n{variants_title}")
        for lang, variant in unit['variants'].items():
            variant_lang_template = LANG.get('detail_info_content', {}).get('variant_lang_template', '[{}]')
            details.append(f"\n{variant_lang_template.format(lang)}")
            variant_text_template = LANG.get('detail_info_content', {}).get('variant_text_template', 'Text: {}')
            details.append(variant_text_template.format(variant['text']))
            
            if variant['attributes']:
                variant_attributes_title = LANG.get('detail_info_content', {}).get('variant_attributes_title', 'Attributes:')
                details.append(variant_attributes_title)
                for key, value in variant['attributes'].items():
                    if not key.startswith('{'):  # 跳过namespace属性
                        details.append(f"  {key}: {value}")
            
            if variant['notes']:
                variant_notes_title = LANG.get('detail_info_content', {}).get('variant_notes_title', 'Notes:')
                details.append(variant_notes_title)
                for note in variant['notes']:
                    details.append(f"  • {note}")
            
            if variant['properties']:
                variant_properties_title = LANG.get('detail_info_content', {}).get('variant_properties_title', 'Properties:')
                details.append(variant_properties_title)
                for prop_type, prop_value in variant['properties'].items():
                    details.append(f"  {prop_type}: {prop_value}")
        
        self.detail_info.setPlainText("\n".join(details))
    
    def on_selection_changed(self):
        """表格选择变化处理"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_units):
            unit = self.filtered_units[current_row + self.current_page * self.page_size]
            self.show_unit_details(unit)
        else:
            no_selection_message = LANG.get('detail_info_content', {}).get('no_selection_message', 'Please select a translation unit to view details')
            self.detail_info.setPlainText(no_selection_message)
    
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
    
    def clear_search(self):
        """清除搜索条件"""
        self.source_search.clear()
        self.target_search.clear()
    
    def update_table(self):
        """更新表格显示"""
        if not self.filtered_units:
            self.table.setRowCount(0)
            no_results_message = LANG.get('search_functionality', {}).get('no_results_message', 'No matching translation units found')
            self.status_bar.showMessage(no_results_message)
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
            
            # 创建表格项
            source_item = QTableWidgetItem(source_text)
            target_item = QTableWidgetItem(target_text)
            
            # 设置为只读
            source_item.setFlags(source_item.flags() & ~Qt.ItemIsEditable)
            target_item.setFlags(target_item.flags() & ~Qt.ItemIsEditable)
            
            # 添加到表格
            self.table.setItem(row, 0, source_item)
            self.table.setItem(row, 1, target_item)
    
    def update_pagination(self):
        """更新分页信息"""
        if not self.filtered_units:
            page_label_default = LANG.get('pagination', {}).get('page_label_default', 'Page 0 of 0')
            self.page_label.setText(page_label_default)
            record_label_default = LANG.get('pagination', {}).get('record_label_default', '0 records total')
            self.record_label.setText(record_label_default)
        else:
            total_pages = (len(self.filtered_units) + self.page_size - 1) // self.page_size
            page_label_template = LANG.get('pagination', {}).get('page_label_template', 'Page {} of {}')
            self.page_label.setText(page_label_template.format(self.current_page + 1, total_pages))
            record_label_template = LANG.get('pagination', {}).get('record_label_template', '{} records total')
            self.record_label.setText(record_label_template.format(len(self.filtered_units)))
        
        self.update_pagination_buttons()
    
    def update_pagination_buttons(self):
        """更新分页按钮状态"""
        if not self.filtered_units:
            self.first_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.last_button.setEnabled(False)
            return
        
        total_pages = (len(self.filtered_units) + self.page_size - 1) // self.page_size
        
        self.first_button.setEnabled(self.current_page > 0)
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        self.last_button.setEnabled(self.current_page < total_pages - 1)
    
    def go_to_page(self, page):
        """跳转到指定页"""
        if not self.filtered_units:
            return
        
        total_pages = (len(self.filtered_units) + self.page_size - 1) // self.page_size
        self.current_page = max(0, min(page, total_pages - 1))
        self.update_table()
        self.update_pagination()
    
    def prev_page(self):
        """上一页"""
        self.go_to_page(self.current_page - 1)
    
    def next_page(self):
        """下一页"""
        self.go_to_page(self.current_page + 1)
    
    def last_page(self):
        """最后一页"""
        if self.filtered_units:
            total_pages = (len(self.filtered_units) + self.page_size - 1) // self.page_size
            self.go_to_page(total_pages - 1)

def main():
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
    
    viewer = TMXViewer()
    viewer.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()