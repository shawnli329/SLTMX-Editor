# -*- coding: utf-8 -*-
"""
菜单栏管理器
"""

from PyQt5.QtWidgets import QAction, QActionGroup
from PyQt5.QtCore import Qt, QObject, pyqtSignal

from config.language import load_language_config

# 加载语言配置
LANG = load_language_config()

class MenuBarManager(QObject):
    """菜单栏管理器"""
    
    # 添加语言切换信号
    language_changed = pyqtSignal(str)
    
    def __init__(self, main_window):
        """
        初始化菜单栏管理器
        
        Args:
            main_window: 主窗口实例
        """
        super().__init__(main_window)
        self.main_window = main_window
        self.file_actions = {}
        self.edit_actions = {}
        self.about_actions = {}
        self.current_language = 'zh-cn'  # 默认语言
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.main_window.menuBar()
        
        # 创建文件菜单
        self.create_file_menu(menubar)
        
        # 创建编辑菜单
        self.create_edit_menu(menubar)
        
        # 创建关于菜单
        self.create_about_menu(menubar)
    
    def create_file_menu(self, menubar):
        """
        创建文件菜单
        
        Args:
            menubar: 菜单栏对象
        """
        file_menu_title = LANG.get('menu', {}).get('file_menu', '文件')
        file_menu = menubar.addMenu(file_menu_title)
        
        # 打开
        open_action = self.create_action(
            'open_action', '打开',
            'Ctrl+O',
            self.main_window.open_file
        )
        file_menu.addAction(open_action)
        self.file_actions['open'] = open_action
        
        # 关闭
        close_action = self.create_action(
            'close_action', '关闭',
            None,
            self.main_window.close_file
        )
        file_menu.addAction(close_action)
        self.file_actions['close'] = close_action
        
        file_menu.addSeparator()
        
        # 另存为
        save_as_action = self.create_action(
            'save_as_action', '另存为',
            None,
            self.main_window.save_as_file
        )
        file_menu.addAction(save_as_action)
        self.file_actions['save_as'] = save_as_action
        
        file_menu.addSeparator()
        
        # 导出
        export_action = self.create_action(
            'export_action', '导出',
            None,
            self.main_window.export_file
        )
        file_menu.addAction(export_action)
        self.file_actions['export'] = export_action
        
        # 导入
        import_action = self.create_action(
            'import_action', '导入',
            None,
            self.main_window.import_file
        )
        file_menu.addAction(import_action)
        self.file_actions['import'] = import_action
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = self.create_action(
            'exit_action', '退出',
            'Ctrl+Q',
            self.main_window.close
        )
        file_menu.addAction(exit_action)
        self.file_actions['exit'] = exit_action
        
        # 初始状态：除了打开和退出，其他都禁用
        self.set_file_loaded(False)
    
    def create_edit_menu(self, menubar):
        """
        创建编辑菜单
        
        Args:
            menubar: 菜单栏对象
        """
        edit_menu_title = LANG.get('menu', {}).get('edit_menu', '编辑')
        edit_menu = menubar.addMenu(edit_menu_title)
        
        # 保存
        save_action = self.create_action(
            'save_action', '保存',
            'Ctrl+S',
            self.main_window.save_file
        )
        edit_menu.addAction(save_action)
        self.edit_actions['save'] = save_action
        
        # 初始状态：禁用保存
        self.set_has_modifications(False)
    
    def create_about_menu(self, menubar):
        """
        创建关于菜单
        
        Args:
            menubar: 菜单栏对象
        """
        about_menu_title = LANG.get('menu', {}).get('about_menu', '关于')
        about_menu = menubar.addMenu(about_menu_title)
        
        # 语言子菜单
        language_menu_title = LANG.get('menu', {}).get('language_menu', '语言')
        language_menu = about_menu.addMenu(language_menu_title)
        
        # 创建语言动作组（确保只能选择一种语言）
        language_group = QActionGroup(self.main_window)
        language_group.setExclusive(True)
        
        # 中文
        chinese_action = self.create_language_action(
            'chinese_action', '中文',
            'zh-cn', language_group
        )
        language_menu.addAction(chinese_action)
        self.about_actions['chinese'] = chinese_action
        
        # English
        english_action = self.create_language_action(
            'english_action', 'English',
            'en-us', language_group
        )
        language_menu.addAction(english_action)
        self.about_actions['english'] = english_action
        
        # 设置默认选中中文
        chinese_action.setChecked(True)
        
        # 关于软件
        about_menu.addSeparator()
        about_software_action = self.create_action(
            'about_software_action', '关于软件',
            None,
            self.main_window.show_about_dialog
        )
        about_menu.addAction(about_software_action)
        self.about_actions['about_software'] = about_software_action
    
    def create_action(self, config_key, default_text, shortcut, callback):
        """
        创建菜单动作
        
        Args:
            config_key (str): 配置文件中的键
            default_text (str): 默认文本
            shortcut (str): 快捷键
            callback: 回调函数
            
        Returns:
            QAction: 菜单动作
        """
        text = LANG.get('menu', {}).get(config_key, default_text)
        action = QAction(text, self.main_window)
        
        if shortcut:
            action.setShortcut(shortcut)
        
        action.triggered.connect(callback)
        return action
    
    def create_language_action(self, config_key, default_text, language_code, action_group):
        """
        创建语言切换动作
        
        Args:
            config_key (str): 配置文件中的键
            default_text (str): 默认文本
            language_code (str): 语言代码
            action_group (QActionGroup): 动作组
            
        Returns:
            QAction: 语言动作
        """
        text = LANG.get('menu', {}).get(config_key, default_text)
        action = QAction(text, self.main_window)
        action.setCheckable(True)
        action_group.addAction(action)
        
        # 连接语言切换信号
        action.triggered.connect(lambda: self.change_language(language_code))
        
        return action
    
    def change_language(self, language_code):
        """
        切换语言
        
        Args:
            language_code (str): 语言代码
        """
        if language_code != self.current_language:
            self.current_language = language_code
            # 通知主窗口语言已切换
            self.main_window.switch_language(language_code)
    
    def update_menu_texts(self, new_lang_config):
        """
        更新菜单文本
        
        Args:
            new_lang_config (dict): 新的语言配置
        """
        global LANG
        LANG = new_lang_config
        
        # 更新所有菜单文本
        self._update_menu_bar_texts()
        self._update_action_texts()
    
    def _update_menu_bar_texts(self):
        """更新菜单栏标题"""
        menubar = self.main_window.menuBar()
        menus = menubar.findChildren(menubar.__class__)
        
        # 更新主菜单标题
        actions = menubar.actions()
        if len(actions) >= 3:
            # 文件菜单
            actions[0].setText(LANG.get('menu', {}).get('file_menu', '文件'))
            # 编辑菜单  
            actions[1].setText(LANG.get('menu', {}).get('edit_menu', '编辑'))
            # 关于菜单
            actions[2].setText(LANG.get('menu', {}).get('about_menu', '关于'))
            
            # 更新语言子菜单标题
            about_menu = actions[2].menu()
            if about_menu and len(about_menu.actions()) >= 1:
                language_action = about_menu.actions()[0]
                if hasattr(language_action, 'menu') and language_action.menu():
                    language_action.setText(LANG.get('menu', {}).get('language_menu', '语言'))
    
    def _update_action_texts(self):
        """更新动作文本"""
        # 更新文件菜单动作
        action_mappings = {
            'open': 'open_action',
            'close': 'close_action', 
            'save_as': 'save_as_action',
            'export': 'export_action',
            'import': 'import_action',
            'exit': 'exit_action'
        }
        
        for action_key, config_key in action_mappings.items():
            if action_key in self.file_actions:
                default_text = self.file_actions[action_key].text()
                new_text = LANG.get('menu', {}).get(config_key, default_text)
                self.file_actions[action_key].setText(new_text)
        
        # 更新编辑菜单动作
        if 'save' in self.edit_actions:
            new_text = LANG.get('menu', {}).get('save_action', '保存')
            self.edit_actions['save'].setText(new_text)
        
        # 更新关于菜单动作
        about_mappings = {
            'chinese': 'chinese_action',
            'english': 'english_action', 
            'about_software': 'about_software_action'
        }
        
        for action_key, config_key in about_mappings.items():
            if action_key in self.about_actions:
                default_text = self.about_actions[action_key].text()
                new_text = LANG.get('menu', {}).get(config_key, default_text)
                self.about_actions[action_key].setText(new_text)
    
    def set_file_loaded(self, loaded):
        """
        设置文件加载状态
        
        Args:
            loaded (bool): 是否已加载文件
        """
        # 根据文件加载状态启用/禁用菜单项
        self.file_actions['close'].setEnabled(loaded)
        self.file_actions['save_as'].setEnabled(loaded)
        self.file_actions['export'].setEnabled(loaded)
        # import 始终可用
        # open 和 exit 始终可用
    
    def set_has_modifications(self, has_modifications):
        """
        设置是否有修改
        
        Args:
            has_modifications (bool): 是否有未保存的修改
        """
        self.edit_actions['save'].setEnabled(has_modifications)