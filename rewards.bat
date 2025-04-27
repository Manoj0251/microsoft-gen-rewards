@echo off
setlocal EnableDelayedExpansion

REM Set the total number of times to run the command
set total_runs=15

REM Get the Python home directory
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_HOME=%%i

REM Set the delay in seconds (300 seconds = 5 minutes)
set delay_seconds=300

REM Loop for the specified number of times
for /l %%i in (1,1,%total_runs%) do (
    echo Running command, iteration %%i
    %PYTHON_HOME% %~dp0/launch.py
    set ret_val=!ERRORLEVEL!
    echo Python script returned !ret_val!

    REM Handle return value if needed
    if !ret_val! equ 0 (
        echo Success!
        set /a total_runs=15
    )

    REM Wait for the specified delay before the next iteration
    echo Waiting for %delay_seconds% seconds....
    timeout /nobreak /t %delay_seconds%
)

echo Batch file completed.
exit /b !ret_val!
