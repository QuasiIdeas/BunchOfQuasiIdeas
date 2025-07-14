@echo off
REM 1) Активация окружения base
call "C:\Users\USER\anaconda3\Scripts\activate.bat" base

REM 2) Запуск скрипта без консоли
start "" "%CONDA_PREFIX%\pythonw.exe" "d:\Projects\BunchOfQuasiIdeas\en\useful_promts\curiosity_drive\know_you_background.py"
exit