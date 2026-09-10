@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 -X utf8 "%~dp0l6s_to_txt.py" %*
goto finished
:use_python
python -X utf8 "%~dp0l6s_to_txt.py" %*
:finished
echo.
pause
