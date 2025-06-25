# === [ HOSTNAMES REGISTRADOS DEL SISTEMA BLOODLINE ] ===
HOST_R7 = "R7-BLOODLINE"
HOST_R5 = "R5-BLOODLINE"

# === [ ESTADOS DE JKANIME ] ===
ESTADOS_VALIDOS = ["emision", "finalizados", "estrenos"]
ORDEN_ASC = "asc"
ORDEN_DESC = "desc"

# === [ PROVEEDORES DE LINKS (ORDEN DE PRIORIDAD) ] ===
ORIGEN_MEGA = "mega"
ORIGEN_MEDIAFIRE = "mediafire"
ORIGEN_MIRROR = "mirror"
PRIORIDAD_PROVEEDORES = [ORIGEN_MEGA, ORIGEN_MEDIAFIRE, ORIGEN_MIRROR]

# === [ CAMPOS ESTÁNDAR DEL LOG MAESTRO ] ===
CAMPO_TIMESTAMP = "timestamp"
CAMPO_LINK = "link"
CAMPO_ORIGEN = "origen"
CAMPO_COMPLETADO = "completado"
CAMPO_METADATA = "metadata"
CAMPO_EPISODIOS_VISTOS = "episodios_vistos"
CAMPO_TOTAL_ESPERADO = "total_esperado"
CAMPO_FALTANTES = "faltantes"
CAMPO_PROXY_VALIDADO = "proxy_validado"
CAMPO_CSV_GENERADO = "csv_generado"
CAMPO_FUENTE = "fuente"
CAMPO_SLUG = "slug"

# === [ NOMBRES DE ARCHIVOS GENERADOS ] ===
NOMBRE_LOG_MAESTRO = "log_maestro.json"
NOMBRE_CSV_MEGA = "mega_links_{slug}.csv"
NOMBRE_CSV_MEDIAFIRE = "mediafire_links_{slug}.csv"
NOMBRE_CSV_MIRRORS = "mirrors_links_{slug}.csv"
NOMBRE_CSV_METADATA = "metadata_{slug}.csv"
NOMBRE_IMAGEN = "{slug}.jpg"

# === [ CARPETAS INTERNAS DEL EXTRACTOR ] ===
FOLDER_COMPLETOS = "completos"
FOLDER_FALTANTES = "faltantes"
FOLDER_TEMP = "temp"
FOLDER_LOGS = "logs"

# === [ TIPOS DE CONTENIDO VÁLIDOS ] ===
TIPO_ANIME = "anime"
TIPO_MANGA = "manga"
TIPO_HENTAI = "hentai"
TIPOS_VALIDOS = [TIPO_ANIME, TIPO_MANGA, TIPO_HENTAI]

# === [ DELAYS Y TIMINGS ] ===
DELAY_CORTO = 1.5
DELAY_LARGO = 3.0
DELAY_VARIABILIDAD = 0.75
SELENIUM_TIMEOUT = 12

# === [ VALIDADORES Y FORMATOS ] ===
SLUG_VALIDO_REGEX = r"^[a-z0-9\-]+$"
EXTENSIONES_VALIDAS_VIDEO = [".mp4", ".mkv", ".webm"]

# === [ COLORES ANSI PARA CONSOLA ] ===
COLOR_RESET = "\033[0m"
COLOR_VERDE = "\033[92m"
COLOR_ROJO = "\033[91m"
COLOR_AMARILLO = "\033[93m"
COLOR_AZUL = "\033[94m"
COLOR_CIAN = "\033[96m"
COLOR_MAGENTA = "\033[95m"

# === [ MENSAJES DE ERROR ESTÁNDAR ] ===
ERROR_TIMEOUT = "[TIMEOUT] Se alcanzo el tiempo limite esperando boton de descarga"
ERROR_NO_LINK = "[ERROR] No se pudo resolver un link de descarga valido"
ERROR_PAGINA_VACIA = "[EMPTY] Pagina sin resultados o sin animes listados"
ERROR_NO_SCRIPT = "[ERROR] No se encontro el bloque <script> esperado con 'animes ='"

# === [ ESTADOS INTERNOS DE PROCESAMIENTO ] ===
ESTADO_RESUELTO = "resuelto"
ESTADO_PENDIENTE = "pendiente"
ESTADO_SIN_LINKS = "sin_links"

# === [ IDENTIFICADORES DE DRIVER Y NAVEGADOR ] ===
BROWSER_CHROME = "chrome"
BROWSER_FIREFOX = "firefox"
MODO_HEADLESS = "headless"
NOMBRE_PERFIL_TEMP = "temp_driver"

# === [ HEADERS ESTÁNDAR USADOS EN REQUESTS ] ===
HEADER_USER_AGENT = "User-Agent"
HEADER_REFERER = "Referer"

# === [ SELECTORES Y CLASES HTML COMUNES ] ===
ID_BOTON_MEGA = "dwld"
CLASS_DIV_MEGA = "download"
PATRON_SCRIPT_ANIMES = "animes ="
