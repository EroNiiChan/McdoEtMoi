#!/bin/bash

# Se place automatiquement dans le dossier où se trouve ce script
cd "$(dirname "$0")" || exit

echo "=========================================="
echo "   LANCEMENT DE L'AUTOMATISATION SSH"
echo "=========================================="

# Lance le script Python qui est juste à côté
python3 script.py

echo "=========================================="
echo "   SCRIPT TERMINE OU ERREUR DETECTEE"
echo "=========================================="
read -p "Appuyez sur Entrée pour fermer..."