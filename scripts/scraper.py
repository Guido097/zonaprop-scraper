# scripts/scraper.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time
import random
import json

# Lista manual de user agents como fallback
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Intentar importar fake-useragent, usar fallback si falla
try:
    from fake_useragent import UserAgent
    ua = UserAgent()
    print("✅ Fake UserAgent cargado correctamente")
except ImportError:
    print("⚠️ Fake UserAgent no disponible, usando lista manual")
    ua = None

def get_random_user_agent():
    """Obtener user agent aleatorio"""
    if ua:
        try:
            return ua.random
        except:
            pass
    return random.choice(USER_AGENTS)

def create_stealthy_driver():
    """Crear un driver con máxima protección anti-detección"""
    print("🔧 Configurando driver anti-detección...")
    
    options = uc.ChromeOptions()
    
    # User agent aleatorio realista
    user_agent = get_random_user_agent()
    options.add_argument(f"user-agent={user_agent}")
    print(f"🎭 Usando User Agent: {user_agent[:50]}...")
    
    # Configuraciones básicas anti-detección (solo las compatibles)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Preferencias básicas del navegador
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "geolocation": 2,
            "media_stream": 2,
        }
    }
    options.add_experimental_option("prefs", prefs)
    
    print("🚀 Iniciando Chrome...")
    # Crear driver con undetected-chromedriver
    driver = uc.Chrome(options=options, version_main=None)
    
    # Scripts adicionales anti-detección
    try:
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        print("✅ Scripts anti-detección inyectados")
    except Exception as e:
        print(f"⚠️ No se pudieron inyectar scripts anti-detección: {e}")
    
    return driver

def human_like_scroll(driver):
    """Simular scroll humano"""
    try:
        scroll_pause_time = random.uniform(0.5, 2.0)
        
        # Scroll gradual hacia abajo
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {300 * (i + 1)});")
            time.sleep(scroll_pause_time)
        
        # Scroll un poco hacia arriba (comportamiento humano)
        driver.execute_script("window.scrollTo(0, 200);")
        time.sleep(scroll_pause_time)
    except Exception as e:
        print(f"⚠️ Error en scroll: {e}")

def wait_for_page_load_advanced(driver, max_attempts=5):
    """Espera avanzada con múltiples verificaciones"""
    for attempt in range(max_attempts):
        # Delay aleatorio inicial
        initial_delay = random.uniform(5, 12)
        print(f"⏱️ Esperando {initial_delay:.1f} segundos para carga inicial...")
        time.sleep(initial_delay)
        
        try:
            title = driver.title.lower()
            print(f"📄 Título detectado (intento {attempt + 1}): {driver.title}")
            
            # Verificar diferentes tipos de bloqueo
            if any(keyword in title for keyword in ["un momento", "verificando", "cloudflare", "checking", "loading"]):
                print(f"🛡️ Detectada página de verificación (intento {attempt + 1}). Esperando más tiempo...")
                # Incrementar delay exponencialmente
                verification_delay = random.uniform(15, 30) * (attempt + 1)
                print(f"⏳ Esperando {verification_delay:.1f} segundos adicionales...")
                time.sleep(verification_delay)
                
                # Simular actividad humana
                try:
                    human_like_scroll(driver)
                except:
                    pass
            else:
                print("✅ Página cargada correctamente")
                break
        except Exception as e:
            print(f"⚠️ Error verificando título: {e}")
            time.sleep(5)
    
    try:
        return driver.title
    except:
        return "Error obteniendo título"

