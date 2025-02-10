import flet as ft
import psutil
import time
import threading
import json
from datetime import datetime
from plyer import notification
import pystray
from pystray import MenuItem as item, Icon
from PIL import Image

# Umbrales de consumo
UMBRAL_CPU = 50  # %
UMBRAL_RAM = 500  # MB

# Archivo de logs
LOG_FILE = "logs.json"

# Icono de la bandeja
ICON_PATH = "img/consumo-recursos.jpeg"

def log_event(event):
    """Registra eventos en un archivo JSON."""
    log_entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "event": event}
    try:
        with open(LOG_FILE, "r+") as file:
            data = json.load(file)
            data.append(log_entry)
            file.seek(0)
            json.dump(data, file, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(LOG_FILE, "w") as file:
            json.dump([log_entry], file, indent=4)

def show_notification(title, message):
    """Muestra una notificación en el escritorio."""
    notification.notify(
        title=title,
        message=message,
        app_name="Monitor de Recursos",
        app_icon=ICON_PATH if ICON_PATH.endswith(".ico") else None  # Solo Windows usa .ico
    )

def create_tray_icon():
    """Crea un icono en la bandeja del sistema."""
    image = Image.open(ICON_PATH)
    menu = (item('Salir', exit_program),)
    tray_icon = Icon("Monitor de Recursos", image, menu=menu)
    tray_icon.run()

def exit_program(icon, item):
    """Cierra la aplicación desde la bandeja."""
    icon.stop()

# Interfaz gráfica con Flet
def main(page: ft.Page):
    page.title = "Monitor de Recursos"
    page.window_width = 800
    page.window_height = 600
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Elementos de la GUI
    procesos_list = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("PID")),
        ft.DataColumn(ft.Text("Nombre")),
        ft.DataColumn(ft.Text("CPU (%)")),
        ft.DataColumn(ft.Text("RAM (MB)")),
        ft.DataColumn(ft.Text("Acciones"))
    ])

    cpu_chart = ft.LineChart(data_series=[ft.LineChartData()])
    ram_chart = ft.LineChart(data_series=[ft.LineChartData()])

    def actualizar_procesos():
        while True:
            procesos_list.rows.clear()
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    cpu = proc.info['cpu_percent']
                    ram = proc.info['memory_info'].rss / (1024 * 1024)
                    boton_cerrar = ft.ElevatedButton("Cerrar", on_click=lambda e, pid=proc.info['pid']: confirmar_cierre(pid))
                    procesos_list.rows.append(ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(proc.info['pid']))),
                            ft.DataCell(ft.Text(proc.info['name'])),
                            ft.DataCell(ft.Text(f"{cpu:.2f}")),
                            ft.DataCell(ft.Text(f"{ram:.2f}")),
                            ft.DataCell(boton_cerrar)
                        ]
                    ))
                    if cpu > UMBRAL_CPU or ram > UMBRAL_RAM:
                        log_event(f"Alerta: {proc.info['name']} ({proc.info['pid']}) supera los límites.")
                        show_notification("Alerta de Consumo", f"{proc.info['name']} está usando demasiados recursos.")
                        page.snack_bar = ft.SnackBar(ft.Text(f"{proc.info['name']} usa demasiados recursos"))
                        page.snack_bar.open = True
                        page.update()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            page.update()
            time.sleep(5)

    def confirmar_cierre(pid):
        def cerrar(e):
            try:
                psutil.Process(pid).terminate()
                log_event(f"Proceso {pid} cerrado por el usuario.")
                page.dialog.open = False
                page.update()
            except Exception as ex:
                log_event(f"Error al cerrar proceso {pid}: {ex}")
                page.dialog.open = False
                page.update()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar cierre"),
            content=ft.Text(f"¿Seguro que quieres cerrar el proceso {pid}?"),
            actions=[
                ft.TextButton("Sí", on_click=cerrar),
                ft.TextButton("No", on_click=lambda e: setattr(page.dialog, "open", False))
            ]
        )
        page.dialog.open = True
        page.update()

    # Iniciar monitoreo en un hilo separado
    threading.Thread(target=actualizar_procesos, daemon=True).start()
    
    # Iniciar icono en la bandeja en un hilo separado
    threading.Thread(target=create_tray_icon, daemon=True).start()
    
    # Layout principal
    page.add(ft.Text("Monitor de Recursos", size=24), procesos_list, cpu_chart, ram_chart)
    page.update()

ft.app(target=main)