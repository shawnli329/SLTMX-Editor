# -*- coding: utf-8 -*-
"""
多行文本编辑器委托
"""

from PyQt5.QtWidgets import QStyledItemDelegate, QTextEdit
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeyEvent, QTextOption

from config.settings import DEFAULT_FONT_SIZE
from utils.ui_utils import UIUtils

class MultiLineTextDelegate(QStyledItemDelegate):
    """多行文本编辑器委托"""
    
    def __init__(self, parent=None):
        """
        初始化委托
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        self.ui_utils = UIUtils()
    
    def createEditor(self, parent, option, index):
        """
        创建编辑器
        
        Args:
            parent: 父窗口
            option: 样式选项
            index: 模型索引
            
        Returns:
            QTextEdit: 多行文本编辑器
        """
        editor = QTextEdit(parent)
        
        # 设置编辑器属性
        editor.setAcceptRichText(False)  # 只接受纯文本
        
        # 修复：使用正确的换行模式
        editor.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)  # 启用自动换行
        editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        editor.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置字体
        font = self.ui_utils.get_scaled_font(DEFAULT_FONT_SIZE)
        editor.setFont(font)
        
        # 设置最小高度
        min_height = self.ui_utils.scale_size(60)  # 最小60px
        editor.setMinimumHeight(min_height)
        
        # 安装事件过滤器
        editor.installEventFilter(self)
        
        return editor
    
    def setEditorData(self, editor, index):
        """
        设置编辑器数据
        
        Args:
            editor: 编辑器
            index: 模型索引
        """
        text = index.model().data(index, Qt.EditRole)
        if text is not None:
            editor.setPlainText(str(text))
        
        # 选中所有文本，方便编辑
        cursor = editor.textCursor()
        cursor.select(cursor.Document)
        editor.setTextCursor(cursor)
    
    def setModelData(self, editor, model, index):
        """
        将编辑器数据设置回模型
        
        Args:
            editor: 编辑器
            model: 数据模型
            index: 模型索引
        """
        text = editor.toPlainText()
        model.setData(index, text, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """
        更新编辑器几何形状
        
        Args:
            editor: 编辑器
            option: 样式选项
            index: 模型索引
        """
        # 获取单元格的矩形区域
        rect = option.rect
        
        # 计算编辑器需要的高度
        editor.document().setTextWidth(rect.width())
        height = editor.document().size().height()
        
        # 设置最小和最大高度
        min_height = self.ui_utils.scale_size(60)
        max_height = self.ui_utils.scale_size(300)  # 最大300px
        
        height = max(min_height, min(height + 10, max_height))  # 添加10px边距
        
        # 调整矩形大小
        rect.setHeight(int(height))
        editor.setGeometry(rect)
    
    def eventFilter(self, editor, event):
        """
        事件过滤器，处理键盘事件
        
        Args:
            editor: 编辑器
            event: 事件
            
        Returns:
            bool: 是否处理了事件
        """
        if isinstance(event, QKeyEvent):
            # Ctrl+Enter 或 Shift+Enter 完成编辑
            if event.type() == QEvent.KeyPress:
                if ((event.modifiers() & Qt.ControlModifier) and event.key() == Qt.Key_Return) or \
                   ((event.modifiers() & Qt.ShiftModifier) and event.key() == Qt.Key_Return):
                    self.commitData.emit(editor)
                    self.closeEditor.emit(editor)
                    return True
                # Escape 取消编辑
                elif event.key() == Qt.Key_Escape:
                    self.closeEditor.emit(editor)
                    return True
        
        return super().eventFilter(editor, event)