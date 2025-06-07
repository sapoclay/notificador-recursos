import tkinter as tk
from tkinter import ttk, messagebox

class VentanaAlertas:
    def __init__(self, parent, cpu_threshold, mem_threshold, cerrar_cb, reiniciar_cb, pausar_cb):
        self.parent = parent
        self.cpu_threshold = cpu_threshold
        self.mem_threshold = mem_threshold
        self.cerrar_cb = cerrar_cb
        self.reiniciar_cb = reiniciar_cb
        self.pausar_cb = pausar_cb
        self.frame = ttk.Frame(parent, padding=10)
        umbral_frame = ttk.LabelFrame(self.frame, text="Umbrales de Alerta")
        umbral_frame.pack(fill=tk.X, pady=5)
        ttk.Label(umbral_frame, text="CPU (%)").pack(side=tk.LEFT)
        ttk.Entry(umbral_frame, textvariable=self.cpu_threshold, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(umbral_frame, text="Memoria (MB)").pack(side=tk.LEFT, padx=(10,0))
        ttk.Entry(umbral_frame, textvariable=self.mem_threshold, width=7).pack(side=tk.LEFT, padx=5)
        self.tree = ttk.Treeview(self.frame, columns=("pid", "nombre", "cpu", "mem"), show="headings")
        self.tree.heading("pid", text="PID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("cpu", text="CPU (%)")
        self.tree.heading("mem", text="Memoria (MB)")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Cerrar Proceso", command=self.cerrar_cb).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reiniciar Proceso", command=self.reiniciar_cb).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Pausar/Continuar Proceso", command=self.pausar_cb).pack(side=tk.LEFT, padx=5)
