import os
import csv
import json
import datetime
from config import BASE_PATH
from config import LOG_MAESTRO_PATH

def cargar_progress():
    if os.path.exists(LOG_MAESTRO_PATH):
        try:
            with open(LOG_MAESTRO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def guardar_progress(data):
    with open(LOG_MAESTRO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def timestamp():
    return datetime.datetime.now().isoformat(timespec='seconds')

def registrar_faltante(slug, alias, ep_tag):
    data = cargar_progress()
    if slug not in data:
        data[slug] = {
            "alias": alias,
            "episodios_totales_declarados": 0,
            "episodios_exitosos_mega": [],
            "episodios_exitosos_mf": [],
            "episodios_faltantes": [],
            "episodios_consultados": [],
            "modo_exploratorio": True,
            "completado": False,
        }

    anime = data[slug]

    # Solo se registra como faltante si no fue exitoso en ninguna fuente
    if ep_tag not in anime["episodios_exitosos_mega"] and ep_tag not in anime["episodios_exitosos_mf"]:
        if ep_tag not in anime["episodios_faltantes"]:
            anime["episodios_faltantes"].append(ep_tag)

    if ep_tag not in anime["episodios_consultados"]:
        anime["episodios_consultados"].append(ep_tag)

    anime["timestamp"] = timestamp()
    guardar_progress(data)

def registrar_exito_mega(slug, alias, ep_tag):
    _registrar_exito(slug, alias, ep_tag, fuente="mega")

def registrar_exito_mf(slug, alias, ep_tag):
    _registrar_exito(slug, alias, ep_tag, fuente="mf")

def _registrar_exito(slug, alias, ep_tag, fuente):
    data = cargar_progress()
    if slug not in data:
        data[slug] = {
            "alias": alias,
            "episodios_totales_declarados": 0,
            "episodios_exitosos_mega": [],
            "episodios_exitosos_mf": [],
            "episodios_faltantes": [],
            "episodios_consultados": [],
            "modo_exploratorio": True,
            "completado": False,
        }

    anime = data[slug]

    if fuente == "mega":
        if ep_tag not in anime["episodios_exitosos_mega"]:
            anime["episodios_exitosos_mega"].append(ep_tag)
    elif fuente == "mf":
        if ep_tag not in anime["episodios_exitosos_mf"]:
            anime["episodios_exitosos_mf"].append(ep_tag)

    if ep_tag in anime["episodios_faltantes"]:
        anime["episodios_faltantes"].remove(ep_tag)

    if ep_tag not in anime["episodios_consultados"]:
        anime["episodios_consultados"].append(ep_tag)

    # Actualiza completado si ya se tienen todos los episodios
    totales = anime.get("episodios_totales_declarados") or 0
    if not anime.get("modo_exploratorio", True) and totales > 0:
        total_exitosos = len(anime["episodios_exitosos_mega"]) + len(anime["episodios_exitosos_mf"])
        if total_exitosos >= totales:
            anime["completado"] = True

    anime["timestamp"] = timestamp()
    guardar_progress(data)

def marcar_completado(slug):
    data = cargar_progress()
    if slug in data:
        data[slug]["completado"] = True
        data[slug]["timestamp"] = timestamp()
        guardar_progress(data)

def obtener_faltantes(slug):
    data = cargar_progress()
    anime = data.get(slug, {})
    return anime.get("episodios_faltantes", [])

def obtener_ultimo_consultado(slug):
    data = cargar_progress()
    anime = data.get(slug, {})
    episodios_consultados = anime.get("episodios_consultados", [])
    if not episodios_consultados:
        return 0
    ult_tag = episodios_consultados[-1]
    try:
        return int(ult_tag.replace("ep", ""))
    except:
        return 0

def registrar_resumen_csv(slug):
    data = cargar_progress()
    info = data.get(slug)
    if not info:
        return

    alias = info.get("alias", slug)
    exitos_mega = len(info.get("episodios_exitosos_mega", []))
    exitos_mf = len(info.get("episodios_exitosos_mf", []))
    total_exitosos = exitos_mega + exitos_mf

    totales = info.get("episodios_totales_declarados", 0)
    if info.get("modo_exploratorio", True) or totales == 0:
        totales = obtener_ultimo_consultado(slug)  # ✅ solo hasta el último episodio válido

    completo = "Sí" if total_exitosos >= totales and totales > 0 else "No"

    resumen_path = os.path.join(BASE_PATH, "resumen_progreso.csv")
    existe = os.path.exists(resumen_path)

    if existe:
        with open(resumen_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("slug") == slug:
                    print(f"[CSV] Ya existe entrada previa para {slug}, omitiendo.")
                    return

    with open(resumen_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["alias", "slug", "episodios", "exitos_mega", "exitos_mf", "completo"])
        writer.writerow([alias, slug, totales, exitos_mega, exitos_mf, completo])

    print(f"[CSV] Resumen actualizado: {slug}")
