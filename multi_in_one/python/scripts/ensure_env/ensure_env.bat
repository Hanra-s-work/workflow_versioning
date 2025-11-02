@echo off
setlocal ENABLEDELAYEDEXPANSION

REM =========================================
REM Constants
REM =========================================
set ERROR=1
set SUCCESS=0
set TRUE=0
set FALSE=1

REM =========================================
REM Determine System Type (Windows Only)
REM =========================================
set "MY_SYSTEM=windows"
set "MAC_SYSTEM=windows"

REM =========================================
REM Helper: ech_info (stdout→stderr)
REM =========================================
:ech_info
    echo %~1 1>&2
    exit /b

REM =========================================
REM Helper: determine_env_name
REM =========================================
:determine_env_name
    if /I "%MY_SYSTEM%"=="linux" (
        set "MY_ENV=lenv"
    ) else if /I "%MAC_SYSTEM%"=="darwin" (
        set "MY_ENV=menv"
    ) else (
        call :ech_info "OS probably not supported"
        call :ech_info "This program has not been tested on your system"
        set "MY_ENV=env_win"
    )
    echo !MY_ENV!
    exit /b

REM =========================================
REM Helper: get_python_binary
REM =========================================
:get_python_binary
    where python3 >nul 2>&1
    set STATUS_PYTHON3=%ERRORLEVEL%
    where python >nul 2>&1
    set STATUS_PYTHON=%ERRORLEVEL%
    where py >nul 2>&1
    set STATUS_PY=%ERRORLEVEL%

    if %STATUS_PYTHON3% NEQ 0 if %STATUS_PYTHON% NEQ 0 if %STATUS_PY% NEQ 0 (
        call :ech_info "You do not have Python installed. Please install Python 3.x and relaunch this script."
        call :ech_info "Aborting program."
        exit /b %ERROR%
    )

    if %STATUS_PYTHON3% EQU 0 (
        echo python3
        exit /b
    ) else if %STATUS_PYTHON% EQU 0 (
        echo python
        exit /b
    ) else if %STATUS_PY% EQU 0 (
        echo py
        exit /b
    )
    exit /b

REM =========================================
REM Helper: get_pip_binary
REM =========================================
:get_pip_binary
    where pip3 >nul 2>&1
    set STATUS_PIP3=%ERRORLEVEL%
    where pip >nul 2>&1
    set STATUS_PIP=%ERRORLEVEL%

    if %STATUS_PIP% NEQ 0 if %STATUS_PIP3% NEQ 0 (
        call :ech_info "You do not have pip installed, please install pip and relaunch this script."
        call :ech_info "Aborting program."
        exit /b %ERROR%
    )

    if %STATUS_PIP% EQU 0 (
        echo pip
        exit /b
    ) else if %STATUS_PIP3% EQU 0 (
        echo pip3
        exit /b
    )
    exit /b

REM =========================================
REM Arguments and Setup
REM =========================================
if "%~1"=="" (
    set "CWD=%CD%"
) else (
    set "CWD=%~1"
)

if "%~2"=="" (
    for /f "delims=" %%E in ('call :determine_env_name') do set "ENV_NAME=%%E"
) else (
    set "ENV_NAME=%~2"
)

for /f "delims=" %%P in ('call :get_python_binary') do set "PYTHON=%%P"
for /f "delims=" %%Q in ('call :get_pip_binary') do set "PIP=%%Q"

call :ech_info "Debug:"
call :ech_info "* MY_SYSTEM: %MY_SYSTEM%"
call :ech_info "* MAC_SYSTEM: %MAC_SYSTEM%"
call :ech_info "* nb args: %*"
call :ech_info "* CWD: %CWD%"
call :ech_info "* ENV_NAME: %ENV_NAME%"
call :ech_info "* PYTHON: %PYTHON%"
call :ech_info "* PIP: %PIP%"

call :ech_info "Entering: %CWD%"
cd /d "%CWD%"

set FRESH_ENV=%FALSE%

REM =========================================
REM Check / Create Virtual Environment
REM =========================================
if not exist "%ENV_NAME%" (
    call :ech_info "Creating environment %ENV_NAME%..."
    "%PYTHON%" -m venv "%ENV_NAME%" 1>&2
    set FRESH_ENV=%TRUE%
) else (
    call :ech_info "Environment %ENV_NAME% already exists, skipping creation."
)

REM =========================================
REM Activation logic
REM =========================================
call :ech_info "Testing environment activation..."
if exist "%CWD%\%ENV_NAME%\Scripts\activate" (
    call :ech_info "Environment activation file found."
    call "%CWD%\%ENV_NAME%\Scripts\activate.bat" 1>&2
) else (
    call :ech_info "No valid environment found, please ensure you are on a proper Windows setup."
    exit /b %ERROR%
)

REM =========================================
REM Update pip if new env
REM =========================================
if %FRESH_ENV%==%TRUE% (
    call :ech_info "Updating pip..."
    "%PYTHON%" -m pip install --upgrade pip 1>&2
)

REM =========================================
REM Deactivate and finish
REM =========================================
call :ech_info "Deactivating environment..."
call deactivate 1>&2

call :ech_info "Exporting the environment path..."
echo %CWD%\%ENV_NAME%

exit /b %SUCCESS%

