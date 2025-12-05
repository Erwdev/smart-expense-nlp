<!-- filepath: e:\SEMESTER 5\TPSC\Final-Project\smart-expense-nlp\SETUP_QUICKSTART.bat -->
@echo off
cls
echo ================================================
echo  SMART EXPENSE NER API - QUICKSTART SETUP
echo ================================================
echo.

REM Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install Python 3.9-3.11 first.
    pause
    exit /b 1
)
python --version
echo.

REM Navigate to project directory
echo [2/6] Navigating to project...
cd /d "e:\SEMESTER 5\TPSC\Final-Project\smart-expense-nlp"
echo Current directory: %CD%
echo.

REM Create virtual environment
echo [3/6] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo [4/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated.
echo.

REM Upgrade pip
echo [5/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] Pip upgraded.
echo.

REM Install requirements
echo [6/6] Installing dependencies...
echo This may take a few minutes...
pip install fastapi uvicorn[standard] transformers torch pydantic python-multipart psutil python-dotenv --quiet
echo [OK] All dependencies installed!
echo.

echo ================================================
echo  SETUP COMPLETE!
echo ================================================
echo.
echo Next steps:
echo   1. Run: RUN_API.bat
echo   2. Open: http://localhost:8000/docs
echo.
pause