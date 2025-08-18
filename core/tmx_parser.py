# -*- coding: utf-8 -*-
"""
TMX文件解析器
"""

import xml.etree.ElementTree as ET
from PyQt5.QtCore import QThread, pyqtSignal

from config.language import load_language_config

# 加载语言配置
LANG = load_language_config()

class TMXParser(QThread):
    """TMX文件解析线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int)
    parsing_finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path):
        """
        初始化TMX解析器
        
        Args:
            file_path (str): TMX文件路径
        """
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        """线程运行方法"""
        try:
            self.parse_tmx_file()
        except Exception as e:
            error_msg = LANG.get('dialogs', {}).get('parse_error_prefix', 'Error while parsing tmx file: ') + str(e)
            self.error_occurred.emit(error_msg)

    def parse_tmx_file(self):
        """
        解析TMX文件
        
        解析TMX文件的结构，提取翻译单元、语言变体等信息
        """
        # 解析XML文件
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        
        # 解析header信息
        header_info = self._parse_header(root)
        
        # 解析translation units
        translation_units = self._parse_translation_units(root)
        
        # 构建结果
        result = {
            'header': header_info,
            'translation_units': translation_units,
            'total_units': len(translation_units)
        }
        
        self.parsing_finished.emit(result)
    
    def _parse_header(self, root):
        """
        解析TMX文件头部信息
        
        Args:
            root: XML根节点
            
        Returns:
            dict: 头部信息字典
        """
        header = root.find('header')
        header_info = {}
        
        if header is not None:
            # 获取header属性
            header_info = dict(header.attrib)
            
            # 查找header中的note元素
            notes = [note.text for note in header.findall('note') if note.text]
            if notes:
                header_info['notes'] = notes
            
            # 查找header中的prop元素
            props = {}
            for prop in header.findall('prop'):
                if prop.text:
                    prop_type = prop.get('type', 'unknown')
                    props[prop_type] = prop.text
            if props:
                header_info['properties'] = props
        
        return header_info
    
    def _parse_translation_units(self, root):
        """
        解析翻译单元
        
        Args:
            root: XML根节点
            
        Returns:
            list: 翻译单元列表
        """
        body = root.find('body')
        translation_units = []
        
        if body is not None:
            tu_elements = body.findall('tu')
            total_units = len(tu_elements)
            
            for i, tu in enumerate(tu_elements):
                # 更新进度
                progress = int((i + 1) / total_units * 100)
                self.progress_updated.emit(progress)
                
                # 解析单个翻译单元
                unit_data = self._parse_single_unit(tu)
                translation_units.append(unit_data)
        
        return translation_units
    
    def _parse_single_unit(self, tu):
        """
        解析单个翻译单元
        
        Args:
            tu: 翻译单元XML节点
            
        Returns:
            dict: 翻译单元数据
        """
        unit_data = {
            'tuid': tu.get('tuid', ''),
            'attributes': dict(tu.attrib),
            'notes': [],
            'properties': {},
            'variants': {},
            'modified': False  # 修改标记
        }
        
        # 解析tu级别的note
        for note in tu.findall('note'):
            if note.text:
                unit_data['notes'].append(note.text)
        
        # 解析tu级别的prop
        for prop in tu.findall('prop'):
            prop_type = prop.get('type', 'unknown')
            if prop.text:
                unit_data['properties'][prop_type] = prop.text
        
        # 解析tuv元素（翻译变体）
        for tuv in tu.findall('tuv'):
            variant_data = self._parse_variant(tuv)
            if variant_data:
                lang = variant_data['lang']
                unit_data['variants'][lang] = variant_data
        
        return unit_data
    
    def _parse_variant(self, tuv):
        """
        解析翻译变体
        
        Args:
            tuv: 翻译变体XML节点
            
        Returns:
            dict: 变体数据
        """
        # 获取语言代码
        lang = (tuv.get('{http://www.w3.org/XML/1998/namespace}lang') or 
                tuv.get('xml:lang', 'unknown'))
        
        # 查找seg元素
        seg = tuv.find('seg')
        if seg is None:
            return None
        
        # 提取文本内容
        seg_text = self._extract_text_from_seg(seg)
        
        variant_data = {
            'lang': lang,
            'text': seg_text,
            'attributes': dict(tuv.attrib),
            'notes': [note.text for note in tuv.findall('note') if note.text],
            'properties': {}
        }
        
        # 解析属性
        for prop in tuv.findall('prop'):
            prop_type = prop.get('type', 'unknown')
            if prop.text:
                variant_data['properties'][prop_type] = prop.text
        
        return variant_data
    
    def _extract_text_from_seg(self, seg_element):
        """
        从seg元素中提取文本内容，处理内联标记
        
        Args:
            seg_element: seg XML节点
            
        Returns:
            str: 提取的文本
        """
        text = seg_element.text or ""
        
        # 处理子元素
        for child in seg_element:
            if child.tag in ['bpt', 'ept', 'ph', 'it', 'hi']:
                # 保留标记信息但简化显示
                text += f"[{child.tag}]"
            
            if child.text:
                text += child.text
            if child.tail:
                text += child.tail
        
        return text.strip()
