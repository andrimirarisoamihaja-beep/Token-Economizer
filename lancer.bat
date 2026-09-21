@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Verificateur de Code - Lancement

echo ============================================
echo   VERIFICATEUR DE CODE (Python, JS, TS, Java)
echo ============================================
echo.

REM --- 1. Verifier Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python introuvable. Lancez d'abord installer.bat
    pause
    exit /b 1
)

REM --- 2. Verifier / activer le venv ---
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Environnement virtuel manquant. Lancement de l'installation...
    call installer.bat
    if errorlevel 1 exit /b 1
)

call .venv\Scripts\activate.bat

REM --- 3. Verifier que Streamlit est bien installe ---
python -c "import streamlit, dotenv, groq" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Dependances manquantes. Installation en cours...
    python -m pip install -r requirements.txt
)

REM --- 4. Verifications optionnelles ---
node --version >nul 2>&1
if errorlevel 1 (
    echo [ATTENTION] Node.js non detecte.
)

javac -version >nul 2>&1
if errorlevel 1 (
    echo [ATTENTION] JDK Java non detecte.
)

REM --- 5. Verification du fichier .env ---
if not exist ".env" goto DEMANDER_CLE

findstr /B /C:"GROQ_API_KEY=" ".env" >nul 2>&1
if errorlevel 1 goto DEMANDER_CLE

goto LANCER_APP

:DEMANDER_CLE
echo.
echo ----------------------------------------------------
echo [CONFIGURATION] Aucune cle API Groq trouvee.
echo ----------------------------------------------------
echo 1. Allez sur https://console.groq.com/keys
echo 2. Creez un compte gratuit et copiez votre cle API
echo.
set /p GROQ_KEY=Collez votre cle API Groq ici : 

if "%GROQ_KEY%"=="" (
    echo.
    echo [ATTENTION] Aucune cle saisie. L'analyse fonctionnera sans IA.
    echo.
) else (
    echo GROQ_API_KEY=%GROQ_KEY%> ".env"
    echo.
    echo [OK] Cle enregistree dans le fichier .env
    echo.
)

:LANCER_APP
echo [INFO] Demarrage de l'interface web...
echo [INFO] Le navigateur va s'ouvrir automatiquement.
echo [INFO] Pour arreter l'application : fermez cette fenetre.
echo.

set PYTHONIOENCODING=utf-8
python -m streamlit run app.py

echo.
echo Application terminee.
pause