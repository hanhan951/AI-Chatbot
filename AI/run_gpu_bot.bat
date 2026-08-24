@echo off
cd /d %~dp0
echo Starting bot with Python 3.11 GPU environment...
.venv311\Scripts\python.exe class_bot.py
pause
