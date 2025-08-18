# SLTMX Editor
SLTMX Editor is a TMX viewer developed specifically for check TMX files, which are widely used by translation and localization companies. SLTMX Editor is developed in Python and uses PyQt5 as its GUI framework. At present, it only supports viewing source and target segments in TMX files as well as the attributes. The segment editing and import/export features will be gradually added in the future.

TMX翻译记忆库文件编辑器，支持查看、编辑和保存TMX文件。

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
