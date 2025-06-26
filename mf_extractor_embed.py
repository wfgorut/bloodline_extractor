import os
import csv
import time
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from driver import cerrar_tabs_adicionales
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 10

def guardar_links_mediafire_csv(path, links, alias, library_path):
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
            writer.writerow(["episodio", "link_mediafire", "ruta_destino"])

        ruta_destino = os.path.join(library_path, alias)
        for episodio, link in links:
            if episodio not in existentes:
                writer.writerow([episodio, link, ruta_destino])

def validar_link_final(link):
    try:
        r = requests.head(link, allow_redirects=True, timeout=10)
        return r.status_code == 200
    except:
        return False

def resolver_link_mediafire(driver, proxy_url):
    try:
        driver.get(proxy_url)
        WebDriverWait(driver, TIMEOUT).until(lambda d: "mediafire.com/file" in d.current_url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        boton = soup.find("a", id="downloadButton")

        if boton and boton.has_attr("href") and "error.php" not in boton["href"]:
            final = boton["href"]
            if validar_link_final(final):
                print(f"    [SUCCESS] Link MediaFire resuelto: {final}")
                return final
        return None
    except:
        return None

def extraer_link_mediafire(slug, alias, episodio_tag, episodio_url, driver, folder_path):
    print(f"  [FALLBACK] Verificando MediaFire para {episodio_url}")
    try:
        driver.get(episodio_url)
        cerrar_tabs_adicionales(driver)
        time.sleep(2)

        if "404" in driver.title or "Oops" in driver.page_source:
            print("    [ERROR] Página 404 detectada, abortando fallback.")
            return {"estado": "no_link", "motivo": "pagina_404"}

        try:
            WebDriverWait(driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "dwld"))
            ).click()
            cerrar_tabs_adicionales(driver)
            time.sleep(1.5)
        except Exception as e:
            print(f"    [WARNING] No se pudo hacer clic en botón de mirrors: {e}")
            return {"estado": "no_link", "motivo": "no_se_pudo_abrir_mirrors"}

        soup = BeautifulSoup(driver.page_source, "html.parser")
        tabla = soup.find("div", class_="download")
        if not tabla:
            print("    [WARNING] No se encontró la tabla de mirrors.")
            return {"estado": "no_link", "motivo": "sin_tabla_mirrors"}

        mirrors_disponibles = []
        for fila in tabla.find_all("tr"):
            celdas = fila.find_all("td")
            if len(celdas) >= 4:
                server = celdas[0].text.strip().lower()
                a = celdas[3].find("a")
                if a and a.has_attr("href"):
                    mirrors_disponibles.append((server, a["href"]))

        for server, link in mirrors_disponibles:
            if server != "mediafire":
                continue
            link_final = resolver_link_mediafire(driver, link)
            if link_final:
                # RUTA FINAL DEL CSV → D:/catalog/BloodlineLibrary/anime/ALIAS/mediafire_ALIAS.csv
                path_csv = os.path.join(folder_path, f"mediafire_{alias}.csv")
                guardar_links_mediafire_csv(path_csv, [(episodio_tag, link_final)], alias, folder_path)
                return {
                    "estado": "ok",
                    "servidor": "Mediafire",
                    "link": link_final,
                    "episodio_tag": episodio_tag
                }

        print("    [WARNING] Ningún link válido de MediaFire fue resuelto.")
        return {"estado": "no_link", "motivo": "sin_mediafire_valido"}

    except Exception as e:
        print(f"    [ERROR] Fallback MediaFire falló: {e}")
        return {"estado": "no_link", "motivo": "excepcion"}
