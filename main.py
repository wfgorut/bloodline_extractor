import socket
from directorio import obtener_slugs_directorio
from metadata_extractor import extraer_metadata
from config import LIBRARY_PATH, SAFE_SLEEP
from utils import generar_alias
from procesar_anime import procesar_anime
from driver import crear_driver_configurado as crear_driver
from progreso import obtener_ultimo_slug_incompleto
import time

print("=== BLOODLINE EXTRACTOR ===")

# --- DETECCIÓN DE HOSTNAME ---
nombre_pc = socket.gethostname().upper()
print(f"[PC] Ejecutando en máquina: {nombre_pc}")
print(f"[PATH] Biblioteca localizada en: {LIBRARY_PATH}\n")

# --- SELECCIÓN DE ESTADO ---
estado_map = {
    "1": "finalizados",
    "2": "emision",
    "3": "estrenos"
}

op_estado = ""
while op_estado not in estado_map:
    print("1. Selecciona el tipo de animes a scrapear:")
    print("   [1] Finalizados")
    print("   [2] En emisión")
    print("   [3] Estrenos (solo metadata)")
    op_estado = input("   Opción (1/2/3): ").strip()

estado = estado_map[op_estado]

# --- SELECCIÓN DE ORDEN ---
op_orden = ""
while op_orden not in ("1", "2"):
    print("\n2. ¿En qué orden deseas procesar?")
    print("   [1] Descendente (por defecto)")
    print("   [2] Ascendente (de los más viejos a los nuevos)")
    op_orden = input("   Opción (1/2): ").strip()

orden = "asc" if op_orden == "2" else "desc"

# --- VISIBILIDAD DEL NAVEGADOR ---
op_visible = ""
while op_visible not in ("1", "2"):
    print("\n3. ¿Deseas que el navegador sea visible?")
    print("   [1] Sí (útil para debug)")
    print("   [2] No (modo oculto fuera del monitor)")
    op_visible = input("   Visibilidad (1/2): ").strip()

modo_oculto = (op_visible == "2")

print(f"\n[SET] Estado: {estado} — Orden: {orden.upper()} — Navegador {'oculto' if modo_oculto else 'visible'}\n")

# === CREAR DRIVER UNA VEZ ===
driver = crear_driver(visible=not modo_oculto)

# --- INICIO DE SCRAPING ---
pagina = 1
ultima_pagina = None
aliases_generados = set()

try:
    while True:
        print(f"[JKANIME] Página {pagina}")
        slugs, ultima_pagina = obtener_slugs_directorio(estado, pagina, orden, driver=driver)
        if not slugs:
            print(f"[JKANIME] No se encontraron más animes en la página {pagina}. Fin del scraping.")
            break

        reanudar_desde = obtener_ultimo_slug_incompleto()
        reanudar_encontrado = False if reanudar_desde else True

        for slug in slugs:
            if not reanudar_encontrado:
                if slug == reanudar_desde:
                    print(f"[RESUME] Reanudando desde {slug}...")
                    reanudar_encontrado = True
                else:
                    print(f"[SKIP] Saltando {slug} (ya completado o no es el último incompleto)...")
                    continue

            try:
                alias = generar_alias(slug, existentes=aliases_generados)
                aliases_generados.add(alias)
                procesar_anime(slug, alias, driver=driver, modo_oculto=modo_oculto)
            except Exception as e:
                print(f"[ERROR] Error en {slug}: {e}")


        if pagina >= ultima_pagina:
            print(f"[SUCCESS] El extractor llegó a la última página: {ultima_pagina}")
            break

        pagina += 1
        print("[SLEEP] Descansando un poco antes de pasar a la siguiente página...\n")
        time.sleep(SAFE_SLEEP())

finally:
    driver.quit()

print("\n[END] Proceso finalizado.")
