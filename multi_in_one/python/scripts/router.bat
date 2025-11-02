@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ===============================
REM Constants
REM ===============================
set SUCCESS=0
set FAILURE=1
set TRUE=0
set FALSE=1

REM ===============================
REM Directories
REM ===============================
set "CWD=%CD%"
set "SCRIPTS_DIR=%CWD%\scripts"

set CONTINUE_LOOPING=%TRUE%

REM ===============================
REM Detect Python
REM ===============================
set PYTHON_FOUND=%FALSE%
set PYTHON=NULL

where python3 >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON=python3"
    set PYTHON_FOUND=%TRUE%
) else (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "PYTHON=python"
        set PYTHON_FOUND=%TRUE%
    ) else (
        where py >nul 2>&1
        if %ERRORLEVEL%==0 (
            set "PYTHON=py"
            set PYTHON_FOUND=%TRUE%
        ) else (
            echo Router: No Python version found on your computer (or its PATH variable), disabling options relying on Python.
            set PYTHON_FOUND=%FALSE%
        )
    )
)

REM As none of the python overlay functionalities are implemented yet, it is disabled
set PYTHON_FOUND=%FALSE%

REM ===============================
REM Helper functions (as labels)
REM ===============================
:compile
    echo compile
    call "%PYTHON%" "%SCRIPTS_DIR%\compile"
    exit /b %ERRORLEVEL%

:coverage
    echo coverage
    call "%SCRIPTS_DIR%\coverage\coverage.bat"
    exit /b %ERRORLEVEL%

:document
    echo document
    call "%SCRIPTS_DIR%\document\document.bat"
    exit /b %ERRORLEVEL%

:library
    echo library
    call "%SCRIPTS_DIR%\lib\lib.bat"
    exit /b %ERRORLEVEL%

:tester
    echo tester
    call "%SCRIPTS_DIR%\test\test.bat"
    exit /b %ERRORLEVEL%

:run_raw
    echo run_raw
    call "%SCRIPTS_DIR%\run_raw\run_raw.bat"
    exit /b %ERRORLEVEL%

:version
    echo version
    call "%SCRIPTS_DIR%\version\version.bat"
    exit /b %ERRORLEVEL%

:help_section
    echo help
    call "%SCRIPTS_DIR%\helper\helper.bat"
    exit /b %ERRORLEVEL%

:author
    echo Author
    echo These sets of scripts were written by (c) Henry Letellier
    echo They are provided as is and without any warranty.
    exit /b %SUCCESS%

:about
    echo about
    call "%SCRIPTS_DIR%\about\about.bat"
    exit /b %ERRORLEVEL%

:gui
    echo gui
    call "%PYTHON%" "%SCRIPTS_DIR%\gui"
    exit /b %ERRORLEVEL%

:tui
    echo tui
    call "%PYTHON%" "%SCRIPTS_DIR%\tui"
    exit /b %ERRORLEVEL%

REM ===============================
REM Main Script
REM ===============================
echo Debug:
echo * CWD: %CWD%
echo * Scripts: %SCRIPTS_DIR%
echo.
echo Welcome to the router script!
call :author
echo.

:mainloop
    echo Router menu options:
    set /p USER_RESPONSE="(com)pile (cov)erage (d)ocument (l)ibrary (te)ster (r)un_raw (v)ersion (h)elp (au)thor (ab)out "
    if "%PYTHON_FOUND%"=="%TRUE%" (
        set /p dummy="(g)ui (tu)i "
    )
    echo (q)uit (e)xit

    set "USER_RESPONSE=!USER_RESPONSE:~0,3!"
    for %%A in (!USER_RESPONSE!) do set "USER_RESPONSE=%%~A"
    set "USER_RESPONSE=!USER_RESPONSE:~0,3!"
    set "USER_RESPONSE=!USER_RESPONSE:~0!"

    REM Convert to lowercase (batch trick)
    for %%A in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
        set "USER_RESPONSE=!USER_RESPONSE:%%A=%%A!"
    )

    if /I "!USER_RESPONSE!"=="com" (
        call :compile
    ) else if /I "!USER_RESPONSE!"=="cov" (
        call :coverage
    ) else if /I "!USER_RESPONSE!"=="d" (
        call :document
    ) else if /I "!USER_RESPONSE!"=="l" (
        call :library
    ) else if /I "!USER_RESPONSE!"=="te" (
        call :tester
    ) else if /I "!USER_RESPONSE!"=="r" (
        call :run_raw
    ) else if /I "!USER_RESPONSE!"=="v" (
        call :version
    ) else if /I "!USER_RESPONSE!"=="h" (
        call :help_section
    ) else if /I "!USER_RESPONSE!"=="au" (
        call :author
    ) else if /I "!USER_RESPONSE!"=="ab" (
        call :about
    ) else if /I "!USER_RESPONSE!"=="g" (
        if "%PYTHON_FOUND%"=="%TRUE%" (
            call :gui
        ) else (
            echo Python is not present on your system, thus this command is disabled.
        )
    ) else if /I "!USER_RESPONSE!"=="tu" (
        if "%PYTHON_FOUND%"=="%TRUE%" (
            call :tui
        ) else (
            echo Python is not present on your system, thus this command is disabled.
        )
    ) else if /I "!USER_RESPONSE!"=="q" (
        echo Exiting the router menu...
        goto :EOF
    ) else if /I "!USER_RESPONSE!"=="e" (
        echo Exiting the router menu...
        goto :EOF
    ) else (
        echo Option '!USER_RESPONSE!' not found in provided options.
    )

echo.
goto mainloop

endlocal

