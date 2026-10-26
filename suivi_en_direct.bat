@echo off
title Suivi en direct - Bot McDo
color 0A
echo ==========================================================
echo       SUIVI EN DIRECT DU BOT MCDO (LIGNE PAR LIGNE)
echo ==========================================================

set IP_SERVEUR=%~1
if "%IP_SERVEUR%" == "" set IP_SERVEUR=10.1.10.3

echo Connexion au serveur (%IP_SERVEUR%)...
echo Appuyez sur Ctrl+C a tout moment pour quitter le suivi.
echo.

ssh -t root@%IP_SERVEUR% "tail -f /root/mcdo-bot/historique_envois.log"

pause
