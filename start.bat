```batch
@echo off
chcp 65001 >nul
title Student Performance System
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:menu
cls
echo ============================================
echo   STUDENT PERFORMANCE SYSTEM
echo ============================================
echo.
echo   1. Запустить СЕРВЕР
echo   2. Запустить КЛИЕНТ
echo   3. Установить библиотеки
echo   4. Добавить Python в PATH
echo   5. Выход
echo.
echo ============================================
set /p choice="Выберите действие (1-5): "

if "%choice%"=="1" goto :server
if "%choice%"=="2" goto :client
if "%choice%"=="3" goto :install
if "%choice%"=="4" goto :add_python
if "%choice%"=="5" exit
goto :menu

:: ============================================
:: ЗАПУСК СЕРВЕРА
:: ============================================
:server
cls
echo ============================================
echo   ЗАПУСК СЕРВЕРА
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [!] Python не найден!
    echo Запустите пункт 4 для добавления Python в PATH
    pause
    goto :menu
)

set saved_ip=
if exist "%SCRIPT_DIR%server_ip.txt" set /p saved_ip=<"%SCRIPT_DIR%server_ip.txt"

if not "%saved_ip%"=="" (
    echo Сохранённый IP: %saved_ip%
    choice /c YN /m "Использовать? (Y/N) "
    if errorlevel 2 goto :new_server_ip
    set server_ip=%saved_ip%
    goto :run_server
)

:new_server_ip
for /f "delims=" %%a in ('powershell -Command "(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notmatch 'Loopback' -and $_.IPAddress -notmatch '169\.'}).IPAddress | Select-Object -First 1"') do set detected_ip=%%a
if "%detected_ip%"=="" set detected_ip=127.0.0.1

echo Ваш IP: %detected_ip%
set /p server_ip="Введите IP [%detected_ip%]: "
if "%server_ip%"=="" set server_ip=%detected_ip%
echo %server_ip%>"%SCRIPT_DIR%server_ip.txt"

:run_server
echo [*] Обновление конфигурации...
powershell -Command "(Get-Content '%SCRIPT_DIR%frontend\js\config.js') -replace 'http://[^:]+:8001', 'http://%server_ip%:8001' | Set-Content '%SCRIPT_DIR%frontend\js\config.js'"

echo [*] Запуск сервера...
start "Server" cmd /k "cd /d %SCRIPT_DIR%backend && python run.py"

echo [*] Ожидание 8 секунд...
timeout /t 8 >nul

echo [*] Открытие браузера...
start "" "http://%server_ip%:8001/static/pages/login.html"

echo.
echo ============================================
echo   Сервер: http://%server_ip%:8001
echo   Для остановки закройте окно Server
echo ============================================
pause
goto :menu

:: ============================================
:: ЗАПУСК КЛИЕНТА
:: ============================================
:client
cls
echo ============================================
echo   ПОДКЛЮЧЕНИЕ К СЕРВЕРУ
echo ============================================
echo.

set saved_ip=
if exist "%SCRIPT_DIR%server_ip.txt" set /p saved_ip=<"%SCRIPT_DIR%server_ip.txt"

if not "%saved_ip%"=="" (
    echo Сохранённый IP: %saved_ip%
    choice /c YN /m "Использовать? (Y/N) "
    if errorlevel 2 goto :new_client_ip
    set server_ip=%saved_ip%
    goto :connect
)

:new_client_ip
set /p server_ip="Введите IP сервера: "
echo %server_ip%>"%SCRIPT_DIR%server_ip.txt"

:connect
powershell -Command "(Get-Content '%SCRIPT_DIR%frontend\js\config.js') -replace 'http://[^:]+:8001', 'http://%server_ip%:8001' | Set-Content '%SCRIPT_DIR%frontend\js\config.js'"
echo [*] Подключение к http://%server_ip%:8001...
start "" "http://%server_ip%:8001/static/pages/login.html"
echo ============================================
pause
goto :menu

:: ============================================
:: УСТАНОВКА БИБЛИОТЕК
:: ============================================
:install
cls
echo ============================================
echo   УСТАНОВКА БИБЛИОТЕК
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [!] Python не найден в PATH!
    echo.
    echo Сначала выполните пункт 4 — "Добавить Python в PATH"
    echo Затем перезапустите этот скрипт.
    echo.
    pause
    goto :menu
)

echo [*] Python найден:
python --version
echo.
echo [*] Установка библиотек...
echo.
pip install -r "%SCRIPT_DIR%backend\requirements.txt"
echo.
echo ============================================
echo   [OK] Установка завершена!
echo ============================================
pause
goto :menu

:: ============================================
:: ДОБАВЛЕНИЕ PYTHON В PATH
:: ============================================
:add_python
cls
echo ============================================
echo   ДОБАВЛЕНИЕ PYTHON В PATH
echo ============================================
echo.

set "PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312"
set "SCRIPTS_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\Scripts"

if exist "%PYTHON_PATH%\python.exe" (
    echo [*] Найден Python: %PYTHON_PATH%
    echo [*] Добавляю в системный PATH...
    powershell -Command "$path = [Environment]::GetEnvironmentVariable('Path', 'Machine'); if ($path -notlike '*Python312*') { [Environment]::SetEnvironmentVariable('Path', \"%PYTHON_PATH%;%SCRIPTS_PATH%;$path\", 'Machine') }"
    set "PATH=%PYTHON_PATH%;%SCRIPTS_PATH%;%PATH%"
    echo [OK] Python добавлен в PATH. Перезапустите командную строку.
) else (
    echo [!] Python не найден по пути: %PYTHON_PATH%
    echo Установите Python с python.org (с галочкой "Add to PATH")
)
pause
goto :menu
```