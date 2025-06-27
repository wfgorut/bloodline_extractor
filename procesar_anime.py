import os
import time
from mega_extractor_embed import extraer_link_mega
from metadata_extractor import extraer_metadata
from mf_extractor_embed import extraer_link_mediafire
from utils import generar_alias
from config import LIBRARY_PATH, SAFE_SLEEP
from driver import cerrar_tabs_adicionales
from progreso import registrar_exito_mega, registrar_exito_mf, registrar_faltante, marcar_completado, obtener_ultimo_consultado

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
        print(f"[WARNING] Metadata inválida o incompleta para {slug}. Se activa exploración extendida.")

    links_validos = 0
    #  Arranca desde el último episodio consultado + 1
    ep = obtener_ultimo_consultado(slug) + 1

    print(f"  [CHECKING] Explorando episodios para {slug} desde ep{ep}...")

    while True:
        resultado = extraer_link_mega(slug, alias, ep, driver, LIBRARY_PATH)
        cerrar_tabs_adicionales(driver)

        if resultado["estado"] == "404":
            print(f"  [VOID] Slug agotado en {slug}/{ep}/ (404)")
            break

        if resultado["estado"] == "ok":
            print(f"  [SUCCESS] {resultado['episodio_tag']} OK (MEGA)")
            registrar_exito_mega(slug, alias, resultado['episodio_tag'])
            links_validos += 1
        else:
            print(f"  [VOID] No hay link válido en MEGA. Intentando fallback MediaFire...")
            url_episodio = f"https://jkanime.net/{slug}/{ep}/"
            fallback = extraer_link_mediafire(slug, alias, resultado['episodio_tag'], url_episodio, driver, folder_path)
            
            if fallback["estado"] == "ok":
                print(f"  [SUCCESS] {resultado['episodio_tag']} OK (MediaFire)")
                registrar_exito_mf(slug, alias, resultado['episodio_tag'])
                links_validos += 1
            else:
                print(f"  [FAIL] Sin links válidos para {resultado['episodio_tag']}")
                registrar_faltante(slug, alias, resultado['episodio_tag'])

        ep += 1
        time.sleep(SAFE_SLEEP())

    if links_validos > 0:
        marcar_completado(slug)
        from progreso import registrar_resumen_csv
        registrar_resumen_csv(slug)

    print(f"  [SUCCESS] Finalizado {slug}: {links_validos} enlaces MEGA válidos.")
    return True
