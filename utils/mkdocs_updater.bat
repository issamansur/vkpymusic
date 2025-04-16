@echo off

REM !!! Execute from the root of the repository

REM Install mkdocs and required plugins
pip install mkdocs
pip install mkdocs-material
pip install mkdocs-autorefs
pip install mkdocstrings[python]

REM Start mkdocs serve in the background
start /B mkdocs serve
set MKDOCS_PID=%!

REM Wait for mkdocs serve to start
timeout /t 10 >nul

REM Ask user to continue
set /p answer="Documentation is running locally at http://127.0.0.1:8000. Continue build and deploy? (Y/n): "

REM Stop mkdocs serve
taskkill /F /IM python.exe >nul 2>&1

REM Check user input
if /i "%answer%"=="Y" (
    echo Building and deploying documentation...
    mkdocs build && mkdocs gh-deploy
) else if /i "%answer%"=="Yes" (
    echo Building and deploying documentation...
    mkdocs build && mkdocs gh-deploy
) else if "%answer%"=="" (
    echo Building and deploying documentation...
    mkdocs build && mkdocs gh-deploy
) else (
    echo Exiting...
)