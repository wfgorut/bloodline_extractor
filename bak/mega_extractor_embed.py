import os
import time
import csv
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

BASE_URL = "https://jkanime.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

scraper = cloudscraper.create_scraper()

# Espera aleatoria entre 2.5 y 3.5 segundos
def SAFE_SLEEP():
    import random
    time.sleep(random.uniform(2.5, 3.5))

def formatear_episodio(n):
    return f"ep{int(n)}"

def resolver_link_proxy(proxy_url, driver):
    try:
        resp = requests.get(proxy_url, headers=HEADERS, allow_redirects=True, timeout=(5, 15))
        if "mega.nz" in resp.url:
            return resp.url
    except:
        pass

    try:
        driver.get(proxy_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        return iframe.get_attribute("src") if iframe and "mega.nz" in iframe.get_attribute("src") else None
    except:
        return None

def verificar_link_mega(link, driver):
    try:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Aceptar todo']"))
            ).click()
            time.sleep(1)
        except:
            pass
        return esperar_botones_descarga(driver)
    except:
        return False

def esperar_botones_descarga(driver, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "button.js-standard-download, a.js-standard-download"))
        )
        return True
    except:
        return False

def extraer_link_mega(slug, alias, episodio, driver, library_path):
    episodio_tag = formatear_episodio(episodio)
    episodio_url = f"{BASE_URL}/{slug}/{episodio}/"
    print(f"[▶] Revisando episodio: {episodio_url}")

    try:
        driver.get(episodio_url)
        SAFE_SLEEP()

        if "404" in driver.title or "Página no encontrada" in driver.page_source:
            print(f"  [❌] Página inexistente para {episodio_tag}")
            return None

        WebDriverWait(driver, 12).until(EC.element_to_be_clickable((By.ID, "dwld"))).click()
        SAFE_SLEEP()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        tabla = soup.find("div", class_="download")
        if tabla:
            for fila in tabla.find_all("tr"):
                celdas = fila.find_all("td")
                if len(celdas) >= 4 and "mega" in celdas[0].text.lower():
                    a = celdas[3].find("a")
                    if a and a.has_attr("href"):
                        proxy_url = a["href"]
                        final_url = resolver_link_proxy(proxy_url, driver)
                        if final_url and "mega.nz" in final_url and verificar_link_mega(final_url, driver):
                            print(f"  [+] {episodio_tag}: {final_url}")
                            guardar_links_csv(os.path.join(library_path, alias, f"{alias}_mega_links.csv"), [(episodio_tag, final_url)], slug, library_path)
                            return final_url

        print(f"  [⚠️] No se encontró link MEGA para {episodio_tag}")
        return None

    except Exception as e:
        print(f"  [!] Error al procesar {episodio_tag}: {e}")
        return None

def guardar_links_csv(path, links, slug, library_path):
    existentes = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and row[0]:
                    existentes.add(row[0])

    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if os.stat(path).st_size == 0 or not existentes:
            writer.writerow(["episodio", "link_mega", "ruta_destino"])

        ruta_destino = os.path.join(library_path, slug)
        for episodio, link in links:
            if episodio not in existentes:
                writer.writerow([episodio, link, ruta_destino])
