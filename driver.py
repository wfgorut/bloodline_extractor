import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def crear_driver_configurado(visible=True):
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--mute-audio')
    options.add_argument('--disable-logging')
    options.add_argument('--log-level=3')
    options.page_load_strategy = "normal"

    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.popups": 2,
        "profile.default_content_setting_values.javascript": 1
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(
    driver_executable_path="C:\\WebDrivers\\chrome\\136\\chromedriver.exe",
    browser_executable_path="C:\\PortableApps\\Chrome136\\chrome.exe",
    options=options
    )
    driver.set_page_load_timeout(45)
    return driver

    if not visible:
        options.add_argument("--window-position=4000,0")

    driver = uc.Chrome(
        options=options,
        driver_executable_path="C:/WebDrivers/chrome/136/chromedriver.exe"
    )
    return driver

def obtener_html_renderizado(url, visible=False):
    driver = crear_driver_configurado(visible)
    try:
        driver.get("https://www.google.com")
        time.sleep(2.5)  # evitar crash inicial sin sesión
        driver.get(url)
        time.sleep(3.5)
        html = driver.page_source
        return html
    finally:
        try:
            driver.quit()
        except Exception:
            pass

