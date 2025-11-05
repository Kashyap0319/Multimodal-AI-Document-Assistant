@echo off
cls
echo ========================================
echo   Ask The Storytell AI - Starting...
echo ========================================
echo.

cd /d "%~dp0"

:: Check if setup was run
if not exist "frontend\node_modules" (
    echo [ERROR] Dependencies not installed!
    echo Run SETUP.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

:: Check .env
if not exist .env (
    echo [ERROR] .env file not found!
    echo Run SETUP.bat first to configure API keys.
    echo.
    pause
    exit /b 1
)

:: Check PDFs
if not exist "data\pdfs\*.pdf" (
    echo [WARNING] No PDF files found in data\pdfs\
    echo Please add your story PDFs to data\pdfs\ folder
    echo.
    pause
)

echo [1/2] Starting Backend Server (Port 9000)...
start "Backend - Ask The Storytell AI" cmd /k "python backend.py"

echo [2/2] Waiting 8 seconds for backend...
timeout /t 8 /nobreak >nul

echo Starting Frontend Server (Port 5173)...
cd frontend
start "Frontend - Ask The Storytell AI" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:9000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:9000/docs
echo.
echo Opening app in browser...
echo.

timeout /t 5 /nobreak >nul
start http://localhost:5173

echo Press any key to STOP all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Backend - Ask The Storytell AI*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend - Ask The Storytell AI*" /T /F >nul 2>&1
echo All servers stopped!
timeout /t 2 >nul
