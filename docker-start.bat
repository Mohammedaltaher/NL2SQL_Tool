@echo off
REM Create .env file from example if it doesn't exist
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
)

REM Check if data directory exists
if not exist data (
    echo Creating data directory...
    mkdir data
)

REM Set Docker project name
set COMPOSE_PROJECT_NAME=nl2sql_tool

REM Start Docker Compose
echo Starting NL2SQL Tool with Docker Compose...
docker-compose up -d

REM Wait for services to be ready
echo Waiting for services to start...
timeout /t 5 /nobreak > nul

REM Display connection info
echo.
echo 🚀 NL2SQL Tool is starting up!
echo 🌐 Access the application at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo 🐳 Docker Services:
echo   - NL2SQL API: Port 8000
echo   - Ollama: Port 11434
echo   - PostgreSQL: Port 5432
echo.
echo To shut down: docker-compose down
echo.

pause
