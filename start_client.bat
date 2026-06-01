@echo off
chcp 65001 >nul
echo ============================================
echo   ПОДКЛЮЧЕНИЕ К СЕРВЕРУ УСПЕВАЕМОСТИ
echo ============================================
echo.

set saved_ip=
if exist "%~dp0server_ip.txt" set /p saved_ip=<"%~dp0server_ip.txt"

if not "%saved_ip%"=="" (
    echo Сохранённый IP сервера: %saved_ip%
    choice /c YN /m "Использовать этот IP? (Y-да, N-новый)"
    if errorlevel 2 goto :new_ip
    set server_ip=%saved_ip%
    goto :connect
)

:new_ip
set /p server_ip="Введите IP-адрес сервера: "
echo %server_ip%>"%~dp0server_ip.txt"

:connect
powershell -Command "(Get-Content '%~dp0frontend\js\config.js') -replace 'http://[^:]+:8001', 'http://%server_ip%:8001' | Set-Content '%~dp0frontend\js\config.js'"
echo.
echo Подключение к http://%server_ip%:8001...
start "" "http://%server_ip%:8001/static/pages/login.html"