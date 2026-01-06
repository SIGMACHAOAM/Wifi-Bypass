@echo off
setlocal EnableDelayedExpansion
title Auto MAC Randomizer - Made by Tohn

REM ADMIN CHECK
net session >nul 2>&1 || (
    cls
    echo ==============================================
    echo                ACCESS DENIED
    echo ==============================================
    echo   Please run this file as Administrator.
    echo ==============================================
    pause
    exit /b
)

cls
echo ==============================================
echo            MAC Address Changer
echo ==============================================
echo              Made by Tohn
echo ==============================================
echo.

REM DETECT ACTIVE ADAPTER
echo [ .. ] Detecting active network adapter...

for /f "tokens=2 delims=:" %%A in ('
    netsh interface show interface ^| findstr /R "Connected.*Dedicated"
') do (
    set "ADAPTER_NAME=%%A"
    goto gotAdapter
)

:gotAdapter
set "ADAPTER_NAME=%ADAPTER_NAME:~1%"

if not defined ADAPTER_NAME (
    echo [ !! ] No active adapter detected.
    echo.
    pause
    exit /b
)

echo [ OK ] Adapter detected
echo       Name : %ADAPTER_NAME%
echo.

REM GET ADAPTER GUID
echo [ .. ] Retrieving adapter identifier...

for /f "tokens=3" %%G in ('
    netsh interface show interface name^="%ADAPTER_NAME%" ^| find "GUID"
') do (
    set "ADAPTER_GUID=%%G"
)

if not defined ADAPTER_GUID (
    echo [ !! ] Failed to retrieve adapter identifier.
    echo.
    pause
    exit /b
)

echo [ OK ] Identifier found
echo       ID   : %ADAPTER_GUID%
echo.

REM GENERATE RANDOM MAC
echo [ .. ] Generating randomized MAC address...

set "MAC=02"
for /L %%i in (1,1,5) do (
    set /A B=!random! %% 256
    set H=00!B!
    set MAC=!MAC!!H:~-2!
)

echo [ OK ] MAC generated
echo       MAC  : %MAC%
echo.

REM LOCATE REGISTRY KEY
echo [ .. ] Locating system registry entry...

set "REGKEY="

for /f "tokens=*" %%K in ('
    reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}" /s /v NetCfgInstanceId ^| find "%ADAPTER_GUID%"
') do (
    set "LINE=%%K"
)

for %%K in (%LINE%) do set "REGKEY=%%K"

if not defined REGKEY (
    echo [ !! ] Registry entry not found.
    echo.
    pause
    exit /b
)

echo [ OK ] Registry entry located
echo.

REM APPLY MAC
echo [ .. ] Applying MAC address...
reg add "%REGKEY%" /v NetworkAddress /t REG_SZ /d %MAC% /f >nul
echo [ OK ] MAC successfully applied
echo.

REM RESTART ADAPTER
echo [ .. ] Restarting network adapter...
netsh interface set interface "%ADAPTER_NAME%" disable >nul
timeout /t 2 >nul
netsh interface set interface "%ADAPTER_NAME%" enable >nul
echo [ OK ] Adapter restarted
echo.

echo ==============================================
echo                  COMPLETE
echo ==============================================
echo   New MAC Address
echo   %MAC%
echo ==============================================
echo.
pause
