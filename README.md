# Bot Hello McDo Automatique (Medallia)

Système automatisé de complétion des questionnaires de satisfaction client McDonald's France (**Hello McDo / Medallia**).

Conçu pour simuler un comportement 100% humain, crédible et indétectable par les algorithmes de détection d'anomalies de Medallia.

---

## 🚀 Caractéristiques Principales

- **Cadence & Durée Naturelles** :
  - Chaque questionnaire dure **entre 68 et 96 secondes** (garantie stricte > 1 minute pour éviter le flag anomalie / speed-run).
  - Pauses de lecture aléatoires réparties sur chaque écran (accueil, âge, ticket, notation par critères, commentaire).
  - Frappe réaliste des caractères dans les champs texte.
- **Portabilité Totale (Windows & Linux)** :
  - **Windows** : Lancement 1-clic via `lancer_mcdo.bat` (auto-installation de Selenium, Selenium Manager gère ChromeDriver automatiquement).
  - **Linux / Debian** : Exécution headless optimisée LXC/Docker, service `systemd` et timer quotidien à 16h30.
- **Rotation d'IP Automatique (Proxies / Tor)** :
  - Relais local Tor intégré sur Debian avec changement d'adresse IP (`SIGNAL NEWNYM`) avant chaque client.
  - Nœuds de sortie européens haute vitesse (`{fr},{be},{ch},{nl},{de}`).
  - Support de proxies personnalisés via `PROXIES = [...]`.
- **Auto-Guérison & Résilience** :
  - Double tentative automatique (1 retry immédiat avec nouvelle IP) en cas de micro-coupure réseau.
  - Nettoyage strict des processus fantômes en fin de chaque passage (`chromedriver`, `chrome`).
  - Purge automatique des captures d'écran vieilles de plus de 7 jours.
- **Alertes Discord & Notifications Admin** :
  - Embeds de démarrage, de fin de session et de progression en direct.
  - Mention d'alerte `@here` (ou ID spécifique) en cas d'incident persistant.

---

## 💻 Utilisation sur Windows

1. Assurez-vous d'avoir [Python](https://www.python.org/) et Google Chrome installés.
2. Double-cliquez sur `lancer_mcdo.bat`.
3. Le script installe automatiquement les dépendances manquantes et lance la session.

---

## 🐧 Utilisation sur Debian / Linux

```bash
# Installation des paquets requis
apt update && apt install -y chromium chromium-driver tor

# Création du venv
python3 -m venv venv
./venv/bin/pip install selenium

# Lancement manuel (ou via les units systemd fournies)
./venv/bin/python script.py
```

Pour la planification automatique quotidienne à 16h30 :
```bash
cp mcdo-bot.service /etc/systemd/system/
cp mcdo-bot.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now mcdo-bot.timer
```

---

## ⚙️ Configuration (`script.py`)

- `ID_RESTO` : Code restaurant à 4 chiffres (ex: `"XXXX"`).
- `DISCORD_WEBHOOK_URL` : URL de votre Webhook Discord pour le monitoring.
- `DISCORD_ADMIN_PING` : Mention en cas d'erreur (ex: `"@here"`, `"@everyone"`).
- `PROXIES` : Liste optionnelle de proxies externes.
