@echo off
echo Setting up Live Interview Assistant Backend with Ollama
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ollama is not installed!
    echo Please install Ollama from: https://ollama.ai
    pause
    exit /b 1
)

echo Ollama is installed
echo.

REM Pull the model
echo Pulling SmolLM2 1.7B model...
ollama pull smollm2:1.7b

echo.
echo Setup complete! You can now run the backend with:
echo   cd backend
echo   python -m venv venv
echo   venv\Scripts\activate
echo   pip install -r requirements.txt
echo   python app.py
echo.
pause
