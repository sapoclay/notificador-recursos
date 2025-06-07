import tkinter as tk
from tkinter import ttk
import webbrowser
import os
from PIL import Image, ImageTk

class VentanaAbout:
    def __init__(self, parent):
        self.parent = parent
        self.create_about_window()
    
    def create_about_window(self):
        # Crear ventana About
        self.about_window = tk.Toplevel(self.parent)
        self.about_window.title("About - ¿Quién se come los recursos?")
        self.about_window.geometry("450x650")  
        self.about_window.resizable(False, False)
        
        # Centrar la ventana
        self.about_window.transient(self.parent)
        self.about_window.grab_set()
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.about_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cargar y mostrar el icono
        self.load_icon(main_frame)
        
        # Título del programa
        title_label = ttk.Label(main_frame, text="¿Quién se come los recursos?", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Versión
        version_label = ttk.Label(main_frame, text="Versión 0.1.2", 
                                 font=("Arial", 11))
        version_label.pack(pady=5)
        
        # Descripción
        desc_text = """Monitor de recursos del sistema en tiempo real.

Identifica procesos que consumen excesivamente 
CPU y memoria, te permite gestionarlos y 
mantiene un monitoreo continuo desde la 
bandeja del sistema.

Características principales:
• Umbrales configurables de CPU y memoria
• Notificaciones automáticas de alertas
• Gestión completa de procesos (cerrar/pausar/reiniciar)
• Integración con bandeja del sistema
• Monitoreo en tiempo real cada 3 segundos"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, 
                              font=("Arial", 10), justify=tk.CENTER)
        desc_label.pack(pady=20)
        
        # Información del autor
        author_label = ttk.Label(main_frame, text="Creado con ☕ y 🚬 para optimizar tu sistema", 
                                font=("Arial", 10, "italic"))
        author_label.pack(pady=10)
        
        # Enlace al repositorio GitHub
        self.create_github_section(main_frame)
        
        # Botón cerrar
        close_btn = ttk.Button(main_frame, text="Cerrar", 
                              command=self.about_window.destroy)
        close_btn.pack(pady=20)
    
    def load_icon(self, parent_frame):
        """Carga y muestra el icono de la aplicación"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'img', 'vitamina.png')
            # Redimensionar imagen para la ventana About
            pil_image = Image.open(icon_path)
            pil_image = pil_image.resize((80, 80), Image.LANCZOS)  # Tamaño un poco más grande
            photo = ImageTk.PhotoImage(pil_image)
            
            icon_label = ttk.Label(parent_frame, image=photo)
            icon_label.image = photo  # Mantener referencia
            icon_label.pack(pady=15)
        except Exception as e:
            print(f"No se pudo cargar el icono en About: {e}")
            # Mostrar un placeholder si no se puede cargar la imagen
            placeholder_label = ttk.Label(parent_frame, text="🐸", 
                                        font=("Arial", 40))
            placeholder_label.pack(pady=15)
    
    def create_github_section(self, parent_frame):
        """Crea la sección del enlace a GitHub"""
        print("DEBUG: Creando sección de GitHub")  # Debug
        
        # Frame para la sección de GitHub con un borde visible para debug
        github_frame = ttk.LabelFrame(parent_frame, text="Código Fuente", padding=10)
        github_frame.pack(pady=15, fill=tk.X)
        
        # Título de la sección
        github_title = ttk.Label(github_frame, text="Repositorio GitHub:", 
                                font=("Arial", 11, "bold"))
        github_title.pack(pady=(0, 10))
        
        # Enlace clickeable con mayor visibilidad
        github_link = tk.Label(github_frame, 
                              text="🔗 https://github.com/sapoclay/notificador-recursos/",
                              font=("Arial", 11, "underline"),
                              fg="#0066cc", 
                              bg="white",
                              cursor="hand2",
                              relief="solid",
                              borderwidth=1,
                              padx=10,
                              pady=5)
        github_link.pack(pady=5, fill=tk.X)
        
        # Función para abrir el enlace
        def open_github(event):
            try:
                webbrowser.open("https://github.com/sapoclay/notificador-recursos/")
                print("DEBUG: Abriendo enlace de GitHub")  # Debug
            except Exception as e:
                print(f"ERROR: No se pudo abrir el enlace: {e}")  # Debug
        
        github_link.bind("<Button-1>", open_github)
        
        # Cambiar color al pasar el mouse
        def on_enter(event):
            github_link.config(bg="#f0f0f0")
        
        def on_leave(event):
            github_link.config(bg="white")
        
        github_link.bind("<Enter>", on_enter)
        github_link.bind("<Leave>", on_leave)
        
        # Información adicional
        info_label = ttk.Label(github_frame, 
                              text="Haz clic en el enlace para visitar el repositorio y ver el código",
                              font=("Arial", 9), 
                              foreground="gray")
        info_label.pack(pady=(5, 0))
        
        print("DEBUG: Sección de GitHub creada exitosamente")  # Debug

def mostrar_about(parent):
    """Función para mostrar la ventana About"""
    VentanaAbout(parent)
