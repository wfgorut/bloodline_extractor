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
        data[slug] = {"alias": alias, "links_validos": 0, "faltantes": [], "intentos": {}, "completado": False}

    anime = data[slug]
    anime.setdefault("faltantes", [])
    anime.setdefault("intentos", {})

    if ep_tag not in anime["faltantes"]:
        anime["faltantes"].append(ep_tag)
    anime["intentos"][ep_tag] = anime["intentos"].get(ep_tag, 0) + 1
    anime["timestamp"] = timestamp()

    guardar_progress(data)

def registrar_exito(slug, alias, ep_tag):
    data = cargar_progress()
    if slug not in data:
        data[slug] = {"alias": alias, "links_validos": 0, "faltantes": [], "intentos": {}, "completado": False}

    anime = data[slug]
    anime["links_validos"] += 1
    if ep_tag in anime.get("faltantes", []):
        anime["faltantes"].remove(ep_tag)
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
    return anime.get("faltantes", [])
