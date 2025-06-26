import os
import time
from mega_extractor_embed import extraer_link_mega
from metadata_extractor import extraer_metadata
from utils import generar_alias
from config import LIBRARY_PATH, SAFE_SLEEP
from driver import cerrar_tabs_adicionales
from progreso import registrar_exito, registrar_faltante, marcar_completado

def procesar_anime(slug, alias=None, driver=None, modo_oculto=True):
    """
    Procesa un anime: extrae metadata, explora episodios, guarda links MEGA.
    Solo se detiene si se detecta 404 en jkanime.net/{slug}/{n}.
    """
    if alias is None:
        alias = generar_alias(slug)

    folder_path = os.path.join(LIBRARY_PATH, alias)
    os.makedirs(folder_path, exist_ok=True)

    # --- METADATA ---
    success = extraer_metadata(slug, alias, modo_oculto=modo_oculto, driver=driver)
    if not success:
        print(f"[⚠️] Metadata inválida o incompleta para {slug}. Se activa exploración extendida.")

    links_validos = 0
    ep = 1

    print(f"  [🔍] Explorando episodios para {slug}...")

    while True:
        ep_tag = f"ep{ep:02}"
        resultado = extraer_link_mega(slug, alias, ep, driver, LIBRARY_PATH)
        cerrar_tabs_adicionales(driver)

        if resultado["estado"] == "404":
            print(f"  [🚫] Slug agotado en {slug}/{ep}/ (404)")
            break

        if resultado["estado"] == "ok":
            print(f"  [+] Episodio {ep:02} OK")
            registrar_exito(slug, alias, ep_tag)
            links_validos += 1
        else:
            print(f"  [✖] Episodio {ep:02} no disponible")
            registrar_faltante(slug, alias, ep_tag)
            # ⚠️ No abortar por error, solo avanzar al siguiente episodio

        ep += 1
        time.sleep(SAFE_SLEEP())

    if links_validos > 0:
        marcar_completado(slug)

    print(f"  [✓] Finalizado {slug}: {links_validos} enlaces MEGA válidos.")
    return True
