import os
import sys
import time
import json
import random
import shutil
import logging
import platform
import subprocess
import urllib.request
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from Com import generer_commentaire

# --- 1. CONFIGURATION GLOBALE & DOSSIERS ---
def charger_config_locale():
    """Charge la configuration depuis un fichier .env local (ignoré par Git pour la confidentialité)"""
    config = {}
    chemin_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.isfile(chemin_env):
        try:
            with open(chemin_env, "r", encoding="utf-8") as f:
                for ligne in f:
                    ligne = ligne.strip()
                    if ligne and not ligne.startswith("#") and "=" in ligne:
                        cle, val = ligne.split("=", 1)
                        config[cle.strip()] = val.strip().strip('"').strip("'")
        except Exception:
            pass
    return config

_cfg = charger_config_locale()

# Code restaurant McDonald's (4 chiffres) - Configurable via .env ou variable d'environnement ID_RESTO
ID_RESTO = os.environ.get("ID_RESTO") or _cfg.get("ID_RESTO") or "0000"

# Optionnel : URL de Webhook Discord (configurable via .env ou variable d'environnement)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL") or _cfg.get("DISCORD_WEBHOOK_URL") or ""

# Mention Admin en cas d'erreur (@here, @everyone, ou ID utilisateur ex: "<@123456789>")
DISCORD_ADMIN_PING = os.environ.get("DISCORD_ADMIN_PING") or _cfg.get("DISCORD_ADMIN_PING") or "@here"

# Optionnel : Liste de proxies (ex: ["http://ip:port", "socks5://ip:port"]). Vide = IP directe ou Tor local
PROXIES = []

DOSSIER_SCREENSHOTS = "erreurs_screenshots"
os.makedirs(DOSSIER_SCREENSHOTS, exist_ok=True)

def purger_anciens_screenshots(dossier, jours_max=7):
    """Supprime automatiquement les captures d'écran vieilles de plus de X jours pour préserver le disque"""
    maintenant = time.time()
    try:
        for f in os.listdir(dossier):
            chemin = os.path.join(dossier, f)
            if os.path.isfile(chemin) and f.endswith(".png"):
                if maintenant - os.path.getmtime(chemin) > jours_max * 86400:
                    os.remove(chemin)
    except Exception:
        pass

def calculer_nombre_passages():
    """Adapte le volume au jour de la semaine pour paraître 100% naturel aux statistiques McDo"""
    jour = datetime.now().weekday()
    if jour in [4, 5, 6]:   # Vendredi, Samedi, Dimanche (Gros rush)
        return random.randint(110, 130)
    elif jour in [2, 3]:   # Mercredi, Jeudi (Moyen)
        return random.randint(85, 105)
    else:                  # Lundi, Mardi (Calme)
        return random.randint(70, 90)

def notifier_discord(titre, description, couleur=0x2ECC71, ping_admin=False):
    """Envoie une notification embed sur Discord sans aucune dépendance externe avec ping optionnel"""
    if not DISCORD_WEBHOOK_URL or not DISCORD_WEBHOOK_URL.startswith("https://discord.com/api/webhooks/"):
        return
    try:
        payload = {
            "embeds": [{
                "title": titre,
                "description": description,
                "color": couleur,
                "footer": {"text": "Bot McDo • Hello McDo Automation"},
                "timestamp": datetime.now().astimezone().isoformat()
            }]
        }
        if ping_admin and DISCORD_ADMIN_PING:
            payload["content"] = f"{DISCORD_ADMIN_PING} ⚠️ **Incident détecté sur le Bot McDo !**"

        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "McDoBot/2.0"}
        )
        urllib.request.urlopen(req, timeout=10)  # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected
    except Exception:
        pass

