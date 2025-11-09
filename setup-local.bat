@echo off

set PYTHON_EXE="C:\Users\Loq Gaming\AppData\Local\Programs\Python\Python312\python.exe"

echo ========================================
echo Smart Expense NLP - Local Setup
echo ========================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create venv
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

echo [4/4] Installing dependencies...
pip install -r requirements-dev.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Activate venv: venv\Scripts\activate
echo 2. Run API: uvicorn src.api.main:app --reload
echo 3. Jupyter: jupyter notebook
echo.
echo For Docker: docker-compose up
echo ========================================

pause