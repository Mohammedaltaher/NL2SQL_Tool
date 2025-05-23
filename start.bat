@echo off
echo 🚀 Starting NL2SQL Tool...

REM Check if virtual environment exists
if not exist "venv\" (
    echo ❌ Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 📋 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Ollama is running
echo 📋 Checking Ollama service...
ollama list >nul 2>&1
if errorlevel 1 (
    echo 📋 Starting Ollama service...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)

REM Start the application
echo 📋 Starting NL2SQL Tool API...
echo 🌐 The application will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
