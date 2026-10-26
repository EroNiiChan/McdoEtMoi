@echo off
title Bot McDonald's - Hello McDo Automatique
cd /d "%~dp0"

echo =======================================================
echo          LANCEMENT DU BOT MCDONALD'S (WINDOWS)
echo =======================================================
echo.

:: Verification de la presence de Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    where py >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERREUR] Python n'est pas installe ou pas dans le PATH Windows.
        echo Merci de telecharger Python sur https://www.python.org/
        echo ATTENTION : Coche bien la case "Add Python to PATH" a l'installation.
        echo.
        pause
        exit /b 1
    )
    set PY_CMD=py
) else (
    set PY_CMD=python
)

:: Verification et auto-installation de Selenium
%PY_CMD% -c "import selenium" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Premier lancement detecte : installation automatique de Selenium...
    %PY_CMD% -m pip install --upgrade selenium
    echo [INFO] Installation terminee avec succes !
    echo.
)

:: Creation du template .env si absent
if not exist .env (
    echo [INFO] Creation du fichier de configuration locale .env...
    (
        echo # Configuration locale du Bot McDo
        echo ID_RESTO=0000
        echo DISCORD_WEBHOOK_URL=
    ) > .env
    echo [INFO] Fichier .env cree. Tu peux y renseigner ton code restaurant.
    echo.
)

:: Lancement du bot McDonald's
echo [INFO] Demarrage de la session du Bot McDo...
%PY_CMD% script.py

echo.
echo =======================================================
echo                 SESSION TERMINEE
echo =======================================================
pause
