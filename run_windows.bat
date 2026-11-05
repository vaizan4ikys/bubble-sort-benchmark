@echo off
rem Second-machine check on Windows. Usage: run_windows.bat [name] [--check]  (or double-click)
rem Finds Python, then runs scripts\run_portable.py, which does the actual work.
setlocal
cd /d "%~dp0"
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY python --version >nul 2>&1 && set "PY=python"
if not defined PY (
    echo ERROR: Python 3 was not found. Install it from https://www.python.org/downloads/ and open a new window.
    pause
    exit /b 1
)
%PY% scripts\run_portable.py %*
set "RC=%errorlevel%"
pause
exit /b %RC%
