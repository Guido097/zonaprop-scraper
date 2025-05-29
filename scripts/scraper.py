
# scripts/scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-logging")
options.add_argument("--log-level=3")
options.add_argument("--silent")
options.add_argument("--disable-web-security")
options.add_argument("--disable-features=VizDisplayCompositor")

# Usar Service en lugar de executable_path
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def scrape_zonaprop(pages=2):
    results = []
    for page in range(1, pages + 1):
        print(f"Scrapeando página {page}...")
        url = f"https://www.zonaprop.com.ar/departamentos-alquiler-cordoba-capital-pagina-{page}.html"
        driver.get(url)
        time.sleep(5)  # Aumentamos el tiempo de espera

        # Usar los selectores correctos encontrados en el análisis
        cards = driver.find_elements(By.CSS_SELECTOR, '[data-qa="posting PROPERTY"]')
        print(f"Encontradas {len(cards)} propiedades en la página {page}")

        for card in cards:
            try:
                # Buscar precio
                price_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_PRICE"]')
                price = price_element.text.strip() if price_element else "Sin precio"
                
                # Buscar ubicación
                location_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_LOCATION"]')
                location = location_element.text.strip() if location_element else "Sin ubicación"
                
                # Buscar características (usar como título)
                features_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_FEATURES"]')
                features = features_element.text.strip() if features_element else "Sin características"
                
                # Buscar descripción
                desc_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_DESCRIPTION"]')
                if desc_element:
                    # Intentar obtener el texto del enlace dentro de la descripción
                    link_element = desc_element.find_element(By.TAG_NAME, "a")
                    description = link_element.text.strip() if link_element else desc_element.text.strip()
                else:
                    description = "Sin descripción"
                
                results.append({
                    "titulo": features,  # Usamos las características como título
                    "precio": price,
                    "descripcion": description,
                    "ubicacion": location
                })
                
            except Exception as e:
                print(f"Error procesando una tarjeta: {e}")
                continue

    return pd.DataFrame(results)

if __name__ == "__main__":
    df = scrape_zonaprop(pages=5)
    df.to_csv("data/zonaprop_raw.csv", index=False, encoding="utf-8")
    print("Datos guardados en data/zonaprop_raw.csv")
    driver.quit()
