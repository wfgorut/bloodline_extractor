import os
import re
import time
from mega_extractor_embed import extraer_link_mega
from metadata_extractor import extraer_metadata
from utils import generar_alias
from config import LIBRARY_PATH, SAFE_SLEEP
from driver import cerrar_tabs_adicionales
from progreso import registrar_exito, registrar_faltante, marcar_completado

def procesar_anime(slug, alias=None, driver=None, modo_oculto=True):
    """
    Procesa un anime: extrae metadata, busca episodios, guarda links MEGA.
    Usa modo exploratorio con errores consecutivos para terminar.
    """
    if alias is None:
        alias = generar_alias(slug)

    folder_path = os.path.join(LIBRARY_PATH, alias)
    os.makedirs(folder_path, exist_ok=True)

    # --- METADATA ---
    success = extraer_metadata(slug, alias, modo_oculto=modo_oculto, driver=driver)
    if not success:
        print(f"[!] No se pudo extraer metadata de {slug}. Abortando procesamiento.")
        return False

    # --- MODO EXPLORATORIO DE EPISODIOS ---
    print(f"  [🔍] Explorando episodios para {slug}...")
    errores_consecutivos = 0
    MAX_ERRORES = 2
    ep = 1
    links_validos = 0

    while errores_consecutivos < MAX_ERRORES:
        ep_tag = f"ep{ep:02}"
        resultado = extraer_link_mega(slug, alias, ep, driver, LIBRARY_PATH)
        cerrar_tabs_adicionales(driver)

        if resultado:
            print(f"  [+] Episodio {ep:02} OK")
            links_validos += 1
            registrar_exito(slug, alias, ep_tag)
            errores_consecutivos = 0
        else:
            print(f"  [✖] Episodio {ep:02} no disponible")
            registrar_faltante(slug, alias, ep_tag)
            errores_consecutivos += 1

        ep += 1
        time.sleep(SAFE_SLEEP())

    if errores_consecutivos < MAX_ERRORES and links_validos > 0:
        marcar_completado(slug)

    print(f"  [✓] Finalizado {slug}: {links_validos} enlaces MEGA válidos.")
    return True
