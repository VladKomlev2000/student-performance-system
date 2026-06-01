@echo off
chcp 65001 >nul
title Сервер учёта успеваемости
echo ============================================
echo   ЗАПУСК СЕРВЕРА
echo ============================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python не найден!
    pause
    exit /b
)

:: Получаем IP
for /f "delims=" %%a in ('powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch 'Loopback' -and $_.IPAddress -notmatch '169\.'}).IPAddress | Select-Object -First 1"') do set server_ip=%%a
if "%server_ip%"=="" set server_ip=127.0.0.1

echo IP сервера: %server_ip%
echo %server_ip%>"%~dp0server_ip.txt"

echo [*] Обновление конфигурации...
powershell -Command "(Get-Content '%~dp0frontend\js\config.js') -replace 'http://[^:]+:8001', 'http://%server_ip%:8001' | Set-Content '%~dp0frontend\js\config.js'"

echo [*] Запуск сервера на порту 8001...
cd /d "%~dp0backend"
python run.py
pause