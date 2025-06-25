import re
import json
from bs4 import BeautifulSoup
from config import HEADERS
from driver import obtener_html_renderizado, crear_driver_configurado

BASE_URL = "https://jkanime.net"

def construir_url_directorio(estado="finalizados", pagina=1, orden="desc"):
    url = f"{BASE_URL}/directorio?estado={estado}"
    if orden == "asc":
        url += "&orden=asc"
    url += f"&p={pagina}"
    return url

def obtener_slugs_directorio(estado, pagina, orden="desc"):
    url = construir_url_directorio(estado, pagina, orden)
    html = obtener_html_renderizado(url, visible=False)
    soup = BeautifulSoup(html, "html.parser")

    script_tags = soup.find_all("script", string=re.compile(r"var animes\s*=\s*\{"))

    for script in script_tags:
        match = re.search(r"var animes\s*=\s*(\{.*?\});", script.string, re.DOTALL)
        if match:
            try:
                animes_json = json.loads(match.group(1))
                slugs = [entry["slug"] for entry in animes_json["data"]]
                last_page = animes_json.get("last_page", pagina)
                print(f"[DEBUG] {len(slugs)} slugs encontrados en página {pagina}")
                return slugs, last_page
            except Exception as e:
                print(f"[!] Error al parsear JSON en página {pagina}: {e}")
                return [], pagina

    print(f"[!] No se encontró bloque 'var animes' en la página {pagina}")
    return [], pagina
