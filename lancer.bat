@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Verificateur de Code - Lancement

echo ============================================
echo   VERIFICATEUR DE CODE (Streamlit + IA)
echo ============================================
echo.

REM --- Verifier Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python introuvable. Lancez d'abord installer.bat
    pause
    exit /b 1
)

REM --- Verifier / creer le venv ---
if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Environnement virtuel manquant. Lancement de l'installation...
    call installer.bat
    if errorlevel 1 exit /b 1
)

call .venv\Scripts\activate.bat

REM --- Verifier les packages essentiels ---
python -c "import streamlit, dotenv, groq" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Dependances manquantes. Installation...
    python -m pip install -r requirements.txt
)

REM --- Gestion de la cle API Groq ---
set "NEED_KEY=0"

if not exist ".env" (
    set "NEED_KEY=1"
) else (
    findstr /B /C:"GROQ_API_KEY=" ".env" >nul 2>&1
    if errorlevel 1 (
        set "NEED_KEY=1"
    ) else (
        REM Verifie que la cle n'est pas vide
        for /f "tokens=1,* delims==" %%a in ('findstr /B /C:"GROQ_API_KEY=" ".env"') do (
            if "%%b"=="" set "NEED_KEY=1"
            if "%%b"=="votre_vraie_cle_api_groq_ici" set "NEED_KEY=1"
        )
    )
)

if "%NEED_KEY%"=="1" (
    echo.
    echo [CONFIGURATION] Aucune cle API Groq valide trouvee.
    echo.
    echo 1. Allez sur https://console.groq.com/keys
    echo 2. Creez un compte / connectez-vous
    echo 3. Generez une cle API
    echo.
    set /p GROQ_KEY=Collez votre cle API Groq ici : 

    if "%GROQ_KEY%"=="" (
        echo [ERREUR] Aucune cle saisie. Abandon.
        pause
        exit /b 1
    )

    echo GROQ_API_KEY=%GROQ_KEY%> ".env"
    echo.
    echo [OK] Cle enregistree dans le fichier .env
    echo.
)

REM --- Lancer Streamlit ---
echo [INFO] Demarrage de l'interface web...
echo [INFO] Votre navigateur va s'ouvrir automatiquement.
echo [INFO] Pour arreter : fermez cette fenetre ou faites Ctrl+C
echo.

set PYTHONIOENCODING=utf-8
python -m streamlit run app.py

echo.
echo Application terminee.
pause