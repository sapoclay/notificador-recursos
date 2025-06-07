import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import threading
import time
import pystray
from PIL import Image, ImageDraw
from plyer import notification
from ventana_alertas import VentanaAlertas
from ventana_todos_procesos import VentanaTodosProcesos

# Umbrales por defecto
DEFAULT_CPU = 50
DEFAULT_MEM = 500  # MB

class MonitorRecursosApp:
    def __init__(self, root):
        self.root = root
        self.set_taskbar_icon()
        self.root.title("¿Quién se come los recursos?")
        self.cpu_threshold = tk.IntVar(value=DEFAULT_CPU)
        self.mem_threshold = tk.IntVar(value=DEFAULT_MEM)
        self.processes = []
        self.setup_menu()  # <-- Añadir menú superior
        self.setup_ui()
        self.running = True
        self.update_thread = threading.Thread(target=self.update_processes, daemon=True)
        self.update_thread.start()
        self.icon_thread = threading.Thread(target=self.init_tray_icon, daemon=True)
        self.icon_thread.start()
        self.last_alerted = set()  # Para evitar notificaciones duplicadas

    def set_taskbar_icon(self):
        # Cambia el icono de la ventana principal por el de la rana
        import os
        icon_path = os.path.join(os.path.dirname(__file__), 'img', 'vitamina.png')
        try:
            if os.name == 'nt':
                from PIL import Image
                ico_path = os.path.join(os.path.dirname(__file__), 'img', 'vitamina.ico')
                if not os.path.exists(ico_path):
                    img = Image.open(icon_path)
                    img.save(ico_path, format='ICO', sizes=[(64,64), (32,32), (16,16)])
                self.root.iconbitmap(ico_path)
            else:
                # En Linux/Mac, usa iconphoto con formato PNG
                from tkinter import PhotoImage
                self.root.iconphoto(True, PhotoImage(file=icon_path))
        except Exception as e:
            print(f"No se pudo establecer el icono de la barra de tareas: {e}")

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Salir", command=self.exit_app)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        self.root.config(menu=menubar)

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña de procesos en alerta
        frame_alerta = ttk.Frame(notebook, padding=0)
        notebook.add(frame_alerta, text="Procesos en alerta")
        self.ventana_alertas = VentanaAlertas(
            frame_alerta,
            self.cpu_threshold,
            self.mem_threshold,
            self.cerrar_proceso,
            self.reiniciar_proceso,
            self.pausar_proceso
        )
        self.ventana_alertas.frame.pack(fill=tk.BOTH, expand=True)
        self.tree = self.ventana_alertas.tree

        # Pestaña de todos los procesos
        frame_todos = ttk.Frame(notebook, padding=0)
        notebook.add(frame_todos, text="Todos los procesos")
        self.ventana_todos = VentanaTodosProcesos(frame_todos)
        self.ventana_todos.frame.pack(fill=tk.BOTH, expand=True)
        # Llama a la actualización periódica de la lista de procesos
        self.ventana_todos.update_all_processes()
        # El menú contextual y refresco ya están gestionados dentro de VentanaTodosProcesos
        # No es necesario referenciar self.tree_all ni crear menú aquí

    def update_processes(self):
        while self.running:
            cpu_max = self.cpu_threshold.get()
            mem_max = self.mem_threshold.get() * 1024 * 1024
            procesos_alerta = []
            nuevos_alertados = set()
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    cpu = proc.info['cpu_percent']
                    mem = proc.info['memory_info'].rss
                    # Filtrar System Idle Process y valores de CPU anómalos
                    if proc.info['name'] and proc.info['name'].lower() in ['system idle process', 'idle']:
                        continue
                    if cpu < 0 or cpu > 100:
                        continue
                    if cpu > cpu_max or mem > mem_max:
                        procesos_alerta.append((proc.info['pid'], proc.info['name'], cpu, mem // (1024*1024)))
                        nuevos_alertados.add(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue
            self.processes = procesos_alerta
            # Notificar solo si hay nuevos procesos en alerta
            nuevos = nuevos_alertados - self.last_alerted
            if nuevos:
                self.show_notification(len(nuevos))
            self.last_alerted = nuevos_alertados
            self.root.after(0, self.refresh_tree)
            time.sleep(3)

    def show_notification(self, n):
        notification.notify(
            title="Los recursos se los comen",
            message=f"{n} proceso(s) superan los límites de recursos.",
            timeout=5
        )

    def create_image(self):
        # Carga el icono de la rana desde img/vitamina.png
        import os
        icon_path = os.path.join(os.path.dirname(__file__), 'img', 'vitamina.png')
        img = Image.open(icon_path)
        img = img.resize((64, 64), Image.LANCZOS)
        return img

    def on_tray_click(self, icon=None):
        # Callback directo para clic izquierdo en el icono
        self.root.after(0, self.restore_window)

    def on_tray_show(self, icon, item=None):
        # Siempre restaurar la ventana en el hilo principal de Tkinter
        self.root.after(0, self.restore_window)

    def on_tray_exit(self, icon, item):
        self.running = False
        icon.stop()
        self.root.after(0, self.root.destroy)

    def init_tray_icon(self):
        try:
            image = self.create_image()
            menu = pystray.Menu(
                pystray.MenuItem('Mostrar ventana', self.on_tray_show, default=True),
                pystray.MenuItem('Salir', self.on_tray_exit)
            )
            
            # Crear el icono de la bandeja
            self.tray_icon = pystray.Icon("MonitorRecursos", image, "Monitor de Recursos", menu)
            self.tray_icon.run()
        except Exception as e:
            print(f"Error creando icono de bandeja: {e}")

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for pid, nombre, cpu, mem in self.processes:
            self.tree.insert('', tk.END, values=(pid, nombre, cpu, mem))

    def get_selected_pid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un proceso.")
            return None
        pid = self.tree.item(sel[0])['values'][0]
        return pid

    def cerrar_proceso(self):
        pid = self.get_selected_pid()
        if pid is None:
            return
        try:
            p = psutil.Process(pid)
            p.terminate()
            messagebox.showinfo("Éxito", f"Proceso {pid} terminado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reiniciar_proceso(self):
        pid = self.get_selected_pid()
        if pid is None:
            return
        try:
            p = psutil.Process(pid)
            exe = p.exe()
            args = p.cmdline()
            p.terminate()
            p.wait(timeout=3)
            psutil.Popen([exe] + args[1:])
            messagebox.showinfo("Éxito", f"Proceso {pid} reiniciado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pausar_proceso(self):
        pid = self.get_selected_pid()
        if pid is None:
            return
        try:
            p = psutil.Process(pid)
            if p.status() == psutil.STATUS_STOPPED:
                p.resume()
                messagebox.showinfo("Proceso", f"Proceso {pid} reanudado.")
            else:
                p.suspend()
                messagebox.showinfo("Proceso", f"Proceso {pid} pausado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_close(self):
        # En vez de ocultar, minimiza a la barra de tareas y bandeja
        self.root.iconify()
        self.root.withdraw()  # Oculta la ventana, pero deja el icono en bandeja
        self.root.after(100, self.ensure_taskbar_icon)

    def ensure_taskbar_icon(self):
        # Vuelve a mostrar el icono en la barra de tareas si está minimizado
        if self.root.state() == 'iconic':
            self.root.deiconify()
            self.root.iconify()

    def restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.state('normal')

    def exit_app(self):
        self.running = False
        try:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.stop()
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorRecursosApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
