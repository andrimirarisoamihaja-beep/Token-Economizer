@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Installation - Verificateur de Code

echo ============================================
echo   INSTALLATION DU VERIFICATEUR DE CODE
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo Telechargez-le sur https://www.python.org/downloads/
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js n'est pas installe ou pas dans le PATH.
    echo Telechargez-le sur https://nodejs.org/
    pause
    exit /b 1
)

echo [1/3] Creation de l'environnement virtuel...
if not exist ".venv" (
    python -m venv .venv
)

echo [2/3] Activation et installation des packages Python...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [3/3] Installation des outils JS (ESLint)...
if exist "package.json" (
    call npm install
) else (
    call npm install eslint --no-save
)

echo.
echo ============================================
echo   INSTALLATION TERMINEE AVEC SUCCES
echo ============================================
echo Vous pouvez maintenant double-cliquer sur lancer.bat
echo.
pause