@echo off
setlocal

REM Set the total number of times to run the command
set total_runs=15


for /f "delims=" %%i in ('python -c "import sys; print(sys.prefix)"') do set PYTHON_HOME=%%i

REM PYTHON_HOME=python -c "import sys; print(sys.prefix)"
REM Set the delay in seconds (300 seconds = 5 minutes)
set delay_seconds=300

REM Loop for the specified number of times
for /l %%i in (1,1,%total_runs%) do (
    echo Running command, iteration %%i
    %PYTHON_HOME%/python.exe ./launch.py

    REM Wait for the specified delay before the next iteration
    timeout /nobreak /t %delay_seconds%
)

echo Batch file completed.
exit
