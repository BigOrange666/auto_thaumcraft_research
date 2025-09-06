# auto_thaumcraft_research
神秘时代自动研究工具

## 项目简介
这是一个用于《我的世界》GTNH模组中神秘时代（Thaumcraft）自动研究的Python工具。它可以自动识别屏幕上的要素并计算最优的合成路径。

## 安装说明

### 1. 创建虚拟环境
```bash
python -m venv .venv
```

### 2. 激活虚拟环境
```bash
# Windows
.venv\Scripts\activate.bat

# 或者使用PowerShell
.venv\Scripts\Activate.ps1
```

### 3. 安装依赖包
```bash
pip install -r requirements.txt
```

### 4. 配置坐标文件
运行前请先运行tools.py并修改gc.txt中的坐标信息，确保绿框框落在要素的中心。

gc.txt中每一行分别代表一个点阵：
- 第1、2个值是点阵左上角定位点的屏幕X、Y坐标
- 第3个值是向右多少个像素是下一个方框
- 第4个值是向右产生多少个方框
- 第5个值是向左多少个像素是下一个方框
- 第6个值是向右左产生多少个方框
- 第7个值是每个方框的边长

## 运行说明

### 推荐方式：使用批处理文件
```bash
# 运行主程序
run.bat

# 运行工具程序
run-tools.bat
```

### 手动运行方式
```bash
# 设置Qt平台插件路径
set QT_QPA_PLATFORM_PLUGIN_PATH=.venv\lib\site-packages\PyQt5\Qt5\plugins\platforms

# 运行工具程序
python tools.py

# 运行主程序
python main.py
```

## 使用方法

### 主程序快捷键
- **Ctrl+8** - 触发detect_boxes功能（检测并识别屏幕上的元素框）
- **Ctrl+5** - 触发mov功能（执行鼠标移动和拖拽操作）

### 重要使用说明
1. 必须先按Ctrl+8执行检测，然后才能按Ctrl+5执行移动操作
2. 如果Ctrl+5没有反应，请检查控制台输出：
   - `[DEBUG] mov() called, self.res length: 0` - 表示需要先运行Ctrl+8
   - `[WARNING] self.res is empty, please run Ctrl+8 first` - 明确提示需要先运行Ctrl+8

## 常见问题解决

### 1. 依赖包安装错误
如果遇到依赖包冲突错误，请使用我们提供的requirements.txt文件，其中已经解决了版本兼容性问题。

### 2. PyQt5平台插件错误
确保正确设置了QT_QPA_PLATFORM_PLUGIN_PATH环境变量，或者使用run.bat批处理文件运行程序。

### 3. 程序无法识别元素
- 检查gc.txt配置文件中的坐标是否正确
- 确保游戏窗口处于前台且未被遮挡
- 调整游戏分辨率和缩放比例

## 项目结构
- `tools.py` - 基础覆盖层工具
- `main.py` - 主程序，包含自动化功能和调试信息
- `hcb.py` - 核心业务逻辑
- `gc.txt` - 配置文件
- `class.txt` - 类别名称映射
- `ys.txt` - 颜色映射配置
- `requirements.txt` - 依赖包列表
- `run.bat` - 运行脚本
- `run-tools.bat` - 工具运行脚本

## 系统要求
- Windows 10/11
- Python 3.8+
- 推荐分辨率：2560*1440 100%缩放
- GTNH 2.8.0，神秘时代模组

## 调试信息
程序添加了详细的调试输出，可以帮助诊断问题：
- `[DEBUG] mov() called, self.res length: X` - 显示mov函数被调用时的结果数量
- `[WARNING] self.res is empty, please run Ctrl+8 first` - 提示需要先运行检测
- `[DEBUG] Processing result X: ...` - 显示正在处理的结果
- `[DEBUG] Moving from (X,Y) to (X,Y)` - 显示鼠标移动的坐标
- `[ERROR] Error in mov() loop: ...` - 显示具体的错误信息