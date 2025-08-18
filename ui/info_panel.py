# -*- coding: utf-8 -*-
"""
信息面板组件
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QGroupBox, 
                             QScrollArea)

from config.language import load_language_config
from utils.ui_utils import UIUtils

# 加载语言配置
LANG = load_language_config()

class InfoPanel(QWidget):
    """信息面板组件"""
    
    def __init__(self, parent=None):
        """
        初始化信息面板
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # UI工具
        self.ui_utils = UIUtils()
        
        # 语言配置
        self.lang_config = LANG
        
        # 缓存当前数据
        self.current_tmx_data = None
        self.current_source_lang = ""
        self.current_target_lang = ""
        self.current_unit = None
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 文件信息组
        self.create_file_info_group(layout)
        
        # 详细信息组
        self.create_detail_info_group(layout)
    
    def create_file_info_group(self, layout):
        """创建文件信息组"""
        file_group_title = self.lang_config.get('info_panel', {}).get('file_info_group_title', 'File Information')
        self.file_info_group = QGroupBox(file_group_title)
        file_layout = QVBoxLayout(self.file_info_group)
        
        self.file_info = QTextEdit()
        # 根据DPI缩放调整高度
        max_height = self.ui_utils.scale_size(200)
        self.file_info.setMaximumHeight(max_height)
        self.file_info.setReadOnly(True)
        file_layout.addWidget(self.file_info)
        
        layout.addWidget(self.file_info_group)
    
    def create_detail_info_group(self, layout):
        """创建详细信息组"""
        detail_group_title = self.lang_config.get('info_panel', {}).get('detail_info_group_title', 'Entry Details')
        self.detail_info_group = QGroupBox(detail_group_title)
        detail_layout = QVBoxLayout(self.detail_info_group)
        
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
        
        layout.addWidget(self.detail_info_group)
    
    def update_language(self, new_lang_config):
        """
        更新语言配置
        
        Args:
            new_lang_config (dict): 新的语言配置
        """
        self.lang_config = new_lang_config
        
        # 更新组标题
        file_group_title = self.lang_config.get('info_panel', {}).get('file_info_group_title', 'File Information')
        self.file_info_group.setTitle(file_group_title)
        
        detail_group_title = self.lang_config.get('info_panel', {}).get('detail_info_group_title', 'Entry Details')
        self.detail_info_group.setTitle(detail_group_title)
        
        # 如果有缓存数据，重新显示以更新语言
        if self.current_tmx_data:
            self.update_file_info(self.current_tmx_data, self.current_source_lang, self.current_target_lang)
        
        if self.current_unit:
            self.show_unit_details(self.current_unit)
    
    def update_file_info(self, tmx_data, source_lang, target_lang):
        """
        更新文件信息显示
        
        Args:
            tmx_data (dict): TMX数据
            source_lang (str): 源语言
            target_lang (str): 目标语言
        """
        # 缓存数据
        self.current_tmx_data = tmx_data
        self.current_source_lang = source_lang
        self.current_target_lang = target_lang
        
        if not tmx_data:
            return
        
        header = tmx_data['header']
        info_text = []
        
        # 基本信息
        file_info_title = self.lang_config.get('file_info_content', {}).get('file_info_title', '=== TMX File Information ===')
        info_text.append(file_info_title)
        
        total_units_label = self.lang_config.get('file_info_content', {}).get('total_units_label', 'Total Translation Units: {}')
        info_text.append(total_units_label.format(tmx_data['total_units']))
        
        source_lang_label = self.lang_config.get('file_info_content', {}).get('source_lang_label', 'Source Language: {}')
        info_text.append(source_lang_label.format(source_lang))
        
        target_lang_label = self.lang_config.get('file_info_content', {}).get('target_lang_label', 'Target Language: {}')
        info_text.append(target_lang_label.format(target_lang))
        info_text.append("")
        
        # Header属性
        header_info_title = self.lang_config.get('file_info_content', {}).get('header_info_title', '=== Header Information ===')
        info_text.append(header_info_title)
        for key, value in header.items():
            if key not in ['notes', 'properties']:
                info_text.append(f"{key}: {value}")
        
        # Notes
        if 'notes' in header:
            notes_title = self.lang_config.get('file_info_content', {}).get('notes_title', '=== Notes ===')
            info_text.append(f"\n{notes_title}")
            for note in header['notes']:
                info_text.append(f"• {note}")
        
        # Properties
        if 'properties' in header:
            properties_title = self.lang_config.get('file_info_content', {}).get('properties_title', '=== Properties ===')
            info_text.append(f"\n{properties_title}")
            for prop_type, prop_value in header['properties'].items():
                info_text.append(f"{prop_type}: {prop_value}")
        
        self.file_info.setPlainText("\n".join(info_text))
    
    def show_unit_details(self, unit):
        """
        显示翻译单元详细信息
        
        Args:
            unit (dict): 翻译单元数据
        """
        # 缓存当前单元
        self.current_unit = unit
        
        if not unit:
            no_selection_message = self.lang_config.get('detail_info_content', {}).get('no_selection_message', 'Please select a translation unit to view details')
            self.detail_info.setPlainText(no_selection_message)
            return
        
        details = []
        
        # 基本信息
        unit_detail_title = self.lang_config.get('detail_info_content', {}).get('unit_detail_title', '=== Translation Unit Details ===')
        details.append(unit_detail_title)
        
        if unit.get('tuid'):
            tuid_label = self.lang_config.get('detail_info_content', {}).get('tuid_label', 'Unit ID: {}')
            details.append(tuid_label.format(unit['tuid']))
        
        # 属性
        if unit.get('attributes'):
            attributes_title = self.lang_config.get('detail_info_content', {}).get('attributes_title', '=== Unit Attributes ===')
            details.append(f"\n{attributes_title}")
            for key, value in unit['attributes'].items():
                if key != 'tuid':  # tuid已经显示过了
                    details.append(f"{key}: {value}")
        
        # 备注
        if unit.get('notes'):
            notes_title = self.lang_config.get('detail_info_content', {}).get('notes_title', '=== Notes ===')
            details.append(f"\n{notes_title}")
            for note in unit['notes']:
                details.append(f"• {note}")
        
        # 属性
        if unit.get('properties'):
            properties_title = self.lang_config.get('detail_info_content', {}).get('properties_title', '=== Properties ===')
            details.append(f"\n{properties_title}")
            for prop_type, prop_value in unit['properties'].items():
                details.append(f"{prop_type}: {prop_value}")
        
        # 所有语言变体
        if unit.get('variants'):
            variants_title = self.lang_config.get('detail_info_content', {}).get('variants_title', '=== All Language Variants ===')
            details.append(f"\n{variants_title}")
            
            for lang, variant in unit['variants'].items():
                variant_lang_template = self.lang_config.get('detail_info_content', {}).get('variant_lang_template', '[{}]')
                details.append(f"\n{variant_lang_template.format(lang)}")
                
                variant_text_template = self.lang_config.get('detail_info_content', {}).get('variant_text_template', 'Text: {}')
                details.append(variant_text_template.format(variant.get('text', '')))
                
                if variant.get('attributes'):
                    variant_attributes_title = self.lang_config.get('detail_info_content', {}).get('variant_attributes_title', 'Attributes:')
                    details.append(variant_attributes_title)
                    for key, value in variant['attributes'].items():
                        if not key.startswith('{'):  # 跳过namespace属性
                            details.append(f"  {key}: {value}")
                
                if variant.get('notes'):
                    variant_notes_title = self.lang_config.get('detail_info_content', {}).get('variant_notes_title', 'Notes:')
                    details.append(variant_notes_title)
                    for note in variant['notes']:
                        details.append(f"  • {note}")
                
                if variant.get('properties'):
                    variant_properties_title = self.lang_config.get('detail_info_content', {}).get('variant_properties_title', 'Properties:')
                    details.append(variant_properties_title)
                    for prop_type, prop_value in variant['properties'].items():
                        details.append(f"  {prop_type}: {prop_value}")
        
        self.detail_info.setPlainText("\n".join(details))
    
    def clear_info(self):
        """清空信息显示"""
        self.current_tmx_data = None
        self.current_source_lang = ""
        self.current_target_lang = ""
        self.current_unit = None
        
        self.file_info.clear()
        self.detail_info.clear()