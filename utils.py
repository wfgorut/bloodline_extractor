import csv
import os
import re
from config import LIBRARY_PATH

def generar_alias(slug, existentes=None, max_len=15):
    """
    Genera un alias legible a partir de un slug.

    :param slug: Texto tipo slug separado por guiones.
    :param existentes: Conjunto opcional de alias ya usados para evitar duplicados.
    :param max_len: Longitud máxima del alias.
    :return: Alias generado.
    """
    partes = [p for p in slug.split("-") if len(p) > 2]  # evita preposiciones y basura
    alias = ""

    for p in partes:
        if len(alias + p.capitalize()) <= max_len:
            alias += p.capitalize()
        else:
            break

    if not alias:
        alias = slug[:max_len].replace("-", "").capitalize()

    original_alias = alias
    contador = 1
    while existentes and alias in existentes:
        alias = f"{original_alias[:max_len - len(str(contador))]}{contador}"
        contador += 1

    return alias

def episodios_mega_guardados(alias, total_esperado):
    """Verifica cuántos episodios con link MEGA han sido extraídos y guardados en el CSV correspondiente."""
    path = os.path.join(LIBRARY_PATH, alias, f"{alias}_mega_links.csv")
    episodios = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Saltar cabecera
            for row in reader:
                if row and row[0].startswith("ep"):
                    try:
                        num = int(re.sub(r"\D", "", row[0]))
                        episodios.add(num)
                    except:
                        continue
    return len(episodios), episodios
