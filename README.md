# SLTMX Editor
SLTMX Editor is a TMX viewer developed specifically for check TMX files, which are widely used by translation and localization companies. SLTMX Editor is developed in Python and uses PyQt5 as its GUI framework. At present, it only supports viewing source and target segments in TMX files as well as the attributes. The segment editing and import/export features will be gradually added in the future.



# SLTMX Editor V1.1

TMX翻译记忆库文件编辑器，支持查看、编辑和保存TMX文件。

## 项目结构

```
SLTMX-Editor/
├── main.py                 # 程序入口
├── config/                 # 配置模块
│   ├── __init__.py
│   ├── language.py         # 语言配置加载和管理
│   └── settings.py         # 程序设置和常量
├── core/                   # 核心功能模块
│   ├── __init__.py
│   ├── tmx_parser.py       # TMX文件解析器
│   └── tmx_writer.py       # TMX文件写入器
├── ui/                     # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── menu_bar.py         # 菜单栏管理器
│   ├── table_widget.py     # 表格组件
│   ├── table_delegate.py   # 多行文本编辑器委托
│   ├── table_pagination.py # 分页控件组件
│   └── info_panel.py       # 信息面板组件
├── utils/                  # 工具模块
│   ├── __init__.py
│   └── ui_utils.py         # UI工具函数
├── en-us.json             # 英文语言配置
├── zh-cn.json             # 中文语言配置
├── icon.ico               # 程序图标
└── README.md              # 项目说明
```

## 模块说明

### 配置模块 (config/)
- **language.py**: 多语言配置加载和管理，支持动态语言切换
- **settings.py**: 程序常量和默认设置，包括界面、颜色、字体等配置

### 核心模块 (core/)
- **tmx_parser.py**: TMX文件解析器，支持多线程解析，完整解析TMX结构
- **tmx_writer.py**: TMX文件写入器，保持原有格式，支持修改标记

### UI模块 (ui/)
- **main_window.py**: 主窗口，负责整体布局和业务逻辑，支持语言切换
- **menu_bar.py**: 菜单栏管理器，处理菜单创建、状态管理和语言切换
- **table_widget.py**: 表格组件，支持编辑、搜索、分页和多行文本显示
- **table_delegate.py**: 多行文本编辑器委托，支持富文本编辑
- **table_pagination.py**: 分页控件，支持大文件的分页浏览
- **info_panel.py**: 信息面板，显示文件和条目详细信息

### 工具模块 (utils/)
- **ui_utils.py**: UI工具函数，包括DPI缩放、样式设置等

## 功能特性

### 文件操作
- ✅ 打开TMX文件
- ✅ 关闭文件
- ✅ 保存文件
- ✅ 另存为
- 🚧 导出功能（待实现）
- 🚧 导入功能（待实现）

### 编辑功能
- ✅ 双击编辑翻译单元
- ✅ 多行文本编辑支持
- ✅ 修改标记（背景色变化）
- ✅ 自动保存状态管理
- ✅ 文本自动折行显示
- ✅ 快捷键支持（Ctrl+Enter确认，Esc取消）

### 查看功能
- ✅ 翻译单元表格显示
- ✅ 源文本和目标文本搜索
- ✅ 分页浏览
- ✅ 详细信息面板
- ✅ 文件信息显示
- ✅ 完整文本内容显示（无省略号）

### 界面特性
- ✅ 高DPI支持
- ✅ 响应式布局
- ✅ 多语言界面（中文/English）
- ✅ 现代化UI设计
- ✅ 实时语言切换
- ✅ 关于软件对话框

### 多语言支持
- ✅ 中文界面 (zh-cn)
- ✅ 英文界面 (en-us)
- ✅ 菜单栏语言切换
- ✅ 实时界面文本更新
- ✅ 完整的本地化框架

## 运行要求

- Python 3.6+
- PyQt5
- 语言配置文件 (en-us.json, zh-cn.json)

## 运行方式

```bash
python main.py
```

## 使用指南

### 基本操作
1. **打开文件**: 菜单 → 文件 → 打开，或使用快捷键 Ctrl+O
2. **编辑内容**: 双击表格中的单元格进行编辑
3. **确认编辑**: Ctrl+Enter 确认修改，Esc 取消修改
4. **保存文件**: 菜单 → 编辑 → 保存，或使用快捷键 Ctrl+S
5. **搜索内容**: 在搜索框中输入关键词过滤翻译单元

### 语言切换
1. 菜单栏 → 关于 → 语言
2. 选择"中文"或"English"
3. 界面将立即切换到对应语言

### 界面功能
- **左侧表格**: 显示源文本和目标文本，支持编辑和搜索
- **右侧面板**: 显示文件信息和选中条目的详细信息
- **底部分页**: 支持大文件的分页浏览
- **状态栏**: 显示当前操作状态和文件加载信息

## 开发说明

### 添加新功能
1. 在对应模块中添加功能代码
2. 在配置文件中添加多语言文本
3. 在主窗口中连接相关信号和槽
4. 更新语言切换处理方法

### 修改界面
1. UI组件修改在 `ui/` 模块中进行
2. 样式调整在 `utils/ui_utils.py` 中统一管理
3. 常量配置在 `config/settings.py` 中定义
4. 确保支持DPI缩放

### 添加语言支持
1. 创建新的语言配置文件 (如 `fr-fr.json`)
2. 在 `config/language.py` 中添加对新语言的支持
3. 在菜单栏中添加对应的语言选项
4. 所有文本都通过语言配置获取

### 代码结构规范
- 所有UI文本必须从语言配置文件中读取
- 新增的UI组件需要实现 `update_language()` 方法
- 使用信号-槽机制进行组件间通信
- 遵循单一职责原则，保持模块解耦

## 技术特点

### 架构设计
- **模块化设计**: 清晰的模块分离，便于维护和扩展
- **信号-槽机制**: 使用PyQt5的信号槽实现组件间通信
- **多线程解析**: TMX文件解析在独立线程中进行，避免界面卡顿
- **内存优化**: 大文件支持分页加载，减少内存占用

### 用户体验
- **响应式设计**: 支持不同分辨率和DPI设置
- **实时反馈**: 编辑状态、保存状态等实时显示
- **完整文本显示**: 表格支持多行文本显示，无内容截断
- **快捷操作**: 丰富的快捷键支持

### 扩展性
- **插件式语言支持**: 易于添加新语言
- **配置驱动**: 界面文本、样式等通过配置文件管理
- **模块化架构**: 易于添加新功能模块

## 版本历史

### V1.1 (当前版本)
- ✅ 多语言界面支持
- ✅ 完整的TMX编辑功能
- ✅ 高DPI支持
- ✅ 多行文本编辑
- ✅ 实时语言切换
- ✅ 关于软件对话框
