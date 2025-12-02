@echo off
REM This batch file should be placed in the same directory as the Python script.

REM Configuration: Change the value below to match the Python script file name.
set "PYTHON_SCRIPT=j2b.py"

echo.
echo ============================
echo Journey to Bethlehem Program
echo ============================
echo.
echo Checking for Python script...

REM Check if the Python script file exists
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: The file "%PYTHON_SCRIPT%" was not found in this directory.
    echo Please ensure the script name above is correct.
    goto :end
)

echo Found script: %PYTHON_SCRIPT%
echo Running execution (assuming 'python' is in your system PATH)...
echo -------------------------------------------

REM Execute the Python script
python "%PYTHON_SCRIPT%"

REM Check the error level of the previous command to see if it succeeded
if errorlevel 1 (
    echo.
    echo [EXECUTION ERROR]
    echo The script finished with an error (Code: %errorlevel%).
    echo A common cause is 'python' not being in the system PATH.
) else (
    echo.
    echo [EXECUTION SUCCESS]
    echo The script finished without errors.
)

:end
echo -------------------------------------------
echo Press any key to close this window...
pause > nul