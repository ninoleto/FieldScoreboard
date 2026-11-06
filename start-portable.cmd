@echo off
cd /d "%~dp0"
start "" "%~dp0fieldscoreboard.exe" --config "%~dp0config.json"
