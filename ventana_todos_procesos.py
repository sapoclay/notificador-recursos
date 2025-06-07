import tkinter as tk
from tkinter import ttk, messagebox
import psutil

class VentanaTodosProcesos:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.tree = ttk.Treeview(self.frame, columns=("pid", "nombre", "cpu", "mem"), show="headings")
        self.tree.heading("pid", text="PID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("cpu", text="CPU (%)")
        self.tree.heading("mem", text="Memoria (MB)")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.menu = tk.Menu(self.frame, tearoff=0)
        self.menu.add_command(label="Cerrar", command=lambda: self.menu_accion_proceso('cerrar'))
        self.menu.add_command(label="Reiniciar", command=lambda: self.menu_accion_proceso('reiniciar'))
        self.menu.add_command(label="Pausar/Continuar", command=lambda: self.menu_accion_proceso('pausar'))
        self.tree.bind("<Button-3>", self.mostrar_menu)
        self.update_all_processes()

    def mostrar_menu(self, event):
        if self.tree.identify_row(event.y):
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.menu.tk_popup(event.x_root, event.y_root)

    def update_all_processes(self):
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
        self.frame.after(5000, self.update_all_processes)

    def menu_accion_proceso(self, accion):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un proceso.")
            return
        pid = self.tree.item(sel[0])['values'][0]
        try:
            p = psutil.Process(pid)
            if accion == 'cerrar':
                p.terminate()
                messagebox.showinfo("Éxito", f"Proceso {pid} terminado.")
            elif accion == 'reiniciar':
                exe = p.exe()
                args = p.cmdline()
                p.terminate()
                p.wait(timeout=3)
                psutil.Popen([exe] + args[1:])
                messagebox.showinfo("Éxito", f"Proceso {pid} reiniciado.")
            elif accion == 'pausar':
                if p.status() == psutil.STATUS_STOPPED:
                    p.resume()
                    messagebox.showinfo("Proceso", f"Proceso {pid} reanudado.")
                else:
                    p.suspend()
                    messagebox.showinfo("Proceso", f"Proceso {pid} pausado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
