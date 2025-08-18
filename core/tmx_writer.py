# -*- coding: utf-8 -*-
"""
TMX文件写入器
"""

import xml.etree.ElementTree as ET
from config.language import load_language_config

# 加载语言配置
LANG = load_language_config()

class TMXWriter:
    """TMX文件写入器"""
    
    def __init__(self, tmx_data):
        """
        初始化TMX写入器
        
        Args:
            tmx_data (dict): TMX数据字典
        """
        self.tmx_data = tmx_data
    
    def save_to_file(self, file_path):
        """
        保存TMX数据到文件
        
        Args:
            file_path (str): 保存文件路径
            
        Raises:
            Exception: 保存失败时抛出异常
        """
        try:
            print(f"开始保存TMX文件到: {file_path}")
            
            # 统计修改的单元数量
            modified_count = sum(1 for unit in self.tmx_data['translation_units'] if unit.get('modified', False))
            print(f"发现 {modified_count} 个修改的翻译单元")
            
            # 创建TMX根元素
            root = self._create_root_element()
            
            # 创建header
            self._create_header(root)
            
            # 创建body
            self._create_body(root)
            
            # 保存文件
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            print(f"TMX文件保存成功: {file_path}")
            
        except Exception as e:
            error_msg = LANG.get('menu', {}).get('save_error', 'Error saving file: ') + str(e)
            print(f"保存失败: {error_msg}")
            raise Exception(error_msg)
    
    def _create_root_element(self):
        """
        创建TMX根元素
        
        Returns:
            Element: XML根元素
        """
        return ET.Element('tmx', version='1.4')
    
    def _create_header(self, root):
        """
        创建header元素
        
        Args:
            root: XML根元素
        """
        header = ET.SubElement(root, 'header')
        header_info = self.tmx_data['header']
        
        # 添加header属性
        for key, value in header_info.items():
            if key not in ['notes', 'properties']:
                header.set(key, str(value))
        
        # 添加header的notes
        if 'notes' in header_info:
            for note_text in header_info['notes']:
                note = ET.SubElement(header, 'note')
                note.text = note_text
        
        # 添加header的properties
        if 'properties' in header_info:
            for prop_type, prop_value in header_info['properties'].items():
                prop = ET.SubElement(header, 'prop', type=prop_type)
                prop.text = prop_value
    
    def _create_body(self, root):
        """
        创建body元素
        
        Args:
            root: XML根元素
        """
        body = ET.SubElement(root, 'body')
        
        # 添加translation units
        for i, unit in enumerate(self.tmx_data['translation_units']):
            self._create_translation_unit(body, unit)
            
            # 打印修改的单元信息
            if unit.get('modified', False):
                print(f"保存修改的单元 {i}: tuid={unit.get('tuid', 'N/A')}")
                for lang, variant in unit['variants'].items():
                    print(f"  {lang}: {variant['text'][:50]}...")
    
    def _create_translation_unit(self, body, unit):
        """
        创建翻译单元元素
        
        Args:
            body: body XML元素
            unit (dict): 翻译单元数据
        """
        tu = ET.SubElement(body, 'tu')
        
        # 设置tuid
        if unit['tuid']:
            tu.set('tuid', unit['tuid'])
        
        # 添加单元属性
        for key, value in unit['attributes'].items():
            if key != 'tuid':  # tuid已经设置过了
                tu.set(key, str(value))
        
        # 添加单元notes
        for note_text in unit['notes']:
            note = ET.SubElement(tu, 'note')
            note.text = note_text
        
        # 添加单元properties
        for prop_type, prop_value in unit['properties'].items():
            prop = ET.SubElement(tu, 'prop', type=prop_type)
            prop.text = prop_value
        
        # 添加语言变体
        for lang, variant in unit['variants'].items():
            self._create_variant(tu, lang, variant)
    
    def _create_variant(self, tu, lang, variant):
        """
        创建语言变体元素
        
        Args:
            tu: 翻译单元XML元素
            lang (str): 语言代码
            variant (dict): 变体数据
        """
        tuv = ET.SubElement(tu, 'tuv')
        tuv.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
        
        # 添加变体属性
        for key, value in variant['attributes'].items():
            if not key.startswith('{'):  # 跳过namespace属性
                tuv.set(key, str(value))
        
        # 添加seg元素
        seg = ET.SubElement(tuv, 'seg')
        seg.text = variant['text']
        
        # 添加变体notes
        for note_text in variant['notes']:
            note = ET.SubElement(tuv, 'note')
            note.text = note_text
        
        # 添加变体properties
        for prop_type, prop_value in variant['properties'].items():
            prop = ET.SubElement(tuv, 'prop', type=prop_type)
            prop.text = prop_value