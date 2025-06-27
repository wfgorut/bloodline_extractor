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
from driver import cerrar_tabs_adicionales
from progreso import registrar_faltante, registrar_exito_mega

BASE_URL = "https://jkanime.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

scraper = cloudscraper.create_scraper()

# Espera aleatoria entre 0.5 y .5 segundos
def SAFE_SLEEP():
    import random
    time.sleep(random.uniform(0.5, 2.5))

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
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframe = driver.find_element(By.TAG_NAME, "iframe")
        return iframe.get_attribute("src") if iframe and "mega.nz" in iframe.get_attribute("src") else None
    except:
        return None

def verificar_link_mega(link, driver):
    try:
        driver.get(link)
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
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
    episodio_tag = formatear_episodio(episodio)  # <- Solo aquí formateamos ep
    episodio_url = f"{BASE_URL}/{slug}/{episodio}/"
    print(f"[CHECKING] Revisando episodio: {episodio_url}")

    try:
        driver.get(episodio_url)
        SAFE_SLEEP()

        if "404" in driver.title or "Página no encontrada" in driver.page_source:
            print(f"  [VOID] Página inexistente para {episodio_tag}")
            registrar_faltante(slug, alias, episodio_tag)
            return {"estado": "404", "link": None, "episodio_tag": episodio_tag}

        WebDriverWait(driver, 12).until(EC.element_to_be_clickable((By.ID, "dwld"))).click()
        cerrar_tabs_adicionales(driver)
        SAFE_SLEEP()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        tabla = soup.find("div", class_="download")
        cerrar_tabs_adicionales(driver)
        if tabla:
            for fila in tabla.find_all("tr"):
                celdas = fila.find_all("td")
                if len(celdas) >= 4 and "mega" in celdas[0].text.lower():
                    a = celdas[3].find("a")
                    if a and a.has_attr("href"):
                        proxy_url = a["href"]
                        final_url = resolver_link_proxy(proxy_url, driver)
                        if final_url and "mega.nz" in final_url and verificar_link_mega(final_url, driver):
                            print(f"  [SUCCESS] {episodio_tag}: {final_url}")
                            guardar_links_csv(
                                os.path.join(library_path, alias, f"mega_{alias}.csv"),
                                [(episodio_tag, final_url)],
                                alias, library_path
                            )
                            registrar_exito_mega(slug, alias, episodio_tag)
                            return {"estado": "ok", "link": final_url, "episodio_tag": episodio_tag}

        print(f"  [WARNING] No se encontró link MEGA para {episodio_tag}")
        registrar_faltante(slug, alias, episodio_tag)
        return {"estado": "no_link", "link": None, "episodio_tag": episodio_tag}

    except Exception as e:
        print(f"  [ERROR] Error al procesar {episodio_tag}: {e}")
        registrar_faltante(slug, alias, episodio_tag)
        return {"estado": "error", "link": None, "episodio_tag": episodio_tag}

def guardar_links_csv(path, links, alias, library_path):
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

        ruta_destino = os.path.join(library_path, alias)
        for episodio, link in links:
            if episodio not in existentes:
                writer.writerow([episodio, link, ruta_destino])