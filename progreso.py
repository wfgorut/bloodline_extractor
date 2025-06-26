import os
import json
import datetime
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
            "episodios_exitosos": [],
            "episodios_faltantes": [],
            "episodios_consultados": [],
            "modo_exploratorio": True,
            "completado": False,
        }

    anime = data[slug]

    if ep_tag not in anime["episodios_faltantes"]:
        anime["episodios_faltantes"].append(ep_tag)

    if ep_tag not in anime["episodios_consultados"]:
        anime["episodios_consultados"].append(ep_tag)

    anime["timestamp"] = timestamp()
    guardar_progress(data)

def registrar_exito(slug, alias, ep_tag):
    data = cargar_progress()
    if slug not in data:
        data[slug] = {
            "alias": alias,
            "episodios_totales_declarados": 0,
            "episodios_exitosos": [],
            "episodios_faltantes": [],
            "episodios_consultados": [],
            "modo_exploratorio": True,
            "completado": False,
        }

    anime = data[slug]

    # Añade a episodios exitosos si no estaba
    if ep_tag not in anime["episodios_exitosos"]:
        anime["episodios_exitosos"].append(ep_tag)

    # Quita de episodios_faltantes si estaba
    if ep_tag in anime.get("episodios_faltantes", []):
        anime["episodios_faltantes"].remove(ep_tag)

    # Añade a episodios_consultados si no estaba
    if ep_tag not in anime["episodios_consultados"]:
        anime["episodios_consultados"].append(ep_tag)

    # Actualiza completado solo si no es modo exploratorio y ya tienes todos los episodios
    totales = anime.get("episodios_totales_declarados") or 0
    if not anime.get("modo_exploratorio", True) and totales > 0:
        if len(anime["episodios_exitosos"]) >= totales:
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
        return 0  # No hay episodios consultados, empieza desde 1
    # Sacar el número del último episodio consultado
    ult_tag = episodios_consultados[-1]  # último episodio tipo "ep4"
    try:
        return int(ult_tag.replace("ep", ""))  # extraer el número
    except:
        return 0
