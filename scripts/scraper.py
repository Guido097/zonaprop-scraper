# scripts/scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random

options = Options()
# Comentamos headless para debuggear, luego lo podemos reactivar
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
# User agent más convincente
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-logging")
options.add_argument("--log-level=3")
options.add_argument("--silent")
options.add_argument("--disable-web-security")
options.add_argument("--disable-features=VizDisplayCompositor")
# Opciones adicionales para evitar detección
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Usar Service en lugar de executable_path
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Ejecutar script para ocultar que es un bot
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

def wait_for_page_load(driver, max_attempts=3):
    """Espera a que la página cargue completamente y maneja verificaciones"""
    for attempt in range(max_attempts):
        time.sleep(random.uniform(3, 7))  # Delay aleatorio entre 3-7 segundos
        
        title = driver.title.lower()
        if "un momento" in title or "verificando" in title or "cloudflare" in title:
            print(f"Detectada página de verificación (intento {attempt + 1}). Esperando...")
            time.sleep(random.uniform(5, 10))  # Espera más tiempo para verificaciones
        else:
            break
    
    return driver.title

def scrape_zonaprop(pages=2):
    results = []
    base_url = "https://www.zonaprop.com.ar/departamentos-alquiler-cordoba-cb-desde-1-hasta-2-habitaciones-mas-de-2-ambientes.html"
    
    print("Verificando la primera página para ver información de paginación...")
    driver.get(base_url)
    final_title = wait_for_page_load(driver)
    print(f"Título de la primera página: {final_title}")
    
    # Verificar si hay paginación en la primera página
    try:
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, '.pagination, .paging, [class*="pag"], [data-qa*="pag"]')
        print(f"Elementos de paginación encontrados: {len(pagination_elements)}")
        
        # Buscar números de página específicamente
        page_numbers = driver.find_elements(By.CSS_SELECTOR, 'a[href*="pagina-"]')
        if page_numbers:
            print(f"Enlaces de página encontrados: {len(page_numbers)}")
            max_page = 1
            for link in page_numbers:
                href = link.get_attribute('href')
                if 'pagina-' in href:
                    try:
                        page_num = int(href.split('pagina-')[1].split('.')[0])
                        max_page = max(max_page, page_num)
                    except:
                        continue
            print(f"Máximo número de página detectado: {max_page}")
        else:
            print("No se encontraron enlaces de paginación - posiblemente solo hay 1 página")
            max_page = 1
    except Exception as e:
        print(f"Error verificando paginación: {e}")
        max_page = 1
    
    # Ajustar el número de páginas a scrapear
    actual_pages = min(pages, max_page)
    print(f"Scrapeando {actual_pages} página(s) en total")
    
    for page in range(1, actual_pages + 1):
        print(f"\nScrapeando página {page}...")
        if page == 1:
            url = base_url
            # Ya cargamos la página 1, no necesitamos cargarla de nuevo
            if page > 1:
                driver.get(url)
                final_title = wait_for_page_load(driver)
        else:
            # Para páginas adicionales, agregamos el parámetro de página
            url = f"https://www.zonaprop.com.ar/departamentos-alquiler-cordoba-cb-desde-1-hasta-2-habitaciones-mas-de-2-ambientes-pagina-{page}.html"
            print(f"URL visitada: {url}")
            driver.get(url)
            final_title = wait_for_page_load(driver)
            print(f"Título final de la página: {final_title}")
            
            # Verificar si aún estamos en una página de verificación
            if "un momento" in final_title.lower():
                print(f"Página {page} sigue en verificación.")
                # Intentar una estrategia diferente: recargar la página 1 y navegar desde ahí
                print("Intentando navegar desde la página 1...")
                driver.get(base_url)
                wait_for_page_load(driver)
                
                # Buscar y hacer click en el enlace de la página específica
                try:
                    page_link = driver.find_element(By.CSS_SELECTOR, f'a[href*="pagina-{page}"]')
                    driver.execute_script("arguments[0].click();", page_link)
                    final_title = wait_for_page_load(driver)
                    print(f"Después del click: {final_title}")
                    if "un momento" in final_title.lower():
                        print(f"Aún en verificación después del click, saltando página {page}")
                        continue
                except Exception as e:
                    print(f"No se pudo hacer click en el enlace de la página {page}: {e}")
                    continue
        
        # Verificar si hay algún mensaje de error o página no encontrada
        page_source_sample = driver.page_source[:500]
        if "404" in page_source_sample or "No encontrado" in page_source_sample:
            print(f"Página {page} parece no existir")
            break

        # Usar los selectores correctos encontrados en el análisis
        cards = driver.find_elements(By.CSS_SELECTOR, '[data-qa="posting PROPERTY"]')
        print(f"Encontradas {len(cards)} propiedades en la página {page}")
        
        # Si no encontramos cards, intentemos con otros selectores alternativos
        if len(cards) == 0:
            print("No se encontraron cards con el selector principal, intentando selector alternativo...")
            alt_cards = driver.find_elements(By.CSS_SELECTOR, '.posting-card')
            print(f"Selector alternativo encontró: {len(alt_cards)} elementos")
            if len(alt_cards) > 0:
                cards = alt_cards

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
        
        # Delay aleatorio entre páginas para simular comportamiento humano
        if page < actual_pages:
            delay = random.uniform(5, 10)  # Aumentamos el delay
            print(f"Esperando {delay:.1f} segundos antes de la siguiente página...")
            time.sleep(delay)

    return pd.DataFrame(results)

if __name__ == "__main__":
    df = scrape_zonaprop(pages=5)
    df.to_csv("data/zonaprop_raw.csv", index=False, encoding="utf-8")
    print("Datos guardados en data/zonaprop_raw.csv")
    driver.quit()
