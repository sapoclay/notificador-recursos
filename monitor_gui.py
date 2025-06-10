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
from ventana_about import mostrar_about

# Importar nuevos sistemas
from configuracion import ConfiguracionManager, cargar_config, guardar_config
from temas import GestorTemas, aplicar_tema_desde_config
from sistema_logs import SistemaLogs

# Umbrales por defecto (se cargarán desde configuración)
DEFAULT_CPU = 50
DEFAULT_MEM = 500  # MB

class MonitorRecursosApp:
    def __init__(self, root):
        self.root = root
        
        # Cargar configuración al inicio
        self.configuracion, self.config_manager = cargar_config()
        
        # Inicializar sistema de logs
        self.logs = SistemaLogs(self.configuracion)
        self.logs.log_info("Iniciando aplicación Monitor de Recursos")
        
        # Inicializar gestor de temas
        self.gestor_temas = GestorTemas()
        
        # Configurar ventana principal
        self.set_taskbar_icon()
        self.root.title("¿Quién se come los recursos?")
        
        # Cargar umbrales desde configuración
        config_umbrales = self.configuracion.get('umbrales', {})
        self.cpu_threshold = tk.IntVar(value=config_umbrales.get('cpu_porcentaje', DEFAULT_CPU))
        self.mem_threshold = tk.IntVar(value=config_umbrales.get('memoria_mb', DEFAULT_MEM))
        
        # Aplicar configuración de ventana
        config_interfaz = self.configuracion.get('interfaz', {})
        ancho = config_interfaz.get('ventana_ancho', 800)
        alto = config_interfaz.get('ventana_alto', 600)
        self.root.geometry(f"{ancho}x{alto}")
        
        # Variables de control
        self.processes = []
        
        # Configurar interfaz
        self.setup_menu()
        self.setup_ui()
        
        # Aplicar tema después de crear la interfaz
        colores, _ = aplicar_tema_desde_config(self.root, self.configuracion)
        self.colores_tema = colores
        
        # Configurar monitoreo
        self.running = True
        config_monitoreo = self.configuracion.get('monitoreo', {})
        self.intervalo_actualizacion = config_monitoreo.get('intervalo_actualizacion', 3)
        self.auto_minimizar = config_monitoreo.get('auto_minimizar_bandeja', True)
        
        # Iniciar hilos
        self.update_thread = threading.Thread(target=self.update_processes, daemon=True)
        self.update_thread.start()
        self.icon_thread = threading.Thread(target=self.init_tray_icon, daemon=True)
        self.icon_thread.start()
        
        # Control de alertas
        self.last_alerted = set()
        self.ultimo_proceso_problematico = None  # Información del último proceso que causó alerta
        
        # Configurar eventos de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Log de inicio completado
        self.logs.log_info("Aplicación iniciada correctamente")

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
        
        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Salir", command=self.exit_app)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        
        # Menú Configuración (nuevo)
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Preferencias...", command=self.abrir_configuracion)
        config_menu.add_command(label="Temas...", command=self.abrir_configuracion_tema)
        config_menu.add_separator()
        config_menu.add_command(label="Exportar configuración...", command=self.exportar_configuracion)
        config_menu.add_command(label="Importar configuración...", command=self.importar_configuracion)
        config_menu.add_separator()
        config_menu.add_command(label="Resetear a valores por defecto", command=self.resetear_configuracion)
        menubar.add_cascade(label="Configuración", menu=config_menu)
        
        # Menú Herramientas (nuevo)
        herramientas_menu = tk.Menu(menubar, tearoff=0)
        herramientas_menu.add_command(label="Ver Logs...", command=self.abrir_visor_logs)
        herramientas_menu.add_command(label="Limpiar Logs antiguos", command=self.limpiar_logs_antiguos)
        menubar.add_cascade(label="Herramientas", menu=herramientas_menu)
        
        # Menú Opciones (modificado)
        opciones_menu = tk.Menu(menubar, tearoff=0)
        opciones_menu.add_command(label="About...", command=self.show_about)
        menubar.add_cascade(label="Opciones", menu=opciones_menu)
        
        self.root.config(menu=menubar)

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña de procesos en alerta
        frame_alerta = ttk.Frame(self.notebook, padding=0)
        self.notebook.add(frame_alerta, text="Procesos en alerta")
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
        frame_todos = ttk.Frame(self.notebook, padding=0)
        self.notebook.add(frame_todos, text="Todos los procesos")
        self.ventana_todos = VentanaTodosProcesos(frame_todos)
        self.ventana_todos.frame.pack(fill=tk.BOTH, expand=True)
        # Llama a la actualización periódica de la lista de procesos
        self.ventana_todos.update_all_processes()
        # El menú contextual y refresco ya están gestionados dentro de VentanaTodosProcesos
        # No es necesario referenciar self.tree_all ni crear menú aquí

    def update_processes(self):
        """Hilo principal de monitoreo de procesos"""
        self.logs.log_info("Iniciando monitoreo de procesos")
        
        while self.running:
            try:
                cpu_max = self.cpu_threshold.get()
                mem_max = self.mem_threshold.get() * 1024 * 1024
                procesos_alerta = []
                nuevos_alertados = set()
                
                # Obtener lista de procesos excluidos de la configuración
                procesos_excluidos = self.configuracion.get('monitoreo', {}).get('procesos_excluidos', 
                                                          ['System Idle Process', 'kernel_task'])
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                    try:
                        cpu = proc.info['cpu_percent']
                        mem = proc.info['memory_info'].rss
                        nombre = proc.info['name'] or 'Proceso sin nombre'
                        
                        # Filtrar procesos excluidos y valores de CPU anómalos
                        if any(nombre.lower() == excluido.lower() for excluido in procesos_excluidos):
                            continue
                        if cpu < 0 or cpu > 100:
                            continue
                        
                        # Verificar si supera umbrales
                        if cpu > cpu_max or mem > mem_max:
                            procesos_alerta.append((proc.info['pid'], nombre, cpu, mem // (1024*1024)))
                            nuevos_alertados.add(proc.info['pid'])
                            
                            # Almacenar información del último proceso problemático
                            self.ultimo_proceso_problematico = {
                                'pid': proc.info['pid'],
                                'nombre': nombre,
                                'cpu': cpu,
                                'memoria': mem // (1024*1024)
                            }
                            
                            # Log de alerta para procesos nuevos
                            if proc.info['pid'] not in self.last_alerted:
                                self.logs.log_alerta_proceso(nombre, proc.info['pid'], cpu, mem // (1024*1024))
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError) as e:
                        # Log solo errores importantes, no accesos denegados rutinarios
                        if not isinstance(e, psutil.AccessDenied):
                            self.logs.log_debug(f"Error accediendo a proceso: {e}")
                        continue
                
                self.processes = procesos_alerta
                
                # Notificar solo si hay nuevos procesos en alerta y las notificaciones están habilitadas
                nuevos = nuevos_alertados - self.last_alerted
                if nuevos and self.configuracion.get('monitoreo', {}).get('mostrar_notificaciones', True):
                    self.show_notification(len(nuevos), self.ultimo_proceso_problematico)
                    self.logs.log_info(f"Notificación mostrada: {len(nuevos)} nuevos procesos en alerta")
                
                self.last_alerted = nuevos_alertados
                self.root.after(0, self.refresh_tree)
                
                # Usar intervalo de actualización de la configuración
                time.sleep(self.intervalo_actualizacion)
                
            except Exception as e:
                self.logs.log_error(f"Error en monitoreo de procesos: {e}")
                time.sleep(5)  # Esperar más tiempo en caso de error
        
        self.logs.log_info("Monitoreo de procesos detenido")

    def show_notification(self, n, proceso_info=None):
        """Muestra notificación del sistema con información específica del proceso"""
        try:
            if proceso_info:
                mensaje = f"Proceso '{proceso_info['nombre']}' (PID: {proceso_info['pid']}) supera los límites.\nCPU: {proceso_info['cpu']:.1f}% | Memoria: {proceso_info['memoria']} MB\n\nHaz clic para ver detalles."
                title = "⚠️ Proceso consumiendo recursos"
            else:
                mensaje = f"{n} proceso(s) superan los límites de recursos.\n\nHaz clic para ver detalles."
                title = "⚠️ Procesos consumiendo recursos"
            
            # Usar plyer notification con timeout configurado
            notification.notify(
                title=title,
                message=mensaje,
                timeout=self.configuracion.get('alertas', {}).get('duracion_notificacion', 5000) // 1000,
                app_name="Monitor de Recursos"
            )
            
            # Nota: plyer no soporta callbacks de clic directamente en todas las plataformas
            # Como alternativa, podemos mostrar el proceso cuando se restaure la ventana
            
        except Exception as e:
            self.logs.log_error(f"Error mostrando notificación: {e}")

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
        # Detener actualizaciones de la ventana de todos los procesos
        if hasattr(self, 'ventana_todos'):
            self.ventana_todos.stop_updates()
        
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
        
        # Si hay un proceso problemático reciente, seleccionarlo automáticamente
        if self.ultimo_proceso_problematico:
            self.root.after(500, lambda: self.abrir_y_seleccionar_proceso(self.ultimo_proceso_problematico['pid']))

    def cambiar_a_todos_procesos(self):
        """Cambia programáticamente a la pestaña 'Todos los procesos'"""
        try:
            # La pestaña "Todos los procesos" es la segunda (índice 1)
            self.notebook.select(1)
            self.logs.log_info("Cambiado a pestaña 'Todos los procesos'")
        except Exception as e:
            self.logs.log_error(f"Error cambiando a pestaña de todos los procesos: {e}")

    def cambiar_a_procesos_alerta(self):
        """Cambia programáticamente a la pestaña 'Procesos en alerta'"""
        try:
            # La pestaña "Procesos en alerta" es la primera (índice 0)
            self.notebook.select(0)
            self.logs.log_info("Cambiado a pestaña 'Procesos en alerta'")
        except Exception as e:
            self.logs.log_error(f"Error cambiando a pestaña de procesos en alerta: {e}")

    def exit_app(self):
        """Cierra completamente la aplicación guardando configuración"""
        self.logs.log_info("Cerrando aplicación...")
        
        # Guardar configuración actual
        self.guardar_configuracion_actual()
        
        # Detener actualizaciones de la ventana de todos los procesos
        if hasattr(self, 'ventana_todos'):
            self.ventana_todos.stop_updates()
        
        self.running = False
        try:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.stop()
        except Exception as e:
            self.logs.log_error(f"Error cerrando icono de bandeja: {e}")
        
        self.logs.log_info("Aplicación cerrada correctamente")
        self.root.destroy()

    def on_closing(self):
        """Maneja el evento de cerrar ventana"""
        config_monitoreo = self.configuracion.get('monitoreo', {})
        if config_monitoreo.get('auto_minimizar_bandeja', True):
            # Minimizar a bandeja
            self.root.withdraw()
            self.logs.log_info("Aplicación minimizada a bandeja del sistema")
        else:
            # Cerrar completamente
            self.exit_app()

    def guardar_configuracion_actual(self):
        """Guarda la configuración actual"""
        try:
            # Actualizar umbrales
            self.configuracion['umbrales']['cpu_porcentaje'] = self.cpu_threshold.get()
            self.configuracion['umbrales']['memoria_mb'] = self.mem_threshold.get()
            
            # Actualizar tamaño de ventana
            geometry = self.root.geometry()
            if 'x' in geometry:
                dims = geometry.split('+')[0]  # Obtener solo ancho y alto
                ancho, alto = dims.split('x')
                self.configuracion['interfaz']['ventana_ancho'] = int(ancho)
                self.configuracion['interfaz']['ventana_alto'] = int(alto)
            
            # Guardar configuración
            if self.config_manager.guardar_configuracion(self.configuracion):
                self.logs.log_info("Configuración guardada exitosamente")
            else:
                self.logs.log_error("Error guardando configuración")
                
        except Exception as e:
            self.logs.log_error(f"Error guardando configuración: {e}")

    # Métodos para configuración
    def abrir_configuracion(self):
        """Abre ventana de configuración general"""
        self.logs.log_info("Abriendo configuración general")
        self._crear_ventana_configuracion()

    def abrir_configuracion_tema(self):
        """Abre ventana de configuración de tema"""
        self.logs.log_info("Abriendo configuración de tema")
        self.gestor_temas.crear_ventana_configuracion_tema(
            self.root, self.configuracion, self._guardar_config_callback
        )

    def exportar_configuracion(self):
        """Exporta configuración a archivo"""
        from tkinter import filedialog
        archivo = filedialog.asksaveasfilename(
            title="Exportar Configuración",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            if self.config_manager.exportar_configuracion(archivo):
                messagebox.showinfo("Éxito", f"Configuración exportada a:\n{archivo}")
                self.logs.log_info(f"Configuración exportada a: {archivo}")
            else:
                messagebox.showerror("Error", "Error al exportar la configuración")

    def importar_configuracion(self):
        """Importa configuración desde archivo"""
        from tkinter import filedialog
        archivo = filedialog.askopenfilename(
            title="Importar Configuración",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            if messagebox.askyesno("Confirmar", "¿Desea importar la configuración?\nEsto sobrescribirá la configuración actual."):
                if self.config_manager.importar_configuracion(archivo):
                    messagebox.showinfo("Éxito", "Configuración importada correctamente.\nReinicie la aplicación para ver los cambios.")
                    self.logs.log_info(f"Configuración importada desde: {archivo}")
                else:
                    messagebox.showerror("Error", "Error al importar la configuración")

    def resetear_configuracion(self):
        """Resetea configuración a valores por defecto"""
        if messagebox.askyesno("Confirmar", "¿Desea resetear la configuración a valores por defecto?\nEsto no se puede deshacer."):
            if self.config_manager.resetear_configuracion():
                messagebox.showinfo("Éxito", "Configuración reseteada correctamente.\nReinicie la aplicación para ver los cambios.")
                self.logs.log_info("Configuración reseteada a valores por defecto")
            else:
                messagebox.showerror("Error", "Error al resetear la configuración")

    def abrir_visor_logs(self):
        """Abre el visor de logs"""
        self.logs.log_info("Abriendo visor de logs")
        self.logs.crear_ventana_logs(self.root)

    def limpiar_logs_antiguos(self):
        """Limpia logs antiguos"""
        if messagebox.askyesno("Confirmar", f"¿Desea limpiar logs antiguos (más de {self.logs.dias_retencion} días)?"):
            self.logs.limpiar_logs_antiguos()
            messagebox.showinfo("Éxito", "Logs antiguos limpiados correctamente")

    def _guardar_config_callback(self, configuracion):
        """Callback para guardar configuración desde ventanas de configuración"""
        self.configuracion = configuracion
        return self.config_manager.guardar_configuracion(configuracion)

    def _crear_ventana_configuracion(self):
        """Crea ventana de configuración general"""
        ventana_config = tk.Toplevel(self.root)
        ventana_config.title("Configuración - Monitor de Recursos")
        ventana_config.geometry("500x600")
        ventana_config.resizable(True, True)
        ventana_config.transient(self.root)
        ventana_config.grab_set()

        # Frame principal con scroll
        canvas = tk.Canvas(ventana_config, highlightthickness=0)
        scrollbar = ttk.Scrollbar(ventana_config, orient="vertical", command=canvas.yview)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        ventana_config.grid_rowconfigure(0, weight=1)
        ventana_config.grid_columnconfigure(0, weight=1)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Configurar el frame para que se expanda
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Función para expandir el contenido al ancho de la ventana
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ajustar el ancho del frame interno al ancho del canvas
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)

        # Configuración de umbrales
        frame_umbrales = ttk.LabelFrame(scrollable_frame, text="Umbrales de Alertas", padding=10)
        frame_umbrales.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        frame_umbrales.columnconfigure(1, weight=1)

        ttk.Label(frame_umbrales, text="CPU máximo (%):").grid(row=0, column=0, sticky=tk.W, pady=2)
        cpu_var = tk.IntVar(value=self.configuracion.get('umbrales', {}).get('cpu_porcentaje', 50))
        ttk.Scale(frame_umbrales, from_=10, to=100, variable=cpu_var, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Label(frame_umbrales, textvariable=cpu_var).grid(row=0, column=2)
        
        ttk.Label(frame_umbrales, text="Memoria máxima (MB):").grid(row=1, column=0, sticky=tk.W, pady=2)
        mem_var = tk.IntVar(value=self.configuracion.get('umbrales', {}).get('memoria_mb', 500))
        ttk.Scale(frame_umbrales, from_=100, to=2000, variable=mem_var, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(frame_umbrales, textvariable=mem_var).grid(row=1, column=2)
        
        # Configuración de monitoreo
        frame_monitoreo = ttk.LabelFrame(scrollable_frame, text="Configuración de Monitoreo", padding=10)
        frame_monitoreo.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        frame_monitoreo.columnconfigure(1, weight=1)

        ttk.Label(frame_monitoreo, text="Intervalo de actualización (seg):").grid(row=0, column=0, sticky=tk.W, pady=2)
        intervalo_var = tk.IntVar(value=self.configuracion.get('monitoreo', {}).get('intervalo_actualizacion', 3))
        ttk.Scale(frame_monitoreo, from_=1, to=10, variable=intervalo_var, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Label(frame_monitoreo, textvariable=intervalo_var).grid(row=0, column=2)
        
        notif_var = tk.BooleanVar(value=self.configuracion.get('monitoreo', {}).get('mostrar_notificaciones', True))
        ttk.Checkbutton(frame_monitoreo, text="Mostrar notificaciones", variable=notif_var).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        minimizar_var = tk.BooleanVar(value=self.configuracion.get('monitoreo', {}).get('auto_minimizar_bandeja', True))
        ttk.Checkbutton(frame_monitoreo, text="Auto-minimizar a bandeja al cerrar", variable=minimizar_var).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # Configuración de logs
        frame_logs = ttk.LabelFrame(scrollable_frame, text="Configuración de Logs", padding=10)
        frame_logs.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        frame_logs.columnconfigure(1, weight=1)

        logs_habilitados_var = tk.BooleanVar(value=self.configuracion.get('logs', {}).get('habilitar_logs', True))
        ttk.Checkbutton(frame_logs, text="Habilitar logs", variable=logs_habilitados_var).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        ttk.Label(frame_logs, text="Nivel de log:").grid(row=1, column=0, sticky=tk.W, pady=2)
        nivel_var = tk.StringVar(value=self.configuracion.get('logs', {}).get('nivel_log', 'INFO'))
        ttk.Combobox(frame_logs, textvariable=nivel_var, values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], state="readonly").grid(row=1, column=1, sticky=tk.EW, padx=5)
        
        ttk.Label(frame_logs, text="Días de retención:").grid(row=2, column=0, sticky=tk.W, pady=2)
        retencion_var = tk.IntVar(value=self.configuracion.get('logs', {}).get('dias_retencion', 30))
        ttk.Scale(frame_logs, from_=7, to=90, variable=retencion_var, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=tk.EW, padx=5)
        ttk.Label(frame_logs, textvariable=retencion_var).grid(row=2, column=2)
        
        # Botones
        frame_botones = ttk.Frame(scrollable_frame)
        frame_botones.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        def guardar_configuracion():
            # Actualizar configuración
            self.configuracion['umbrales']['cpu_porcentaje'] = cpu_var.get()
            self.configuracion['umbrales']['memoria_mb'] = mem_var.get()
            self.configuracion['monitoreo']['intervalo_actualizacion'] = intervalo_var.get()
            self.configuracion['monitoreo']['mostrar_notificaciones'] = notif_var.get()
            self.configuracion['monitoreo']['auto_minimizar_bandeja'] = minimizar_var.get()
            self.configuracion['logs']['habilitar_logs'] = logs_habilitados_var.get()
            self.configuracion['logs']['nivel_log'] = nivel_var.get()
            self.configuracion['logs']['dias_retencion'] = retencion_var.get()
            
            # Guardar y aplicar cambios
            if self._guardar_config_callback(self.configuracion):
                # Aplicar cambios inmediatamente
                self.cpu_threshold.set(cpu_var.get())
                self.mem_threshold.set(mem_var.get())
                self.intervalo_actualizacion = intervalo_var.get()
                
                # Reconfigurar sistema de logs
                self.logs.configuracion = self.configuracion
                self.logs.log_config = self.configuracion.get('logs', {})
                self.logs.nivel_log = nivel_var.get()
                self.logs.dias_retencion = retencion_var.get()
                self.logs.habilitar_logs = logs_habilitados_var.get()
                self.logs.configurar_logger()
                
                self.logs.log_info("Configuración actualizada desde ventana de preferencias")
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                ventana_config.destroy()
            else:
                messagebox.showerror("Error", "Error al guardar la configuración")
        
        ttk.Button(frame_botones, text="Guardar", command=guardar_configuracion).grid(row=0, column=1, padx=(5, 0), sticky=tk.E)
        ttk.Button(frame_botones, text="Cancelar", command=ventana_config.destroy).grid(row=0, column=0, sticky=tk.W)
        
        # Configurar canvas y scrollbar para expansión
        scrollable_frame.columnconfigure(0, weight=1)
        
        # Hacer que los frames internos se expandan con la ventana
        for i in range(4):  # 4 filas: umbrales, monitoreo, logs, botones
            scrollable_frame.grid_rowconfigure(i, weight=0)
        scrollable_frame.grid_rowconfigure(3, weight=1)  # Los botones al final

    def show_about(self):
        """Muestra la ventana About"""
        mostrar_about(self.root)

    def abrir_y_seleccionar_proceso(self, pid):
        """Abre la aplicación y selecciona un proceso específico por PID"""
        # Restaurar ventana si está minimizada
        if self.root.state() == 'withdrawn' or self.root.state() == 'iconic':
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.root.state('normal')
        
        # Cambiar a la pestaña de todos los procesos
        self.cambiar_a_todos_procesos()
        
        # Esperar un momento para que la UI se actualice, luego seleccionar el proceso
        self.root.after(200, lambda: self._seleccionar_proceso_delayed(pid))

    def _seleccionar_proceso_delayed(self, pid):
        """Método auxiliar para seleccionar proceso con delay"""
        exito = self.ventana_todos.seleccionar_proceso_por_pid(pid)
        if exito:
            self.logs.log_info(f"Proceso PID {pid} seleccionado automáticamente")
        else:
            self.logs.log_warning(f"No se pudo seleccionar el proceso PID {pid} - puede que ya no exista")


if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorRecursosApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
