@echo off
echo ========================================
echo   Ask The Storytell AI - One-Click Setup
echo ========================================
echo.

:: Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python found!

:: Check Node.js
echo [2/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found!

:: Check FFmpeg
echo [3/6] Checking FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not found! Voice input won't work.
    echo Install using: winget install --id=Gyan.FFmpeg -e
    echo Then restart this script.
    echo.
    choice /C YN /M "Continue without FFmpeg?"
    if errorlevel 2 exit /b 1
) else (
    echo [OK] FFmpeg found!
)

:: Check .env file
echo [4/6] Checking API keys...
if not exist .env (
    echo [WARNING] .env file not found!
    echo Creating .env template...
    (
        echo GEMINI_API_KEY=your_gemini_key_here
        echo ELEVENLABS_API_KEY=your_elevenlabs_key_here
    ) > .env
    echo [OK] .env created! Please add your API keys to .env file
    echo.
    echo Get your FREE API keys:
    echo   - Gemini: https://makersuite.google.com/app/apikey
    echo   - ElevenLabs: https://elevenlabs.io/
    echo.
    pause
    notepad .env
    echo.
    echo Please save .env and close Notepad to continue...
    pause
)

:: Install Python dependencies
echo [5/6] Installing Python dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies!
    pause
    exit /b 1
)
echo [OK] Python dependencies installed!

:: Install Node dependencies
echo [6/6] Installing Node dependencies...
cd frontend
call npm install --silent
if errorlevel 1 (
    echo [ERROR] Failed to install Node dependencies!
    pause
    exit /b 1
)
cd ..
echo [OK] Node dependencies installed!

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure your API keys are in .env file
echo 2. Add your PDF books to data/pdfs/ folder
echo 3. Run START.bat to launch the app
echo.
pause
