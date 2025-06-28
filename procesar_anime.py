import os
import time
from mega_extractor_embed import extraer_link_mega
from metadata_extractor import extraer_metadata
from mf_extractor_embed import extraer_link_mediafire
from utils import generar_alias
from config import LIBRARY_PATH, SAFE_SLEEP
from driver import cerrar_tabs_adicionales
from progreso import (
    registrar_exito_mega,
    registrar_exito_mf,
    registrar_faltante,
    marcar_completado,
    obtener_ultimo_consultado,
    cargar_progress,
    registrar_resumen_csv
)

def procesar_anime(slug, alias=None, driver=None, modo_oculto=True):
    if alias is None:
        alias = generar_alias(slug)

    folder_path = os.path.join(LIBRARY_PATH, alias)
    os.makedirs(folder_path, exist_ok=True)

    # --- METADATA ---
    success = extraer_metadata(slug, alias, modo_oculto=modo_oculto, driver=driver)
    if not success:
        print(f"[WARNING] Metadata inválida o incompleta para {slug}. Se activa exploración extendida.")

    data = cargar_progress()
    info = data.get(slug, {})
    total_eps = info.get("episodios_totales_declarados", 0)
    modo_exploratorio = info.get("modo_exploratorio", True)

    # --- CARGA DE EPISODIOS YA DESCARGADOS (MEGA o MF) ---
    vistos_mega = set(info.get("episodios_exitosos_mega", []))
    vistos_mf = set(info.get("episodios_exitosos_mf", []))
    vistos_totales = vistos_mega.union(vistos_mf)

    if not total_eps or modo_exploratorio:
        # === MODO EXPLORATORIO ===
        ep = obtener_ultimo_consultado(slug) + 1
        print(f"  [INFO] Modo exploratorio activado. Explorando hasta encontrar 404...")
        while True:
            episodio_tag = f"ep{ep}"
            if episodio_tag in vistos_totales:
                print(f"[SKIP] {episodio_tag} ya descargado por MEGA o MF, saltando...")
                ep += 1
                continue

            resultado = extraer_link_mega(slug, alias, ep, driver, LIBRARY_PATH)
            cerrar_tabs_adicionales(driver)

            if resultado["estado"] == "404":
                print(f"  [VOID] Slug agotado en {slug}/{ep}/ (404)")
                break

            if resultado["estado"] == "ok":
                print(f"  [SUCCESS] {resultado['episodio_tag']} OK (MEGA)")
                registrar_exito_mega(slug, alias, resultado['episodio_tag'])
            else:
                print(f"  [VOID] No hay link válido en MEGA. Intentando fallback MediaFire...")
                url_episodio = f"https://jkanime.net/{slug}/{ep}/"
                fallback = extraer_link_mediafire(slug, alias, resultado['episodio_tag'], url_episodio, driver, folder_path)

                if fallback["estado"] == "ok":
                    print(f"  [SUCCESS] {resultado['episodio_tag']} OK (MediaFire)")
                    registrar_exito_mf(slug, alias, resultado['episodio_tag'])
                else:
                    print(f"  [FAIL] Sin links válidos para {resultado['episodio_tag']}")
                    registrar_faltante(slug, alias, resultado['episodio_tag'])

            ep += 1
            time.sleep(SAFE_SLEEP())
    else:
        # === MODO DECLARADO ===
        print(f"  [INFO] Metadata válida: recorriendo 1 → {total_eps}")
        for ep in range(1, total_eps + 1):
            episodio_tag = f"ep{ep}"
            if episodio_tag in vistos_totales:
                print(f"[SKIP] {episodio_tag} ya descargado por MEGA o MF, saltando...")
                continue

            resultado = extraer_link_mega(slug, alias, ep, driver, LIBRARY_PATH)
            cerrar_tabs_adicionales(driver)

            if resultado["estado"] == "ok":
                print(f"  [SUCCESS] {resultado['episodio_tag']} OK (MEGA)")
                registrar_exito_mega(slug, alias, resultado['episodio_tag'])
            else:
                print(f"  [VOID] No hay link válido en MEGA. Intentando fallback MediaFire...")
                url_episodio = f"https://jkanime.net/{slug}/{ep}/"
                fallback = extraer_link_mediafire(slug, alias, resultado['episodio_tag'], url_episodio, driver, folder_path)

                if fallback["estado"] == "ok":
                    print(f"  [SUCCESS] {resultado['episodio_tag']} OK (MediaFire)")
                    registrar_exito_mf(slug, alias, resultado['episodio_tag'])
                else:
                    print(f"  [FAIL] Sin links válidos para {resultado['episodio_tag']}")
                    registrar_faltante(slug, alias, resultado['episodio_tag'])

            time.sleep(SAFE_SLEEP())

    # Actualiza resumen CSV si hubo al menos un link correcto
    data = cargar_progress()
    info = data.get(slug, {})
    ok_mega = len(info.get("episodios_exitosos_mega", []))
    ok_mf = len(info.get("episodios_exitosos_mf", []))
    total_ok = ok_mega + ok_mf

    if total_ok > 0:
        marcar_completado(slug)
        registrar_resumen_csv(slug)

    print(f"  [SUCCESS] Finalizado {slug}: {ok_mega} MEGA, {ok_mf} MF (total: {total_ok})")
    return True
