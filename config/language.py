# -*- coding: utf-8 -*-
"""
语言配置模块
"""

import json
import os

def load_language_config(language='zh-cn'):
    """
    加载语言配置文件
    
    Args:
        language (str): 语言代码，如 'en-us', 'zh-cn'
        
    Returns:
        dict: 语言配置字典
    """
    try:
        config_path = f"{language}.json"
        if not os.path.exists(config_path):
            print(f"Language config file {config_path} not found, using default texts")
            # 如果请求的语言文件不存在，尝试加载默认语言
            if language != 'zh-cn':
                return load_language_config('zh-cn')
            return {}
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"Successfully loaded language config: {config_path}")
            return config
            
    except json.JSONDecodeError as e:
        print(f"Error parsing {config_path}: {e}, using default texts")
        # 如果解析出错，尝试加载默认语言
        if language != 'zh-cn':
            return load_language_config('zh-cn')
        return {}
    except Exception as e:
        print(f"Error loading language config: {e}, using default texts")
        # 如果加载出错，尝试加载默认语言
        if language != 'zh-cn':
            return load_language_config('zh-cn')
        return {}

def get_text(config, key_path, default_text=""):
    """
    从配置中获取文本
    
    Args:
        config (dict): 语言配置字典
        key_path (str): 键路径，如 'menu.file_menu'
        default_text (str): 默认文本
        
    Returns:
        str: 对应的文本
    """
    keys = key_path.split('.')
    current = config
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default_text

def get_available_languages():
    """
    获取可用的语言列表
    
    Returns:
        list: 可用语言代码列表
    """
    available_languages = []
    
    # 检查常见的语言文件
    language_files = ['zh-cn.json', 'en-us.json']
    
    for lang_file in language_files:
        if os.path.exists(lang_file):
            lang_code = lang_file.replace('.json', '')
            available_languages.append(lang_code)
    
    return available_languages

def switch_language_globally(language_code):
    """
    全局切换语言（这个函数可以用于需要全局语言切换的场景）
    
    Args:
        language_code (str): 语言代码
        
    Returns:
        dict: 新的语言配置
    """
    return load_language_config(language_code)