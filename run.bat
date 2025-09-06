@echo off
call .venv\Scripts\activate.bat
set QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0.venv\lib\site-packages\PyQt5\Qt5\plugins\platforms
python main.py
pause