import os
import socket

# === HOSTNAMES REGISTRADOS ===
HOST_R7 = "R7-BLOODLINE"
HOST_R5 = "R5-BLOODLINE"

# === DETECCIÓN DEL EQUIPO ACTUAL ===
HOSTNAME = socket.gethostname().upper()

if HOSTNAME == HOST_R7:
    LIBRARY_PATH = "D:/catalog/BloodlineLibrary/anime"
elif HOSTNAME == HOST_R5:
    LIBRARY_PATH = "C:/catalog/BloodlineLibrary/anime"
else:
    LIBRARY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "anime"))  # fallback

# === RUTAS DERIVADAS ===
BASE_PATH = os.path.abspath(os.path.join(LIBRARY_PATH, ".."))
LOG_DIR = os.path.join(BASE_PATH, "logs")
LOG_MAESTRO_PATH = os.path.join(BASE_PATH, "progress_master.json")
GLOBAL_FALTANTES_CSV = os.path.join(BASE_PATH, "faltantes_globales.csv")

# === CONFIGURACIÓN DE RED ===
BASE_URL = "https://jkanime.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# === PAUSAS ENTRE ACCIONES ===
FAST_SLEEP = 0.5

def SAFE_SLEEP():
    import random
    return random.uniform(0.5, 2.5)


