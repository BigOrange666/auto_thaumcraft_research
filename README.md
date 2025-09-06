# auto_thaumcraft_research
神秘时代自动研究

运行前请先运行tools并修改gc.txt中的坐标信息，确保绿框框落在要素的中心。
gc中每一行分别代表一个点阵,第1，2个值是点阵左上角定位点的屏幕X，Y坐标、3是向右多少个像素是下一个方框、4是向右产生多少个方框、5是向左多少个像素是下一个方框、6是向右左产生多少个方框、7是每个方框的边长。

我的分辨率是2560*1440 100%缩放 GTNH2.8.0 尺寸比例3

## 安装命令

```bash
# 安装所有依赖
pip install -r requirements.txt

## 运行说明
建议使用venv环境，安装依赖后运行run.bat

```
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