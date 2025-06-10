import tkinter as tk
from tkinter import ttk

class GestorTemas:
    def __init__(self):
        self.tema_actual = 'claro'
        self.temas = {
            'claro': {
                'nombre': 'Tema Claro',
                'colores': {
                    'fondo_principal': '#ffffff',
                    'fondo_secundario': '#f5f5f5',
                    'fondo_input': '#ffffff',
                    'texto_principal': '#000000',
                    'texto_secundario': '#333333',
                    'texto_deshabilitado': '#888888',
                    'borde': '#cccccc',
                    'acento': '#0078d4',
                    'acento_hover': '#106ebe',
                    'alerta_alta': '#d13438',
                    'alerta_media': '#ff8c00',
                    'alerta_baja': '#ffd700',
                    'exito': '#107c10',
                    'header': '#f0f0f0',
                    'seleccion': '#e3f2fd'
                }
            },
            'oscuro': {
                'nombre': 'Tema Oscuro',
                'colores': {
                    'fondo_principal': '#2d2d2d',
                    'fondo_secundario': '#404040',
                    'fondo_input': '#3c3c3c',
                    'texto_principal': '#ffffff',
                    'texto_secundario': '#e0e0e0',
                    'texto_deshabilitado': '#888888',
                    'borde': '#555555',
                    'acento': '#0078d4',
                    'acento_hover': '#106ebe',
                    'alerta_alta': '#ff6b6b',
                    'alerta_media': '#ffa726',
                    'alerta_baja': '#ffeb3b',
                    'exito': '#66bb6a',
                    'header': '#1e1e1e',
                    'seleccion': '#0d47a1'
                }
            },
            'sistema': {
                'nombre': 'Tema del Sistema',
                'colores': {
                    # Colores seguros que funcionan en todos los sistemas
                    'fondo_principal': '#f0f0f0',
                    'fondo_secundario': '#e0e0e0',
                    'fondo_input': '#ffffff',
                    'texto_principal': '#000000',
                    'texto_secundario': '#333333',
                    'texto_deshabilitado': '#888888',
                    'borde': '#cccccc',
                    'acento': '#0078d4',
                    'acento_hover': '#106ebe',
                    'alerta_alta': '#d32f2f',
                    'alerta_media': '#f57500',
                    'alerta_baja': '#fbc02d',
                    'exito': '#388e3c',
                    'header': '#f0f0f0',
                    'seleccion': '#e3f2fd'
                }
            }
        }
        
        # Estilos TTK para cada tema
        self.estilos_ttk = {
            'claro': {
                'TLabel': {
                    'configure': {'background': '#ffffff', 'foreground': '#000000'}
                },
                'TFrame': {
                    'configure': {'background': '#ffffff'}
                },
                'TButton': {
                    'configure': {
                        'background': '#f0f0f0',
                        'foreground': '#000000',
                        'borderwidth': 1,
                        'relief': 'raised'
                    },
                    'map': {
                        'background': [('active', '#e0e0e0'), ('pressed', '#d0d0d0')]
                    }
                },
                'TEntry': {
                    'configure': {
                        'fieldbackground': '#ffffff',
                        'foreground': '#000000',
                        'borderwidth': 1
                    }
                },
                'Treeview': {
                    'configure': {
                        'background': '#ffffff',
                        'foreground': '#000000',
                        'fieldbackground': '#ffffff'
                    },
                    'map': {
                        'background': [('selected', '#e3f2fd')],
                        'foreground': [('selected', '#000000')]
                    }
                },
                'Treeview.Heading': {
                    'configure': {
                        'background': '#f0f0f0',
                        'foreground': '#000000',
                        'relief': 'raised'
                    }
                }
            },
            'oscuro': {
                'TLabel': {
                    'configure': {'background': '#2d2d2d', 'foreground': '#ffffff'}
                },
                'TFrame': {
                    'configure': {'background': '#2d2d2d'}
                },
                'TButton': {
                    'configure': {
                        'background': '#404040',
                        'foreground': '#ffffff',
                        'borderwidth': 1,
                        'relief': 'raised'
                    },
                    'map': {
                        'background': [('active', '#555555'), ('pressed', '#333333')]
                    }
                },
                'TEntry': {
                    'configure': {
                        'fieldbackground': '#3c3c3c',
                        'foreground': '#ffffff',
                        'borderwidth': 1
                    }
                },
                'Treeview': {
                    'configure': {
                        'background': '#2d2d2d',
                        'foreground': '#ffffff',
                        'fieldbackground': '#2d2d2d'
                    },
                    'map': {
                        'background': [('selected', '#0d47a1')],
                        'foreground': [('selected', '#ffffff')]
                    }
                },
                'Treeview.Heading': {
                    'configure': {
                        'background': '#1e1e1e',
                        'foreground': '#ffffff',
                        'relief': 'raised'
                    }
                }
            }
        }
    
    def detectar_tema_sistema(self):
        """Detecta si el sistema usa tema claro u oscuro"""
        try:
            # En Linux, intentar detectar el tema del sistema
            import subprocess
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], 
                                  capture_output=True, text=True)
            if 'dark' in result.stdout.lower():
                return 'oscuro'
            else:
                return 'claro'
        except:
            # Por defecto, usar tema claro
            return 'claro'
    
    def aplicar_tema(self, root, nombre_tema):
        """Aplica un tema a la ventana principal y sus widgets"""
        if nombre_tema == 'sistema':
            tema_real = self.detectar_tema_sistema()
        else:
            tema_real = nombre_tema
        
        if tema_real not in self.temas:
            print(f"Tema '{tema_real}' no encontrado, usando tema claro")
            tema_real = 'claro'
        
        colores = self.temas[tema_real]['colores']
        
        # Aplicar colores a la ventana principal
        root.configure(bg=colores['fondo_principal'])
        
        # Configurar estilo TTK
        style = ttk.Style()
        
        if tema_real in self.estilos_ttk:
            for widget_class, config in self.estilos_ttk[tema_real].items():
                if 'configure' in config:
                    style.configure(widget_class, **config['configure'])
                if 'map' in config:
                    style.map(widget_class, **config['map'])
        
        # Actualizar widgets existentes
        self._aplicar_tema_recursivo(root, colores)
        
        self.tema_actual = tema_real
        print(f"Tema aplicado: {self.temas[tema_real]['nombre']}")
        
        return colores
    
    def _aplicar_tema_recursivo(self, widget, colores):
        """Aplica tema recursivamente a todos los widgets hijo"""
        try:
            # Obtener tipo de widget
            widget_class = widget.winfo_class()
            
            # Aplicar colores según el tipo de widget
            if widget_class in ['Frame', 'Toplevel']:
                widget.configure(bg=colores['fondo_principal'])
            elif widget_class == 'Label':
                widget.configure(
                    bg=colores['fondo_principal'],
                    fg=colores['texto_principal']
                )
            elif widget_class == 'Button':
                widget.configure(
                    bg=colores['fondo_secundario'],
                    fg=colores['texto_principal'],
                    activebackground=colores['acento_hover'],
                    activeforeground=colores['texto_principal']
                )
            elif widget_class == 'Entry':
                widget.configure(
                    bg=colores['fondo_input'],
                    fg=colores['texto_principal'],
                    insertbackground=colores['texto_principal']
                )
            elif widget_class == 'Text':
                widget.configure(
                    bg=colores['fondo_input'],
                    fg=colores['texto_principal'],
                    insertbackground=colores['texto_principal']
                )
            elif widget_class == 'Listbox':
                widget.configure(
                    bg=colores['fondo_input'],
                    fg=colores['texto_principal'],
                    selectbackground=colores['seleccion']
                )
            
            # Aplicar recursivamente a widgets hijo
            for child in widget.winfo_children():
                self._aplicar_tema_recursivo(child, colores)
                
        except Exception as e:
            # Ignorar errores de widgets que no soportan ciertos atributos
            pass
    
    def obtener_color(self, nombre_tema, color_key):
        """Obtiene un color específico de un tema"""
        if nombre_tema == 'sistema':
            nombre_tema = self.detectar_tema_sistema()
        
        if nombre_tema in self.temas:
            return self.temas[nombre_tema]['colores'].get(color_key, '#000000')
        return '#000000'
    
    def obtener_temas_disponibles(self):
        """Retorna lista de temas disponibles"""
        return [(key, self.temas[key]['nombre']) for key in self.temas.keys()]
    
    def crear_ventana_configuracion_tema(self, parent, configuracion, callback_guardar):
        """Crea ventana para configurar temas"""
        ventana_tema = tk.Toplevel(parent)
        ventana_tema.title("Configuración de Tema")
        ventana_tema.geometry("500x450")
        ventana_tema.resizable(True, True)
        ventana_tema.transient(parent)
        ventana_tema.grab_set()
        
        # Frame principal
        frame_principal = ttk.Frame(ventana_tema, padding=20)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(frame_principal, text="Selección de Tema", 
                          font=("Arial", 14, "bold"))
        titulo.pack(pady=(0, 20))
        
        # Variable para el tema seleccionado
        tema_var = tk.StringVar(value=configuracion.get('interfaz', {}).get('tema', 'claro'))
        
        # Frame para los radiobuttons
        frame_temas = ttk.LabelFrame(frame_principal, text="Temas Disponibles", padding=10)
        frame_temas.pack(fill=tk.X, pady=(0, 20))
        
        # Radiobuttons para cada tema
        for tema_key, tema_nombre in self.obtener_temas_disponibles():
            rb = ttk.Radiobutton(frame_temas, text=tema_nombre, 
                               variable=tema_var, value=tema_key,
                               command=lambda: actualizar_preview())
            rb.pack(anchor=tk.W, pady=2)
        
        # Frame para vista previa
        frame_preview = ttk.LabelFrame(frame_principal, text="Vista Previa", padding=10)
        frame_preview.pack(fill=tk.X, pady=(0, 20))
        
        def actualizar_preview():
            tema_seleccionado = tema_var.get()
            colores = self.temas.get(tema_seleccionado, self.temas['claro'])['colores']
            
            # Limpiar preview anterior
            for widget in frame_preview.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.destroy()
            
            # Crear muestra de colores más completa
            muestra_frame = tk.Frame(frame_preview, bg=colores['fondo_principal'], 
                                   relief=tk.RAISED, borderwidth=2, padx=10, pady=8)
            muestra_frame.pack(fill=tk.X, pady=5)
            
            # Mostrar diferentes elementos de la interfaz
            tk.Label(muestra_frame, text="Fondo principal", 
                    bg=colores['fondo_principal'], fg=colores['texto_principal'],
                    font=("Arial", 10, "bold")).pack(pady=2)
            
            tk.Label(muestra_frame, text="Texto secundario en fondo secundario", 
                    bg=colores['fondo_secundario'], fg=colores['texto_secundario'],
                    relief=tk.SUNKEN, padx=5, pady=2).pack(pady=2, fill=tk.X)
            
            # Frame para mostrar colores de alerta
            alert_frame = tk.Frame(muestra_frame, bg=colores['fondo_principal'])
            alert_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(alert_frame, text="Alta", bg=colores['alerta_alta'], 
                    fg="white", width=8, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
            tk.Label(alert_frame, text="Media", bg=colores['alerta_media'], 
                    fg="white", width=8, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
            tk.Label(alert_frame, text="Baja", bg=colores['alerta_baja'], 
                    fg="black", width=8, font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=2)
        
        # Preview inicial
        actualizar_preview()
        
        # Botones
        frame_botones = ttk.Frame(frame_principal)
        frame_botones.pack(fill=tk.X, pady=(20, 0))
        
        def aplicar_tema():
            """Aplica el tema seleccionado sin cerrar la ventana"""
            tema_seleccionado = tema_var.get()
            configuracion['interfaz']['tema'] = tema_seleccionado
            if callback_guardar(configuracion):
                # Aplicar tema inmediatamente
                self.aplicar_tema(parent, tema_seleccionado)
                # Actualizar preview
                actualizar_preview()
        
        def aplicar_y_cerrar():
            configuracion['interfaz']['tema'] = tema_var.get()
            if callback_guardar(configuracion):
                # Aplicar tema inmediatamente
                self.aplicar_tema(parent, tema_var.get())
                ventana_tema.destroy()
        
        # Organizar botones de derecha a izquierda: Cancelar, Aplicar, Aplicar y Cerrar
        ttk.Button(frame_botones, text="Aplicar y Cerrar", 
                  command=aplicar_y_cerrar).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(frame_botones, text="Aplicar", 
                  command=aplicar_tema).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(frame_botones, text="Cancelar", 
                  command=ventana_tema.destroy).pack(side=tk.RIGHT)

# Función de conveniencia
def aplicar_tema_desde_config(root, configuracion):
    """Aplica tema basado en la configuración"""
    gestor = GestorTemas()
    tema = configuracion.get('interfaz', {}).get('tema', 'claro')
    colores = gestor.aplicar_tema(root, tema)
    return colores, gestor
