# 项目依赖包总结

## 已安装的依赖包

### 核心依赖
- **PyQt5==5.15.11** - GUI界面框架
- **PyQt5-Qt5==5.15.2** - Qt5库文件
- **PyQt5_sip==12.17.0** - PyQt5的SIP绑定

### 图像处理
- **Pillow==11.3.0** - Python图像处理库

### 数学计算
- **sympy==1.14.0** - 符号数学计算库
- **mpmath==1.3.0** - 多精度浮点运算库

### 自动化控制
- **keyboard==0.13.5** - 键盘事件监听
- **PyAutoGUI==0.9.54** - GUI自动化控制
- **PyDirectInput==1.0.4** - 直接输入控制
- **pyautogui** - 鼠标和键盘自动化

### 网页解析
- **beautifulsoup4==4.13.5** - HTML/XML解析器
- **soupsieve==2.8** - CSS选择器支持

### 其他工具
- **click==8.2.1** - 命令行工具
- **colorama==0.4.6** - 彩色终端输出
- **MouseInfo==0.1.3** - 鼠标信息工具
- **PyGetWindow==0.0.9** - 窗口管理
- **PyMsgBox==1.0.9** - 消息框工具
- **pyperclip==1.9.0** - 剪贴板操作
- **PyRect==0.2.0** - 矩形操作
- **PyScreeze==1.0.1** - 屏幕截图
- **pytweening==1.2.0** - 缓动函数
- **python-dotenv==1.1.1** - 环境变量管理
- **typing_extensions==4.15.0** - 类型提示扩展

## 安装命令

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或者单独安装核心依赖
pip install Pillow PyQt5 sympy keyboard pydirectinput beautifulsoup4 pyautogui
```

## 运行说明

### 运行tools.py
由于PyQt5需要特定的平台插件，需要设置环境变量：

```bash
# Windows批处理文件方式
run.bat

# 或者手动设置环境变量
set QT_QPA_PLATFORM_PLUGIN_PATH=.venv\lib\site-packages\PyQt5\Qt5\plugins\platforms
python tools.py
```

### 运行main.py
```bash
# 推荐使用批处理文件运行
cmd /c run.bat

# 或者手动设置环境变量后运行
set QT_QPA_PLATFORM_PLUGIN_PATH=.venv\lib\site-packages\PyQt5\Qt5\plugins\platforms
python main.py
```

## 快捷键说明

### main.py程序快捷键
- **Ctrl+8** - 触发detect_boxes功能（检测并识别屏幕上的元素框）
- **Ctrl+5** - 触发mov功能（执行鼠标移动和拖拽操作）

**重要使用说明：**
1. 必须先按Ctrl+8执行检测，然后才能按Ctrl+5执行移动操作
2. 如果Ctrl+5没有反应，请检查控制台输出：
   - `[DEBUG] mov() called, self.res length: 0` - 表示需要先运行Ctrl+8
   - `[WARNING] self.res is empty, please run Ctrl+8 first` - 明确提示需要先运行Ctrl+8

### tools.py程序
- 程序启动后会在屏幕上显示覆盖层，无特定快捷键

## 功能说明

### detect_boxes() 功能
当按下Ctrl+8时，程序会：
1. 读取配置文件中的坐标信息
2. 截取屏幕图像
3. 识别元素框中的内容
4. 计算最优路径和放置方案
5. 在覆盖层上显示识别结果
6. 将结果存储在`self.res`中供mov()函数使用
7. 在控制台输出计算结果

### mov() 功能
当按下Ctrl+5时，程序会：
1. 读取之前detect_boxes()计算出的放置方案（存储在self.res中）
2. 自动执行鼠标移动和拖拽操作
3. 将元素从源位置拖拽到目标位置
4. 在控制台显示详细的调试信息

**重要：如果直接按Ctrl+5而没有先执行Ctrl+8，将显示警告信息并提示需要先运行Ctrl+8。**

## 调试信息说明

程序添加了详细的调试输出，可以帮助诊断问题：

- `[DEBUG] mov() called, self.res length: X` - 显示mov函数被调用时的结果数量
- `[WARNING] self.res is empty, please run Ctrl+8 first` - 提示需要先运行检测
- `[DEBUG] Processing result X: ...` - 显示正在处理的结果
- `[DEBUG] Moving from (X,Y) to (X,Y)` - 显示鼠标移动的坐标
- `[ERROR] Error in mov() loop: ...` - 显示具体的错误信息

## 常见问题排查

### Ctrl+5没有反应
1. **检查是否先按了Ctrl+8** - 这是必须的步骤
2. **检查控制台输出** - 查看是否有警告信息
3. **检查self.res是否为空** - 如果为空说明检测没有找到元素
4. **检查element_boxes_have** - 确保源元素被正确识别

### 程序启动失败
1. **Qt平台插件错误** - 使用run.bat或设置QT_QPA_PLATFORM_PLUGIN_PATH环境变量
2. **缺少依赖包** - 运行`pip install -r requirements.txt`

## 项目结构
- `tools.py` - 基础覆盖层工具
- `main.py` - 主程序，包含自动化功能和调试信息
- `hcb.py` - 核心业务逻辑
- `gc.txt` - 配置文件
- `class.txt` - 类别名称映射
- `ys.txt` - 颜色映射配置
- `requirements.txt` - 依赖包列表
- `run.bat` - 运行脚本
- `DEPENDENCIES.md` - 依赖包和使用说明文档