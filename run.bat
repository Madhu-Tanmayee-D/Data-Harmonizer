@echo off
REM Dataset Harmonization Platform - Windows Startup Script

echo.
echo ============================================
echo Dataset Harmonization Platform - Startup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo [3/4] Initializing database...
python database.py

echo.
echo [4/4] Starting application...
echo.
echo ============================================
echo Opening Streamlit app at http://localhost:8501
echo ============================================
echo.
echo Press CTRL+C to stop the application
echo.

streamlit run app.py --server.port=8501

pause
