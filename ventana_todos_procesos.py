import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import platform

class VentanaTodosProcesos:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.running = True  # Flag para controlar la actualización
        self.update_job = None  # Referencia al trabajo programado
        self.is_windows = platform.system().lower() == 'windows'
        
        # Variables para el ordenamiento
        self.sort_column = None
        self.sort_reverse = False
        
        self.tree = ttk.Treeview(self.frame, columns=("pid", "nombre", "cpu", "mem"), show="headings")
        self.tree.heading("pid", text="PID", command=lambda: self.sort_by_column("pid"))
        self.tree.heading("nombre", text="Nombre", command=lambda: self.sort_by_column("nombre"))
        self.tree.heading("cpu", text="CPU (%)", command=lambda: self.sort_by_column("cpu"))
        self.tree.heading("mem", text="Memoria (MB)", command=lambda: self.sort_by_column("mem"))
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.menu = tk.Menu(self.frame, tearoff=0)
        self.menu.add_command(label="Cerrar", command=lambda: self.menu_accion_proceso('cerrar'))
        self.menu.add_command(label="Reiniciar", command=lambda: self.menu_accion_proceso('reiniciar'))
        self.menu.add_command(label="Pausar/Continuar", command=lambda: self.menu_accion_proceso('pausar'))
        
        # Configurar eventos del menú contextual - compatible con Windows y Linux
        if self.is_windows:
            # En Windows, Button-3 es clic derecho
            self.tree.bind("<Button-3>", self.mostrar_menu)
        else:
            # En Linux, tanto Button-3 como Control+Button-1 funcionan
            self.tree.bind("<Button-3>", self.mostrar_menu)
            self.tree.bind("<Control-Button-1>", self.mostrar_menu)
        
        # Iniciar actualización
        self.update_all_processes()

    def mostrar_menu(self, event):
        # Seleccionar item bajo el cursor antes de mostrar menú
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            try:
                # Mostrar menú contextual en la posición del cursor
                self.menu.tk_popup(event.x_root, event.y_root)
            except tk.TclError:
                # Error común en sistemas donde no se puede mostrar el menú
                pass
            finally:
                # Asegurar que el menú se cierre correctamente
                self.menu.grab_release()

    def update_all_processes(self):
        if not self.running:
            return
            
        for i in self.tree.get_children():
            self.tree.delete(i)
        procesos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                cpu = proc.info['cpu_percent']
                mem = proc.info['memory_info'].rss // (1024*1024)
                procesos.append((proc.info['pid'], proc.info['name'], cpu, mem))
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
        for pid, nombre, cpu, mem in procesos:
            self.tree.insert('', tk.END, values=(pid, nombre, cpu, mem))
        
        # Solo programar la siguiente actualización si seguimos ejecutándose
        if self.running:
            self.update_job = self.frame.after(5000, self.update_all_processes)
    
    def stop_updates(self):
        """Detiene las actualizaciones programadas - Multiplataforma"""
        self.running = False
        if self.update_job:
            try:
                self.frame.after_cancel(self.update_job)
                self.update_job = None
            except tk.TclError:
                # En caso de que tkinter ya esté destruido (común en Windows)
                pass

    def menu_accion_proceso(self, accion):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un proceso.")
            return
        pid = self.tree.item(sel[0])['values'][0]
        try:
            p = psutil.Process(pid)
            if accion == 'cerrar':
                # Compatibilidad multiplataforma para terminar procesos
                if self.is_windows:
                    p.terminate()  # En Windows, terminate es más confiable
                else:
                    p.terminate()  # En Linux también funciona bien
                messagebox.showinfo("Éxito", f"Proceso {pid} terminado.")
            elif accion == 'reiniciar':
                exe = p.exe()
                args = p.cmdline()
                p.terminate()
                p.wait(timeout=3)
                # Compatibilidad multiplataforma para reiniciar
                if self.is_windows:
                    import subprocess
                    subprocess.Popen([exe] + args[1:], shell=False)
                else:
                    psutil.Popen([exe] + args[1:])
                messagebox.showinfo("Éxito", f"Proceso {pid} reiniciado.")
            elif accion == 'pausar':
                if p.status() == psutil.STATUS_STOPPED:
                    p.resume()
                    messagebox.showinfo("Proceso", f"Proceso {pid} reanudado.")
                else:
                    p.suspend()
                    messagebox.showinfo("Proceso", f"Proceso {pid} pausado.")
        except psutil.NoSuchProcess:
            messagebox.showerror("Error", "El proceso ya no existe.")
        except psutil.AccessDenied:
            messagebox.showerror("Error", "Permisos insuficientes para gestionar este proceso.")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def sort_by_column(self, col):
        """Ordena la vista por la columna especificada con soporte para diferentes tipos de datos."""
        if self.sort_column == col:
            # Si ya está ordenado por esta columna, invertir el orden
            self.sort_reverse = not self.sort_reverse
        else:
            # Si es una nueva columna, ordenar de forma ascendente
            self.sort_reverse = False
        self.sort_column = col
        
        # Actualizar indicadores visuales en los encabezados
        self.update_column_headers()

        # Obtener los datos actuales en la Treeview
        data = []
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            data.append((values, child))
        
        # Función de ordenación personalizada según el tipo de columna
        def sort_key(item):
            values = item[0]
            col_index = self.get_column_index(col)
            if col_index is None:
                return ""
            
            value = values[col_index]
            
            # Convertir según el tipo de columna
            if col == "pid":
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return 0
            elif col in ["cpu", "mem"]:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            else:  # columna "nombre"
                return str(value).lower()
        
        # Ordenar los datos
        data.sort(key=sort_key, reverse=self.sort_reverse)
        
        # Reorganizar los elementos en el Treeview
        for index, (values, child) in enumerate(data):
            self.tree.move(child, '', index)

    def update_column_headers(self):
        """Actualiza los encabezados de las columnas para mostrar indicadores de ordenación."""
        column_names = {
            "pid": "PID",
            "nombre": "Nombre", 
            "cpu": "CPU (%)",
            "mem": "Memoria (MB)"
        }
        
        for col in column_names:
            header_text = column_names[col]
            if self.sort_column == col:            # Agregar indicador de dirección de ordenación
                arrow = " ↓" if self.sort_reverse else " ↑"
                header_text += arrow
            
            self.tree.heading(col, text=header_text)

    def get_column_index(self, col):
        """Devuelve el índice de la columna dado su nombre."""
        columns = ("pid", "nombre", "cpu", "mem")
        try:
            return columns.index(col)
        except ValueError:
            return None

    def seleccionar_proceso_por_pid(self, pid):
        """Selecciona un proceso específico por su PID en la lista"""
        # Buscar el elemento con el PID especificado
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            if str(values[0]) == str(pid):  # Comparar PIDs como strings                # Limpiar selección actual
                self.tree.selection_remove(self.tree.selection())
                # Seleccionar el proceso encontrado
                self.tree.selection_set(child)
                # Hacer scroll para que sea visible
                self.tree.see(child)
                # Resaltar visualmente (opcional)
                self.tree.focus(child)
                return True
        return False
        return False