def renouveler_ip():
    """Demande un nouveau circuit Tor pour changer immédiatement d'adresse IP publique"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(("127.0.0.1", 9051))
            s.sendall(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n')
            res = s.recv(512)
            if b"250" in res:
                logging.info("   -> Rotation IP effectuée avec succès (nouveau circuit).")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    handlers=[
        logging.FileHandler("historique_envois.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# --- 2. PROFILS D'APPAREILS & VRAIS SÉLECTEURS MEDALLIA ---
PROFILS_APPAREILS = [
    {
        "nom": "iPhone (Safari)",
        "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "taille": "393,852",
        "mobile": True
    },
    {
        "nom": "iPhone Pro Max (Safari)",
        "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "taille": "430,932",
        "mobile": True
    },
    {
        "nom": "Samsung Galaxy (Chrome Android)",
        "ua": "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36",
        "taille": "360,800",
        "mobile": True
    },
    {
        "nom": "Google Pixel (Chrome Android)",
        "ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
        "taille": "412,915",
        "mobile": True
    },
    {
        "nom": "PC Windows (Chrome)",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "taille": "1920,1080",
        "mobile": False
    },
    {
        "nom": "MacBook (Safari)",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        "taille": "1440,900",
        "mobile": False
    }
]

# Vrais sélecteurs extraits de ta vérification (sans les < 15 ans qui bloquent l'enquête)
TRANCHES_AGE = [
    '[data-test-name="option-entre-15-et-24-ans"]',
    '[data-test-name="option-entre-25-et-34-ans"]',
    '[data-test-name="option-entre-35-et-49-ans"]',
    '[data-test-name="option-50-ans-et-plus"]'
]
POIDS_AGE = [30, 35, 25, 10] # Répartition réaliste de la clientèle

MODES_COMMANDE = [
    '[data-test-name="option-a-une-borne-de-commande-en-restaurant"]',
    '[data-test-name="option-au-drive"]',
    '[data-test-name="option-au-comptoir"]'
]
# Répartition réaliste : 50% Borne, 40% Drive, 10% Comptoir (ajuste selon ton resto !)
POIDS_COMMANDE = [50, 40, 10]

LIEUX_CONSO = [
    '[data-test-name="option-consommé-sur-place"]',
    '[data-test-name="option-pris-à-emporter"]'
]
POIDS_LIEU = [55, 45] # Quand c'est en resto : 55% sur place, 45% à emporter

# On garde "pris-à-emporter" pour éviter la question supplémentaire du service à table
# --- 3. FONCTIONS DE SIMULATION HUMAINE & ROBUSTESSE ---

def pause_humaine(min_sec=1.0, max_sec=2.8):
    """Pause aléatoire avec décimales pour casser le rythme robotique"""
    time.sleep(random.uniform(min_sec, max_sec))

def cliquer_element(driver, by_type, selecteur, timeout=15):
    """Attend que l'élément soit présent, le centre à l'écran, marque une pause et clique (naturel ou JS) avec gestion de rechargement DOM (stale)"""
    fin = time.time() + timeout
    while time.time() < fin:
        try:
            element = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((by_type, selecteur))
            )
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            except Exception:
                pass
            pause_humaine(0.4, 1.0)
            try:
                element.click()
            except TimeoutException:
                return # Si le clic a déclenché une navigation qui met du temps à répondre
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", element)
                except TimeoutException:
                    return
            return
        except Exception as e:
            if "stale" in str(e).lower():
                time.sleep(0.4)
                continue
            time.sleep(0.4)
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by_type, selecteur)))
    try:
        driver.execute_script("arguments[0].click();", element)
    except TimeoutException:
        pass

def remplir_champ(driver, by_type, selecteur, texte, timeout=15):
    """Attend que le champ soit prêt et tape le texte caractère par caractère avec gestion du rechargement DOM"""
    fin = time.time() + timeout
    while time.time() < fin:
        try:
            element = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((by_type, selecteur))
            )
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            except Exception:
                pass
            pause_humaine(0.3, 0.7)
            try:
                element.clear()
            except Exception:
                pass
            for caractere in texte:
                element.send_keys(caractere)
                time.sleep(random.uniform(0.03, 0.12))
            return
        except Exception as e:
            if "stale" in str(e).lower():
                time.sleep(0.4)
                continue
            time.sleep(0.4)
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by_type, selecteur)))
    element.send_keys(texte)

def generer_options_furtives():
    """Crée une configuration Chrome unique, réaliste et optimisée faible RAM (512 Mo)"""
    profil = random.choices(PROFILS_APPAREILS, weights=[25, 20, 25, 15, 10, 5], k=1)[0]
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"--user-agent={profil['ua']}")
    options.add_argument(f"--window-size={profil['taille']}")
    options.add_argument("--lang=fr-FR")
    
    # Stabilité Linux / LXC / Docker
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Optimisation mémoire LXC (512 Mo RAM max)
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-component-update")
    options.add_argument("--renderer-process-limit=1")
    options.add_argument("--js-flags=--max-old-space-size=128")
    
    # Proxy tournant optionnel (vide par défaut = connexion directe ultra-rapide)
    if PROXIES:
        proxy_choisi = random.choice(PROXIES)
        options.add_argument(f"--proxy-server={proxy_choisi}")

    # Camouflage anti-bot Selenium
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    return options, profil

def generer_horaire_ticket():
    """Génère une date et une heure réalistes entre 12h00 et 22h00"""
    maintenant = datetime.now()
    debut_service = maintenant.replace(hour=12, minute=0, second=0, microsecond=0)
    fin_service = maintenant.replace(hour=22, minute=0, second=0, microsecond=0)

    # CAS 1 : Tôt le matin ou avant 12h30 -> Ticket d'HIER (12h - 22h)
    if maintenant < debut_service + timedelta(minutes=30):
        jour_ticket = maintenant - timedelta(days=1)
        heure_choisie = random.choices(
            [12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            weights=[20, 20, 8, 5, 5, 5, 10, 15, 15, 10],
            k=1
        )[0]
        minute_choisie = random.randint(0, 59)
        moment_achat = jour_ticket.replace(hour=heure_choisie, minute=minute_choisie)

    # CAS 2 : Après 22h20 -> Ticket d'AUJOURD'HUI (12h - 22h)
    elif maintenant >= fin_service + timedelta(minutes=20):
        heure_choisie = random.choices(
            [12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            weights=[20, 20, 8, 5, 5, 5, 10, 15, 15, 10],
            k=1
        )[0]
        minute_choisie = random.randint(0, 59)
        moment_achat = maintenant.replace(hour=heure_choisie, minute=minute_choisie)

    # CAS 3 : En pleine journée (12h30 - 22h20) -> Ticket d'aujourd'hui (au moins 20 min avant)
    else:
        limite_max = maintenant - timedelta(minutes=20)
        secondes_ecoulees = int((limite_max - debut_service).total_seconds())
        secondes_aleatoires = random.randint(0, secondes_ecoulees)
        moment_achat = debut_service + timedelta(seconds=secondes_aleatoires)

    return moment_achat.strftime("%d/%m/%Y"), moment_achat.strftime("%H"), moment_achat.strftime("%M")

def nettoyer_processus_fantomes(driver):
    """Ferme proprement Selenium et purge les processus Chrome/Chromium bloqués en RAM"""
    if driver is not None:
        try:
            driver.quit()
        except Exception:
            pass

    systeme = platform.system()
    try:
        if systeme == "Linux":
            subprocess.run(["pkill", "-9", "-f", "chromedriver"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-9", "-f", "chrome.*--headless"], stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-9", "-f", "chromium.*--headless"], stderr=subprocess.DEVNULL)
        elif systeme == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe", "/T"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


# Détection automatique du pilote ChromeDriver (Linux / Windows / Mac)
chemin_driver = shutil.which("chromedriver")
if not chemin_driver and platform.system() == "Windows":
    candidats = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver.exe"),
        os.path.join(os.getcwd(), "chromedriver.exe")
    ]
    for c in candidats:
        if os.path.isfile(c):
            chemin_driver = c
            break

# Purge automatique des vieux screenshots (> 7 jours)
purger_anciens_screenshots(DOSSIER_SCREENSHOTS, jours_max=7)

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    NOMBRE_DE_REPETITIONS = int(sys.argv[1])
else:
    NOMBRE_DE_REPETITIONS = calculer_nombre_passages()
nb_succes = 0
nb_erreurs = 0

logging.info(f"=== DÉMARRAGE DE LA SESSION ({NOMBRE_DE_REPETITIONS} formulaires prévus) ===")
notifier_discord(
    "🚀 Session McDo Démarrée",
    f"**Restaurant** : `{ID_RESTO}`\n**Objectif du jour** : `{NOMBRE_DE_REPETITIONS}` formulaires prévus\n**Heure** : {datetime.now().strftime('%H:%M')}",
    couleur=0x3498DB
)

# --- 5. BOUCLE PRINCIPALE ---
for i in range(NOMBRE_DE_REPETITIONS):
    for tentative in range(2):
        driver = None
        renouveler_ip()
        chrome_options, profil_actuel = generer_options_furtives()
        
        if tentative == 0:
            logging.info(f"=== LANCEMENT N°{i+1}/{NOMBRE_DE_REPETITIONS} | {profil_actuel['nom']} ({profil_actuel['taille']}) ===")
            notifier_discord(
                f"▶️ Début Passage #{i+1:03d}/{NOMBRE_DE_REPETITIONS}",
                f"**Appareil** : {profil_actuel['nom']}\n**Restaurant** : `{ID_RESTO}`",
                couleur=0x3498DB
            )
        else:
            logging.warning(f"   -> Réessai automatique passage #{i+1:03d} (tentative 2/2) avec nouvelle IP...")
        try:
            if chemin_driver:
                service = Service(chemin_driver)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Selenium Manager natif (gère automatiquement Chrome sous Windows et Mac sans configuration)
                driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(25)
            t_debut_passage = time.time()
            duree_cible_sondage = random.uniform(68.0, 96.0) # Toujours > 1 min pour éviter le flag anomalie
            
            plateforme_js = "iPhone" if "iPhone" in profil_actuel["nom"] else ("Linux armv8l" if profil_actuel["mobile"] else "Win32")
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": f"""
                    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
                    Object.defineProperty(navigator, 'platform', {{get: () => '{plateforme_js}'}});
                """
            })
    
            # 1. Accès au site
            logging.info("1. Connexion au site McDonald's...")
            for tentative_page in range(2):
                try:
                    driver.get("https://survey2.medallia.eu/?hellomcdo")
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "buttonBegin")))
                    break
                except Exception:
                    if tentative_page == 0:
                        logging.warning("   -> Page lente à répondre, nouvel essai immédiat...")
                        time.sleep(2)
                    else:
                        raise
            pause_humaine(3.0, 5.0) # Lecture humaine page accueil
    
            # 2. Bouton Commencer
            logging.info("2. Clic sur 'Commencer'...")
            cliquer_element(driver, By.ID, "buttonBegin")
            pause_humaine(2.0, 3.5)
    
            # 3. Choix de l'âge aléatoire pondéré
            age_choisi = random.choices(TRANCHES_AGE, weights=POIDS_AGE, k=1)[0]
            logging.info(f"3. Sélection de l'âge : {age_choisi}")
            cliquer_element(driver, By.CSS_SELECTOR, age_choisi)
            pause_humaine(1.5, 2.5)
            cliquer_element(driver, By.ID, "buttonNext")
            pause_humaine(2.0, 3.5)
    
            # 4. Génération de l'horaire réaliste (12h - 22h)
            date_ticket, heure_ticket, minute_ticket = generer_horaire_ticket()
    
            # 5. Remplissage Ticket
            logging.info(f"4. Remplissage infos ticket : {date_ticket} à {heure_ticket}:{minute_ticket}")
            remplir_champ(driver, By.ID, "cal_q_mc_q_date_", date_ticket)
            remplir_champ(driver, By.ID, "spl_rng_q_mc_q_hour", heure_ticket)
            remplir_champ(driver, By.ID, "spl_rng_q_mc_q_minute", minute_ticket)
            remplir_champ(driver, By.ID, "spl_rng_q_mc_q_idrestaurant", ID_RESTO)
            cliquer_element(driver, By.ID, "buttonNext")
    
           # 6. Questions de parcours (Borne, Drive ou Comptoir + gestion dynamique)
            mode_choisi = random.choices(MODES_COMMANDE, weights=POIDS_COMMANDE, k=1)[0]
            nom_mode_propre = mode_choisi.split('"')[1].replace("option-", "")
            
            cliquer_element(driver, By.CSS_SELECTOR, mode_choisi)
            cliquer_element(driver, By.ID, "buttonNext")
            pause_humaine(1.5, 2.5)
    
            parcours_detail = nom_mode_propre
    
            # Boucle intelligente : avance jusqu'à trouver la page de Satisfaction Globale
            for _ in range(4): # Maximum 4 sous-questions possibles avant la note globale
                # Si on voit déjà le bouton de la note globale, on sort de la boucle !
                if len(driver.find_elements(By.ID, "onf_q_feedback_m_based_upon_this_visit_to_this_6_1")) > 0:
                    break
    
                # Cas A : La page demande "Sur place ou À emporter"
                if len(driver.find_elements(By.CSS_SELECTOR, '[data-test-name="option-pris-à-emporter"]')) > 0:
                    lieu_choisi = random.choices(LIEUX_CONSO, weights=POIDS_LIEU, k=1)[0]
                    nom_lieu_propre = lieu_choisi.split('"')[1].replace("option-", "")
                    parcours_detail += f" -> {nom_lieu_propre}"
                    logging.info(f"5. Parcours : {parcours_detail}")
                    
                    cliquer_element(driver, By.CSS_SELECTOR, lieu_choisi)
                    cliquer_element(driver, By.ID, "buttonNext")
                    pause_humaine(1.5, 2.5)
    
                # Cas B : Question intermédiaire (ex: Service à table sur place, ou question spécifique Drive)
                else:
                    logging.info("   -> Sous-question intermédiaire détectée, réponse automatique...")
                    radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    if radios:
                        choix = random.choice(radios)
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", choix)
                            driver.execute_script("arguments[0].click();", choix)
                        except Exception:
                            pass
                    else:
                        options_dispo = driver.find_elements(By.CSS_SELECTOR, "[data-test-name^='option-']")
                        if options_dispo:
                            choix = random.choice(options_dispo)
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", choix)
                                driver.execute_script("arguments[0].click();", choix)
                            except Exception:
                                pass
                    pause_humaine(0.8, 1.5)
                    cliquer_element(driver, By.ID, "buttonNext")
                    pause_humaine(1.5, 2.5)
    
            # 7. Satisfaction globale et commentaire (65% de chance de laisser un texte)
            logging.info("6. Notation globale et commentaire...")
            cliquer_element(driver, By.ID, "onf_q_feedback_m_based_upon_this_visit_to_this_6_1")
    
            if random.random() < 0.65:
                commentaire_choisi = generer_commentaire()
                remplir_champ(driver, By.CSS_SELECTOR, "textarea", commentaire_choisi)
                logging.info(f"   -> Commentaire tapé : '{commentaire_choisi}'")
            else:
                commentaire_choisi = "[Aucun commentaire]"
                logging.info("   -> Aucun commentaire laissé (comportement naturel).")
    
            cliquer_element(driver, By.ID, "buttonNext")
    
            # 8. Notes détaillées (S'adapte automatiquement aux critères Salle, Emporter ou Drive)
            logging.info("7. Remplissage des notes détaillées...")
            pause_humaine(2.5, 4.5)
            
            # Trouve tous les boutons radio de note maximale (ceux dont l'ID commence par 'onf_q_' et finit par '_1')
            radios_max = driver.find_elements(By.CSS_SELECTOR, "input[id^='onf_q_'][id$='_1']")
            random.shuffle(radios_max)
            for r in radios_max:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", r)
                    pause_humaine(1.2, 2.4) # Lecture réaliste de chaque critère
                    driver.execute_script("arguments[0].click();", r)
                except Exception:
                    pass
    
            pause_humaine(2.0, 3.5)
            cliquer_element(driver, By.ID, "buttonNext")
    
            # 9. Finalisation
            logging.info("8. Finalisation de l'enquête...")
            pause_humaine(2.0, 3.5)
            cliquer_element(driver, By.CSS_SELECTOR, '[data-test-name="option-oui"]')
            pause_humaine(1.5, 2.5)
            cliquer_element(driver, By.ID, "buttonNext")
            
            pause_humaine(2.0, 3.5)
            cliquer_element(driver, By.CSS_SELECTOR, '[data-test-name="option-non"]')

            # Sécurité anti-anomalie Medallia : garantit une durée totale >= 1 minute (68s - 96s)
            temps_ecoule = time.time() - t_debut_passage
            if temps_ecoule < duree_cible_sondage:
                attente_antifraude = duree_cible_sondage - temps_ecoule
                logging.info(f"   -> Temporisation humaine anti-anomalie ({int(temps_ecoule)}s écoulées, validation dans {attente_antifraude:.1f}s)...")
                time.sleep(attente_antifraude)

            cliquer_element(driver, By.ID, "buttonFinish")
            pause_humaine(3.0, 5.0)
            
            duree_totale_sec = int(time.time() - t_debut_passage)
            nb_succes += 1
            logging.info(
                f"Passage #{i+1:03d} OK ({duree_totale_sec}s) | Ticket: {date_ticket} {heure_ticket}:{minute_ticket} | "
                f"Appareil: {profil_actuel['nom']} | Com: {commentaire_choisi}"
            )
            notifier_discord(
                f"✅ Passage #{i+1:03d}/{NOMBRE_DE_REPETITIONS} Réussi",
                f"**Ticket** : `{date_ticket} {heure_ticket}:{minute_ticket}`\n**Durée** : `{duree_totale_sec}s` (humaine > 1 min)\n**Appareil** : {profil_actuel['nom']}\n**Commentaire** : {commentaire_choisi}\n**Progression** : `{nb_succes}/{NOMBRE_DE_REPETITIONS}` réussis",
                couleur=0x2ECC71
            )
    
            break # Sortie du retry puisque cette tentative a réussi !

        except Exception as e:
            detail_err = str(e).strip().splitlines()[0] if str(e).strip() else ""
            message_erreur_court = f"{type(e).__name__} ({detail_err})" if detail_err else type(e).__name__
            if tentative == 0:
                logging.warning(f"   -> Passage #{i+1:03d} échec tentative 1/2 ({message_erreur_court}). Rotation IP et nouvel essai...")
                time.sleep(3)
                continue

            # Échec définitif après 2 tentatives
            nb_erreurs += 1
            horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_image = f"{DOSSIER_SCREENSHOTS}/erreur_tour_{i+1:03d}_{horodatage}.png"
            
            try:
                if driver is not None:
                    driver.save_screenshot(nom_image)
                    info_screen = f"Screen: {nom_image}"
                else:
                    info_screen = "Screen: Non dispo"
            except Exception:
                info_screen = "Screen: Impossible"
    
            logging.error(
                f"Passage #{i+1:03d} ÉCHEC | Appareil: {profil_actuel['nom']} | "
                f"{info_screen} | Cause: {message_erreur_court}"
            )
            notifier_discord(
                f"⚠️ Incident Passage #{i+1:03d}",
                f"**Cause** : `{message_erreur_court}`\n**Appareil** : {profil_actuel['nom']}\n**Restaurant** : `{ID_RESTO}`",
                couleur=0xE74C3C,
                ping_admin=True
            )
    
        finally:
            print("Nettoyage du navigateur et de la RAM...")
            nettoyer_processus_fantomes(driver)

    attente = random.randint(120, 420)
    if i < NOMBRE_DE_REPETITIONS - 1:
        print(f"Pause de {attente} secondes avant le prochain client...")
        time.sleep(attente)

bilan_msg = f"**Restaurant** : `{ID_RESTO}`\n**Formulaires réussis** : `{nb_succes}/{NOMBRE_DE_REPETITIONS}`\n**Échecs** : `{nb_erreurs}`"
logging.info(f"=== FIN DE LA SESSION : {nb_succes} réussis / {nb_erreurs} échoués ===")
notifier_discord(
    "🏁 Session McDo Terminée",
    bilan_msg,
    couleur=0x2ECC71 if nb_erreurs == 0 else 0xE67E22
)