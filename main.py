import os
import platform
import psutil
import time
from plyer import notification

# Configuración de umbrales
PROCESO_OBJETIVO = "chrome.exe"  # Cambiar según el proceso a monitorear
UMBRAL_CPU = 50  # Máximo % de CPU permitido
UMBRAL_RAM = 500  # Máximo MB de RAM permitidos
INTERVALO = 5  # Intervalo de monitoreo en segundos

def detectar_sistema():
    """Detecta el sistema operativo y el entorno de escritorio."""
    sistema = platform.system()

    if sistema == "Windows":
        return "Windows"
    elif sistema == "Darwin":
        return "MacOS"
    elif sistema == "Linux":
        escritorio = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION")
        return escritorio if escritorio else "Linux (desconocido)"
    return "Desconocido"

def enviar_notificacion(mensaje):
    """Envía una notificación según el sistema operativo y escritorio."""
    sistema = detectar_sistema()

    if sistema == "Windows":
        notification.notify(
            title="⚠️ Alerta de Consumo",
            message=mensaje,
            timeout=5
        )
    elif sistema == "MacOS":
        os.system(f'''osascript -e 'display notification "{mensaje}" with title "⚠️ Alerta de Consumo"' ''')
    elif "GNOME" in sistema or "KDE" in sistema:
        os.system(f'notify-send "⚠️ Alerta de Consumo" "{mensaje}"')
    elif "XFCE" in sistema or "LXDE" in sistema or "MATE" in sistema:
        os.system(f'notify-send "⚠️ Alerta de Consumo" "{mensaje}"')
    elif "i3" in sistema or "sway" in sistema:
        os.system(f'dunstify "⚠️ Alerta de Consumo" "{mensaje}"')
    else:
        print(f"⚠️ Notificación no soportada en {sistema}")

def obtener_proceso(nombre):
    """Busca un proceso por nombre y devuelve el objeto psutil.Process."""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() == nombre.lower():
            return psutil.Process(proc.info['pid'])
    return None

def verificar_recursos():
    """Monitorea el proceso y envía una notificación si excede los límites."""
    proceso = obtener_proceso(PROCESO_OBJETIVO)
    if proceso:
        uso_cpu = proceso.cpu_percent(interval=1)
        uso_ram = proceso.memory_info().rss / (1024 * 1024)  # Convertir a MB

        if uso_cpu > UMBRAL_CPU or uso_ram > UMBRAL_RAM:
            mensaje = f"{PROCESO_OBJETIVO} usa {uso_cpu:.2f}% CPU y {uso_ram:.2f} MB RAM."
            enviar_notificacion(mensaje)
    else:
        print(f"Proceso '{PROCESO_OBJETIVO}' no encontrado.")

# Bucle de monitoreo
while True:
    verificar_recursos()
    time.sleep(INTERVALO)
