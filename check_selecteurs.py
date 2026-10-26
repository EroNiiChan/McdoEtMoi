from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import shutil
import platform
import time

# --- DÉTECTION AUTOMATIQUE DU DRIVER ---
if platform.system() == "Linux" and shutil.which("chromedriver"):
    chemin_driver = shutil.which("chromedriver")
    from selenium.webdriver.chrome.service import Service as ChromeService
    service = ChromeService(chemin_driver)
else:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    service = ChromeService(ChromeDriverManager().install())

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=service, options=options)

def explorer_chemin(nom_test, selecteur_mode):
    print(f"\n==============================================")
    print(f"TEST DU PARCOURS : {nom_test}")
    print(f"==============================================")
    
    try:
        # 1. Connexion et accueil
        driver.get("https://survey2.medallia.eu/?hellomcdo")
        time.sleep(2.5)
        driver.find_element(By.ID, "buttonBegin").click()
        time.sleep(2)

        # 2. Âge (On prend 25-34 ans)
        driver.find_element(By.CSS_SELECTOR, '[data-test-name="option-entre-25-et-34-ans"]').click()
        driver.find_element(By.ID, "buttonNext").click()
        time.sleep(2)

        # 3. Ticket (Hier à 13h00)
        hier = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        driver.find_element(By.ID, "cal_q_mc_q_date_").send_keys(hier)
        driver.find_element(By.ID, "spl_rng_q_mc_q_hour").send_keys("13")
        driver.find_element(By.ID, "spl_rng_q_mc_q_minute").send_keys("15")
        driver.find_element(By.ID, "spl_rng_q_mc_q_idrestaurant").send_keys("0000")
        driver.find_element(By.ID, "buttonNext").click()
        time.sleep(2)

        # 4. Mode de commande testé (Drive ou autre)
        driver.find_element(By.CSS_SELECTOR, selecteur_mode).click()
        driver.find_element(By.ID, "buttonNext").click()
        time.sleep(2.5)

        # 5. Exploration des pages suivantes jusqu'à la note globale (max 4 étapes)
        for etape in range(1, 5):
            # Vérifie si on est arrivé à la page de notation globale
            if len(driver.find_elements(By.ID, "onf_q_feedback_m_based_upon_this_visit_to_this_6_1")) > 0:
                print(f"-> Arrivé avec succès sur la page de SATISFACTION GLOBALE !")
                break

            # Récupère le texte de la question affichée à l'écran
            titre_question = "Intitulé introuvable"
            try:
                titre_question = driver.find_element(By.TAG_NAME, "h1").text
            except Exception:
                try:
                    titre_question = driver.find_element(By.TAG_NAME, "legend").text
                except Exception:
                    pass

            print(f"\n[Page {etape}] Question détectée : '{titre_question}'")
            print("Options disponibles sur cette page :")
            
            options_page = driver.find_elements(By.CSS_SELECTOR, "[data-test-name]")
            if options_page:
                for el in options_page:
                    print(f"  -> {el.get_attribute('data-test-name')}")
                # Clique sur la première option par défaut pour continuer le parcours
                options_page[0].click()
            else:
                print("  -> (Aucun bouton [data-test-name] trouvé, champ texte ou autre ?)")

            time.sleep(1)
            driver.find_element(By.ID, "buttonNext").click()
            time.sleep(2.5)

    except Exception as e:
        print(f"Erreur pendant l'exploration de {nom_test} : {e}")

try:
    # Test 1 : Parcourir le mode Drive
    explorer_chemin("AU DRIVE", '[data-test-name="option-au-drive"]')
    
    # Test 2 : Parcourir le mode Sur place
    explorer_chemin("CONSOMMÉ SUR PLACE", '[data-test-name="option-consommé-sur-place"]')

finally:
    driver.quit()
    print("\nExploration des parcours terminée !")