def scrape_zonaprop(pages=2):
    """Función principal de scraping con máxima protección anti-bot"""
    print("🚀 Iniciando scraper avanzado anti-detección...")
    
    # Crear driver stealth
    driver = create_stealthy_driver()
    
    try:
        results = []
        base_url = "https://www.zonaprop.com.ar/departamentos-alquiler-cordoba-cb-desde-1-hasta-2-habitaciones-mas-de-2-ambientes.html"
        
        for page in range(1, pages + 1):
            print(f"\n{'='*50}")
            print(f"SCRAPEANDO PÁGINA {page}")
            print(f"{'='*50}")
            
            if page == 1:
                url = base_url
            else:
                url = f"https://www.zonaprop.com.ar/departamentos-alquiler-cordoba-cb-desde-1-hasta-2-habitaciones-mas-de-2-ambientes-pagina-{page}.html"
            
            print(f"🌐 URL visitada: {url}")
            
            # Navegar con delay aleatorio
            driver.get(url)
            
            # Espera avanzada para carga
            final_title = wait_for_page_load_advanced(driver)
            
            # Verificar si seguimos bloqueados
            if any(keyword in final_title.lower() for keyword in ["un momento", "verificando", "cloudflare"]):
                print(f"⚠️ Página {page} sigue bloqueada después de múltiples intentos")
                
                # Último intento: cambiar user agent y reintentar
                if page > 1:  # Solo para páginas > 1
                    print("🔄 Cambiando user agent y reintentando...")
                    new_ua = get_random_user_agent()
                    try:
                        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                            "userAgent": new_ua
                        })
                        print(f"🎭 Nuevo User Agent: {new_ua[:50]}...")
                        
                        driver.get(url)
                        final_title = wait_for_page_load_advanced(driver, max_attempts=2)
                    except Exception as e:
                        print(f"⚠️ Error cambiando user agent: {e}")
                
                if any(keyword in final_title.lower() for keyword in ["un momento", "verificando", "cloudflare"]):
                    print(f"❌ Saltando página {page} - No se pudo acceder")
                    continue
            
            print(f"✅ Acceso exitoso a página {page}")
            
            # Simular comportamiento humano antes de extraer datos
            human_like_scroll(driver)
            
            # Buscar propiedades
            cards = driver.find_elements(By.CSS_SELECTOR, '[data-qa="posting PROPERTY"]')
            print(f"🏠 Encontradas {len(cards)} propiedades en la página {page}")
            
            # Selector alternativo si no encuentra nada
            if len(cards) == 0:
                print("🔍 Probando selectores alternativos...")
                alt_selectors = [
                    '.posting-card',
                    '[class*="posting"]',
                    '[data-testid*="property"]',
                    '.property-card'
                ]
                
                for selector in alt_selectors:
                    cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if cards:
                        print(f"✅ Selector alternativo '{selector}' encontró {len(cards)} elementos")
                        break

            # Procesar cada propiedad
            for i, card in enumerate(cards):
                try:
                    # Delay aleatorio entre extracciones para simular lectura humana
                    if i > 0 and i % 5 == 0:  # Cada 5 propiedades
                        read_delay = random.uniform(1, 3)
                        time.sleep(read_delay)
                    
                    # Extraer datos con manejo robusto de errores
                    price = "Sin precio"
                    location = "Sin ubicación"
                    features = "Sin características"
                    description = "Sin descripción"
                    address = "Sin dirección"
                    
                    try:
                        price_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_PRICE"]')
                        price = price_element.text.strip()
                    except:
                        pass
                    
                    try:
                        location_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_LOCATION"]')
                        location = location_element.text.strip()
                    except:
                        pass
                    
                    try:
                        features_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_FEATURES"]')
                        features = features_element.text.strip()
                    except:
                        pass
                    
                    try:
                        desc_element = card.find_element(By.CSS_SELECTOR, '[data-qa="POSTING_CARD_DESCRIPTION"]')
                        if desc_element:
                            try:
                                link_element = desc_element.find_element(By.TAG_NAME, "a")
                                description = link_element.text.strip()
                            except:
                                description = desc_element.text.strip()
                    except:
                        pass
                    
                    # Extraer dirección usando múltiples selectores
                    try:
                        # Intentar con diferentes selectores para la dirección
                        address_selectors = [
                            'div.postingCard-module__posting-top > div:nth-child(1) > div:nth-child(2) > div > div',
                            '[data-qa*="ADDRESS"]',
                            '[class*="address"]',
                            '.posting-address',
                            'div[class*="posting-top"] div:nth-child(2) div',
                            'div:nth-child(2) > div > div'  # Selector más simple y robusto
                        ]
                        
                        for selector in address_selectors:
                            try:
                                address_element = card.find_element(By.CSS_SELECTOR, selector)
                                if address_element and address_element.text.strip():
                                    address = address_element.text.strip()
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    results.append({
                        "titulo": address,  # Ahora título es la dirección
                        "caracteristicas": features,  # Las características van en un campo separado
                        "precio": price,
                        "descripcion": description,
                        "ubicacion": location,
                        "pagina": page
                    })
                    
                except Exception as e:
                    print(f"⚠️ Error procesando propiedad {i+1}: {e}")
                    continue

            print(f"✅ Página {page} completada - {len([r for r in results if r['pagina'] == page])} propiedades extraídas")
            
            # Delay largo y aleatorio entre páginas
            if page < pages:
                # Base 20-35 segundos + random adicional
                base_delay = random.uniform(20, 35)
                extra_delay = random.uniform(0, 15)
                total_delay = base_delay + extra_delay
                
                print(f"⏳ Esperando {total_delay:.1f} segundos antes de la página {page + 1}...")
                print("💭 Simulando comportamiento humano...")
                
                # Durante la espera, simular actividad ocasional
                for wait_chunk in range(int(total_delay // 10)):
                    time.sleep(10)
                    if random.random() < 0.3:  # 30% chance de actividad
                        try:
                            driver.execute_script("window.scrollTo(0, Math.random() * 500);")
                        except:
                            pass
                
                # Esperar el tiempo restante
                remaining_time = total_delay % 10
                time.sleep(remaining_time)

        return pd.DataFrame(results)
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        return pd.DataFrame()
    
    finally:
        print("\n🔚 Cerrando navegador...")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    try:
        print("🚀 Iniciando scraper avanzado anti-detección...")
        df = scrape_zonaprop(pages=5)
        
        if not df.empty:
            df.to_csv("data/zonaprop_raw.csv", index=False, encoding="utf-8")
            print(f"✅ Datos guardados en data/zonaprop_raw.csv")
            print(f"📊 Total de propiedades extraídas: {len(df)}")
            print(f"📄 Propiedades por página:")
            for page in sorted(df['pagina'].unique()):
                count = len(df[df['pagina'] == page])
                print(f"   Página {page}: {count} propiedades")
        else:
            print("❌ No se pudieron extraer datos")
        
        print("🎉 Proceso completado")
    
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
