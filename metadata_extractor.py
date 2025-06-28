import os 
import re
import csv
import time
import cloudscraper
import requests
from bs4 import BeautifulSoup
from progreso import registrar_resumen_csv, cargar_progress, guardar_progress
from config import LIBRARY_PATH
from utils import generar_alias
from driver import crear_driver_configurado, cerrar_tabs_adicionales

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

BASE_URL = "https://jkanime.net"

def extraer_metadata(slug, alias=None, existentes_aliases=None, modo_oculto=True, driver=None):
    if alias is None:
        alias = generar_alias(slug, existentes_aliases)

    carpeta_destino = os.path.join(LIBRARY_PATH, alias)
    os.makedirs(carpeta_destino, exist_ok=True)

    metadata_csv_path = os.path.join(carpeta_destino, f"{alias}_metadata.csv")
    imagen_path = os.path.join(carpeta_destino, f"{alias}.jpg")

    if os.path.exists(metadata_csv_path):
        try:
            with open(metadata_csv_path, encoding="utf-8") as f:
                if f.read().strip():
                    print(f"  [SUCCESS] Metadata guardada: {alias}_metadata.csv")
                    return True
        except:
            pass

    try:
        scraper = cloudscraper.create_scraper()
        url = f"{BASE_URL}/{slug}/"
        res = scraper.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"[ERROR] Error al acceder a {url} (status {res.status_code})")
            return False

        soup = BeautifulSoup(res.text, "html.parser")

        info_box = soup.select_one(".anime_info")
        datos_box = soup.select_one(".anime_data")

        # --- Titulo y sinopsis ---
        titulo = info_box.find("h3").text.strip() if info_box and info_box.find("h3") else slug
        sinopsis_tag = info_box.find("p", class_="scroll") if info_box else None
        sinopsis = sinopsis_tag.text.strip() if sinopsis_tag else ""
        sinopsis = sinopsis.replace("\n", " ").replace("\r", " ").strip()

        # --- Imagen ---
        img_tag = info_box.find("img") if info_box else None
        imagen_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
        if imagen_url.startswith("//"):
            imagen_url = "https:" + imagen_url
        elif imagen_url.startswith("/"):
            imagen_url = BASE_URL + imagen_url

        # --- Generos ---
        generos = ""
        if datos_box:
            genero_tags = datos_box.select("li span:-soup-contains('Generos') ~ a")
            generos = ", ".join([a.text.strip() for a in genero_tags])

        # --- Estado ---
        estado_div = info_box.select_one(".dropmenu") if info_box else None
        estado = estado_div["data-status"].capitalize() if estado_div and estado_div.has_attr("data-status") else "Desconocido"

        # --- Extras ---
        def extraer_valor(label):
            if not datos_box:
                return ""
            for li in datos_box.find_all("li"):
                span = li.find("span")
                if span and label.lower() in span.text.lower():
                    return li.text.replace(span.text, "").strip()
            return ""

        tipo = extraer_valor("Tipo") or "Serie"
        idioma = "Japonés"
        episodios = extraer_valor("Episodios")
        emitido = extraer_valor("Emitido")
        anio = ""
        if emitido:
            match = re.search(r"(\d{4})", emitido)
            if match:
                anio = match.group(1)

        # --- Guardar imagen local ---
        if imagen_url:
            try:
                img_response = requests.get(imagen_url, headers=HEADERS, timeout=10)
                img_response.raise_for_status()
                with open(imagen_path, "wb") as f:
                    f.write(img_response.content)
                print(f"  [SUCCESS] Imagen guardada como {alias}.jpg")
            except Exception as e:
                print(f"  [ERROR] Error al guardar imagen de {slug}: {e}")
        else:
            print(f"  [WARNING] No se encontró imagen para {slug}")

        # --- Guardar CSV ---
        with open(metadata_csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["titulo", "sinopsis", "generos", "estado", "episodios", "tipo", "idioma", "anio"])
            writer.writerow([titulo, sinopsis, generos, estado, episodios, tipo, idioma, anio])

        print(f"  [SUCCESS] Metadata guardada: {metadata_csv_path}")

        # === INICIO EXTRACCIÓN MEGA ===
        try:
            encontrados = re.findall(r"\d+", episodios)
            if encontrados:
                total_eps = int(encontrados[-1])
            else:
                total_eps = 0
        except:
            total_eps = 0

        # === ACTUALIZAR PROGRESO SIN PERDER INFO PREVIA ===
        data = cargar_progress()
        prev = data.get(slug, {})

        data[slug] = {
            "alias": alias,
            "episodios_totales_declarados": total_eps if total_eps > 0 else prev.get("episodios_totales_declarados", 0),
            "episodios_exitosos_mega": prev.get("episodios_exitosos_mega", []),
            "episodios_exitosos_mf": prev.get("episodios_exitosos_mf", []),
            "episodios_faltantes": prev.get("episodios_faltantes", []),
            "episodios_consultados": prev.get("episodios_consultados", []),
            "modo_exploratorio": total_eps == 0 if "modo_exploratorio" not in prev else prev["modo_exploratorio"],
            "completado": prev.get("completado", False),
            "timestamp": prev.get("timestamp")
        }

        guardar_progress(data)

        print(f"  [INFO] Metadata registrada correctamente. Episodios serán procesados por el extractor principal.")
        return True

    except Exception as e:
        print(f"[ERROR] Error extrayendo metadata de {slug}: {e}")
        return False
